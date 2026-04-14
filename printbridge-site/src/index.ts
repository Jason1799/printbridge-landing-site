export interface Env {
  ASSETS: Fetcher;
  PRINTBRIDGE_EXTENSION_ID: string;
  PRINTBRIDGE_VERSION: string;
  DOWNLOAD_DMG: string;
  DOWNLOAD_ZIP: string;
  DOWNLOAD_DMG_URL: string;
  DOWNLOAD_ZIP_URL: string;
}

const PLACEHOLDER_PAGES = new Set(['/']);

const PLACEHOLDER_EXT_ID = 'EXTENSION_ID_PLACEHOLDER';
const FALLBACK_DMG = 'PrintBridge for Zebra Installer.dmg';
const FALLBACK_ZIP = 'PrintBridge for Zebra Installer.zip';
const FALLBACK_VERSION = '0.4.2';
const PLACEHOLDER_DOWNLOAD_URLS = [
  'https://example.com',
  'https://example.com/PrintBridge%20for%20Zebra%20Installer.dmg',
  'https://example.com/PrintBridge%20for%20Zebra%20Installer.zip',
];

function resolveExtensionId(env: Env): string {
  return (env?.PRINTBRIDGE_EXTENSION_ID || PLACEHOLDER_EXT_ID).trim() || PLACEHOLDER_EXT_ID;
}

function resolveVersion(env: Env): string {
  return (env?.PRINTBRIDGE_VERSION || FALLBACK_VERSION).trim() || FALLBACK_VERSION;
}

function resolveDownloadFile(env: Env, key: 'dmg' | 'zip'): string {
  if (key === 'zip') {
    return (env?.DOWNLOAD_ZIP || FALLBACK_ZIP).trim() || FALLBACK_ZIP;
  }
  return (env?.DOWNLOAD_DMG || FALLBACK_DMG).trim() || FALLBACK_DMG;
}

function resolveDownloadUrl(env: Env, key: 'dmg' | 'zip'): string {
  const rawUrl = (key === 'zip' ? env?.DOWNLOAD_ZIP_URL : env?.DOWNLOAD_DMG_URL) || '';
  const normalized = rawUrl.trim();
  if (normalized && !PLACEHOLDER_DOWNLOAD_URLS.includes(normalized)) {
    return normalized;
  }
  return key === 'zip' ? '/download/zip' : '/download/dmg';
}

function isValidAssetBinding(value: unknown): value is Fetcher {
  return Boolean(value && typeof (value as Fetcher).fetch === 'function');
}

async function safeFetchAssets(env: Env, request: Request): Promise<Response | null> {
  if (!isValidAssetBinding((env as Env).ASSETS)) {
    return null;
  }
  try {
    return await (env as Env).ASSETS.fetch(new URL(request.url).toString());
  } catch {
    return null;
  }
}

async function serveDownloadAsset(
  env: Env,
  request: Request,
  fileName: string,
  defaultLabel: string,
): Promise<Response> {
  const publicPath = `/downloads/${fileName || defaultLabel}`;
  const fileReq = new Request(new URL(publicPath, request.url).toString(), request);
  const localResponse = await safeFetchAssets(env, fileReq);
  if (localResponse && localResponse.status !== 404) {
    return localResponse;
  }
  return new Response(`Download is not available yet: ${defaultLabel}

You can still host the installer file elsewhere and set DOWNLOAD_DMG_URL / DOWNLOAD_ZIP_URL in wrangler.toml.
`, {
    status: 404,
    headers: { 'content-type': 'text/plain; charset=utf-8' },
  });
}

function injectPageVariables(html: string, env: Env): string {
  const extensionId = resolveExtensionId(env);
  const webstoreUrl = extensionId === PLACEHOLDER_EXT_ID
    ? 'https://chrome.google.com/webstore/detail/EXTENSION_ID_PLACEHOLDER'
    : `https://chrome.google.com/webstore/detail/${extensionId}`;
  const version = resolveVersion(env);
  const dmg = resolveDownloadFile(env, 'dmg');
  const zip = resolveDownloadFile(env, 'zip');
  return html
    .replaceAll('__EXTENSION_ID__', extensionId)
    .replaceAll('__WEBSTORE_URL__', webstoreUrl)
    .replaceAll('__APP_VERSION__', version)
    .replaceAll('__DMG_URL__', resolveDownloadUrl(env, 'dmg'))
    .replaceAll('__ZIP_URL__', resolveDownloadUrl(env, 'zip'))
    .replaceAll('__DMG_LABEL__', dmg)
    .replaceAll('__ZIP_LABEL__', zip);
}

function isPlaceholderPage(pathname: string): boolean {
  return PLACEHOLDER_PAGES.has(pathname) || pathname === '/index.html';
}

function isHealth(pathname: string): boolean {
  return pathname === '/health' || pathname === '/health/';
}

function isDownloadProxy(pathname: string): 'dmg' | 'zip' | null {
  if (pathname === '/download/dmg' || pathname === '/download/dmg/') return 'dmg';
  if (pathname === '/download/zip' || pathname === '/download/zip/') return 'zip';
  return null;
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);
    const pathname = url.pathname;

    if (pathname === '/download' || pathname === '/download/') {
      const redirectUrl = new URL('/#files', request.url).toString();
      return Response.redirect(redirectUrl, 302);
    }

    if (pathname === '/chrome-extension' || pathname === '/chrome-extension/') {
      const redirectUrl = new URL('/#extension-guide', request.url).toString();
      return Response.redirect(redirectUrl, 302);
    }

    if (isHealth(pathname)) {
      return Response.json({
        ok: true,
        service: 'printbridge-launch',
        version: resolveVersion(env),
        extensionId: resolveExtensionId(env),
        updatedAt: new Date().toISOString(),
      });
    }

    if (isPlaceholderPage(pathname)) {
      const renderedPath = '/index.html';
      const page = await safeFetchAssets(env, new Request(new URL(renderedPath, request.url).toString(), request));
      if (!page) {
        return new Response('Assets are not configured.', {
          status: 500,
          headers: { 'content-type': 'text/plain; charset=utf-8' },
        });
      }
      const html = await page.text();
      return new Response(injectPageVariables(html, env), {
        headers: { 'content-type': 'text/html; charset=utf-8' },
      });
    }

    const proxyKind = isDownloadProxy(pathname);
    if (proxyKind) {
      const target = resolveDownloadUrl(env, proxyKind);
      if (target.startsWith('/') && target.includes('/download/')) {
        const filename = proxyKind === 'dmg' ? resolveDownloadFile(env, 'dmg') : resolveDownloadFile(env, 'zip');
        const response = await serveDownloadAsset(env, request, filename, proxyKind === 'dmg' ? FALLBACK_DMG : FALLBACK_ZIP);
        if (response.status !== 404) {
          return response;
        }
        const localTarget = `/download/${proxyKind}`;
        if (target === localTarget || target === `${localTarget}/`) {
          return response;
        }
      }
      return Response.redirect(target, 302);
    }

    const response = await safeFetchAssets(env, request);
    if (!response) {
      return new Response('Not found', {
        status: 404,
        headers: { 'content-type': 'text/plain; charset=utf-8' },
      });
    }
    return response;
  },
};
