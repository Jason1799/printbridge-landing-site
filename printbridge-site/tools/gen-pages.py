#!/usr/bin/env python3
"""Generate the CrispDock SEO landing pages into public/.

    python3 tools/gen-pages.py

Writes one HTML file per page (public/<slug>.html, served at /<slug>) for the printer
model pages, the problem guides and the /guides hub. This script lives outside public/
so it is never deployed. Re-run it after editing the copy below; it overwrites only the
files it owns (listed in PAGES at the bottom) and checks title/description lengths.

Printer specs mirror zp505-mac-bridge/rust/crates/printbridge-core/src/models.rs — keep
them in sync when that table changes. Only ZP500, ZP505 and GK420d were tested on real
hardware; every other model uses its published specs.
"""
from __future__ import annotations

import html
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
PUBLIC = ROOT / "public"
SITE = "https://crispdock.com"
OG_IMAGE = SITE + "/assets/og-image.png"
ASSET_VERSION = "20261018"
# styles.css gained the guide-page rules after 20261018 shipped: a fresh query string keeps
# a cached copy of the old file from styling these pages.
STYLES_VERSION = "20261019"
ZEBRA_ARTICLE = "https://support.zebra.com/article/000022631"

# ---------------------------------------------------------------------------------------
# Printer data (from models.rs): dpi, max speed at (203, 300, 600) dpi (0 = not offered),
# printable head width in inches, print method (DT direct thermal, TT thermal transfer,
# ANY = both versions exist).
# ---------------------------------------------------------------------------------------
SPECS = {
    "LP2844": (203, (4, 0, 0), 4.09, "DT"),
    "TLP2844": (203, (4, 0, 0), 4.09, "TT"),
    "GC420d": (203, (4, 0, 0), 4.09, "DT"),
    "GC420t": (203, (4, 0, 0), 4.09, "TT"),
    "GK420d": (203, (5, 0, 0), 4.09, "DT"),
    "GK420t": (203, (5, 0, 0), 4.09, "TT"),
    "GX420d": (203, (6, 0, 0), 4.09, "DT"),
    "GX420t": (203, (6, 0, 0), 4.09, "TT"),
    "GX430t": (300, (0, 4, 0), 4.09, "TT"),
    "ZP450": (203, (5, 0, 0), 4.09, "DT"),
    "ZP500": (203, (5, 0, 0), 4.09, "DT"),
    "ZP505": (203, (5, 0, 0), 4.09, "DT"),
    "ZD220": (203, (4, 0, 0), 4.09, "ANY"),
    "ZD230": (203, (6, 0, 0), 4.09, "ANY"),
    "ZD410": (203, (6, 4, 0), 2.2, "DT"),
    "ZD411": (203, (6, 4, 0), 2.2, "ANY"),
    "ZD420": (203, (6, 4, 0), 4.09, "ANY"),
    "ZD421": (203, (6, 4, 0), 4.09, "ANY"),
    "ZD620": (203, (8, 6, 0), 4.09, "ANY"),
    "ZD621": (203, (8, 6, 0), 4.09, "ANY"),
    "ZT111": (203, (10, 8, 0), 4.09, "ANY"),
    "ZT210": (203, (6, 6, 0), 4.09, "ANY"),
    "ZT220": (203, (6, 6, 0), 4.09, "ANY"),
    "ZT230": (203, (6, 6, 0), 4.09, "ANY"),
    "ZT231": (203, (12, 10, 0), 4.09, "ANY"),
    "ZT410": (203, (14, 12, 6), 4.09, "ANY"),
    "ZT411": (203, (14, 12, 6), 4.09, "ANY"),
    "ZT420": (203, (12, 10, 0), 6.6, "ANY"),
    "ZT421": (203, (12, 10, 0), 6.6, "ANY"),
    "ZT510": (203, (12, 10, 0), 4.09, "ANY"),
    "ZT610": (203, (14, 14, 6), 4.09, "ANY"),
    "ZT620": (203, (12, 10, 0), 6.6, "ANY"),
}
TESTED = {"ZP500", "ZP505", "GK420d"}
METHOD = {"DT": "Direct thermal", "TT": "Thermal transfer", "ANY": "Direct or transfer"}
DISPLAY = {"LP2844": "LP 2844-Z", "TLP2844": "TLP 2844-Z", "ZP450": "ZP 450", "ZP500": "ZP 500", "ZP505": "ZP 505"}


def esc(text: str) -> str:
    return html.escape(text, quote=True)


def plain(fragment: str) -> str:
    """HTML fragment -> plain text (for JSON-LD)."""
    text = re.sub(r"<[^>]+>", "", fragment)
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def resolutions(family: str) -> list[tuple[int, int]]:
    _, speeds, _, _ = SPECS[family]
    return [(dpi, s) for dpi, s in zip((203, 300, 600), speeds) if s]


def spec_row(family: str) -> str:
    _, _, width, method = SPECS[family]
    res = resolutions(family)
    res_text = " or ".join(str(d) for d, _ in res) + " dpi"
    speed_text = ", ".join(f"{s} in/s at {d} dpi" for d, s in res) if len(res) > 1 else f"{res[0][1]} in/s"
    mm = round(width * 25.4)
    name = DISPLAY.get(family, family)
    status = "Tested" if family in TESTED else "Published specs"
    return (
        f"<tr><th scope=\"row\">{esc(name)}</th><td>{res_text}</td><td>{width:g} in ({mm} mm)</td>"
        f"<td>{speed_text}</td><td>{METHOD[method]}</td><td>{status}</td></tr>"
    )


def spec_table(families: list[str]) -> str:
    rows = "\n".join("            " + spec_row(f) for f in families)
    return f"""<div class="table-wrap">
        <table class="specs">
          <thead><tr><th scope="col">Model</th><th scope="col">Resolution</th><th scope="col">Print width</th><th scope="col">Max speed</th><th scope="col">Method</th><th scope="col">Basis</th></tr></thead>
          <tbody>
{rows}
          </tbody>
        </table>
      </div>"""


# ---------------------------------------------------------------------------------------
# Shared page pieces
# ---------------------------------------------------------------------------------------
HEADER = """  <header class="nav">
    <div class="container nav-inner">
      <a class="brand" href="/"><img src="/assets/favicon.svg" alt="" width="32" height="32" /><span>CrispDock <small>for Zebra printers</small></span></a>
      <div class="nav-actions">
        <a class="btn btn-small btn-ghost" href="/#pricing">Pricing</a>
        <a class="btn btn-small btn-primary" href="/download">Download</a>
      </div>
    </div>
  </header>"""

FOOTER = """  <footer class="footer">
    <div class="container footer-inner">
      <div class="footer-brand">
        <a class="brand" href="/"><span>CrispDock <small>for Zebra printers</small></span></a>
      </div>
      <nav class="footer-links" aria-label="Footer">
        <a href="/#pricing">Pricing</a>
        <a href="/#faq">FAQ</a>
        <a href="/guides">Guides</a>
        <a href="/terms">Terms</a>
        <a href="/privacy">Privacy</a>
        <a href="/refunds">Refunds</a>
        <a href="mailto:cs@crispdock.com">Contact</a>
      </nav>
      <p class="fine">CrispDock is not affiliated with or endorsed by Zebra Technologies. Zebra and ZPL are trademarks of their respective owners.</p>
      <p class="fine">Support: <a href="mailto:cs@crispdock.com">cs@crispdock.com</a></p>
      <p class="fine">© 2026 solesolution Inc</p>
    </div>
  </footer>"""

CTA_BUTTONS = """<div class="cta-row page-actions">
        <a class="btn btn-primary btn-lg" href="/download">Download free</a>
        <a class="btn btn-ghost btn-lg" href="/#pricing">Try Pro free for 7 days</a>
      </div>"""

