# -*- coding: utf-8 -*-
r"""Layout 14: validation of the machine candidates, by review and by reference (NEXT-STEPS 3.7, KB §46).

Built before the review starts and rerun after each review session, so the sheet fills in as the
digitising proceeds. Per type area and class:

  candidates     rows in the candidate class, split by Review: accept / reject / unsure / not reviewed
  precision      accept / (accept + reject): the detector's precision as judged in review
  drawn by hand  digitised features in the window with no SourceID: what the detector missed
                 (breached craters, lava margins, channels it never traced)
  recall         accepted copies / (accepted copies + drawn by hand): the share of the features mapped
                 by hand that the detector had proposed
  Robbins        for the closed depressions, recall and precision against Ref_Craters_Robbins2020 at
                 D >= 1 km, read from logs\crater_density.json (make_crater_density.py, KB §42.3)

  maps "Ius Chasma — validation", "Athabasca Valles — validation"   the candidates by review state, the
                 accepted copies and the hand-drawn misses, Robbins craters for reference; every split is
                 a definition query, so the maps are live in Pro while reviewing
  layout 14_validation, logs\validation.json

--tally only reads the gdb, prints the table and writes the log (works with Pro open). Without it,
Pro must be closed: the .aprx is backed up first. --aprx <copy> rehearses on a copy BESIDE the real
.aprx (§31.5). Run polish_layouts.py afterwards (§33).
"""
import os, sys, time, json, shutil
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import arcpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from paths import on_drive, GDB
import areas
from layoutkit import text, rect, cell_text

TALLY_ONLY = "--tally" in sys.argv
APRX = (sys.argv[sys.argv.index("--aprx") + 1] if "--aprx" in sys.argv
        else on_drive(r"Mars Project\Mars Project.aprx"))
LOG = os.path.join(HERE, "logs", "validation.json")
DENSITY = os.path.join(HERE, "logs", "crater_density.json")
LNAME = "14_validation"
CHAN, RIMS, LAVA = "Landform_ChannelCenterlines", "Landform_CraterRims", "Landform_LavaFlowMargins"
ROBBINS = "Ref_Craters_Robbins2020"
DECISIONS = ("accept", "reject", "unsure")
# colours by review state; lines for channels, outlines for depressions
COL = {"open": (0, 197, 255), "reject": (227, 73, 72), "unsure": (255, 190, 0),
       "accept": (0, 230, 118), "drawn": (255, 0, 197), "lava": (230, 76, 0), "robbins": (20, 40, 110)}

if not TALLY_ONLY:
    assert not any("ArcGISPro" in l for l in os.popen("tasklist").read().splitlines()), "close ArcGIS Pro first"


def in_window(xy, b):
    return b[0] <= xy[0] <= b[2] and b[1] <= xy[1] <= b[3]


def digitised(fc, cand_class, bounds):
    """(copied from cand_class, drawn by hand) in the window, by centroid."""
    copied = drawn = 0
    with arcpy.da.SearchCursor(os.path.join(GDB, fc), ["SHAPE@XY", "SourceID"] if fc != LAVA else ["SHAPE@XY"]) as c:
        for r in c:
            if r[0] is None or not in_window(r[0], bounds):
                continue
            sid = r[1] if len(r) > 1 else None
            if sid:
                copied += sid.split(":")[0] == cand_class
            else:
                drawn += 1
    return copied, drawn


def review(cand_class):
    t = dict.fromkeys(DECISIONS + ("open",), 0)
    with arcpy.da.SearchCursor(os.path.join(GDB, cand_class), ["Review"]) as c:
        for (v,) in c:
            t[v if v in DECISIONS else "open"] += 1
    return t


def tally():
    dens = json.load(open(DENSITY))["areas"]
    res = {"read": time.strftime("%Y-%m-%d %H:%M"), "areas": {}}
    for key, A in areas.AREAS.items():
        b = A["bounds"]
        rows = {}
        for kind, cand, dst in (("channels", A["channels"], CHAN), ("depressions", A["craters"], RIMS)):
            t = review(cand)
            copied, drawn = digitised(dst, cand, b)
            judged = t["accept"] + t["reject"]
            mapped = copied + drawn
            r = dict(t, candidates=sum(t.values()), candidate_class=cand, copied=copied, drawn=drawn,
                     precision=t["accept"] / judged if judged else None, judged=judged,
                     recall=copied / mapped if mapped else None, mapped=mapped)
            if kind == "depressions":
                m = dens[key]["detector_vs_robbins"]["1.0"]
                r["robbins_1km"] = {"recall": m["recall"], "precision": m["precision"], "robbins": m["robbins"]}
            rows[kind] = r
        _, lava = digitised(LAVA, None, b)
        rows["lava margins"] = {"drawn": lava}
        res["areas"][key] = {"name": A["name"], "rows": rows}
    return res


