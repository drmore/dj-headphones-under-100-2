from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from urllib.parse import urlencode, urlparse, parse_qsl, urlunparse

PAGE_TITLE = "DJ headphones — shortlist"
PAGE_DESC = "A simple shortlist of DJ headphones with photos, short notes, and Amazon links."
INPUT_JSON = "products_input.json"


def esc(s: str) -> str:
    return (s.replace("&", "&amp;")
             .replace("<", "&lt;")
             .replace(">", "&gt;")
             .replace('"', "&quot;")
             .replace("'", "&#39;"))


def with_affiliate_tag(url: str, tag: str) -> str:
    """Ensure the Amazon URL contains ?tag=... while keeping existing params."""
    u = urlparse(url)
    q = dict(parse_qsl(u.query, keep_blank_values=True))
    q["tag"] = tag
    new_query = urlencode(q, doseq=True)
    return urlunparse((u.scheme, u.netloc, u.path, u.params, new_query, u.fragment))


def load_products(path: str = INPUT_JSON) -> list[dict]:
    items = json.loads(open(path, "r", encoding="utf-8").read())
    out = []
    seen = set()
    for it in items:
        asin = (it.get("amazon_asin") or "").strip()
        if not asin or asin in seen:
            continue
        out.append({
            "asin": asin,
            "name": (it.get("product_name") or "").strip() or f"Product ({asin})",
            "description": (it.get("description") or "").strip(),
            "image_url": (it.get("image_url") or "").strip(),
            "amazon_url": (it.get("amazon_url") or f"https://www.amazon.com/dp/{asin}").strip(),
        })
        seen.add(asin)
    return out


HTML = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <meta name="description" content="{desc}">
  <style>
    body {{ font-family: system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif; margin: 0; background:#fafafa; color:#111; }}
    header, main, footer {{ max-width: 1060px; margin: 0 auto; padding: 18px 16px; }}
    h1 {{ font-size: 28px; margin: 10px 0 8px; }}
    p {{ margin: 6px 0; line-height: 1.45; }}
    .meta {{ color:#444; font-size: 14px; }}
    .grid {{ display:grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px; }}
    .card {{ background:white; border-radius: 14px; overflow:hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.06); display:flex; flex-direction:column; }}
    .img {{ background:#f3f4f6; aspect-ratio: 4 / 3; overflow:hidden; }}
    .img img {{ width:100%; height:100%; object-fit:contain; display:block; background:#fff; }}
    .content {{ padding: 12px 14px 14px; display:flex; flex-direction:column; gap:8px; flex:1; }}
    .name {{ font-weight: 800; font-size: 16px; margin: 0; }}
    .desc {{ color:#333; font-size: 14px; margin:0; }}
    .asin {{ color:#666; font-size: 12px; margin:0; }}
    .actions {{ margin-top:auto; display:flex; gap:10px; align-items:center; }}
    .btn {{ display:inline-block; padding: 10px 12px; border:1px solid #ddd; border-radius: 12px; background:#fff; font-weight: 700; text-align:center; }}
    .btn:hover {{ background:#f7f7f7; text-decoration:none; }}
    a {{ color:#0b57d0; text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    @media (max-width: 980px) {{
      .grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
    }}
    @media (max-width: 640px) {{
      .grid {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <header>
    <h1>{h1}</h1>
    <p>{pdesc}</p>
    <p class="meta">Last updated: {updated}</p>
  </header>

  <main>
    <div class="grid">
      {cards}
    </div>
  </main>

  <footer>
    <p><strong>Affiliate disclosure:</strong> As an Amazon Associate, I earn from qualifying purchases.</p>
    <p><a href="privacy.html">Privacy</a> · <a href="disclosure.html">Disclosure</a></p>
  </footer>
</body>
</html>
"""


def card(p: dict, tag: str) -> str:
    url = with_affiliate_tag(p["amazon_url"], tag)
    img = p.get("image_url") or ""
    img_html = f'<img src="{esc(img)}" alt="{esc(p["name"])}" loading="lazy" referrerpolicy="no-referrer">' if img else ''
    return (
        '<div class="card">'
        f'  <div class="img">{img_html}</div>'
        '  <div class="content">'
        f'    <p class="name">{esc(p["name"])}</p>'
        f'    <p class="desc">{esc(p.get("description") or "")}</p>'
        f'    <p class="asin">ASIN: {esc(p["asin"])}</p>'
        '    <div class="actions">'
        f'      <a class="btn" href="{esc(url)}" rel="nofollow sponsored">Check price on Amazon</a>'
        '    </div>'
        '  </div>'
        '</div>'
    )


def main() -> None:
    tag = os.environ.get("AMZ_PARTNER_TAG", "").strip()
    if not tag:
        raise SystemExit("Missing AMZ_PARTNER_TAG (set as GitHub Actions secret).")

    products = load_products()
    updated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    cards = "\n".join(card(p, tag) for p in products)

    html = HTML.format(
        title=esc(PAGE_TITLE),
        desc=esc(PAGE_DESC),
        h1=esc(PAGE_TITLE),
        pdesc=esc(PAGE_DESC),
        updated=updated,
        cards=cards,
    )
    open("index.html", "w", encoding="utf-8").write(html)
    open("products.json", "w", encoding="utf-8").write(json.dumps({"products": products, "updated": updated}, indent=2))


if __name__ == "__main__":
    main()
