#!/usr/bin/env python3
"""Build the Nordic Chase route maps from the GPX files.

Usage:  python3 build.py

Reads chases.json and the GPX files in routes/, then writes:
  series.html          all Chases on one map, drawn in order
  <slug>.html          one page per Chase with an elevation profile

(cph-oslo.html is a hand-written redirect to cph-osl.html, kept so older embeds keep working.)

Pure Python 3, no packages needed. The MapLibre library in vendor/ is inlined
into every page, so each page is a single self-contained file.
"""
import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).parent
ROUTE_PAGE_COLOR = "#ff6a2b"   # route colour on the single-Chase pages
PROFILE_STEP_KM = 0.15         # elevation profile sample spacing
CLIMB_THRESHOLD_M = 0.5        # ignore elevation wiggles smaller than this (closest to Strava)
SIMPLIFY_SINGLE = 0.00004      # line simplification tolerance (degrees), single-Chase pages
SIMPLIFY_SERIES = 0.00006      # line simplification tolerance (degrees), series map

MAPLIBRE_CSS_TAG = '<link rel="stylesheet" href="https://unpkg.com/maplibre-gl@4.7.1/dist/maplibre-gl.css">'
MAPLIBRE_JS_TAG = '<script src="https://unpkg.com/maplibre-gl@4.7.1/dist/maplibre-gl.js"></script>'


def load_gpx(path):
    src = Path(path).read_text(encoding="utf-8")
    pts = [(float(a), float(b), float(c)) for a, b, c in re.findall(
        r'<trkpt lat="([^"]+)" lon="([^"]+)">\s*<ele>([^<]+)</ele>', src)]
    if len(pts) < 2:
        raise SystemExit(f"{path}: no track points with elevation found")
    return pts


def haversine_km(a, b):
    la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 2 * 6371.0088 * math.asin(math.sqrt(h))


def cumulative_km(pts):
    cum = [0.0]
    for i in range(1, len(pts)):
        cum.append(cum[-1] + haversine_km(pts[i - 1], pts[i]))
    return cum


def total_ascent(pts):
    asc, ref = 0.0, pts[0][2]
    for _, _, e in pts:
        if e - ref > CLIMB_THRESHOLD_M:
            asc += e - ref
            ref = e
        elif ref - e > CLIMB_THRESHOLD_M:
            ref = e
    return round(asc)


def simplify(pts, eps):
    """Ramer-Douglas-Peucker; returns indices of points to keep."""
    xy = [(p[1] * math.cos(math.radians(p[0])), p[0]) for p in pts]
    keep = [False] * len(xy)
    keep[0] = keep[-1] = True
    stack = [(0, len(xy) - 1)]
    while stack:
        s, e = stack.pop()
        if e <= s + 1:
            continue
        ax, ay = xy[s]
        bx, by = xy[e]
        dx, dy = bx - ax, by - ay
        length = math.hypot(dx, dy)
        best, best_d = -1, -1.0
        for i in range(s + 1, e):
            px, py = xy[i]
            d = math.hypot(px - ax, py - ay) if length == 0 else abs(dx * (py - ay) - dy * (px - ax)) / length
            if d > best_d:
                best, best_d = i, d
        if best_d > eps:
            keep[best] = True
            stack += [(s, best), (best, e)]
    return [i for i, k in enumerate(keep) if k]


def inline_maplibre(html):
    js = (ROOT / "vendor/maplibre-gl.js").read_text(encoding="utf-8").replace("</script", "<\\/script")
    css = (ROOT / "vendor/maplibre-gl.css").read_text(encoding="utf-8")
    assert MAPLIBRE_CSS_TAG in html and MAPLIBRE_JS_TAG in html, "template is missing the MapLibre tags"
    html = html.replace(MAPLIBRE_CSS_TAG, "<style>/* MapLibre GL 4.7.1 */\n" + css + "\n</style>")
    return html.replace(MAPLIBRE_JS_TAG, "<script>/* MapLibre GL 4.7.1 (BSD-3) */\n" + js + "\n</script>")


def to_json(data):
    return json.dumps(data, separators=(",", ":"), ensure_ascii=False)


def build_route_page(chase, pts, cum, ascent, template):
    keep = simplify(pts, SIMPLIFY_SINGLE)
    profile, t, i, n = [], 0.0, 0, len(pts)
    while t <= cum[-1]:
        while i < n - 1 and cum[i + 1] < t:
            i += 1
        profile.append([round(t, 2), round(pts[i][2]), round(pts[i][0], 5), round(pts[i][1], 5)])
        t += PROFILE_STEP_KM
    profile.append([round(cum[-1], 2), round(pts[-1][2]), round(pts[-1][0], 5), round(pts[-1][1], 5)])
    data = {
        "name": chase["name"], "km": round(cum[-1], 1), "ascent": ascent,
        "max": round(max(p[2] for p in pts)),
        "line": [[round(pts[i][1], 5), round(pts[i][0], 5), round(cum[i], 2)] for i in keep],
        "profile": profile,
    }
    html = template.replace("/*ROUTE_DATA*/", to_json(data)).replace("/*ROUTE_COLOR*/", ROUTE_PAGE_COLOR)
    return inline_maplibre(html)


def main():
    chases = json.loads((ROOT / "chases.json").read_text(encoding="utf-8"))
    route_tpl = (ROOT / "src/route-template.html").read_text(encoding="utf-8")
    series_tpl = (ROOT / "src/series-template.html").read_text(encoding="utf-8")
    series = []
    for c in chases:
        pts = load_gpx(ROOT / c["gpx"])
        cum = cumulative_km(pts)
        ascent = total_ascent(pts)
        (ROOT / f"{c['slug']}.html").write_text(build_route_page(c, pts, cum, ascent, route_tpl), encoding="utf-8")
        keep = simplify(pts, SIMPLIFY_SERIES)
        series.append({
            "tag": c["tag"], "name": c["name"], "color": c["color"], "link": c["link"],
            "km": round(cum[-1], 1), "ascent": ascent,
            "line": [[round(pts[i][1], 5), round(pts[i][0], 5)] for i in keep],
        })
        print(f"{c['tag']:8} {c['name']:26} {cum[-1]:6.1f} km  {ascent:5d} m  -> {c['slug']}.html")
    html = inline_maplibre(series_tpl.replace("/*SERIES_DATA*/", to_json(series)))
    (ROOT / "series.html").write_text(html, encoding="utf-8")
    print("series map -> series.html")


if __name__ == "__main__":
    main()
