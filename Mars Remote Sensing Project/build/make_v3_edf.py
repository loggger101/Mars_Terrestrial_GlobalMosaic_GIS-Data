# -*- coding: utf-8 -*-
r"""The lead U-Net trained again for its volcanic edifice (D37, the author 2026-11-11: "Yes, retrain before the freeze";
KB §69.107, NEXT-STEPS §14 row 4). Nothing here replaces a map: the run classifies windows only, like make_v3_extras.py's.

The fault. The published v3 U-Net maps volcanic edifice on 18.0 % of ±60° (§69.81), where the geologic map's edifice
units cover 1.1 %; a second training with the same labels maps 8.7 % of the windows against 16.3 % (§69.106).
Measured 2026-11-11 before this script was written (a description, on 3.2 km cells, training blocks only): 2,257,999
of 13,005,490 cells off the edifice, apron and landslide units are mostly edifice on the published map; 55 % of them
lie on the highland group, 26 % on volcanic plains; 96 % have relief <= 150 m, 63.6 % pass v3's piece test for Normal
Ground (slope <= 2°, crater cover <= 0.3) and 22.3 % the stricter test of v3's new Normal Ground squares; 0.7 % pass
its hills test. The extra edifice is flat, uncratered plains, which v3's own rule calls Normal Ground.

The run, `edf` (tag v3e), differs from the existing run `fresh` (v3f, §69.84) in one thing:
  validation blocks  fresh's 14 blocks (seed 60), never used for a choice, stay out of training, as in fresh. edf
                     trains on fresh's training polygons (9,366), so fresh is its control on those blocks, and they are
                     where the change is judged first. The model's own stopping rule is unchanged (10 % of chips).
  negatives          new Normal Ground squares, by v3's rule for a new Normal Ground square unchanged (4 x 4 cells of
                     3.2 km, every cell median slope <= 1°, p90 <= 3°, relief <= 150 m, no crater >= 4 km within 1.3 R,
                     off the edifice, apron and landslide units), with one more condition: every cell is at least half
                     volcanic edifice on the published v3 U-Net map. Up to 8 a block (v3 placed 5), seed 107, one cell
                     clear of every v3 proposal, v2 polygon and each other; none in the 14 held-out blocks or in
                     fresh's 14. Placed by rule; no one looks at them.
  class weights      unchanged: every v3 run already weights the loss by inverse class frequency (class_balancing).
                     The question put to the author named class weights as new; they are not.
Everything else is make_dl_pixels.py's training as in every v3 run (seven bands, the same chips and settings).

Maps compared (make_v3_extras.py's window classification, one pass):
  on the standard windows (the 14 held-out blocks)   base, rep, freshw (fresh's model there, a third training without
                                                    negatives, on 9,366 polygons) and edf
  on fresh's windows (the validation blocks)         fresh and edfv (edf's model there)

Written 2026-11-11 before the negatives were drawn and before any export. Nothing below is adjusted after the run.

**Predictions** (each reported held or not held):
  E1  validation: edf's accuracy on fresh's 899 polygons is within 3 points of fresh's (86.6 %; R1's bound for one
      training against another, which rep met by 0.74 and 0.87).
  E2  validation: on fresh's windows edf maps volcanic edifice on less of the ground off the SIM 3292 edifice units
      than fresh does (area-weighted, the pixels both maps hold).
  E3  test: edf's accuracy is within 3 points of base's on each polygon set (237 v2, 1,652 v3).
  E4  test: edf's edifice share of the windows' ground off the edifice units is below the lowest of the three
      trainings without negatives (base, rep, freshw).
  E5  test: edf's producer's accuracy of volcanic edifice on the 1,652 v3 polygons is not more than 10 points below
      the lower of base's and rep's (rep's is 9.9 below base's, §69.106).
  Described, no prediction: the class areas of each map, the edifice share on the highland group and on the volcanic
  plains, the six off-Tharsis edifice polygons at Syrtis Major (base 7.7 %, §69.105), every producer's accuracy.
**Reading rule.** E1-E5 all held: the negatives shrink the extra edifice by more than one training differs from
another, at no cost in score, and the rule recommends edf's labels for the lead U-Net; the author picks, and only then
is ±60° classified. E1 or E3 not held: the negatives cost accuracy; not recommended. E4 not held: the change is not
larger than one training against another; reported as a test. E5 not held: the edifice itself is lost; not recommended.

  "<ArcGIS Pro Python>" make_v3_edf.py --negatives          writes the squares and edf's training class into extras.gdb
  "<ArcGIS Pro Python>" make_v3_extras.py --run edf --step export | train | classify     (run_v3_edf.ps1)
  "<ArcGIS Pro Python>" make_v3_extras.py --run edfv --step classify ; --run freshw --step classify
  "<ArcGIS Pro Python>" make_v3_edf.py --report
Writes logs\v3_edf_plan.json and logs\v3_edf.json.
"""
import os, sys, json, time, collections
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np
import arcpy
import make_v3_extras as X
import make_block_bootstrap as B
from labelsets import SEVEN
from paths import GDB