COMPARE_FIGURE = """<figure class="page-figure card">
        <picture><source srcset="/assets/compare-before.webp" type="image/webp" /><img src="/assets/compare-before.jpg" alt="Label printed with the built-in macOS driver: jagged letters and fuzzy, ragged barcode bars" width="1600" height="692" loading="lazy" /></picture>
        <picture><source srcset="/assets/compare-after.webp" type="image/webp" /><img src="/assets/compare-after.jpg" alt="The same label printed with CrispDock: sharp letters and clean, straight barcode bars" width="1600" height="692" loading="lazy" /></picture>
        <figcaption>Top: the built-in macOS driver. Bottom: the same label through CrispDock.</figcaption>
      </figure>"""

SHEET_FIGURE = """<figure class="page-figure page-figure-sheet card">
        <div class="paper"><picture><source srcset="/assets/sheet-letter.webp" type="image/webp" /><img src="/assets/sheet-letter.png" alt="Two shipping labels printed side by side on a letter-size sheet, with a note below" width="386" height="500" loading="lazy" /></picture></div>
        <div class="paper"><img src="/assets/sheet-label-4x6.png" alt="The first label, cut out and filling a 4×6 label" width="408" height="609" loading="lazy" /></div>
        <figcaption>A letter-size sheet in, a full-size 4×6 label out.</figcaption>
      </figure>"""

APP_FIGURE = """<figure class="page-figure card">
        <picture><source srcset="/assets/app-preview.webp" type="image/webp" /><img src="/assets/app-preview.png" alt="The CrispDock app previewing two labels cut from one letter sheet" width="1372" height="873" loading="lazy" /></picture>
        <figcaption>Drop a PDF into the CrispDock app to see every label before it prints.</figcaption>
      </figure>"""

PRICE_ANSWER = (
    "Free forever with a watermark. Pro is $29.99 a year (7-day free trial, card required, once per Mac) "
    "or $79 lifetime; Pro + AirShare, for clean labels from iPhone and iPad too, is $49.99 a year or $119 "
    "lifetime. One Mac per key, refunds within 30 days. <a href=\"/#pricing\">See pricing</a>."
)
FREE_ANSWER = (
    "Yes. Every feature works and it never expires; labels just carry a “CrispDock FREE” watermark "
    "until you choose a Pro plan."
)


def faq_html(faqs: list[tuple[str, str]]) -> str:
    items = "\n".join(
        f"        <details class=\"card\"><summary>{esc(q)}</summary><p>{a}</p></details>" for q, a in faqs
    )
    return f"""<div class="faq page-faq">
{items}
      </div>"""


def faq_ld(faqs: list[tuple[str, str]]) -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": plain(a)}}
            for q, a in faqs
        ],
    }


def crumbs_ld(trail: list[tuple[str, str]]) -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": name, "item": SITE + path}
            for i, (name, path) in enumerate(trail)
        ],
    }


def crumbs_html(trail: list[tuple[str, str]]) -> str:
    parts = []
    for i, (name, path) in enumerate(trail):
        if i == len(trail) - 1:
            parts.append(f'<span aria-current="page">{esc(name)}</span>')
        else:
            parts.append(f'<a href="{path}">{esc(name)}</a>')
    return '<nav class="crumbs" aria-label="Breadcrumb">' + ' <span aria-hidden="true">/</span> '.join(parts) + "</nav>"


def related_html(links: list[tuple[str, str]]) -> str:
    items = "\n".join(f'          <li><a href="{path}">{esc(text)}</a></li>' for path, text in links)
    return f"""<ul class="related-links">
{items}
        </ul>"""


def page(path: str, title: str, description: str, body: str, ld: list[dict]) -> str:
    assert len(title) <= 60, f"title too long ({len(title)}): {title}"
    assert len(description) <= 155, f"description too long ({len(description)}): {description}"
    url = SITE + path
    scripts = "\n".join(
        f'  <script type="application/ld+json">{json.dumps(block, ensure_ascii=False)}</script>' for block in ld
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <meta name="color-scheme" content="light" />
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(description)}" />
  <link rel="canonical" href="{url}" />
  <meta property="og:type" content="article" />
  <meta property="og:site_name" content="CrispDock" />
  <meta property="og:url" content="{url}" />
  <meta property="og:title" content="{esc(title)}" />
  <meta property="og:description" content="{esc(description)}" />
  <meta property="og:image" content="{OG_IMAGE}" />
  <meta property="og:image:width" content="1200" />
  <meta property="og:image:height" content="630" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="{esc(title)}" />
  <meta name="twitter:description" content="{esc(description)}" />
  <meta name="twitter:image" content="{OG_IMAGE}" />
  <link rel="icon" href="/assets/favicon.svg" type="image/svg+xml" />
  <link rel="icon" href="/assets/icon-128.png" type="image/png" sizes="128x128" />
  <link rel="apple-touch-icon" href="/assets/apple-touch-icon.png" />
  <link rel="preload" href="/fonts/manrope-latin.woff2" as="font" type="font/woff2" crossorigin />
  <link rel="preload" href="/fonts/jersey10-latin.woff2" as="font" type="font/woff2" crossorigin />
  <link rel="stylesheet" href="/fonts.css?v={ASSET_VERSION}" />
  <link rel="stylesheet" href="/styles.css?v={STYLES_VERSION}" />
{scripts}
</head>
<body>
{HEADER}

  <main class="section">
    <article class="container legal guide">
{body}
    </article>
  </main>

