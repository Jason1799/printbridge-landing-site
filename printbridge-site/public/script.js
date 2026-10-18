// Language switch (English default, 中文 on request or for Chinese browsers) and the
// buy buttons (disabled until CHECKOUT_BASE points at the licence server).
(() => {
  const zh = {
    "nav.features": "功能", "nav.how": "使用方法", "nav.pricing": "价格", "nav.faq": "常见问题", "nav.download": "下载",
    "hero.eyebrow": "Mac 上的 Zebra ZPL 标签打印机驱动",
    "hero.title1": "任何 Mac 软件，", "hero.title2": "都能打出清晰的 Zebra 标签。", "cta.title1": "打得清晰，", "cta.title2": "今天就发货。",
    "hero.lead": "CrispDock 取代 macOS 自带的模糊驱动：条码清晰，打印不再一顿一顿；印在 Letter 大纸上的面单，会自动抠出来、转正，铺满 4×6。",
    "hero.download": "免费下载", "hero.pricing": "查看价格",
    "hero.trial": "免费版一直能用（带水印）——也可以<a href=\"#pricing\">免费试用 Pro 7 天</a>。",
    "hero.fact1": "macOS 13 及以上", "hero.fact2": "M 芯片和 Intel 都支持", "hero.fact3": "苹果签名并公证",
    "hero.caption": "真实输出：一张 Letter 纸上的两张面单，各自打成一张 4×6。",
    "features.title": "自带驱动做不好的，它都做好了",
    "features.lead": "macOS 自带的 Zebra 驱动会把条码打虚，而且边传边打。CrispDock 把每一页都转换成专为热敏标签优化的打印指令。",
    "f1.title": "条码清晰", "f1.body": "条码、二维码和小字都精准落在打印头的点阵上，扫一次就能读出来。",
    "f2.title": "不再一顿一顿", "f2.body": "每张标签压缩后一次发给打印机，打印过程顺畅，中途不停顿。",
    "f3.title": "任何软件，大小一致", "f3.body": "Chrome、Safari、预览或任何 PDF 软件，按 ⌘P 就能打。软件自己加的页边距会被忽略，标签总是铺满 4×6。",
    "f4.title": "大纸面单自动抠", "f4.body": "为 8.5×11 纸张准备的面单——一页一张或两张、有框或没框、横放或竖放——都会被自动找出来、抠出、转正。",
    "f5.title": "USB 和网络都行", "f5.body": "安装器会找出 USB 和局域网里的 Zebra 打印机，并自动识别 203、300、600 dpi 打印头。",
    "f6.title": "打印前先预览", "f6.body": "把 PDF、PNG、JPEG 或 iPhone 照片拖进 CrispDock App，就能看到每张标签打出来的样子，跟打印机收到的完全一致。",
    "preview.title": "每一张标签，打印前都看得到",
    "preview.lead": "CrispDock App 显示的就是驱动的真实输出，一张标签一格。一张纸上两张面单，就变成两张竖放的 4×6 标签。",
    "preview.c1": "一键设置打印机", "preview.c2": "每台打印机单独调浓度和速度", "preview.c3": "打测试标签，确认扫码没问题",
    "how.title": "两分钟上手",
    "how.s1.title": "安装", "how.s1.body": "接好 Zebra 打印机后打开安装器。它会设置好找到的每一台打印机，并保留原来的名字，其他软件照常能用。",
    "how.s2.title": "照常打印", "how.s2.body": "在任何软件里按 ⌘P，选 Zebra 打印机和 4×6 纸张。",
    "how.s3.title": "贴上发货", "how.s3.body": "清晰、完整尺寸的标签一次顺畅打完。",
    "compat.yes.title": "支持", "compat.yes.body": "支持 ZPL 指令的 Zebra 打印机，例如 GK420、GX420/430、ZD410/420/421/620、ZP 450/500/505（ZPL 版）和 ZT 系列；USB、有线网络或 WiFi 连接；203、300、600 dpi 都可以。",
    "compat.no.title": "不支持", "compat.no.body": "只支持 EPL 的型号（如 LP 2844）、CPCL 便携打印机，以及蓝牙连接（macOS 不支持往蓝牙打印机打印）。",
    "pricing.title": "简单的价格", "pricing.lead": "所有功能都能免费试用。年付（先免费试用 7 天）或一次买断，任选一种就能去掉标签上的“CrispDock FREE”水印。",
    "plan.yearly.ribbon": "免费试用 7 天", "plan.yearly.name": "年付", "plan.yearly.tag": "适合每周都要发货的店铺", "plan.yearly.per": "/ 年",
    "plan.yearly.sub": "<span class=\"save\">前 7 天免费</span> · 之后约合每月 <span data-tier-text data-pro=\"$2.50\" data-airshare=\"$4.17\">$2.50</span>",
    "plan.yearly.cta": "免费试用 7 天", "plan.yearly.note": "需要绑卡。7 天内不扣钱，之后每年 <span data-tier-text data-pro=\"$29.99\" data-airshare=\"$49.99\">$29.99</span>，直到你取消。",
    "plan.lifetime.name": "买断", "plan.lifetime.tag": "一次付款，永久使用", "plan.lifetime.per": "一次性", "plan.lifetime.sub": "不续费，永远可以离线使用",
    "plan.lifetime.l2": "每个卡密 1 台 Mac，随时可以换到新电脑", "plan.lifetime.l3": "1.x 版本免费更新", "plan.lifetime.l4": "付款后立即拿到卡密",
    "plan.lifetime.cta": "一次买断", "plan.lifetime.note": "只付一次，不会续费。",
    "plan.l.nowm": "没有水印", "plan.l.macs": "每个卡密 1 台 Mac", "plan.l.subupdates": "订阅期间所有更新", "plan.l.upgrade": "随时可转买断，没用完的天数可抵扣",
    "plan.soon": "在线购买即将开放。",
    "tier.label": "套餐", "tier.pro": "Pro", "tier.airshare": "Pro + AirShare",
    "tier.pro.note": "本机打印的标签没有水印。",
    "tier.airshare.note": "同一 Wi‑Fi 下的 iPhone、iPad 和其它 Mac 也能通过这台 Mac 打印，同样没有水印。",
    "plan.l.share.pro": "iPhone、iPad、其它 Mac 共享打印：带水印", "plan.l.share.air": "AirShare：iPhone、iPad、其它 Mac 都能打印",
    "compare.price.pro": "Pro", "compare.price.air": "Pro + AirShare",
    "compare.price.ay": "$49.99 / 年", "compare.price.al": "$119 一次性",
    "compare.trial": "免费使用", "compare.trial.free": "一直免费，带水印", "compare.trial.y": "前 7 天免费，无水印",
    "compare.card": "要不要绑卡", "compare.card.free": "不用", "compare.card.y": "要，7 天免费期过后才扣款", "compare.card.l": "要，付一次",
    "compare.cancel": "取消和退款", "compare.cancel.y": "随时取消 · 每笔付款 30 天内可全额退款", "compare.cancel.l": "30 天内可全额退款",
    "compare.share": "iPhone、iPad、其它 Mac 共享打印", "compare.share.free": "带水印", "compare.share.paid": "有 AirShare 才无水印",
    "faq.q12": "AirShare 是什么？", "faq.a12": "CrispDock 可以把这台 Mac 上的 Zebra 打印机共享到 Wi‑Fi，iPhone、iPad 和其它 Mac 都能往上打印。Pro 套餐这样打出来的标签带水印，Pro + AirShare 没有。在这台 Mac 上直接打印的标签，两档都没有水印。已经是 Pro？在账户页加上 AirShare：订阅只补当期剩余时间的差价，Pro 买断补 $40 即可。",
    "plan.free.name": "免费版", "plan.free.body": "全部功能，不限时间。每张标签上会铺满“CrispDock FREE”水印。", "plan.free.cta": "免费下载",
    "compare.title": "套餐对比", "compare.price": "价格", "compare.price.y": "$29.99 / 年", "compare.price.l": "$79 一次性",
    "compare.wm": "“CrispDock FREE”水印", "compare.wm.free": "每张标签都有", "compare.none": "没有",
    "compare.macs": "每个卡密可用 Mac 数", "compare.any": "不限台数", "compare.updates": "更新", "compare.all": "全部", "compare.while": "订阅期间全部", "compare.1x": "1.x 全部",
    "compare.offline": "离线能用多久", "compare.always": "一直能用", "compare.offline.sub": "已付期结束后再 24 小时",
    "compare.switch": "转成买断", "compare.switch.sub": "补差价即可，没用完的天数可抵扣",
    "account.lead": "已经是客户？", "account.link": "管理订阅",
    "pricing.fine": "价格以美元计，可能另收销售税。新客户的年付先免费试用 7 天：试用结束时扣款，之前取消就不扣。订阅会按所示价格自动续费，直到你取消；随时可以在账户里取消，取消后 Pro 用到已付期结束。Pro 卡密需要 CrispDock 1.3 或更新版本。付款由 Stripe 处理。",
    "faq.title": "常见问题",
    "faq.q1": "需要另外装 Zebra 官方驱动吗？", "faq.a1": "不需要，CrispDock 本身就是驱动。Zebra 没有出 macOS 驱动，标签模糊、打得慢，正是 macOS 自带的通用驱动造成的。",
    "faq.q2": "能从哪些软件和网站打印？", "faq.a2": "Mac 上能打印的都可以：浏览器、预览、各种 PDF 软件。电商平台、发货工具、快递网站下载的面单都能用，不管是 4×6 页面还是印在 Letter 大纸上。",
    "faq.q3": "免费版少了什么？", "faq.a3": "什么功能都不少，只是每张标签上会铺满重复的“CrispDock FREE”水印。免费版可以一直用；买任一套餐就没有水印——年付还可以先免费试用 7 天，不带水印先用起来。",
    "faq.q4": "授权怎么用？", "faq.a4": "下单后（包括开始免费试用时）马上通过邮件收到卡密，在 CrispDock App 里粘贴激活。每个卡密只能用 1 台 Mac；在 App（或账户页面）里解除激活，就能换到新电脑。免费试用每台 Mac 只有一次。",
    "faq.q7": "需要哪个版本的 CrispDock？", "faq.a7": "Pro 卡密需要 CrispDock 1.3 或更新版本，旧版本激活不了；1.3.2 及以上在卡密激活不了时会说清楚原因。在本页下载最新版，直接覆盖安装即可，打印机和设置都会保留。",
    "faq.q13": "7 天免费试用怎么算？", "faq.a13": "新客户的年付先免费用 7 天，没有水印。下单时要绑卡，但试用结束前不会扣钱——结束日期写在卡密邮件和账户页里。在那之前去账户页取消，就一分钱不付；不取消就按年付价格扣款，之后每年续费。买断没有试用，不过免费版可以先带水印把所有功能试一遍。",
    "faq.q8": "怎么取消订阅？", "faq.a8": "点本页的“管理订阅”，用邮箱登录后取消。取消后不会再扣款，Pro 会一直用到已经付过钱的这一期结束。在同一个页面还能换银行卡、下载发票。",
    "faq.q9": "订阅到期后会怎样？", "faq.a9": "已付期结束后（你取消了，或者续费扣款失败且 24 小时内没有更新银行卡），Pro 还能再用 24 小时。之后标签会重新带上免费版水印。其他都不变：卡密、Mac 和设置都还在，续费后用同一个卡密自动恢复 Pro。",
    "faq.q10": "订阅能转成买断吗？", "faq.a10": "可以，在账户页面操作，卡密和 Mac 都不变。当前这一年没用完的天数会从买断价（$79，带 AirShare 是 $119）里扣掉，你只付差价。已经用掉的时间不抵扣，订阅本身也不退款。例如 Pro 年付还剩半年时转 Pro 买断，大约付 $64。免费试用期间还没付过钱，所以没有可抵扣的。",
    "faq.q11": "退款政策是什么？", "faq.a11": "如果 CrispDock 不适合你，在付款后 30 天内联系我们，这笔付款全额退款。退款后，对应的卡密会立即失效。",
    "faq.q5": "我的面单会上传到哪里吗？", "faq.a5": "不会。所有标签都在你自己的 Mac 上转换。CrispDock 只在激活授权和偶尔检查授权时联网，打印本身不需要网络。订阅会在 Mac 联网时在后台自动续上；如果一台 Mac 在已付期结束后超过 24 小时一直没联网，它会先打带水印的标签，联网后自动恢复。",
    "faq.q6": "会改动我现有的打印机吗？", "faq.a6": "会把它们换成 CrispDock 驱动，但名字不变，所以直接往打印机发 ZPL 指令的工具照常能用。卸载后会还原成系统自带驱动。",
    "footer.note": "CrispDock 与 Zebra Technologies 公司无关，也未获其认可。Zebra 和 ZPL 是各自所有者的商标。",
    "footer.support": "客服：",
    "footer.terms": "服务条款", "footer.privacy": "隐私政策", "footer.refunds": "退款政策",
    "ba.before": "macOS 自带驱动", "ba.after": "CrispDock", "ba.label": "前后对比",
    "ba.caption": "真实照片局部放大：左边是 macOS 自带驱动打的 USPS 面单，右边是 CrispDock 打的。左右拖动中间的竖线对比。",
  };

  const english = new Map();
  const nodes = document.querySelectorAll("[data-i18n]");
  nodes.forEach((node) => english.set(node, node.innerHTML));

  const toggle = document.getElementById("lang-toggle");
  const apply = (lang) => {
    nodes.forEach((node) => {
      const key = node.getAttribute("data-i18n");
      node.innerHTML = lang === "zh" && zh[key] ? zh[key] : english.get(node);
    });
    document.querySelectorAll("[data-i18n-label]").forEach((node) => {
      if (!node.dataset.enLabel) node.dataset.enLabel = node.getAttribute("aria-label");
      const key = node.getAttribute("data-i18n-label");
      node.setAttribute("aria-label", lang === "zh" && zh[key] ? zh[key] : node.dataset.enLabel);
    });
    document.documentElement.lang = lang === "zh" ? "zh-CN" : "en";
    toggle.textContent = lang === "zh" ? "English" : "中文";
    try { localStorage.setItem("pb-lang", lang); } catch {}
    showTier(tier); // translated text may contain tier-dependent amounts
  };

  // Pro / Pro + AirShare switch on the pricing cards: prices, the AirShare line and the
  // checkout links (…/checkout?plan=…&tier=airshare) follow the chosen tier.
  let tier = "pro";
  const showTier = (next) => {
    tier = next;
    document.querySelectorAll(".tier-switch [data-tier]").forEach((b) => b.setAttribute("aria-checked", String(b.dataset.tier === tier)));
    document.querySelectorAll("[data-tier-only]").forEach((n) => { n.hidden = n.dataset.tierOnly !== tier; });
    document.querySelectorAll(".price[data-pro]").forEach((p) => {
      if (p.firstChild && p.firstChild.nodeType === Node.TEXT_NODE) p.firstChild.textContent = p.dataset[tier] + " ";
    });
    document.querySelectorAll("[data-tier-text]").forEach((n) => { n.textContent = n.dataset[tier]; });
    document.querySelectorAll("a[data-checkout]").forEach((a) => {
      if (!a.dataset.baseHref) a.dataset.baseHref = a.getAttribute("href") || "";
      if (a.dataset.baseHref && a.hasAttribute("href")) a.setAttribute("href", a.dataset.baseHref + (tier === "airshare" ? "&tier=airshare" : ""));
    });
  };
  document.querySelectorAll(".tier-switch [data-tier]").forEach((b) => b.addEventListener("click", () => showTier(b.dataset.tier)));

  let lang = "en";
  const fromUrl = new URLSearchParams(location.search).get("lang");
  try { lang = fromUrl || localStorage.getItem("pb-lang") || (navigator.language.startsWith("zh") ? "zh" : "en"); } catch {}
  if (lang !== "en") apply(lang);
  toggle.addEventListener("click", () => apply(document.documentElement.lang === "zh-CN" ? "en" : "zh"));

  // Checkout: the Worker fills data-checkout-base from the CHECKOUT_BASE var. Empty = not
  // open yet: buy buttons are disabled with an "opens soon" note and the account link stays hidden.
  const plans = document.querySelector("[data-checkout-base]");
  const checkoutBase = (plans && plans.getAttribute("data-checkout-base")) || "";
  if (/^https?:\/\//.test(checkoutBase)) {
    document.querySelectorAll("[data-account]").forEach((p) => { p.hidden = false; });
  } else {
    document.querySelectorAll("[data-checkout]").forEach((a) => { a.setAttribute("aria-disabled", "true"); a.removeAttribute("href"); });
    document.querySelectorAll("[data-checkout-soon]").forEach((p) => { p.hidden = false; });
  }
  if (window.PB && /@/.test(window.PB.supportEmail || "")) {
    document.querySelectorAll("[data-support]").forEach((p) => { p.hidden = false; });
  }
  document.getElementById("year").textContent = String(new Date().getFullYear());
})();

