# -*- coding: utf-8 -*-
r"""Sheets for the author's check of the 86 lava-flow margins the agent traced on CTX (D33; KB §69.52, §69.104), so
the check can be done without Pro, as the candidate review is (§69.51).

    python make_margin_check_sheets.py [--out <folder>]      (default <drive>\Mars Project\review_sheets\margins_check)

Each margin in Landform_LavaFlowMargins gets a slot, M01-M86 in OBJECTID order, and a row of two panels over its own
24 km tracing plate (make_margin_plates.py's windows, the same cached CTX view the tracing used): 1. CTX with the
margin in orange, its slot at its middle, and the plate's other margins thin and white; 2. the same CTX with only the
margin's two ends ringed, so the ground under the line stays visible. Three rows to a sheet (margins_01.png holds
M01-M03). Neither the agent's confidence nor its margin type nor the geologic map's contact is shown, so the check is
of the line against the image alone. index.json maps each slot to its OBJECTID, plate, length, confidence and type,
and the rule the answers are scored by (README.md in the folder; registered before any answer, KB §69.104).

Read-only on the gdb and the CTX cache: a plate whose view is not cached is refused, never rendered (no network,
no Pro). ArcGIS Python.
"""
import os, sys, json
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import numpy as np
import arcpy
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from paths import GDB, on_drive
from make_ctx_chips import checked_far, checked_near
from make_review_chips import arg

PLATES = on_drive(r"Mars Project\review_sheets\margins_ath")
FC = os.path.join(GDB, "Landform_LavaFlowMargins")
ROWS = 3
ORANGE, WHITE = "#ff7a1a", "#ffffff"


def no_render():
    raise SystemExit("a plate's CTX view is not in the cache; this script never renders (run make_margin_plates.py)")


def margins():
    """Every margin: OBJECTID, plate, vertices (x, y) in the CM180 metres the plates use, length, confidence, type."""
    out = []
    with arcpy.da.SearchCursor(FC, ["OID@", "Evidence", "Confidence", "MarginType", "SHAPE@LENGTH", "SHAPE@"],
                               sql_clause=(None, "ORDER BY OBJECTID")) as cur:
        for oid, ev, conf, typ, length, shp in cur:
            plate = ev.rsplit("plate ", 1)[1].split()[0].strip(",;)")
            pts = [(p.X, p.Y) for part in shp for p in part if p]
            out.append({"oid": oid, "plate": plate, "pts": pts, "km": round(length / 1000.0, 2),
                        "confidence": conf, "type": typ})
    return out


def midpoint(pts):
    """The point halfway along the line, for its label."""
    a = np.array(pts)
    seg = np.hypot(*np.diff(a, axis=0).T)
    cum = np.concatenate([[0], np.cumsum(seg)])
    h = cum[-1] / 2.0
    i = min(int(np.searchsorted(cum, h)) - 1, len(seg) - 1)
    i = max(i, 0)
    t = (h - cum[i]) / seg[i] if seg[i] else 0.0
    return a[i] + t * (a[i + 1] - a[i])


def main():
    out = arg("--out", on_drive(r"Mars Project\review_sheets\margins_check"))
    os.makedirs(out, exist_ok=True)
    idx = json.load(open(os.path.join(PLATES, "index.json")))
    half, cell = idx["half_m"], idx["cell_m"]
    ms = margins()
    for k, m in enumerate(ms, 1):
        m["slot"] = "M%02d" % k
    by_plate = {}
    for m in ms:
        by_plate.setdefault(m["plate"], []).append(m)
    views = {}
    for plate in sorted(by_plate):
        w = idx["windows"][plate]
        cx, cy = w["cx"], w["cy"]
        key = "margin_%d_%d" % (round(cx / cell - 0.5), round(cy / cell - 0.5))
        far, e_far, _ = checked_far(no_render, key, cx, cy, 48)
        img, ext, note = checked_near(no_render, key, cx, cy, half, far, e_far)
        views[plate] = (img, ext, note, w)
    plt.rcParams.update({"font.family": "Arial", "font.size": 8})
    sheets = [ms[i:i + ROWS] for i in range(0, len(ms), ROWS)]
    for s, rows in enumerate(sheets, 1):
        fig, axes = plt.subplots(len(rows), 2, figsize=(10.4, 5.1 * len(rows)), dpi=110, squeeze=False)
        for r, m in enumerate(rows):
            img, ext, note, w = views[m["plate"]]
            x0, y0 = w["x0"], w["y0"]
            a = np.array(m["pts"])
            for c, ax in enumerate(axes[r]):
                ax.imshow(img, extent=ext, interpolation="nearest")
                ax.set_xlim(x0, x0 + 2 * half); ax.set_ylim(y0, y0 + 2 * half)
                ticks = np.arange(0, 2 * half + 1, 4000.0)
                ax.set_xticks(x0 + ticks); ax.set_xticklabels(["%d" % (t / 1000) for t in ticks])
                ax.set_yticks(y0 + ticks); ax.set_yticklabels(["%d" % (t / 1000) for t in ticks])
                ax.tick_params(labelsize=6)
                if c == 0:
                    for o in by_plate[m["plate"]]:
                        if o is not m:
                            b = np.array(o["pts"])
                            ax.plot(b[:, 0], b[:, 1], color=WHITE, lw=0.7, alpha=0.7)
                            q = midpoint(o["pts"])
                            ax.text(q[0], q[1], o["slot"], color=WHITE, fontsize=6, alpha=0.8)
                    ax.plot(a[:, 0], a[:, 1], color=ORANGE, lw=1.4)
                    q = midpoint(m["pts"])
                    ax.text(q[0], q[1], " " + m["slot"], color=ORANGE, fontsize=10, fontweight="bold",
                            path_effects=[matplotlib.patheffects.withStroke(linewidth=2, foreground="black")])
                    ax.set_title("%s   CTX + line (%.1f km), plate %s, %.2f E %.2f N   %s"
                                 % (m["slot"], m["km"], m["plate"], w["lon"], w["lat"], note), loc="left", fontsize=8)
                else:
                    for p in (a[0], a[-1]):
                        ax.plot(p[0], p[1], "o", ms=11, mfc="none", mec=ORANGE, mew=1.4)
                    ax.set_title("%s   CTX, the line's two ends ringed   km from the plate's SW corner" % m["slot"],
                                 loc="left", fontsize=8)
        fig.tight_layout()
        fig.savefig(os.path.join(out, "margins_%02d.png" % s), facecolor="white")
        plt.close(fig)
        print("margins_%02d.png  %s" % (s, " ".join(m["slot"] for m in rows)), flush=True)
    json.dump({"source": "Landform_LavaFlowMargins (%d lines)" % len(ms),
               "letters": {"k": "keep", "p": "partly", "n": "no margin", "u": "unsure"},
               "slots": {m["slot"]: {k: m[k] for k in ("oid", "plate", "km", "confidence", "type")} for m in ms}},
              open(os.path.join(out, "index.json"), "w", encoding="utf-8"), indent=1)
    print("%d margins on %d sheets -> %s" % (len(ms), len(sheets), out))


if __name__ == "__main__":
    import matplotlib.patheffects
    main()
