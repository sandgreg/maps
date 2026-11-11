# Nordic Chase route maps

Interactive route maps embedded on nordicchase.com, hosted with GitHub Pages.

| Page | What it shows |
|---|---|
| `series.html` | All four Chases on one map, drawn in order, each linking to its page |
| `ber-cph.html` | Chase 1, Berlin to Copenhagen, with elevation profile (road; `?edition=gravel` for gravel) |
| `cph-osl.html` | Chase 2, Copenhagen to Oslo, with elevation profile |
| `ams-cph.html` | Chase 3, Amsterdam to Copenhagen, with elevation profile |
| `cph-sto.html` | Chase 4, Copenhagen to Stockholm, with elevation profile |

Live at `https://sandgreg.github.io/maps/<page>`.

## Update a map

1. Replace a GPX in `routes/` (`<slug>-road.gpx`, `<slug>-gravel.gpx`) or edit `chases.json` (names, colours, links).
2. Run `python3 build.py`.
3. Commit and push to `main`.

## Embed on Squarespace

Add a Code Block and paste:

```html
<div style="position:relative;width:100%;height:75vh;min-height:520px;max-height:800px;border-radius:12px;overflow:hidden">
  <iframe src="https://sandgreg.github.io/maps/series.html"
          style="position:absolute;inset:0;width:100%;height:100%;border:0"
          loading="lazy" allowfullscreen title="Nordic Chase route map"></iframe>
</div>
```

Map data © OpenStreetMap contributors, basemap by OpenFreeMap, rendered with MapLibre GL (BSD-3, see `vendor/`).

On the race pages the map runs in story mode (`?mode=story`), driven by the page as you scroll. See `CLAUDE.md` for the options.
