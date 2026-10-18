// CrispDock — marketing site (Cloudflare Worker + static assets).
// Serves public/, fills the page's {{…}} placeholders from wrangler vars, and keeps
// /download pointing at the current installer.

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
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);
    const live = url.hostname === "crispdock.com" || url.hostname === "www.crispdock.com";
    // One canonical address: https://crispdock.com (plain http and www both redirect).
    if (live && (url.protocol === "http:" || url.hostname === "www.crispdock.com")) {
      url.protocol = "https:";
      url.hostname = "crispdock.com";
      return Response.redirect(url.toString(), 301);
    }
    return withHeaders(await route(request, env, url), url, live);
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
        .replaceAll(" data-checkout-soon hidden", " data-checkout-soon");
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