PLAN = os.path.join(HERE, "logs", "v3_edf_plan.json")
OUT = os.path.join(HERE, "logs", "v3_edf.json")
NEG = X.fc("edf", "train")[:-len("train")] + "neg"
SEED, CAP, EDIFICE_MIN = 107, 8, 0.5
ED = SEVEN.index("volcanic edifice")
OFFT = "Landform_TrainingSamples_offtharsis_draw"
FIELDS = ["SHAPE@", "Classcode", "Classname", "Classvalue", "RED", "GREEN", "BLUE", "Subtype", "ProposalOID", "OldOID",
          "MappedBy", "Split", "Block"]


def cell_share(a, P, value):
    """Per 3.2 km cell (8 x 8 pixels of the 400 m lattice): the share of pixels equal to value, and the valid share."""
    k = 8
    sh = np.zeros((P.NR, P.NC), np.float32)
    va = np.zeros((P.NR, P.NC), np.float32)
    for r0 in range(0, P.NR, 256):
        r1 = min(P.NR, r0 + 256)
        blk = np.asarray(a[r0 * k:r1 * k, :P.NC * k]).reshape(r1 - r0, k, P.NC, k)
        sh[r0:r1] = (blk == value).mean(axis=(1, 3))
        va[r0:r1] = (blk != 255).mean(axis=(1, 3))
    return sh, va


