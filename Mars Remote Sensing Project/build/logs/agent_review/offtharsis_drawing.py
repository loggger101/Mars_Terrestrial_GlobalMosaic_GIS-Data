# -*- coding: utf-8 -*-
r"""The agent's off-Tharsis labels (KB §69.105; rule in offtharsis_registration.md), as vertices read off the plates in
review_sheets\offtharsis\plates. Writes offtharsis_drawing.json beside this file, the input of
apply_offtharsis_labels.py. Edifice only: no apron polygon could be drawn by the rule (see the KB).

Positions: the caldera walls and the cone as the 200 m DEM hillshade shows them (the maps' own grid, global60_dem.tif),
identified on CTX (S1, S2: the same rims; CTX against the stack's day IR at Syrtis correlates weakly, r <= 0.25, so
the hillshade sets the line). Meroe Patera's ring is near-circular, so its pieces are drawn as annular sectors about
the centre read off S2's hillshade; Nili Patera's open caldera is drawn vertex by vertex off S1.
"""
import os, json, math

HERE = os.path.dirname(os.path.abspath(__file__))


def ring(cx, cy, r, n=24):
    k = 1.0 / math.cos(math.radians(cy))
    return [[round(cx + r * k * math.cos(2 * math.pi * i / n), 4), round(cy + r * math.sin(2 * math.pi * i / n), 4)]
            for i in range(n)]


def sector(cx, cy, r0, r1, a0, a1, n=16):
    """Annulus between radii r0 and r1 (deg of latitude), angles a0..a1 (deg, counter-clockwise from east)."""
    k = 1.0 / math.cos(math.radians(cy))
    angs = [math.radians(a0 + (a1 - a0) * i / n) for i in range(n + 1)]
    out = [[cx + r1 * k * math.cos(a), cy + r1 * math.sin(a)] for a in angs]
    out += [[cx + r0 * k * math.cos(a), cy + r0 * math.sin(a)] for a in reversed(angs)]
    return [[round(x, 4), round(y, 4)] for x, y in out]


MEROE = (68.78, 7.00)       # the ring's centre on S2's hillshade (gazetteer 68.8E, 7.0N, 53 km)
polys = {
    "E1": {"plate": "S1", "note": "Nili Patera caldera floor, inside the west and north walls",
           "pts": [[66.80, 8.65], [66.80, 9.05], [66.90, 9.28], [67.05, 9.36], [67.25, 9.37], [67.25, 9.10],
                   [67.10, 8.90], [67.00, 8.65]]},
    "E2": {"plate": "S1", "note": "Nili Patera caldera wall and rim, west and north",
           "pts": [[66.58, 8.60], [66.60, 9.05], [66.70, 9.35], [66.92, 9.55], [67.30, 9.60], [67.30, 9.45],
                   [67.00, 9.44], [66.80, 9.28], [66.73, 9.05], [66.72, 8.60]]},
    "E3": {"plate": "S1", "note": "Nili Tholus, the cone in Nili Patera (gazetteer 7 km)",
           "pts": ring(67.32, 9.17, 0.06)},
    "E4": {"plate": "S2", "note": "Meroe Patera caldera floor, inside the ring",
           "pts": ring(MEROE[0], MEROE[1], 0.32)},
    "E5": {"plate": "S2", "note": "Meroe Patera caldera wall and rim, north",
           "pts": sector(MEROE[0], MEROE[1], 0.36, 0.47, 25, 155)},
    "E6": {"plate": "S2", "note": "Meroe Patera caldera wall and rim, south-east",
           "pts": sector(MEROE[0], MEROE[1], 0.36, 0.47, -80, 10)},
}
for p in polys.values():
    p["class"] = 5
json.dump(polys, open(os.path.join(HERE, "offtharsis_drawing.json"), "w", encoding="utf-8"), indent=1)
print(len(polys), "polygons")
