// CrispDock — marketing site (Cloudflare Worker + static assets).
// Serves public/, fills the page's {{…}} placeholders from wrangler vars, keeps
// /download pointing at the current installer, and counts page views and downloads per day
// (traffic_daily in the licence server's D1; no cookies, no IPs, no JavaScript needed).

export interface Env {
  ASSETS: Fetcher;
  PRINTBRIDGE_VERSION: string;
  /** File name under public/downloads/, e.g. "CrispDock-1.2.0.pkg". */
  DOWNLOAD_FILE: string;
  /** Shown on the download button, e.g. "3.1 MB". */
  DOWNLOAD_SIZE: string;
  /**
   * Licence server base URL. Buy buttons link to <base>/checkout?plan=…, "Manage subscription"
   * to <base>/account. Empty (or not an http(s) URL) = checkout shown as "opens soon".
   */
  CHECKOUT_BASE?: string;
  SUPPORT_EMAIL?: string;
  /**
   * The licence server's D1 ("printbridge-license"); only traffic_daily is written here
   * (migrations live in zp505-mac-bridge/license-server/migrations). Missing = nothing counted.
   */
  DB?: D1Database;
}

export default {
  async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
    const url = new URL(request.url);
    const live = url.hostname === "crispdock.com" || url.hostname === "www.crispdock.com";
    // One canonical address: https://crispdock.com (plain http and www both redirect).
    if (live && (url.protocol === "http:" || url.hostname === "www.crispdock.com")) {
      url.protocol = "https:";
      url.hostname = "crispdock.com";
      return Response.redirect(url.toString(), 301);
    }
    const response = withHeaders(await route(request, env, url), url, live);
    const hit = env.DB ? trafficHit(request, url, response) : null;
    if (hit) ctx.waitUntil(countTraffic(env.DB!, hit));
    return response;
  },
};

async function route(request: Request, env: Env, url: URL): Promise<Response> {
  if (url.pathname === "/download" || url.pathname === "/download/") {
    return Response.redirect(new URL(downloadPath(env), url).toString(), 302);
  }
  if (url.pathname === "/health") {
    return Response.json({ ok: true, version: env.PRINTBRIDGE_VERSION });
  }
  if (url.pathname === "/" || url.pathname === "/index.html") {
    // Ask for "/" — the assets layer redirects "/index.html" to "/", which would leave us
    // with an empty redirect body.
    const page = await env.ASSETS.fetch(new Request(new URL("/", url), request));
    const base = checkoutBase(env.CHECKOUT_BASE);
    let html = (await page.text())
      .replaceAll("{{VERSION}}", escape(env.PRINTBRIDGE_VERSION))
      .replaceAll("{{DOWNLOAD_URL}}", "/download")
      .replaceAll("{{DOWNLOAD_SIZE}}", escape(env.DOWNLOAD_SIZE))
      .replaceAll("{{CHECKOUT_BASE}}", escape(base))
      .replaceAll("{{SUPPORT_EMAIL}}", escape(env.SUPPORT_EMAIL ?? ""));
    if (!base) {
      // No checkout yet: render the "opens soon" state here too, so it holds without JS.
      html = html
        .replace(/ href="\/checkout\?plan=[a-z]+"( data-checkout)/g, ' aria-disabled="true"$1')
        .replaceAll(" data-checkout-soon hidden", " data-checkout-soon")
        // …and no account to sign in to: drop the "Sign in" / "Account" links.
        .replace(/\s*<a [^>]*data-account-link[^>]*>[\s\S]*?<\/a>/g, "");
    }
    return new Response(html, {
      headers: { "content-type": "text/html; charset=utf-8", "cache-control": "public, max-age=60" },
    });
  }
  const asset = await env.ASSETS.fetch(request);
  if (asset.status !== 404 || request.method !== "GET") return asset;
  // Friendly 404 page instead of an empty response.
  const notFound = await env.ASSETS.fetch(new Request(new URL("/404", url), request));
  return new Response(notFound.body, { status: 404, headers: { "content-type": "text/html; charset=utf-8", "cache-control": "public, max-age=60" } });
}

/** Security headers everywhere; longer browser caching for images and fonts. */
function withHeaders(response: Response, url: URL, live: boolean): Response {
  const out = new Response(response.body, response);
  const h = out.headers;
  if (live) h.set("Strict-Transport-Security", "max-age=31536000");
  h.set("X-Content-Type-Options", "nosniff");
  h.set("Referrer-Policy", "strict-origin-when-cross-origin");
  h.set("X-Frame-Options", "SAMEORIGIN");
  if (response.status === 200) {
    if (url.pathname.startsWith("/fonts/")) h.set("Cache-Control", "public, max-age=31536000, immutable");
    else if (url.pathname.startsWith("/assets/")) h.set("Cache-Control", "public, max-age=604800, stale-while-revalidate=86400");
    else if (/\.(css|js)$/.test(url.pathname)) h.set("Cache-Control", "public, max-age=3600, stale-while-revalidate=86400");
  }
  return out;
}

