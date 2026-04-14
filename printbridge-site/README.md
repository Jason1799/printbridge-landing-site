# PrintBridge for Zebra Landing Site

This folder contains the Cloudflare Worker that hosts the public PrintBridge landing page.

## Files

- `wrangler.toml` - Worker config and defaults.
- `src/index.ts` - route logic and placeholder variable injection.
- `public/index.html` - landing page.
- `public/styles.css` - style sheet.
- `public/script.js` - page enhancements (version, file size, route jump).

## Local setup

```bash
cd printbridge-site
npm install
npm run dev
```

Open:

`http://localhost:8787/`

If you only need a static preview, open `public/index.html`.

## Deploy

1. Login Cloudflare once:

```bash
npm run whoami
```

2. Deploy:

```bash
npm run deploy
```

If `wrangler` is not on PATH:

```bash
npx wrangler deploy
```

## Route behavior

- `/` → 首页
- `/chrome-extension` → 重定向到 `/#extension-guide`
- `/download` / `/download/` → 重定向到 `/#files`
- `/health` → 健康检查 JSON
- `/download/dmg` 和 `/download/zip` → 优先返回 `public/downloads` 中对应文件；如果本地文件不存在，返回“未就绪”提示。
- other paths → 返回同名静态资源，未找到则返回 404

## Download links

Set package names and routing in `wrangler.toml`:

```toml
PRINTBRIDGE_VERSION = "0.4.2"
DOWNLOAD_DMG = "PrintBridge for Zebra Installer.dmg"
DOWNLOAD_ZIP = "PrintBridge for Zebra Installer.zip"
DOWNLOAD_DMG_URL = "/download/dmg"
DOWNLOAD_ZIP_URL = "/download/zip"
```

Optional remote fallback:

```toml
DOWNLOAD_DMG_URL = "https://你的下载文件地址/PrintBridge%20for%20Zebra%20Installer.dmg"
DOWNLOAD_ZIP_URL = "https://你的下载文件地址/PrintBridge%20for%20Zebra%20Installer.zip"
```

If set, the worker redirects `/download/dmg` and `/download/zip` to these URLs when local files are unavailable.

## File size note

Cloudflare static assets are capped at 25 MiB each in this mode. Keep installers outside `public/` for larger files.

## Notes

`wrangler.toml` uses placeholder:

`PRINTBRIDGE_EXTENSION_ID = "EXTENSION_ID_PLACEHOLDER"`

If needed, replace it with your real Chrome Web Store extension id before production deploy.
