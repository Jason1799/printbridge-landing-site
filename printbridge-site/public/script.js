(() => {
  const PLACEHOLDER_ID = 'EXTENSION_ID_PLACEHOLDER';
  const warning = document.getElementById('placeholder-warning');
  const releaseNodes = document.querySelectorAll('#release-version');
  const webstoreButtons = document.querySelectorAll('a[href*=\"chrome.google.com/webstore/detail/\"]');

  function humanFileSize(bytes) {
    if (typeof bytes !== 'number' || Number.isNaN(bytes) || bytes <= 0) return 'Unknown';
    const units = ['B', 'KB', 'MB', 'GB'];
    let size = bytes;
    let unit = 0;
    while (size >= 1024 && unit < units.length - 1) {
      size /= 1024;
      unit += 1;
    }
    return `${size.toFixed(unit === 0 ? 0 : size >= 10 ? 1 : 2)} ${units[unit]}`;
  }

  async function hydrateHealth() {
    try {
      const resp = await fetch('/health', { cache: 'no-store' });
      if (!resp.ok) return;
      const payload = await resp.json();
      const { extensionId, version } = payload || {};
      if (version) {
        releaseNodes.forEach((node) => {
          node.textContent = String(version);
        });
      }
      if (extensionId && extensionId === PLACEHOLDER_ID && warning) {
        warning.removeAttribute('hidden');
      }
      if (extensionId && webstoreButtons.length) {
        webstoreButtons.forEach((btn) => {
          const url = extensionId === PLACEHOLDER_ID
            ? 'https://chrome.google.com/webstore/detail/EXTENSION_ID_PLACEHOLDER'
            : `https://chrome.google.com/webstore/detail/${extensionId}`;
          btn.href = url;
        });
      }
    } catch {
      // keep static content on page as fallback
    }
  }

  async function hydrateFileSize() {
    const links = document.querySelectorAll('[data-size]');
    await Promise.all(Array.from(links).map(async (link) => {
      const url = link.getAttribute('data-size');
      const label = link.querySelector('.size');
      if (!url || !label) return;
      try {
        const resp = await fetch(url, { method: 'HEAD' });
        const size = Number(resp.headers.get('content-length'));
        label.textContent = humanFileSize(size);
      } catch {
        label.textContent = 'Unable to get size';
      }
    }));
  }

  async function scrollToRouteTarget() {
    const path = window.location.pathname;
    const hash = window.location.hash.replace('#', '');
    if (hash === 'extension-guide') {
      const target = document.getElementById('extension-guide');
      if (target) target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
    if (hash === 'files') {
      const target = document.getElementById('files');
      if (target) target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
    if (path === '/chrome-extension') {
      const target = document.getElementById('extension-guide');
      if (target) target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
    if (path === '/download' || path === '/download/') {
      const target = document.getElementById('files');
      if (target) target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }

  hydrateHealth();
  hydrateFileSize();
  scrollToRouteTarget();
})();