{FOOTER}
</body>
</html>
"""


# ---------------------------------------------------------------------------------------
# A. Printer model pages
# ---------------------------------------------------------------------------------------
MODELS = [
    {
        "slug": "zebra-zd421-mac-driver",
        "name": "Zebra ZD421",
        "short": "ZD421",
        "title": "Zebra ZD421 Driver for Mac — Sharp 4×6 Labels | CrispDock",
        "desc": "Use a Zebra ZD421 on macOS 13+ with sharp barcodes, smooth printing and letter-size shipping labels cut to 4×6. Free download.",
        "families": ["ZD421"],
        "hub": "A common 4-inch shipping printer; 203 or 300 dpi.",
        "intro": [
            "The ZD421 is one of the most common 4-inch desktop printers in shipping rooms: the direct thermal ZD421d prints 4×6 shipping labels without a ribbon, and the ZD421t adds a ribbon for labels that need to last. Zebra doesn’t publish an official macOS driver for its label printers (see <a href=\"" + ZEBRA_ARTICLE + "\">Zebra support article 000022631</a>), so on a Mac the ZD421 ends up on the generic driver that comes with macOS.",
            "CrispDock is a macOS printer driver built for exactly this. It installs as a system driver, so your ZD421 shows up in every app’s Print dialog and prints clean ZPL instead of a fuzzy picture.",
        ],
        "notes": [
            ("Both 203 and 300 dpi heads", "The ZD421 ships with a 203 dpi head or a 300 dpi head. CrispDock reads which one your printer has and converts each label for that dot grid, so a 300 dpi unit keeps its finer detail on small text and 2D codes."),
        ],
        "extra_faq": [
            ("Can I use my ZD421 over the network?", "Yes. CrispDock finds Zebra printers on USB and on your network during setup. Bluetooth isn’t supported, because macOS can’t print to Bluetooth label printers."),
        ],
        "siblings": ["zebra-zd420-mac-driver", "zebra-zd620-zd621-mac-driver"],
    },
    {
        "slug": "zebra-zd420-mac-driver",
        "name": "Zebra ZD420",
        "short": "ZD420",
        "title": "Zebra ZD420 Driver for Mac — Crisp Labels | CrispDock",
        "desc": "A macOS driver for the Zebra ZD420: clean barcodes, continuous printing and 4×6 labels from any Mac app. macOS 13+, free to download.",
        "families": ["ZD420"],
        "hub": "The ZD421’s predecessor, still in many warehouses.",
        "intro": [
            "The ZD420 came before the ZD421 and is still at work on plenty of packing benches. It’s a 4-inch desktop printer, so it takes standard 4×6 shipping labels, and it was sold in direct thermal and thermal transfer versions.",
            "What it doesn’t have is a Mac driver from Zebra: the company doesn’t provide official macOS drivers for its label printers (<a href=\"" + ZEBRA_ARTICLE + "\">support article 000022631</a>). CrispDock fills that gap with a signed, notarized macOS driver that works from any app’s Print dialog.",
        ],
        "notes": [
            ("Older printer, same sharp output", "Because CrispDock does the conversion on your Mac and sends the printer plain ZPL, an older ZD420 prints labels just as sharp as a newer model with the same head. There’s nothing to install on the printer itself."),
        ],
        "extra_faq": [
            ("Should I upgrade my ZD420 to a ZD421 for Mac use?", "Not for the driver’s sake. CrispDock supports both with the same features, using each model’s published specs."),
        ],
        "siblings": ["zebra-zd421-mac-driver", "zebra-gk420d-mac-driver"],
    },
    {
        "slug": "zebra-zd411-mac-driver",
        "name": "Zebra ZD411",
        "short": "ZD411",
        "title": "Zebra ZD411 Driver for Mac — 2-Inch Labels | CrispDock",
        "desc": "Print sharp barcodes and product labels on a Zebra ZD411 or ZD410 from any Mac app. macOS 13+, Apple silicon and Intel. Free download.",
        "families": ["ZD411", "ZD410"],
        "hub": "Compact 2-inch printer (also covers the ZD410).",
        "two_inch": True,
        "intro": [
            "The ZD411 is Zebra’s compact 2-inch desktop printer, the successor to the ZD410. It’s made for small labels — product and barcode stickers, price tags, sample and bin labels — rather than 4×6 shipping labels.",
            "Like the rest of Zebra’s label printers it has no official macOS driver (<a href=\"" + ZEBRA_ARTICLE + "\">Zebra support article 000022631</a>), and small labels are exactly where the generic macOS driver hurts most: at that size a slightly fuzzy barcode quickly becomes one a scanner can’t read. CrispDock is a macOS driver that prints them as clean ZPL from any app.",
        ],
        "notes": [
            ("A 2-inch head, not a shipping printer", "The ZD411’s print width is about 2.2 inches (56 mm), so it can’t print a full 4×6 shipping label. For shipping labels you need a 4-inch model such as the <a href=\"/zebra-zd421-mac-driver\">ZD421</a>. CrispDock will still print anything that fits the labels you load."),
        ],
        "extra_faq": [
            ("Can the ZD411 print 4×6 shipping labels?", "No. Its head prints about 2.2 inches wide, so 4×6 labels don’t fit. Use a 4-inch printer for shipping labels; the ZD411 is ideal for small barcode and product labels."),
        ],
        "siblings": ["zebra-zd421-mac-driver", "zebra-zd620-zd621-mac-driver"],
    },
    {
        "slug": "zebra-zd220-zd230-mac-driver",
        "name": "Zebra ZD220 / ZD230",
        "short": "ZD220 or ZD230",
        "title": "Zebra ZD220 & ZD230 Driver for Mac | CrispDock",
        "desc": "Get crisp 4×6 shipping labels from a Zebra ZD220 or ZD230 on a Mac: a macOS 13+ driver for Apple silicon and Intel. Free to download.",
        "families": ["ZD220", "ZD230"],
        "hub": "Zebra’s value 4-inch desktop printers.",
        "intro": [
            "The ZD220 and ZD230 are Zebra’s value 4-inch desktop printers — a popular way to get started with thermal shipping labels without paying for the bigger desktop range. Both take 4×6 labels and both come in direct thermal and thermal transfer versions; the ZD230 is the faster of the two.",
            "Zebra doesn’t ship an official macOS driver for them (<a href=\"" + ZEBRA_ARTICLE + "\">support article 000022631</a>). CrispDock is a signed and notarized macOS driver that makes either model a normal Mac printer you can use from any app.",
        ],
        "notes": [
            ("A budget printer, full-quality labels", "Label sharpness depends on the head and on what the printer is sent. With CrispDock the ZD220 and ZD230 get the same clean ZPL as more expensive models, so a 203 dpi value printer still produces barcodes that scan first time."),
        ],
        "extra_faq": [
            ("Is there a difference between the ZD220 and ZD230 with CrispDock?", "Only what the hardware itself does: CrispDock uses the ZD230’s higher top speed (6 in/s against 4 in/s). Every CrispDock feature works on both."),
        ],
        "siblings": ["zebra-zd421-mac-driver", "zebra-gc420d-mac-driver"],
    },
    {
        "slug": "zebra-zd620-zd621-mac-driver",
        "name": "Zebra ZD620 / ZD621",
        "short": "ZD620 or ZD621",
        "title": "Zebra ZD620 & ZD621 Driver for Mac | CrispDock",
        "desc": "A macOS driver for the Zebra ZD620 and ZD621: sharp ZPL output at up to 8 in/s, USB or network, letter sheets cut to 4×6. Free download.",
        "families": ["ZD620", "ZD621"],
        "hub": "Zebra’s fastest 4-inch desktop printers.",
        "intro": [
            "The ZD620 and its successor the ZD621 sit at the top of Zebra’s 4-inch desktop range. They print faster than the ZD42x models — up to 8 inches per second at 203 dpi — which makes them a common choice for busy shipping and warehouse stations.",
            "Speed is wasted if the printer keeps stopping to wait for data, and that is what the generic macOS driver tends to cause. Zebra itself offers no official macOS driver for its label printers (<a href=\"" + ZEBRA_ARTICLE + "\">support article 000022631</a>). CrispDock is a macOS driver that sends each label as compact ZPL in one piece, so the printer can run at its pace.",
        ],
        "notes": [
            ("Built for volume", "When you print a batch, CrispDock sends each label in one piece so the ZD620 or ZD621 runs smoothly from one label to the next instead of pausing partway through. The 300 dpi versions are supported too, at their own top speed of 6 in/s."),
        ],
        "extra_faq": [
            ("Does CrispDock work with the 300 dpi ZD621?", "Yes. CrispDock detects 203 and 300 dpi heads and converts labels for the one your printer has."),
        ],
        "siblings": ["zebra-zd421-mac-driver", "zebra-zt-series-mac-driver"],
    },
    {
        "slug": "zebra-zp450-mac-driver",
        "name": "Zebra ZP 450",
        "short": "ZP 450",
        "title": "Zebra ZP 450 Driver for Mac — Sharp Labels | CrispDock",
        "desc": "Keep your Zebra ZP 450 printing sharp 4×6 shipping labels on a modern Mac. macOS 13+, Apple silicon and Intel, ZPL. Free to download.",
        "families": ["ZP450"],
        "hub": "Older 4-inch shipping printer, still widely used.",
        "intro": [
            "The ZP 450 is an older 4-inch direct thermal printer that is still printing shipping labels in a lot of small businesses. It takes standard 4×6 labels and needs no ribbon.",
            "Zebra provides no official macOS driver for its label printers (<a href=\"" + ZEBRA_ARTICLE + "\">support article 000022631</a>), and the generic driver built into macOS often leaves ZP 450 labels fuzzy and slow. CrispDock is a modern, signed and notarized macOS driver that runs on Apple silicon and Intel Macs, so an older printer keeps working on a new Mac.",
        ],
        "notes": [
            ("Check that it speaks ZPL", "CrispDock talks to printers in ZPL, Zebra’s label language. It needs a ZP 450 that runs ZPL; a unit that only understands the older EPL language won’t work with CrispDock. The free version is the easiest way to check yours."),
        ],
        "extra_faq": [
            ("My ZP 450 is old. Will it work on an M-series Mac?", "If it runs ZPL, yes. CrispDock runs natively on Apple silicon and on Intel Macs, and the printer only ever receives standard ZPL."),
        ],
        "siblings": ["zebra-zp500-zp505-mac-driver", "zebra-gk420d-mac-driver"],
    },
    {
        "slug": "zebra-zp500-zp505-mac-driver",
        "name": "Zebra ZP 500 / ZP 505",
        "short": "ZP 500 or ZP 505",
        "title": "Zebra ZP 500 & ZP 505 Driver for Mac | CrispDock",
        "desc": "Tested on real ZP 500 and ZP 505 printers: a macOS driver for sharp barcodes and smooth 4×6 shipping labels from any Mac app. Free.",
        "families": ["ZP500", "ZP505"],
        "hub": "Tested on real hardware.",
        "intro": [
            "The ZP 500 and ZP 505 are 4-inch direct thermal printers that were widely used for shipping labels. They are two of the printers CrispDock was tested on with real hardware, so this is the setup we know best.",
            "Zebra doesn’t provide an official macOS driver for its label printers (<a href=\"" + ZEBRA_ARTICLE + "\">Zebra support article 000022631</a>). Left on the generic macOS driver, these printers show the classic symptoms: dotted barcodes, pauses mid-label and labels that come out the wrong size. CrispDock fixes all three from any app’s Print dialog.",
        ],
        "notes": [
            ("Tested, not just listed", "The ZP 500 and ZP 505 are, with the GK420d, the printers CrispDock was tested on with real hardware, so their speed limits and settings were checked on actual units. CrispDock prints in ZPL, so it needs the ZPL version of these printers."),
        ],
        "extra_faq": [
            ("Have you actually tested the ZP 500 and ZP 505?", "Yes. Along with the GK420d, they are the printers CrispDock was tested on with real hardware."),
        ],
        "siblings": ["zebra-zp450-mac-driver", "zebra-gk420d-mac-driver"],
    },
    {
        "slug": "zebra-gk420d-mac-driver",
        "name": "Zebra GK420d",
        "short": "GK420d",
        "title": "Zebra GK420d Driver for Mac — Tested | CrispDock",
        "desc": "Tested on a real GK420d: a macOS driver that prints sharp barcodes and full-size 4×6 shipping labels from any Mac app. Free download.",
        "families": ["GK420d", "GK420t"],
        "hub": "Tested on real hardware (GK420t supported too).",
        "intro": [
            "The GK420d is a 4-inch direct thermal workhorse — one of the most common printers for 4×6 shipping labels, and one of the printers CrispDock was tested on with real hardware. The GK420t is the thermal transfer version of the same printer.",
            "Zebra provides no official macOS driver for its label printers (<a href=\"" + ZEBRA_ARTICLE + "\">support article 000022631</a>). On the generic macOS driver a GK420d prints, but barcodes come out dithered and the printer often stops and starts. CrispDock is a signed, notarized macOS driver that prints clean ZPL instead.",
        ],
        "notes": [
            ("Tested on a real GK420d", "CrispDock’s GK420d settings, including its 5 in/s top speed, were checked on a real printer. The GK420t uses the same published specs and is supported with the same features."),
        ],
        "extra_faq": [
            ("Does it work with the GK420t too?", "Yes. The GK420t is supported using its published specs; only the GK420d was tested on our own hardware."),
        ],
        "siblings": ["zebra-gx420d-mac-driver", "zebra-gc420d-mac-driver"],
    },
    {
        "slug": "zebra-gx420d-mac-driver",
        "name": "Zebra GX420d",
        "short": "GX420d",
        "title": "Zebra GX420d Driver for Mac — Crisp Labels | CrispDock",
        "desc": "A macOS driver for the Zebra GX420d, GX420t and GX430t: clean ZPL barcodes, 4×6 labels from any app, USB or network. Free download.",
        "families": ["GX420d", "GX420t", "GX430t"],
        "hub": "Faster sibling of the GK420 (GX420t and GX430t too).",
        "intro": [
            "The GX420d is the faster sibling of the GK420d — up to 6 inches per second — and a common choice for 4×6 shipping labels. The same family includes the GX420t (thermal transfer) and the 300 dpi GX430t.",
            "None of them has an official macOS driver from Zebra (<a href=\"" + ZEBRA_ARTICLE + "\">Zebra support article 000022631</a>). CrispDock is a macOS printer driver that turns each page into clean ZPL so barcodes come out sharp and the printer runs without stuttering.",
        ],
        "notes": [
            ("The 300 dpi GX430t", "The GX430t has a 300 dpi head. CrispDock detects it and converts labels at 300 dpi, using the GX430t’s published top speed of 4 in/s."),
        ],
        "extra_faq": [
            ("Is the GX430t supported?", "Yes, using its published specs: 300 dpi, 4.09 inch print width and up to 4 in/s."),
        ],
        "siblings": ["zebra-gk420d-mac-driver", "zebra-gc420d-mac-driver"],
    },
    {
        "slug": "zebra-gc420d-mac-driver",
        "name": "Zebra GC420d",
        "short": "GC420d",
        "title": "Zebra GC420d Driver for Mac — Sharp Labels | CrispDock",
        "desc": "Print sharp 4×6 shipping labels from a Zebra GC420d or GC420t on macOS 13+. Works from any app's Print dialog. Free to download.",
        "families": ["GC420d", "GC420t"],
        "hub": "Entry-level 4-inch desktop printer (GC420t too).",
        "intro": [
            "The GC420d is an entry-level 4-inch direct thermal printer from the same generation as the GK420d, and many small sellers bought one for their first 4×6 shipping labels. The GC420t is its thermal transfer twin.",
            "As with every Zebra label printer, there is no official macOS driver (<a href=\"" + ZEBRA_ARTICLE + "\">Zebra support article 000022631</a>). CrispDock is a macOS driver that installs alongside your other printers and prints clean ZPL from any app.",
        ],
        "notes": [
            ("Speed matched to the printer", "The GC420d tops out at 4 inches per second. CrispDock uses that limit and sends each label in one piece, so the printer runs smoothly rather than pausing while it waits for data."),
        ],
        "extra_faq": [
            ("Is the GC420d tested?", "It’s supported using its published specs. The printers we tested on real hardware are the GK420d, ZP 500 and ZP 505."),
        ],
        "siblings": ["zebra-gk420d-mac-driver", "zebra-zd220-zd230-mac-driver"],
    },
    {
        "slug": "zebra-lp2844-mac-driver",
        "name": "Zebra LP 2844",
        "short": "LP 2844-Z",
        "title": "Zebra LP 2844 Driver for Mac — Which Models Work",
        "desc": "Does your Zebra LP 2844 work on a Mac? The ZPL LP 2844-Z works with CrispDock on macOS 13+; the EPL-only LP 2844 doesn't. Here's how to tell.",
        "families": ["LP2844", "TLP2844"],
        "hub": "LP 2844-Z (ZPL) supported; EPL-only LP 2844 isn’t.",
        "intro": [
            "The LP 2844 is a classic 4-inch direct thermal printer that still turns up on many shipping desks. One thing matters before anything else: it was sold in two versions. The LP 2844-Z runs ZPL, Zebra’s label language; the plain LP 2844 runs only the older EPL language.",
            "CrispDock talks ZPL, so it supports the <strong>LP 2844-Z</strong> (and the thermal transfer TLP 2844-Z) but not the EPL-only LP 2844. Zebra itself provides no official macOS driver for its label printers (<a href=\"" + ZEBRA_ARTICLE + "\">support article 000022631</a>).",
        ],
        "notes": [
            ("How to tell which one you have", "Look for the “-Z” in the model name on the label under the printer. If it says LP 2844-Z, CrispDock can drive it. If it says LP 2844 with no “Z”, it’s EPL-only and CrispDock can’t print to it. The free version is a no-cost way to check."),
        ],
        "extra_faq": [
            ("Does CrispDock work with the EPL-only LP 2844?", "No. CrispDock prints in ZPL, and the plain LP 2844 only understands EPL. The ZPL model, the LP 2844-Z, is supported using its published specs."),
        ],
        "siblings": ["zebra-gk420d-mac-driver", "zebra-gc420d-mac-driver"],
    },
    {
        "slug": "zebra-zt-series-mac-driver",
        "name": "Zebra ZT series",
        "short": "ZT printer",
        "title": "Zebra ZT Series Driver for Mac (ZT230, ZT411) | CrispDock",
        "desc": "Run Zebra ZT industrial printers (ZT111–ZT620, incl. ZT230, ZT411) from a Mac: clean ZPL, 203/300/600 dpi, USB or network. Free download.",
        "families": ["ZT111", "ZT210", "ZT220", "ZT230", "ZT231", "ZT410", "ZT411", "ZT420", "ZT421", "ZT510", "ZT610", "ZT620"],
        "hub": "Industrial printers, ZT111 to ZT620.",
        "industrial": True,
        "intro": [
            "Zebra’s ZT printers are industrial machines for warehouses and production lines: metal frames, large label rolls and speeds of up to 14 inches per second. Several models offer 300 or 600 dpi heads, and the ZT420, ZT421 and ZT620 print up to about 6.6 inches wide.",
            "They’re still label printers without an official macOS driver from Zebra (<a href=\"" + ZEBRA_ARTICLE + "\">support article 000022631</a>). CrispDock is a macOS driver that lets a Mac print to a ZT printer from any app, sending clean ZPL rather than a dithered image.",
        ],
        "notes": [
            ("High resolution and wide heads", "CrispDock detects 203, 300 and 600 dpi heads and converts each label for the one your printer has, so fine print and small 2D codes keep their detail. The table shows each model’s top speed at each resolution; CrispDock stays within those limits."),
        ],
        "extra_faq": [
            ("Does CrispDock support 600 dpi ZT printers?", "Yes. The ZT410, ZT411 and ZT610 come with 600 dpi options, and CrispDock detects the head and converts labels at 600 dpi."),
        ],
        "siblings": ["zebra-zd620-zd621-mac-driver", "zebra-zd421-mac-driver"],
    },
]

MODEL_BY_SLUG = {m["slug"]: m for m in MODELS}


def model_page(m: dict) -> tuple[str, str]:
    path = "/" + m["slug"]
    name, short = m["name"], m["short"]
    two_inch = m.get("two_inch", False)
    industrial = m.get("industrial", False)
    trail = [("Home", "/"), ("Printers & guides", "/guides"), (name, path)]

    size_step = (
        "pick the label size you’ve loaded, such as 2×1 inches"
        if two_inch
        else "pick 4×6 (or the label size you’ve loaded)"
    )
    steps = [
        ("Download and install", "Download CrispDock free and open the installer (macOS 13 or later)."),
        ("CrispDock finds your printer", f"With the {short} on USB or your network, the installer finds it and sets it up, keeping its name."),
        ("Print from any app", f"Press ⌘P in any app, choose the {short} and {size_step}."),
    ]
    steps_html = "\n".join(
        f'        <li class="card"><span class="step-n">0{i + 1}</span><h3>{esc(t)}</h3><p>{esc(d)}</p></li>'
        for i, (t, d) in enumerate(steps)
    )

    families = m["families"]
    tested = [DISPLAY.get(f, f) for f in families if f in TESTED]
    if tested and len(tested) == len(families):
        spec_note = "These printers were tested with CrispDock on real hardware."
    elif tested:
        spec_note = f"The {' and '.join(tested)} was tested with CrispDock on real hardware; the other models are supported using their published specs."
    else:
        spec_note = "Supported using the model’s published specs (CrispDock’s hardware testing was done on the ZP 500, ZP 505 and GK420d)."
    spec_intro = (
        "The limits CrispDock uses for each printer it supports, from Zebra’s published specs. Speeds are the top print speed at each resolution."
        if len(families) > 2
        else f"What CrispDock uses for the {short}. Speeds are the top print speed at each resolution."
    )

    if two_inch:
        letter_html = (
            "<p>A lot of shipping labels arrive as a letter-size PDF with the label in one corner. CrispDock can find a label on a letter or A4 sheet, cut it out and rotate it — but a shipping label needs a 4-inch printer, and the "
            f"{short} prints about 2.2 inches wide. If you ship from the same Mac, pair it with a 4-inch printer and read "
            "<a href=\"/print-shipping-labels-4x6-mac\">how CrispDock prints letter-size shipping labels on 4×6</a>.</p>"
        )
    else:
        where = "on a warehouse line" if industrial else "at the packing bench"
        letter_html = (
            "<p>Many sites hand you a shipping label on a letter-size page, which the built-in driver shrinks onto the 4×6 label. "
            f"With CrispDock the {short} gets just the label: found on the letter or A4 sheet, cut out and rotated to fill 4×6, with no cropping {where}. "
            "That covers USPS, UPS, FedEx (including international), DHL, TikTok Shop, Amazon return “cut here” pages and letter-size labels from marketplaces and carrier sites. "
            "<a href=\"/print-shipping-labels-4x6-mac\">Platform-by-platform guide</a>.</p>"
        )

    notes_html = "\n".join(f"      <h2>{esc(t)}</h2>\n      <p>{d}</p>" for t, d in m["notes"])

    faqs = [
        (f"Does CrispDock work with the {short} on Apple silicon Macs?", "Yes. CrispDock runs on Apple silicon and Intel Macs, and it’s signed and notarized."),
        ("Which macOS version do I need?", "macOS 13 Ventura or later."),
        ("Is there a free version?", FREE_ANSWER),
        ("How much does CrispDock cost?", PRICE_ANSWER),
    ] + m["extra_faq"]

    sib = [MODEL_BY_SLUG[s] for s in m["siblings"]]
    related = [
        ("/fix-blurry-zebra-labels-mac", "Fix blurry Zebra labels on a Mac"),
        ("/print-shipping-labels-4x6-mac", "Letter-size shipping labels on 4×6"),
    ] + [("/" + s["slug"], f"{s['name']} driver") for s in sib] + [("/guides", "All printers and guides")]

    intro_html = "\n      ".join(f"<p>{p}</p>" for p in m["intro"])
    body = f"""      {crumbs_html(trail)}
      <h1 class="heading">{esc(name)} driver for Mac</h1>
      {intro_html}
      {CTA_BUTTONS}

      <h2>Why the built-in Mac driver makes {esc(short)} labels blurry</h2>
      <p>Without a Zebra driver, macOS uses its generic “Zebra ZPL Label Printer” driver, which sends each page as a picture. A thermal head can only print a dot or leave it blank, so soft edges and greys become a speckled dot pattern: fuzzy barcodes. It also tends to stop and start mid-label and get sizes wrong. CrispDock converts each page into clean ZPL instead, so bars land on the printer’s dot grid and each label goes over in one piece. <a href="/fix-blurry-zebra-labels-mac">Why labels blur, in detail</a>.</p>
      {COMPARE_FIGURE}

      <h2>Set up your {esc(short)} in three steps</h2>
      <ol class="steps page-steps">
{steps_html}
      </ol>

      <h2>{esc(name)} specs CrispDock uses</h2>
      <p>{spec_intro}</p>
      {spec_table(families)}
      <p class="fine">{spec_note}</p>

      <h2>Labels on letter sheets</h2>
      {letter_html}

