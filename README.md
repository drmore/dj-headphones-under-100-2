# DJ headphones shortlist (No-API, human-friendly)

This version is intentionally **human-readable** without Amazon PA-API access.

## What you can show (compliant)
- Product name (manual)
- One-line summary (manual)
- Typical price range (manual)
- Optional image URL (ONLY if you have rights to use the image)

## What you should NOT do without PA-API
- Scrape Amazon for titles/images/prices
- Hotlink/copy Amazon images without permission

## Update content
Edit `asin_list.json` and fill in `name`, `summary`, `price_range`.
Optionally add `image_url` if you have a licensed image.

Then run the GitHub Action (workflow_dispatch) or wait for daily rebuild.