def show(res):
    print("read", res["read"])
    print("%-17s %-12s %6s %6s %6s %6s %6s %9s %6s %7s %9s" % ("area", "class", "cands", "accept", "reject",
          "unsure", "open", "precision", "drawn", "recall", "Robbins"))
    for key, a in res["areas"].items():
        for kind, r in a["rows"].items():
            if kind == "lava margins":
                print("%-17s %-12s %s drawn by hand" % (a["name"], kind, r["drawn"])); continue
            f = lambda v: "-" if v is None else "%.0f%%" % (100 * v)
            rb = r.get("robbins_1km")
            print("%-17s %-12s %6d %6d %6d %6d %6d %9s %6d %7s %9s" % (
                a["name"], kind, r["candidates"], r["accept"], r["reject"], r["unsure"], r["open"],
                f(r["precision"]), r["drawn"], f(r["recall"]),
                "%s / %s" % (f(rb["recall"]), f(rb["precision"])) if rb else ""))


# ----------------------------------------------------------------------------- the project

def build(res):
    from make_global60_maps import outline, add, get_map, page, add_text, legend_classes, order, CREDIT, BKDIR
    from make_candidate_maps import line_style
    from make_reference_maps import add_graticule, G2
    OUTD = os.path.join(on_drive(r"Mars Project\Global60"), "layouts")
    if "--aprx" not in sys.argv:
        os.makedirs(BKDIR, exist_ok=True)
        bk = os.path.join(BKDIR, "Mars Project %s.aprx" % time.strftime("%Y%m%d-%H%M%S"))
        shutil.copy2(APRX, bk); print("backup", bk)
    p = arcpy.mp.ArcGISProject(APRX)
    sr = arcpy.Describe(os.path.join(GDB, CHAN)).spatialReference
    maps = {}
    for key, A in areas.AREAS.items():
        name = "%s — validation" % A["name"]
        print("map:", name)
        m = get_map(p, name)
        m.spatialReference = sr
        folder = on_drive(os.path.join("Mars Project", A["folder"]))
        chan, crat = os.path.join(GDB, A["channels"]), os.path.join(GDB, A["craters"])
        names = []

        def lyr(path, nm, q, colour, w, line):
            l = add(m, path, nm)
            if q:
                l.definitionQuery = q
            (line_style if line else outline)(l, colour, w)
            names.append(l.name)
            return l
        drawn_q = "SourceID IS NULL OR SourceID = ''"
        lyr(os.path.join(GDB, CHAN), "Channels: drawn by hand (missed)", drawn_q, COL["drawn"], 2.2, True)
        lyr(os.path.join(GDB, RIMS), "Crater rims: drawn by hand (missed)", drawn_q, COL["drawn"], 2.0, False)
        lyr(os.path.join(GDB, LAVA), "Lava flow margins: drawn by hand", None, COL["lava"], 2.2, True)
        lyr(os.path.join(GDB, CHAN), "Channels: accepted", "SourceID LIKE '%s:%%'" % A["channels"], COL["accept"], 2.0, True)
        lyr(os.path.join(GDB, RIMS), "Crater rims: accepted", "SourceID LIKE '%s:%%'" % A["craters"], COL["accept"], 1.8, False)
        lyr(chan, "Channels: unsure", "Review = 'unsure'", COL["unsure"], 1.6, True)
        lyr(crat, "Depressions: unsure", "Review = 'unsure'", COL["unsure"], 1.4, False)
        lyr(chan, "Channels: rejected", "Review = 'reject'", COL["reject"], 1.2, True)
        lyr(crat, "Depressions: rejected", "Review = 'reject'", COL["reject"], 1.2, False)
        lyr(chan, "Channels: not reviewed", "Review IS NULL OR Review = ''", COL["open"], 0.6, True)
        lyr(crat, "Depressions: not reviewed", "Review IS NULL OR Review = ''", COL["open"], 0.7, False)
        rb = add(m, os.path.join(GDB, ROBBINS), "Robbins craters ≥ 1 km (reference)")
        s = rb.symbology
        s.renderer.symbol.color = {"RGB": list(COL["robbins"]) + [100]}
        s.renderer.symbol.size = 1.6
        rb.symbology = s
        names.append(rb.name)
        hs = add(m, os.path.join(folder, A["prefix"] + "_hillshade.tif"), "Hillshade 225°/45°")
        order(m, names + [hs.name])
        add_graticule(p, name, G2, 6)
        maps[key] = (m, names)

    lyt = page(p, LNAME)
    frames = {}
    y0, fh = 3.98, 2.85
    x = 0.45
    for key in ("ius", "ath"):
        A = areas.AREAS[key]
        xmin, ymin, xmax, ymax = A["bounds"]
        fw = fh * (xmax - xmin) / (ymax - ymin)
        mf = lyt.createMapFrame(arcpy.Polygon(arcpy.Array([arcpy.Point(x, y0), arcpy.Point(x, y0 + fh),
                                arcpy.Point(x + fw, y0 + fh), arcpy.Point(x + fw, y0)])), maps[key][0], "frame_" + key)
        mf.camera.setExtent(arcpy.Extent(xmin, ymin, xmax, ymax, spatial_reference=sr))
        frames[key] = (mf, x, fw)
        x += fw + 0.25
    els = [text(0.45, 7.80, "Validation — the machine candidates against review and reference", 21, "title", bold=True),
           text(0.45, 7.20, "Candidates are judged in review (accept / reject / unsure, KB §46); features the detector "
                "missed are drawn by hand. Live in Pro: every layer\nis a query on the review fields. The table is "
                "rerun with make_validation_sheet.py after each review session. Read %s." % res["read"],
                9.6, "subtitle", colour=(70, 70, 70))]
    for key, (mf, fx, fw) in frames.items():
        els.append(text(fx, y0 + fh + 0.06, areas.AREAS[key]["name"], 10.5, "label_" + key, bold=True))
    els += table(res, 0.45, 2.70)
    els.append(text(0.45, 0.55, notes(res), 7.6, "notes", colour=(40, 40, 40)))
    els.append(text(0.45, 0.28, CREDIT, 7.5, "credit", colour=(90, 90, 90)))
    add_text(lyt, els)
    order_legend = [n for n in maps["ius"][1]]
    legend_classes(p, lyt, frames["ius"][0], 0.45, 3.80, 10.1, 0.9, order_legend, names=False, cols=5)
    out = os.path.join(OUTD, LNAME + ".png"); lyt.exportToPNG(out, resolution=150); print("   ", out)
    p.save()
    print("saved. layouts:", sorted(x.name for x in p.listLayouts()))