// Before / after slider: drag (mouse or finger), click anywhere, or use the arrow keys.
// Vertical swipes still scroll the page on phones (touch-action: pan-y).
(() => {
  const frame = document.getElementById("ba");
  if (!frame) return;
  const tagL = document.querySelector(".ba-tag-l");
  const tagR = document.querySelector(".ba-tag-r");
  let pos = 50;
  let touched = false;
  const set = (value) => {
    pos = Math.min(100, Math.max(0, value));
    frame.style.setProperty("--pos", pos + "%");
    frame.setAttribute("aria-valuenow", String(Math.round(pos)));
    tagL.classList.toggle("is-hidden", pos < 22);
    tagR.classList.toggle("is-hidden", pos > 78);
  };
  const fromEvent = (e) => {
    const r = frame.getBoundingClientRect();
    set(((e.clientX - r.left) / r.width) * 100);
  };
  let dragging = false;
  frame.addEventListener("pointerdown", (e) => {
    touched = true;
    dragging = true;
    frame.setPointerCapture(e.pointerId);
    fromEvent(e);
  });
  frame.addEventListener("pointermove", (e) => { if (dragging) fromEvent(e); });
  const stop = () => { dragging = false; };
  frame.addEventListener("pointerup", stop);
  frame.addEventListener("pointercancel", stop);
  frame.addEventListener("keydown", (e) => {
    const step = e.shiftKey ? 10 : 2;
    const next = { ArrowLeft: pos - step, ArrowRight: pos + step, Home: 0, End: 100 }[e.key];
    if (next === undefined) return;
    e.preventDefault();
    touched = true;
    set(next);
  });

  // First time it scrolls into view, sweep once so people see it moves.
  const still = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (still || !("IntersectionObserver" in window)) return;
  const io = new IntersectionObserver((entries) => {
    if (!entries.some((en) => en.isIntersecting)) return;
    io.disconnect();
    const keys = [[0, 50], [600, 75], [1300, 25], [1900, 50]];
    let t0 = null;
    const tick = (now) => {
      if (touched) return;
      if (t0 === null) t0 = now;
      const t = now - t0;
      let i = 0;
      while (i < keys.length - 2 && t > keys[i + 1][0]) i++;
      const [ta, va] = keys[i];
      const [tb, vb] = keys[i + 1];
      const k = Math.min(1, (t - ta) / (tb - ta));
      const ease = k < 0.5 ? 2 * k * k : 1 - Math.pow(-2 * k + 2, 2) / 2;
      set(va + (vb - va) * ease);
      if (t < keys[keys.length - 1][0]) requestAnimationFrame(tick);
    };
    setTimeout(() => requestAnimationFrame(tick), 300);
  }, { threshold: 0.6 });
  io.observe(frame);
})();
