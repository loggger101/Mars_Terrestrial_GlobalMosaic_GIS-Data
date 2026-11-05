# -*- coding: utf-8 -*-
r"""The v3 maps on R2's probability sample (KB §69.53, §69.55; NEXT-STEPS row 3b).

score_v3_maps.py compares the v2 and v3 maps on hand-drawn polygons, which sit where a class is clear and which v3's
labels were drawn around. R2's 175 points were drawn at random on 2026-11-02, before v3's labels and whatever v3 learns
from them, with the seven-class SVM's classes as strata. The stratified estimator is unbiased for any map (score_r2.py),
so the v3 maps can be read at the same points, with the same labels and the same weights, and each v3-minus-v2 difference
estimated on the same rows. This is beside score_v3_maps.py's recommendation, not part of it.

Written 2026-11-05 with the U-Net's first pass running: no v3 map exists. Only the training run's validation table has
been read (per-class F1 on chips, Normal Ground 0.21 against v2's 0.63). Nothing below is adjusted after the run.

**Predictions** (each reported held or not held; R2 has svm_v2 39.9 %, unet_v2 21.7 %, §69.55):
  P1  unet_v3's sample accuracy is above unet_v2's 21.7 %: Normal Ground is most of the sample's ground (79.8 %, §69.55)
      and trains in 178 blocks, and the v2 map's edifice takes 40.0 % of ±60°.
  P2  svm_v3's lies in 34.9-44.9 %, within 5 points of svm_v2's 39.9 %: more polygons of the same stack.
  P3  unet_v3 minus unet_v2: the 95 % interval lies above 0.
  P4  svm_v3 minus svm_v2: the 95 % interval includes 0.
  P5  unet_v3 stays below svm_v3 on the sample, as unet_v2 is below svm_v2, though it leads on the polygons.

**How much of the U-Net's deficit is the labeller's lean?** The rehearsal of this script gave a figure not in the record:
on the sample the seven-class U-Net trails the seven-class SVM by 18.3 points (-26.7 to -9.9), against its 26.5-point
lead on the polygons (§69.44). The lean to Normal Ground (above) favours the SVM, which maps 33.3 % of ±60° as Normal
Ground against the U-Net's 20.2 %, so every difference is also estimated on the rows whose reference is not Normal Ground
(a ratio estimator, as score_r2.py's four-class one), with each map's accuracy there. Written before that was computed:
  P6  unet_v2 minus svm_v2 on the rows not Normal Ground: the 95 % interval includes 0, so the deficit is the lean's.

**Limits, for whatever is reported:** the labels are the agent's, whose gate failed (agreement 0.667, κ 0.604) and was
waived at the author's word (§69.55); that labeller leans to Normal Ground, so a map that calls more ground Normal Ground
gains on this sample whether it is right or not. Any answers of the author's replace the labels: pass them as the file.

Route check, or nothing is written: the cached v2 arrays must give the map class r2_key.json recorded at every one of the
210 slots, and svm_v2 and unet_v2 the logged estimates of r2_agent_waived_result.json to 0.0001 (agent's labels only).
--rehearse stands the v2 arrays in for the v3 maps, so the route can run before they exist: every v3-minus-v2 difference
must then be exactly 0. --plant (with --rehearse) rolls unet_v2's array half a planet, and the route check must refuse.

  python score_r2_v3.py [<labels.json or answers.txt>] [--author] [--rehearse [--plant]]
Writes logs\r2\r2_v3_result.json (--rehearse: r2_v3_rehearsal.json). Reads the drive only; under a minute. System Python.
"""
import os, sys, json
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from paths import on_drive
import score_r2 as R

REHEARSE, PLANT, AUTHOR = "--rehearse" in sys.argv, "--plant" in sys.argv, "--author" in sys.argv
R2 = os.path.join(HERE, "logs", "r2")
AGENT = os.path.join(R2, "agent_labels.json")
LOGGED = os.path.join(R2, "r2_agent_waived_result.json")
OUT = os.path.join(R2, "r2_v3_rehearsal.json" if REHEARSE else "r2_v3_result.json")
G60 = r"Mars Project\Global60\%s.tif"
ARRAYS = {"svm7": ("global60_landforms_v2_200m_mode11_ov400.npy", "global60_landforms_svm_v2_200m_mode11"),
          "unet7": ("global60_landforms_global60_landforms_unet_v2_200m_seamfix_ov400.npy",
                    "global60_landforms_unet_v2_200m_seamfix"),
          "svm_v3": ("global60_landforms_v3_200m_mode11_ov400.npy", "global60_landforms_svm_v3_200m_mode11"),
          "unet_v3": ("global60_landforms_global60_landforms_unet_v3_200m_seamfix_ov400.npy",
                      "global60_landforms_unet_v3_200m_seamfix")}
STAND_IN = {"svm_v3": "svm7", "unet_v3": "unet7"}
PAIRS = (("unet_v3", "unet7"), ("svm_v3", "svm7"), ("unet_v3", "svm_v3"), ("unet7", "svm7"))


