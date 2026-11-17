# Changelog

Versions are git tags on `main`. Pages updates a minute or two after a push to `main`.
Change things on a branch, check the preview, then merge. Never hand-edit the built `*.html` pages.

## v2.0 (unreleased, branch `series-embed`)
- New `series-embed.html`: same map as `series.html`, legend hidden on phones, route fills the frame, refits if the iframe is resized.
- `series.html` unchanged in behaviour, so older embeds keep working.
- `squarespace/chases-section-v2.html`: homepage Chases section Code Block that uses `series-embed.html`.

## v1.0 (commit 47857ef)
- `series.html` with legend (road and gravel distance per Chase), one page per Chase with elevation profile.
- `squarespace/chases-section-v1.html`: homepage Chases section Code Block that uses `series.html`.
