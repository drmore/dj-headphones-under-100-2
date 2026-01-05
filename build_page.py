from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import List, Dict
from urllib.parse import quote_plus

PAGE_TITLE = "DJ headphones under $100 — shortlist"
PAGE_DESC = (
    "A fast shortlist of DJ headphones with short notes and a 'check current price' link to Amazon. "
    "This no-API mode uses manual product details (name, summary, typical price range). "
    "Images are optional and must be provided as URLs you have rights to use."
)

DEFAULT_KEYWORDS = "dj headphones"
DEFAULT_MAX_PRICE_CENTS = 10000  # $100.00


def esc(s: str) -> str:
    return (s.replace("&", "&amp;")
             .replace("<", "&lt;")
             .replace(">", "&gt;")
             .replace('"', "&quot;")
             .replace("'", "&#39;"))


def load_products(path: str = "asin_list.json") -> List[Dict[str, str]]:
    data = json.loads(open(path, "r", encoding="utf-8").read())
    out: List[Dict[str, str]] = []
    seen = set()
    for row in data:
        asin = (row.get("asin") or "").strip()
        if not asin or asin in seen:
            continue
        out.append({
            "asin": asin,
            "name": (row.get("name") or "").strip(),
            "summary": (row.get("summary") or "").strip(),
            "price_range": (row.get("price_range") or "").strip(),
            "image_url": (row.get("image_url") or "").strip(),
        })
        seen.add(asin)
    return out


def dp_url(asin: str, tag: str) -> str:
    return f"https://www.amazon.com/dp/{asin}?tag={tag}"


def search_url(tag: str, keywords: str = DEFAULT_KEYWORDS, max_price_cents: int = DEFAULT_MAX_PRICE_CENTS) -> str:
    return (
        "https://www.amazon.com/s?"
        f"k={quote_plus(keywords)}"
        f"&rh=p_36%3A-{max_price_cents}"
        "&s=price-asc-rank"
        f"&tag={tag}"
    )


HTML = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <meta name="description" content="{desc}">
  <style>
    body {{ font-family: system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif; margin: 0; background:#fafafa; color:#111; }}
    header, main, footer {{ max-width: 980px; margin: 0 auto; padding: 18px 16px; }}
    h1 {{ font-size: 28px; margin: 8px 0 8px; }}
    p {{ margin: 6px 0; line-height: 1.45; }}
    .meta {{ color:#444; font-size: 14px; }}
    .card {{ background:white; border-radius: 14px; overflow:hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.06); padding: 14px; margin: 12px 0; }}
    .grid {{ display:grid; grid-template-columns: 120px 1fr 170px; gap: 14px; align-items:center; }}
    .imgwrap {{ width:120px; height:80px; border-radius: 12px; background:#f3f4f6; overflow:hidden; }}
    .imgwrap img {{ width:100%; height:100%; object-fit:cover; display:block; }}
    .name {{ font-weight: 750; font-size: 16px; margin: 0 0 4px; }}
    .sub {{ color:#444; font-size: 14px; margin: 0 0 6px; }}
    .price {{ font-weight: 750; font-size: 14px; margin: 0; }}
    .btn {{ display:inline-block; padding: 10px 12px; border:1px solid #ddd; border-radius: 12px; background:#fff; font-weight: 700; text-align:center; }}
    .btn:hover {{ background:#f7f7f7; text-decoration:none; }}
    a {{ color:#0b57d0; text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    @media (max-width: 760px) {{
      .grid {{ grid-template-columns: 1fr; }}
      .imgwrap {{ width:100%; height:180px; }}
    }}
  </style>
</head>
<body>
  <header>
    <h1>{h1}</h1>
    <p>{pdesc}</p>
    <p class="meta">Daily build: {updated}</p>
  </header>

  <main>
    <div class="card">
      <p><strong>Note:</strong> Prices change constantly. “Typical price” is a manual guide. Use the button to check the current price on Amazon.</p>
      <p><a class="btn" href="{search}" rel="nofollow sponsored">Browse Amazon under $100 (price low→high)</a></p>
    </div>

    {cards}
  </main>

  <footer>
    <p><strong>Affiliate disclosure:</strong> As an Amazon Associate, I earn from qualifying purchases.</p>
    <p><a href="privacy.html">Privacy</a> · <a href="disclosure.html">Disclosure</a></p>
  </footer>
</body>
</html>
"""


def card(p: Dict[str, str], tag: str) -> str:
    asin = p["asin"]
    name = p.get("name") or f"Product ({asin})"
    summary = p.get("summary") or "Add a one-line note in asin_list.json."
    price_range = p.get("price_range") or "(add a typical price range)"
    img = p.get("image_url") or "assets/placeholder.svg"
    url = dp_url(asin, tag)

    return (
        '<div class="card">'
        '  <div class="grid">'
        f'    <div class="imgwrap"><img src="{esc(img)}" alt="{esc(name)}"></div>'
        '    <div>'
        f'      <div class="name">{esc(name)}</div>'
        f'      <div class="sub">{esc(summary)}</div>'
        f'      <div class="price">Typical: {esc(price_range)}</div>'
        f'      <div class="sub">ASIN: {esc(asin)}</div>'
        '    </div>'
        f'    <div><a class="btn" href="{esc(url)}" rel="nofollow sponsored">Check current price</a></div>'
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
        search=esc(search_url(tag)),
    )

    open("index.html", "w", encoding="utf-8").write(html)
    open("products.json", "w", encoding="utf-8").write(json.dumps({"products": products, "updated": updated}, indent=2))


if __name__ == "__main__":
    main()