// ---------------------------------------------------------------- funnel counters

interface TrafficHit {
  kind: "view" | "download";
  path: string;
  source: string;
  campaign: string;
}

const BOT_UA = /bot|crawl|spider|slurp|preview|monitor|curl|wget|python|headless/i;

/**
 * What this request adds to traffic_daily, or null. Views: GET of an HTML page (200, or the
 * 404 page as "(404)" so scanners don't fill the table). Downloads: /download, path = the page
 * of this site the click came from ("/download" when unknown). Bots, link previews and
 * browser prefetches aren't counted. Source: utm_source, else (downloads) the src tag that
 * script.js adds, else the referring site's host ('' = typed in, bookmark or a click on this site).
 */
function trafficHit(request: Request, url: URL, response: Response): TrafficHit | null {
  if (request.method !== "GET") return null;
  const ua = request.headers.get("User-Agent") ?? "";
  if (!ua || BOT_UA.test(ua)) return null;
  const purpose = request.headers.get("Sec-Purpose") ?? request.headers.get("Purpose") ?? "";
  if (/prefetch|prerender/i.test(purpose)) return null;

  const download = url.pathname === "/download" || url.pathname === "/download/";
  const referer = referrerOf(request, url);
  let path: string;
  if (download) {
    path = referer?.sameSite ? pagePath(referer.url.pathname) : "/download";
  } else {
    if (response.status !== 200 && response.status !== 404) return null;
    if (!(response.headers.get("Content-Type") ?? "").startsWith("text/html")) return null;
    path = response.status === 404 ? "(404)" : pagePath(url.pathname);
  }
  const campaign = dim(url.searchParams.get("utm_campaign"));
  let source = dim(url.searchParams.get("utm_source"));
  if (!source && download) source = dim(url.searchParams.get("src"));
  if (!source && referer && !referer.sameSite) source = dim(referer.host);
  return { kind: download ? "download" : "view", path, source, campaign };
}

/** "/privacy.html", "/privacy/" → "/privacy"; "/index.html" → "/". */
function pagePath(pathname: string): string {
  const path = pathname.toLowerCase().replace(/\.html$/, "").replace(/\/index$/, "/").replace(/(.)\/+$/, "$1");
  return path.slice(0, 80) || "/";
}

/**
 * The Referer, its host without "www.", and whether it's this site. api.crispdock.com counts
 * as another site: its purchase and account pages link to /download.
 */
function referrerOf(request: Request, url: URL): { url: URL; host: string; sameSite: boolean } | null {
  const header = request.headers.get("Referer");
  if (!header) return null;
  try {
    const ref = new URL(header);
    const host = ref.hostname.toLowerCase().replace(/^www\./, "");
    return { url: ref, host, sameSite: host === url.hostname.toLowerCase().replace(/^www\./, "") };
  } catch {
    return null;
  }
}

/** A dimension as stored: trimmed, lower-case, printable, short; '' when empty. */
function dim(value: string | null): string {
  return String(value ?? "").trim().toLowerCase().replace(/[^\x21-\x7e]+/g, "_").slice(0, 64);
}

/** +1 on today's row. Runs after the response (waitUntil); a DB error only gets logged. */
async function countTraffic(db: D1Database, hit: TrafficHit): Promise<void> {
  try {
    await db.prepare(
      `INSERT INTO traffic_daily (day, kind, path, source, campaign, count) VALUES (?, ?, ?, ?, ?, 1)
       ON CONFLICT (day, kind, path, source, campaign) DO UPDATE SET count = count + 1`,
    ).bind(new Date().toISOString().slice(0, 10), hit.kind, hit.path, hit.source, hit.campaign).run();
  } catch (error) {
    console.error("traffic: count failed", hit.kind, error);
  }
}

// ----------------------------------------------------------------

function downloadPath(env: Env): string {
  return `/downloads/${encodeURIComponent(env.DOWNLOAD_FILE)}`;
}

/** Normalises CHECKOUT_BASE to "scheme://host[/path]" without a trailing slash; "" if unusable. */
function checkoutBase(raw: string | undefined): string {
  const value = (raw ?? "").trim();
  if (!value) return "";
  let url: URL;
  try {
    url = new URL(value);
  } catch {
    return "";
  }
  if (url.protocol !== "https:" && url.protocol !== "http:") return "";
  if (url.username || url.password || url.search || url.hash) return "";
  return url.origin + url.pathname.replace(/\/+$/, "");
}

function escape(value: string): string {
  return value.replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]!);
}
