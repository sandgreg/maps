# Nordic Chase route maps

Interactive route maps for nordicchase.com (Squarespace 7.1). Hosted with GitHub Pages from `main` at
`https://sandgreg.github.io/maps/<file>.html` and embedded on the site with an iframe in a Squarespace Code Block.

## Layout

- `chases.json`: one entry per Chase (slug, tag, name, GPX path, series colour, link to its page on nordicchase.com). Order = draw order on the series map.
- `routes/*.gpx`: route GPX files exported from Strava (they carry Strava's elevation data).
- `src/route-template.html`: single-Chase page (route, km markers, interactive elevation profile, draw-on animation).
- `src/series-template.html`: all Chases on one map, drawn one after another, legend links to each Chase page.
- `build.py`: turns the GPX files into map data and writes the pages. Pure Python 3, no dependencies.
- `vendor/`: MapLibre GL 4.7.1, inlined into every page by the build.
- Built output (committed, served by Pages): `series.html`, `<slug>.html`. `cph-oslo.html` is a hand-written redirect to `cph-osl.html` for older links.

## Workflow

1. Edit `chases.json`, a GPX in `routes/`, or a template in `src/`. Never hand-edit the built `*.html` pages; they are overwritten.
2. `python3 build.py`
3. Preview: `python3 -m http.server 8000`, then open `http://localhost:8000/series.html` (or a Chase page) in a browser and check the basemap, route, animation and phone width.
4. Commit source and built pages together, push to `main`. Pages updates in a minute or two.

To add a Chase: drop the GPX in `routes/`, add an entry to `chases.json`, build. To update a route: replace its GPX with the same file name, build.

## Decisions worth keeping

- Basemap: OpenFreeMap "dark" style, no API key and no billing (chosen over Mapbox to avoid any per-load cost). Maritime boundary lines are hidden at runtime (`maritime != 1` added to every `boundary` layer filter).
- MapLibre is inlined rather than loaded from a CDN so each page is one self-contained file. Keep the version pinned.
- Elevation gain: raw GPX elevation with a 0.5 m threshold, which lands closest to Strava's figure. Profile plots raw elevation every 150 m; below sea level (ferry/water) is shown as 0.
- Series animation grows each route's GeoJSON and its leading dot in the same source, so the dot stays on the tip of the line (a `line-gradient` + DOM marker drifted apart).
- Single-Chase pages use one brand orange (`ROUTE_PAGE_COLOR` in `build.py`); series colours come from `chases.json`.
- Clicking a Chase (legend row or route line) opens its page with `target="_top"`, so it leaves the iframe.
- `cooperativeGestures` is on when embedded, so visitors scroll the Squarespace page instead of zooming the map.
- The Copenhagen hub marker position is the `CPH` constant in `src/series-template.html`.
