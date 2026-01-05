# DJ headphones shortlist (JSON-driven, image fixes)

If you are seeing missing images, it is usually one of:
- Hotlink protection by the image host
- Mixed-content / redirects / blocked referrers
- Intermittent CDN issues

This build includes:
- `onerror` fallback to a local placeholder
- Optional image caching during build (recommended)

## Recommended: Cache images during build
This avoids hotlink protection and makes your site faster.

1) In GitHub Actions secrets: set `AMZ_PARTNER_TAG`
2) In the workflow, ensure `CACHE_IMAGES=1` (already set in this repo template)

The action will download images and commit them to `assets/img/`.

## Editing products
Edit `products_input.json` and commit.