COLS = [("candidates", "candidates"), ("accept", "accepted"), ("reject", "rejected"), ("unsure", "unsure"),
        ("open", "not\nreviewed"), ("precision", "precision\n(review)"), ("drawn", "drawn by\nhand"),
        ("recall", "recall\n(review)"), ("robbins", "Robbins ≥ 1 km\nrecall / precision")]


def table(res, x0, ytop):
    wl, wc, wr, hh, hr, fs = 2.6, 0.74, 1.30, 0.34, 0.2, 7.4
    widths = [wc] * 8 + [wr]
    xs = [x0 + wl]
    for w in widths[:-1]:
        xs.append(xs[-1] + w)
    y = ytop - hh
    els = [cell_text(x0, y, wl, hh, "type area · class", fs, "v_h", bold=True, align="Left")]
    for i, (k, lab) in enumerate(COLS):
        els.append(cell_text(xs[i], y, widths[i], hh, lab, fs, "v_h%d" % i, bold=True))
    els.append(rect(x0, y - 0.01, xs[-1] + wr - x0, 0.012, "v_rule", (120, 120, 120)))
    f = lambda v: "–" if v is None else "%.0f%%" % (100 * v)
    k = 0
    for key, a in res["areas"].items():
        for kind, r in a["rows"].items():
            y -= hr; k += 1
            if k % 2 == 0:
                els.append(rect(x0, y, xs[-1] + wr - x0, hr, "v_band%d" % k, (244, 244, 242)))
            els.append(cell_text(x0, y, wl, hr, "%s · %s" % (a["name"], kind), fs, "v_l%d" % k, align="Left"))
            if kind == "lava margins":
                vals = ["–"] * 6 + [str(r["drawn"]), "–", "–"]
            else:
                rb = r.get("robbins_1km")
                vals = [str(r["candidates"]), str(r["accept"]), str(r["reject"]), str(r["unsure"]), str(r["open"]),
                        f(r["precision"]), str(r["drawn"]), f(r["recall"]),
                        "%s / %s" % (f(rb["recall"]), f(rb["precision"])) if rb else "–"]
            for i, v in enumerate(vals):
                els.append(cell_text(xs[i], y, widths[i], hr, v, fs, "v_c%d_%d" % (k, i), colour=(30, 30, 30)))
    return els


def notes(res):
    judged = sum(r.get("judged", 0) for a in res["areas"].values() for r in a["rows"].values())
    mapped = sum(r.get("mapped", 0) + (r["drawn"] if "judged" not in r else 0)
                 for a in res["areas"].values() for r in a["rows"].values())
    state = ("No candidate has been reviewed and nothing has been drawn yet: the review columns fill in on the "
             "next run after a review session.\n" if not judged and not mapped else "")
    return (state + "Precision = accepted ÷ (accepted + rejected). Recall = accepted ÷ (accepted + drawn by hand): "
            "the share of the features mapped by hand that the detector proposed.\nRobbins: a candidate matches a "
            "catalogued crater whose centre lies within half its diameter, with a diameter within ×2 (KB §42.3). "
            "The depressions are closed depressions, not a crater count.")


def main():
    res = tally()
    show(res)
    json.dump(res, open(LOG, "w"), indent=1)
    print("wrote", LOG)
    if not TALLY_ONLY:
        build(res)


if __name__ == "__main__":
    main()