{notes_html}

      <h2>Questions</h2>
      {faq_html(faqs)}

      <section class="page-cta card">
        <h2>Try CrispDock with your {esc(short)}</h2>
        <p>Free to download; Pro starts with 7 days free. Questions: <a href="mailto:cs@crispdock.com">cs@crispdock.com</a>.</p>
        {CTA_BUTTONS}
      </section>

      <h2>Related</h2>
        {related_html(related)}"""

    howto = {
        "@context": "https://schema.org",
        "@type": "HowTo",
        "name": f"How to set up a {name} printer on a Mac",
        "description": f"Install CrispDock to print sharp labels from any Mac app on a {name}.",
        "tool": [{"@type": "HowToTool", "name": "CrispDock for Zebra printers (macOS 13 or later)"}],
        "step": [
            {"@type": "HowToStep", "position": i + 1, "name": t, "text": d, "url": f"{SITE}{path}#setup"}
            for i, (t, d) in enumerate(steps)
        ],
    }
    body = body.replace(f"<h2>Set up your {esc(short)} in three steps</h2>", f"<h2 id=\"setup\">Set up your {esc(short)} in three steps</h2>")
    ld = [crumbs_ld(trail), howto, faq_ld(faqs)]
    return m["slug"], page(path, m["title"], m["desc"], body, ld)


# ---------------------------------------------------------------------------------------
# B. Problem guides
# ---------------------------------------------------------------------------------------
def model_links(slugs: list[str]) -> str:
    return related_html([("/" + s, f"{MODEL_BY_SLUG[s]['name']} driver for Mac") for s in slugs])


GUIDES = []


def guide(slug, title, desc, h1, lead, hub, sections, faqs, models, extra_related=()):
    GUIDES.append(dict(slug=slug, title=title, desc=desc, h1=h1, lead=lead, hub=hub, sections=sections, faqs=faqs, models=models, extra_related=list(extra_related)))


guide(
    "fix-blurry-zebra-labels-mac",
    "Zebra Labels Blurry on Mac? Why and How to Fix It",
    "Fuzzy, dotted barcodes from a Zebra on macOS? Why the built-in driver dithers labels, what you can try yourself, and the fix that removes it.",
    "Why Zebra labels print blurry on a Mac",
    "Fuzzy barcodes, speckled text and labels that scanners reject usually aren’t the printer’s fault.",
    "Why barcodes come out fuzzy and dotted, and what actually fixes it.",
    f"""      <p>If your Zebra prints sharp labels from a PC but fuzzy ones from your Mac, you’re seeing a driver problem. Typical symptoms: barcode bars with ragged or uneven edges, small text that looks sprayed on, grey areas turned into dot patterns, and scanners that need several tries.</p>

      <h2>Why it happens</h2>
      <p>Zebra doesn’t provide an official macOS driver for its label printers (<a href="{ZEBRA_ARTICLE}">Zebra support article 000022631</a>). So macOS falls back to the generic “Zebra ZPL Label Printer” driver that comes with the system. That driver prints each page as a picture.</p>
      <p>A thermal printhead can only do two things with each dot: heat it (black) or not (white). Any shade of grey in the picture — the soft, anti-aliased edges of text and bars, a logo, a PDF that was scaled to fit — has to be faked with a pattern of scattered dots. That’s called dithering, and it’s what makes barcode edges look fuzzy. When the page is also scaled, bar widths stop lining up with whole dots, so some bars print thicker than others.</p>
      <p>The same driver often makes the printer stop and start mid-label, and app margins can shrink the label.</p>
      {COMPARE_FIGURE}

      <h2>What you can try with the built-in driver</h2>
      <ul>
        <li><strong>Match the paper size to the label.</strong> In the Print dialog choose the exact label size, such as 4×6, rather than letter.</li>
        <li><strong>Print at 100%.</strong> Turn off “Scale to fit” where the app offers it, so bars aren’t resized.</li>
        <li><strong>Set the right resolution.</strong> In the printer’s options, pick the resolution your printhead actually has (203 or 300 dpi).</li>
        <li><strong>Adjust darkness and speed.</strong> A little more darkness or a lower print speed can make thin bars more solid.</li>
        <li><strong>Rule out the hardware.</strong> Faint or streaky labels (rather than dotted ones) can mean a dirty printhead or old labels; clean the head with isopropyl alcohol and try a fresh roll.</li>
        <li><strong>Ask for a 4×6 file.</strong> If the website offers a 4×6 or thermal label format, use it instead of a letter page.</li>
      </ul>
      <p>These help with size and darkness. They don’t remove the dithering, because turning the page into a dotted picture is how the built-in driver works.</p>

      <h2>The fix: a driver that prints ZPL</h2>
      <p>CrispDock is a macOS printer driver for Zebra ZPL label printers. It replaces the generic driver for your Zebra and converts each page into clean ZPL, so bars, 2D codes and small print land exactly on the printer’s dot grid and scan first time. Each label goes to the printer in one piece, so it prints in one smooth pass, and margins added by apps are ignored so the label fills 4×6.</p>
      <p>It works from any app’s Print dialog, on macOS 13 or later, on Apple silicon and Intel. Your printers keep their names, so tools that send raw ZPL keep working, and uninstalling restores the built-in driver.</p>
      {APP_FIGURE}
      {CTA_BUTTONS}""",
    [
        ("Is my Zebra printer broken if labels look fuzzy on a Mac?", "Usually not. If labels look dotted only when printed from the Mac, the cause is the way the built-in driver converts the page. Faint or streaky labels are more likely a dirty printhead or old labels."),
        ("Can I fix blurry labels without new software?", "You can improve size and darkness by matching the paper size, printing at 100%, setting the right resolution and adjusting darkness. The dithering itself stays, because it comes from the built-in driver."),
        ("Does CrispDock change my printer settings?", "It switches your Zebra printers to the CrispDock driver but keeps their names. Uninstalling restores the built-in macOS driver."),
        ("Is there a free version?", FREE_ANSWER),
    ],
    ["zebra-zd421-mac-driver", "zebra-gk420d-mac-driver", "zebra-zp500-zp505-mac-driver", "zebra-zd620-zd621-mac-driver"],
    [("/print-shipping-labels-4x6-mac", "Print letter-size shipping labels on a 4×6 Zebra")],
)

guide(
    "print-shipping-labels-4x6-mac",
    "Print Letter-Size Shipping Labels on 4×6 Zebra (Mac)",
    "Got a letter-size PDF but a 4×6 Zebra? How to print eBay, Etsy, Amazon, Shopify, Pirate Ship, TikTok Shop and carrier labels on a Mac.",
    "Print letter-size shipping labels on a 4×6 Zebra from a Mac",
    "The label is on an 8.5×11 page, the printer takes 4×6. Here’s how to get a full-size label without cropping.",
    "eBay, Etsy, Amazon, Shopify, Pirate Ship, TikTok Shop and carrier labels.",
    f"""      <p>Many marketplaces and carrier sites give you shipping labels as a letter-size PDF: the label on one half, instructions or a packing slip on the other, sometimes two labels side by side. Send that page to a 4×6 thermal printer through the built-in macOS driver and the whole sheet gets shrunk onto the label — the barcode ends up too small to scan — or the label is cut off.</p>
      <p>The manual workaround is to crop each label in Preview, rotate it, and print at the right size every time. That works, but it’s slow and easy to get wrong when you have a stack of orders.</p>

      <h2>How CrispDock handles letter sheets</h2>
      <p>CrispDock is a macOS printer driver for Zebra ZPL printers. When a shipping label arrives on a letter or A4 page, it finds the label, cuts it out and rotates it to fill a 4×6 label automatically — one or two labels per page, framed or not, sideways or upright. You print the PDF as it came; the Zebra gets just the label, sharp enough to scan.</p>
      {SHEET_FIGURE}

      <h2>By platform</h2>
      <p>If your platform lets you choose a 4×6 label format, CrispDock prints that directly too. If you get a letter-size page instead, here’s what to expect.</p>
      <h3>eBay</h3>
      <p>Labels you buy on eBay that come as a letter-size PDF are cut out and printed as a 4×6 label. Print straight from the browser’s PDF view.</p>
      <h3>Etsy</h3>
      <p>Etsy shipping labels downloaded as a letter page print as a full 4×6 label; you don’t need to crop them first.</p>
      <h3>Amazon</h3>
      <p>Amazon return labels come on a page with a “cut here” line. CrispDock finds the label on that page and prints just the label on 4×6.</p>
      <h3>Shopify</h3>
      <p>Shopify shipping labels saved as letter-size PDFs are found on the sheet, rotated if needed and printed at full 4×6 size.</p>
      <h3>Pirate Ship</h3>
      <p>Pirate Ship labels that come as a letter page are cut out automatically; labels already set up as 4×6 print as they are.</p>
      <h3>TikTok Shop</h3>
      <p>TikTok Shop shipping labels on letter sheets are covered too, so you can print them from the browser without editing.</p>
      <h3>USPS, UPS, FedEx and DHL</h3>
      <p>Labels printed from carrier sites on letter or A4 paper — USPS, UPS, FedEx (including international) and DHL — are found, cut out and rotated to 4×6.</p>

      <h2>How to print one</h2>
      <ol>
        <li>Install CrispDock and let it set up your Zebra (USB or network).</li>
        <li>Open the label PDF in your browser or in Preview and press ⌘P.</li>
        <li>Choose your Zebra printer and 4×6 paper, then print.</li>
      </ol>
      <p>Want to check first? Drop the PDF into the CrispDock app to preview every label exactly as the printer will get it. And as with any label, check important ones before you ship.</p>
      {CTA_BUTTONS}""",
    [
        ("Do I need to crop the PDF first?", "No. Print the letter-size page as it is; CrispDock finds the label, cuts it out and rotates it to fill 4×6."),
        ("What if there are two labels on one page?", "CrispDock finds one or two labels per page, framed or not, sideways or upright."),
        ("Can I print 4×6 shipping labels on a 2-inch printer?", "No. A 4×6 label needs a 4-inch printer such as the ZD421, GK420d or ZP 500. Two-inch models like the ZD411 are for smaller labels."),
        ("Does it work with A4 sheets?", "Yes. Labels printed on letter or A4 sheets are both found and cut to 4×6."),
        ("Is there a free version?", FREE_ANSWER),
    ],
    ["zebra-zd421-mac-driver", "zebra-zd420-mac-driver", "zebra-gk420d-mac-driver", "zebra-zp450-mac-driver"],
    [("/fix-blurry-zebra-labels-mac", "Why Zebra labels are blurry on a Mac")],
)

guide(
    "print-from-iphone-to-zebra-printer",
    "Print from iPhone or iPad to a Zebra Label Printer",
    "Print Zebra labels from iPhone and iPad with AirPrint: CrispDock AirShare shares your Mac's Zebra printer on Wi‑Fi. Sharp ZPL, no app needed.",
    "Print from iPhone or iPad to a Zebra printer",
    "Use the Mac you already have as the bridge: AirShare shares its Zebra printer with your iPhone, iPad and other Macs.",
    "Share your Mac’s Zebra with iPhone, iPad and other Macs (AirShare).",
    f"""      <p>Orders come in on your phone, but the Zebra is plugged into the Mac. With CrispDock’s AirShare, the Mac shares its Zebra printers on your Wi‑Fi, so an iPhone or iPad can print to them through AirPrint, the printing built into iOS and iPadOS. Other Macs on the network can use the shared printer the same way.</p>

      <h2>How it works</h2>
      <p>Your iPhone sends the label to the Mac’s shared printer like any AirPrint job. On the Mac, CrispDock’s driver converts it into clean ZPL for the Zebra, so you get the same sharp barcodes as printing on the Mac itself — and the same handling of shipping labels that arrive on a letter-size page, which are cut out and rotated to 4×6.</p>

      <h2>Set it up</h2>
      <ol>
        <li><strong>On the Mac:</strong> install CrispDock with your Zebra connected by USB or on the network. It sets up the printer for you.</li>
        <li><strong>Share the printer:</strong> in the CrispDock app, on the Printers page, turn on “Print from iPhone and iPad (AirPrint)” and choose which printers to share. Turning on “Keep this Mac awake while sharing” stops the Mac sleeping while it’s needed.</li>
        <li><strong>On the iPhone or iPad:</strong> open the label, tap Share → Print (or the app’s Print button), choose the shared Zebra and print.</li>
      </ol>
      <p>The Mac needs to stay turned on and on the same Wi‑Fi for shared printing to work. Bluetooth isn’t involved: macOS can’t print to Bluetooth label printers, so the Zebra connects to the Mac by USB or network.</p>

      <h2>Which plan you need</h2>
      <p>AirShare works on every plan; what changes is the watermark on labels printed from other devices.</p>
      <div class="table-wrap">
        <table class="specs">
          <thead><tr><th scope="col">Plan</th><th scope="col">Printed on the Mac</th><th scope="col">Printed from iPhone, iPad or other Macs</th><th scope="col">Price</th></tr></thead>
          <tbody>
            <tr><th scope="row">Free</th><td>Watermark</td><td>Watermark</td><td>$0, forever</td></tr>
            <tr><th scope="row">Pro</th><td>No watermark</td><td>Watermark</td><td>$29.99/yr or $79 lifetime</td></tr>
            <tr><th scope="row">Pro + AirShare</th><td>No watermark</td><td>No watermark</td><td>$49.99/yr or $119 lifetime</td></tr>
          </tbody>
        </table>
      </div>
      <p>The yearly plans start with a 7-day free trial (card required, once per Mac). Already on Pro? You can add AirShare from your account: subscriptions pay only the difference for the rest of the period, and Pro Lifetime upgrades for $40.</p>
      {CTA_BUTTONS}""",
    [
        ("Does my Mac have to stay on?", "Yes. The iPhone prints through the Mac’s shared printer, so the Mac needs to stay on, awake and on the same Wi‑Fi. CrispDock can keep it awake while sharing."),
        ("Can other Macs use the shared Zebra?", "Yes. Other Macs on the network can print to the shared printer, just like an iPhone or iPad."),
        ("Can I print to a Bluetooth Zebra from my iPhone this way?", "No. macOS can’t print to Bluetooth label printers, so the Zebra has to be connected to the Mac by USB or on the network."),
        ("Why do labels from my iPhone have a watermark on Pro?", "Pro removes the watermark for labels printed on the Mac itself. Pro + AirShare also removes it for jobs from iPhone, iPad and other Macs."),
    ],
    ["zebra-zd421-mac-driver", "zebra-zd620-zd621-mac-driver", "zebra-gk420d-mac-driver"],
    [("/print-shipping-labels-4x6-mac", "Print letter-size shipping labels on a 4×6 Zebra")],
)

guide(
    "peninsula-mac-driver-alternative",
    "Peninsula Mac Driver Alternative for Zebra | CrispDock",
    "Comparing CrispDock and Peninsula's Mac thermal printer driver for Zebra printers: price, licence, trial, iPhone printing and letter-sheet labels.",
    "A Peninsula Mac driver alternative for Zebra printers",
    "Two ways to drive a Zebra label printer from a Mac, side by side.",
    "How CrispDock and Peninsula’s Mac driver compare, fact by fact.",
    """      <p>Because Zebra doesn’t publish an official macOS driver for its label printers, Mac users who want good labels look for a third-party driver. Peninsula sells one for thermal printers; CrispDock is another, made for Zebra ZPL printers. Both install as macOS printer drivers. Here’s how they compare on the points you can check publicly.</p>

      <h2>Side by side</h2>
      <div class="table-wrap">
        <table class="specs compare-table">
          <thead><tr><th scope="col"></th><th scope="col">CrispDock</th><th scope="col">Peninsula</th></tr></thead>
          <tbody>
            <tr><th scope="row">Price</th><td>Free with watermark; Pro $29.99/yr or $79 lifetime; Pro + AirShare $49.99/yr or $119 lifetime</td><td>£97 (about $118 at checkout) per computer</td></tr>
            <tr><th scope="row">Licence</th><td>Yearly or one-time lifetime; 1 Mac per key, movable</td><td>One-time, per computer, includes 1 year of upgrades</td></tr>
            <tr><th scope="row">Try before you buy</th><td>Free version with every feature (watermarked); 7-day free trial of Pro</td><td>Watermarked demo</td></tr>
            <tr><th scope="row">Labels on letter sheets cut to 4×6</th><td>Yes</td><td>Yes</td></tr>
            <tr><th scope="row">Print from iPhone / iPad (AirPrint)</th><td>Yes, with AirShare</td><td>Not mentioned on their product page</td></tr>
            <tr><th scope="row">macOS</th><td>13 or later</td><td>10.14 or later</td></tr>
            <tr><th scope="row">Apple silicon</th><td>Yes, plus Intel; signed and notarized</td><td>See Peninsula’s site</td></tr>
            <tr><th scope="row">Refunds</th><td>30 days on every payment</td><td>See Peninsula’s site</td></tr>
          </tbody>
        </table>
      </div>
      <p class="fine">Peninsula details are from their public product page in October 2026 and may change; check their site for current information. CrispDock isn’t affiliated with Peninsula.</p>

      <h2>When Peninsula may suit you</h2>
      <p>If your Mac runs a macOS version older than 13, Peninsula’s driver supports macOS 10.14 and later, while CrispDock needs macOS 13. And if you prefer a single payment that includes a year of upgrades, that is how Peninsula’s licence works.</p>

      <h2>When CrispDock may suit you</h2>
      <ul>
        <li><strong>Lower cost:</strong> Pro is $29.99 a year or $79 once, and the free version never expires.</li>
        <li><strong>Try it fully first:</strong> every feature works in the free version, and Pro starts with 7 days free.</li>
        <li><strong>iPhone and iPad:</strong> AirShare shares your Mac’s Zebra so phones and tablets can print to it with AirPrint.</li>
        <li><strong>Made for Zebra ZPL:</strong> sharp barcodes, continuous printing, the same 4×6 size from any app, and out-of-paper or cover-open status reported.</li>
      </ul>

      <h2>Trying CrispDock</h2>
      <p>Download the free version and run the installer with your Zebra connected; it switches the Zebra printers it finds to the CrispDock driver and keeps their names. Uninstalling CrispDock restores the built-in macOS driver, so if you go back to another driver you’d reinstall it.</p>
      """ + CTA_BUTTONS,
    [
        ("How much cheaper is CrispDock than Peninsula?", "Peninsula is £97 (about $118 at checkout) per computer as a one-time purchase with a year of upgrades. CrispDock Pro is $29.99 a year or $79 lifetime, and the free version costs nothing."),
        ("Do both cut labels out of letter-size sheets?", "Yes. Both can take a shipping label printed on a letter-size page and print it as a 4×6 label."),
        ("Can I try CrispDock before buying?", "Yes. The free version has every feature with a watermark, and Pro’s yearly plan starts with a 7-day free trial (card required, once per Mac)."),
        ("Does CrispDock run on older macOS versions?", "No. CrispDock needs macOS 13 or later, on Apple silicon or Intel."),
    ],
    ["zebra-zd421-mac-driver", "zebra-gk420d-mac-driver", "zebra-zp500-zp505-mac-driver", "zebra-zt-series-mac-driver"],
    [("/print-from-iphone-to-zebra-printer", "Print from iPhone or iPad to a Zebra printer")],
)


def guide_page(g: dict) -> tuple[str, str]:
    path = "/" + g["slug"]
    trail = [("Home", "/"), ("Printers & guides", "/guides"), (g["h1"], path)]
    related = g["extra_related"] + [("/guides", "All printers and guides")]
    body = f"""      {crumbs_html(trail)}
      <h1 class="heading">{esc(g["h1"])}</h1>
      <p class="page-lead">{g["lead"]}</p>
{g["sections"]}

      <h2>Questions</h2>
      {faq_html(g["faqs"])}

      <section class="page-cta card">
        <h2>Printer guides</h2>
        <p>Setup steps and specs for the printers people use this with most:</p>
        {model_links(g["models"])}
      </section>

      <h2>Related</h2>
        {related_html(related)}"""
    ld = [crumbs_ld(trail), faq_ld(g["faqs"])]
    return g["slug"], page(path, g["title"], g["desc"], body, ld)


# ---------------------------------------------------------------------------------------
# C. Hub
# ---------------------------------------------------------------------------------------
def hub_page() -> tuple[str, str]:
    path = "/guides"
    trail = [("Home", "/"), ("Printers & guides", path)]
    def cards(items):
        return "\n".join(
            f'        <li><a class="guide-card card" href="{href}"><strong>{esc(t)}</strong><span>{esc(d)}</span></a></li>'
            for href, t, d in items
        )
    printers = [("/" + m["slug"], f"{m['name']} driver for Mac", m["hub"]) for m in MODELS]
    guides = [("/" + g["slug"], g["h1"], g["hub"]) for g in GUIDES]
    body = f"""      {crumbs_html(trail)}
      <h1 class="heading">Zebra printers &amp; Mac guides</h1>
      <p class="page-lead">Setup steps and specs for each Zebra model CrispDock supports, and fixes for the problems Mac users run into most.</p>
      <p>CrispDock is a macOS printer driver for Zebra ZPL label printers. It works from any app’s Print dialog on macOS 13 or later, on Apple silicon and Intel. CrispDock was tested on real ZP 500, ZP 505 and GK420d printers; the other models use their published specs.</p>

      <h2>Printers</h2>
      <ul class="guide-grid">
{cards(printers)}
      </ul>
      <p class="fine">Not supported: EPL-only printers (such as the original LP 2844), CPCL mobile printers and Bluetooth connections.</p>

      <h2>Guides</h2>
      <ul class="guide-grid">
{cards(guides)}
      </ul>

      <section class="page-cta card">
        <h2>Try it with your printer</h2>
        <p>CrispDock is free to download and use, with a watermark on labels until you pick a plan. Pro starts with 7 days free.</p>
        {CTA_BUTTONS}
      </section>"""
    item_list = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": "CrispDock printers and guides",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "url": SITE + href, "name": t}
            for i, (href, t, _) in enumerate(printers + guides)
        ],
    }
    return "guides", page(
        path,
        "Zebra Printer Mac Drivers & Guides | CrispDock",
        "Mac setup guides for Zebra ZD421, ZD420, GK420d, ZP 450, ZP 500, ZT series and more, plus fixes for blurry labels and letter-size shipping labels.",
        body,
        [crumbs_ld(trail), item_list],
    )


def main() -> None:
    pages = [model_page(m) for m in MODELS] + [guide_page(g) for g in GUIDES] + [hub_page()]
    for slug, text in pages:
        (PUBLIC / f"{slug}.html").write_text(text, encoding="utf-8")
        print(f"wrote public/{slug}.html  ->  {SITE}/{slug}")


if __name__ == "__main__":
    main()
