# DJ headphones shortlist (JSON-driven, no Amazon API)

This build renders product cards (name, image, description) from `products_input.json`,
and appends your Amazon Associates tag to each product link at build time.

## Setup
- Add GitHub Secret: `AMZ_PARTNER_TAG` (e.g. `yourtag-20`)
- Run Actions → Daily rebuild

## Edit products
Edit `products_input.json` and commit. The site rebuilds.