def negatives():
    import propose_v3_labels as P
    t0 = time.time()
    plan = json.load(open(X.PLAN, encoding="utf-8"))
    sr = arcpy.Describe(X.V3_TRAIN).spatialReference
    held = sorted({b for (b,) in arcpy.da.SearchCursor(X.V3_TEST, ["Block"])} | {b for (b,) in arcpy.da.SearchCursor(X.V2_TEST, ["Block"])})
    val = plan["fresh"]["blocks"]
    assert len(held) == 14 and len(val) == 14 and not set(held) & set(val), (held, val)
    ctx = P.Ctx()
    ctx.T = P.terrain_cells()
    rob = P.read_robbins()
    m10, m13 = P.crater_masks(rob)
    ctx.rim4, ctx.cov4, ctx.cov10 = P.cover(m10, 4), P.cover(m13, 4), P.cover(m13, 10)
    ctx.kind = P.unit_cells(sr)
    T, kind = ctx.T, ctx.kind
    a = np.load(os.path.join(HERE, X.ARR % "v3"), mmap_mode="r")
    ed, valid = cell_share(a, P, ED)
    print("cells, masks, map shares (%.0f s)" % (time.time() - t0), flush=True)
    ctx.occ = P.Occupancy()
    n = 0
    for f in (X.V3_PROP, X.V2_TRAIN, X.V2_TEST, X.V3_TRAIN, X.V3_TEST):
        for (g,) in arcpy.da.SearchCursor(f, ["SHAPE@"]):
            ctx.occ.mark(*P.cells_of(P.plain(g), all_touched=True))
            n += 1
    print("occupied by %d existing polygons: %d cells (%.0f s)" % (n, int(ctx.occ.a.sum()), time.time() - t0), flush=True)
    off = np.isin(kind, (P.KIND["ve"], P.KIND["slide"]) + P.APRON_KINDS) | (kind == 0)
    ng = (T["smed"] <= P.NG_SMED) & (T["sp90"] <= P.NG_SP90) & (T["z95"] - T["z05"] <= P.NG_RELIEF) & (ctx.cov4 == 0) & ~off
    ok = ng & (ed >= EDIFICE_MIN) & (valid >= 1.0)
    print("cells passing v3's Normal Ground test %d, and mostly edifice on the published map %d" % (int(ng.sum()), int(ok.sum())), flush=True)
    rng = np.random.default_rng(SEED)
    rows = P.new_squares(ctx, 4, ok, P.NG_K, P.NG_K * P.NG_K, CAP, sr, rng,
                         "edf negative: v3's new Normal Ground square where the published v3 U-Net maps edifice")
    kept = [r for r in rows if r["block"] not in held and r["block"] not in val]
    by_block = collections.Counter(r["block"] for r in kept)
    print("squares placed %d, kept outside the 28 held-out and validation blocks %d, in %d blocks" % (len(rows), len(kept), len(by_block)), flush=True)
    assert kept, "no negative placed"
    for f in (NEG, X.fc("edf", "train")):
        if arcpy.Exists(f):
            arcpy.management.Delete(f)
    src = X.fc("fresh", "train")
    arcpy.management.CreateFeatureclass(os.path.dirname(NEG), os.path.basename(NEG), "POLYGON", src, spatial_reference=sr)
    with arcpy.da.SearchCursor(src, FIELDS[1:7], "Classvalue = 4") as c:
        code, name, value, red, green, blue = next(c)
    with arcpy.da.InsertCursor(NEG, FIELDS) as c:
        for r in kept:
            c.insertRow([r["geom"], code, name, value, red, green, blue, "edf negative", None, None, "make_v3_edf.py", "train", r["block"]])
    lyr = arcpy.management.MakeFeatureLayer(NEG, "neg_touch")
    arcpy.management.SelectLayerByLocation(lyr, "INTERSECT", src)
    touching = int(arcpy.management.GetCount(lyr)[0]) if arcpy.Describe(lyr).FIDSet else 0
    for f in (X.V3_TEST, X.V2_TEST, X.fc("fresh", "test")):
        arcpy.management.SelectLayerByLocation(lyr, "INTERSECT", f)
        touching += int(arcpy.management.GetCount(lyr)[0]) if arcpy.Describe(lyr).FIDSet else 0
    assert touching == 0, "%d negatives touch an existing polygon" % touching
    arcpy.management.Merge([src, NEG], X.fc("edf", "train"))
    n_train = int(arcpy.management.GetCount(X.fc("edf", "train"))[0])
    cls = collections.Counter(v for (v,) in arcpy.da.SearchCursor(X.fc("edf", "train"), ["Classvalue"]))
    m = [r["m"] for r in kept]
    res = dict(script="make_v3_edf.py", when=time.strftime("%Y-%m-%d %H:%M"), seed=SEED, cap_per_block=CAP,
               edifice_min=EDIFICE_MIN, held_out_blocks=held, validation_blocks=val,
               cells_normal_ground=int(ng.sum()), cells_eligible=int(ok.sum()), squares_placed=len(rows),
               negatives=len(kept), blocks_with_negatives=len(by_block), by_block=dict(sorted(by_block.items())),
               on_highland=round(float(np.mean([x["highland"] >= 0.5 for x in m])), 4),
               on_volcanic_plains=round(float(np.mean([x["volc"] >= 0.5 for x in m])), 4),
               fresh_training=int(arcpy.management.GetCount(src)[0]), edf_training=n_train,
               edf_training_by_class={SEVEN[k - 1]: cls[k] for k in range(1, 8)})
    json.dump(res, open(PLAN, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(json.dumps({k: v for k, v in res.items() if k != "by_block"}, ensure_ascii=False), flush=True)
    print("->", PLAN, "(%.0f s)" % (time.time() - t0))


def kinds400(shape):
    """SIM 3292 unit kinds (propose_v3_labels' 3.2 km cells) on the 400 m lattice; 0 where the cells do not reach."""
    import propose_v3_labels as P
    kind = P.unit_cells(arcpy.Describe(X.V3_TRAIN).spatialReference)
    out = np.zeros(shape, np.uint8)
    big = np.repeat(np.repeat(kind.astype(np.uint8), 8, axis=0), 8, axis=1)
    h, w = min(shape[0], big.shape[0]), min(shape[1], big.shape[1])
    out[:h, :w] = big[:h, :w]
    return out, P.KIND


def areas(maps, kind, KIND, g):
    """Class shares of the ground every map of the set holds, area-weighted by latitude; edifice by unit kind."""
    both = np.all([a != 255 for a in maps.values()], axis=0)
    H = both.shape[0]
    lat = g["lat_top"] - (np.arange(H) + 0.5) * g["dpy"]
    w = np.cos(np.radians(lat))
    rows_w = lambda m: float((m.sum(1) * w).sum())
    tot = rows_w(both)
    groups = {"off_edifice_units": both & (kind != KIND["ve"]) & (kind != 0), "highland": both & (kind == KIND["highland"]),
              "volcanic_plains": both & (kind == KIND["volc"]), "edifice_units": both & (kind == KIND["ve"])}
    gt = {k: rows_w(m) for k, m in groups.items()}
    out = dict(common_ground_share_of_lattice=round(float(both.mean()), 5), group_share_of_ground={k: round(v / tot, 4) for k, v in gt.items()})
    for name, a in maps.items():
        out[name] = dict(classes={SEVEN[k]: round(rows_w(both & (a == k)) / tot, 4) for k in range(len(SEVEN))},
                         edifice={k: round(rows_w(m & (a == ED)) / gt[k], 4) if gt[k] else None for k, m in groups.items()})
    return out


def report():
    X.route()
    a3 = np.load(os.path.join(HERE, X.ARR % "v3"), mmap_mode="r")
    shape, g = a3.shape, B.grid(a3.shape)
    win = lambda run: X.window_array(os.path.join(X.WORK, "classified", run), shape)
    pack = lambda a: (a, a != 255, g)
    kind, KIND = kinds400(shape)
    res = dict(script="make_v3_edf.py", when=time.strftime("%Y-%m-%d %H:%M"), boot=B.NBOOT, seed=B.SEED,
               plan=json.load(open(PLAN, encoding="utf-8")))
    again = "--rerun" in sys.argv                  # edf2: the same labels trained at fresh's learning rate (KB §69.125);
    E, EV = ("edf2", "edf2v") if again else ("edf", "edfv")   # its maps stand under the keys edf and edfv, in v3_edf2.json
    if again:
        res["rerun"] = "edf2: edf's labels and chips, learning rate fixed at the control's (fresh's); decided after edf was scored"
    std = {r: win(E if r == "edf" else r) for r in ("base", "rep", "freshw", "edf")}
    maps = {r: pack(a) for r, a in std.items()}
    pairs = [("edf", "base"), ("edf", "rep"), ("edf", "freshw"), ("base", "rep")]
    for name, f in (("v2_polygons", X.V2_TEST), ("v3_polygons", X.V3_TEST)):
        res[name], _, _ = X.score(maps, B.polys(f), pairs)
        print(name, json.dumps(res[name]["full"], ensure_ascii=False)[:1200], flush=True)
    res["standard_windows"] = areas(std, kind, KIND, g)
    print("standard windows", json.dumps(res["standard_windows"], ensure_ascii=False)[:1500], flush=True)
    val = {"fresh": win("fresh"), "edfv": win(EV)}
    res["validation_polygons"], _, _ = X.score({r: pack(a) for r, a in val.items()}, B.polys(X.fc("fresh", "test")), [("edfv", "fresh")])
    print("validation", json.dumps(res["validation_polygons"]["full"], ensure_ascii=False)[:900], flush=True)
    res["validation_windows"] = areas(val, kind, KIND, g)
    print("validation windows", json.dumps(res["validation_windows"], ensure_ascii=False)[:900], flush=True)
    # the six off-Tharsis edifice polygons (§69.105): the area-weighted share each map calls each class
    with arcpy.da.SearchCursor(os.path.join(GDB, OFFT), ["SHAPE@", "Classvalue"], spatial_reference=B.MARS) as cur:   # no Block field
        P6 = [(int(v), [[(p.X, p.Y) for p in part if p is not None] for part in s], "4_0") for s, v in cur]
    res["syrtis_edifice"] = {}
    for r, (a, m, gg) in maps.items():
        c = B.rows(a, m, gg, P6, len(SEVEN)).sum(0)
        res["syrtis_edifice"][r] = {SEVEN[k]: round(float(c[ED, k] / c[ED].sum()), 4) for k in range(len(SEVEN))} if c[ED].sum() else None
    print("syrtis", res["syrtis_edifice"], flush=True)
    res["predictions"] = judge(res)
    print(res["predictions"])
    out = OUT.replace("v3_edf.json", "v3_edf2.json") if again else OUT
    json.dump(res, open(out, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print("->", out)


def judge(res):
    v2, v3, vp = res["v2_polygons"]["full"], res["v3_polygons"]["full"], res["validation_polygons"]["full"]
    sw, vw = res["standard_windows"], res["validation_windows"]
    off = lambda w, r: w[r]["edifice"]["off_edifice_units"]
    pe = lambda f, r: f[r]["producers"]["volcanic edifice"]
    v = dict(E1=abs(vp["edfv"]["accuracy"] - vp["fresh"]["accuracy"]) <= 0.03,
             E2=off(vw, "edfv") < off(vw, "fresh"),
             E3=all(abs(f["edf"]["accuracy"] - f["base"]["accuracy"]) <= 0.03 for f in (v2, v3)),
             E4=off(sw, "edf") < min(off(sw, r) for r in ("base", "rep", "freshw")),
             E5=pe(v3, "edf") >= min(pe(v3, "base"), pe(v3, "rep")) - 0.10)
    out = {p: "held" if x else "NOT held" for p, x in v.items()}
    out["rule"] = "recommends edf's labels" if all(v.values()) else "does not recommend edf's labels"
    return out


if __name__ == "__main__":
    if "--negatives" in sys.argv:
        negatives()
    elif "--report" in sys.argv:
        report()
    else:
        sys.exit(__doc__)