def load(name):
    npy, tif = ARRAYS[STAND_IN[name] if REHEARSE and name in STAND_IN else name]
    p = os.path.join(HERE, npy)
    if os.path.getmtime(p) < os.path.getmtime(on_drive(G60 % tif)):
        sys.exit("%s is older than %s.tif: rerun verify_global60_classification.py on it first" % (npy, tif))
    a = np.load(p, mmap_mode="r")
    return np.roll(np.asarray(a), a.shape[1] // 2, axis=1) if PLANT and name == "unet7" else a


def at(a, v):
    H, W = a.shape
    return int(a[min(v["row"], H - 1), v["col"] % W])


def not_normal(rows, Wh):
    """Accuracy and differences on the rows whose reference is not Normal Ground (class index 3)."""
    den = lambda r: float(r["ref"] != 3)
    hit = lambda m: (lambda r: float(r["v"][m] == r["ref"] and r["ref"] != 3))
    return dict(rows=sum(r["ref"] != 3 for r in rows),
                overall={m: R.strat(rows, Wh, hit(m), den=den) for m in ARRAYS},
                differences={"%s-%s" % (a, b): R.strat(rows, Wh, lambda r, a=a, b=b: hit(a)(r) - hit(b)(r), den=den)
                             for a, b in PAIRS})


def judge(res):
    o, d = res["overall"], res["differences"]
    has0 = lambda x: x["lo"] <= 0 <= x["hi"]
    v = {"P1": o["unet_v3"]["est"] > 0.2166,
         "P2": 0.349 <= o["svm_v3"]["est"] <= 0.449,
         "P3": d["unet_v3-unet7"]["lo"] > 0,
         "P4": has0(d["svm_v3-svm7"]),
         "P5": o["unet_v3"]["est"] < o["svm_v3"]["est"],
         "P6": has0(res["not_normal_ground"]["differences"]["unet7-svm7"])}
    return {p: "held" if x else "NOT held" for p, x in v.items()}


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    path = args[0] if args else AGENT
    key = json.load(open(R.KEY, encoding="utf-8"))
    K, Wh, classes = key["slots"], key["Wh"], key["classes"]
    lab = R.read_labels(path)
    A = {m: load(m) for m in ARRAYS}
    wrong = sum(at(A[m], v) != v["maps"][m] for m in ("svm7", "unet7") for v in K.values())
    print("route: %d slots, %d map classes differ from r2_key.json" % (len(K), wrong))
    if wrong:
        sys.exit(2)

    rows = [dict(K[s], ref=R.LETTERS.index(lab[s]), slot=s) for s in K if K[s]["kind"] == "r2" and lab.get(s, "u") != "u"]
    for r in rows:
        r["v"] = {m: at(A[m], r) for m in A}
    print("%d rows decided, %d unsure" % (len(rows), sum(1 for s in K if K[s]["kind"] == "r2") - len(rows)))
    if path == AGENT:
        logged = json.load(open(LOGGED, encoding="utf-8"))["overall"]
        for m in ("svm7", "unet7"):
            e = R.strat(rows, Wh, lambda r, m=m: float(r["v"][m] == r["ref"]))
            ok = abs(e["est"] - logged[m]["est"]) <= 1e-4 and abs(e["lo"] - logged[m]["lo"]) <= 1e-4
            print("route: %s %s, its log %s -> %s" % (m, e, logged[m], "ok" if ok else "MISMATCH"))
            if not ok:
                sys.exit(2)
    nodata = {m: sum(r["v"][m] >= len(classes) for r in rows) for m in A}
    used = [r for r in rows if all(r["v"][m] < len(classes) for m in A)]    # the v3 maps may lack a pixel the v2 maps have
    hit = lambda m: (lambda r: float(r["v"][m] == r["ref"]))
    res = dict(script="score_r2_v3.py", labels=os.path.basename(path), rehearsal=REHEARSE,
               labeller="author" if AUTHOR else "agent, gate waived by the author (KB 69.55)", rows=len(used),
               rows_without_a_map_class=nodata, overall={m: R.strat(used, Wh, hit(m)) for m in A},
               differences={"%s-%s" % (a, b): R.strat(used, Wh, lambda r, a=a, b=b: hit(a)(r) - hit(b)(r)) for a, b in PAIRS},
               users={m: {n: R.strat(used, Wh, lambda r, m=m, k=k: float(r["v"][m] == k and r["ref"] == k),
                                     den=lambda r, m=m, k=k: float(r["v"][m] == k)) for k, n in enumerate(classes)
                          if any(r["v"][m] == k for r in used)} for m in A})
    if REHEARSE:      # stand-ins: the same maps, so every v3-minus-v2 difference is exactly nothing
        for p in ("unet_v3-unet7", "svm_v3-svm7"):
            assert res["differences"][p] == dict(est=0.0, lo=0.0, hi=0.0), (p, res["differences"][p])
        print("rehearsal: every v3-minus-v2 difference is 0, as stand-ins must be; verdicts below mean nothing")
    res["not_normal_ground"] = not_normal(used, Wh)
    res["predictions"] = judge(res)
    for m, e in res["overall"].items():
        print("%-8s %s" % (m, e))
    for p, e in res["differences"].items():
        print("%-16s %s" % (p, e))
    print("rows not Normal Ground (%d):" % res["not_normal_ground"]["rows"])
    for p, e in list(res["not_normal_ground"]["overall"].items()) + list(res["not_normal_ground"]["differences"].items()):
        print("  %-16s %s" % (p, e))
    print("predictions:", res["predictions"])
    json.dump(res, open(OUT, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
