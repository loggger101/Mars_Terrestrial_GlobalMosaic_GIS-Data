r"""The two fresh draws together, and each at one class mix (KB §69.84, §69.96). Reads only; writes logs\fresh_pooled.json.

fresh2 (seed 61) repeated the U-Net's accuracy, 85.4 % against fresh's 86.6 %, but not its lead over the nearest training
polygon: that baseline scored 80.6 % there against 65.5 %, and 698 of fresh2's 1,603 held-out polygons are apron (43.5 %,
against 29.7 % on fresh), a class the baseline gets 92.7 % right; U-Net minus nearest polygon, accuracy, was -2.5 to +26.7
(F6.5 not held), by balanced accuracy +3.8 to +16.7. Two readings are left: the lead depends on the draw's class mix, or
on the draw's ground. This check separates them, with nothing retrained:

  pooled    both draws' 28 blocks, each scored by the model that held it out (block -1_-3 is in both, scored by each
            draw's own models, so it counts twice); the bootstrap resamples 14 blocks within each draw, every map on the
            same draw, 10,000 times, seed 60 as make_block_bootstrap.py.
  mix       each draw's confusion rows rescaled to one class mix, the pixels of the 1,652 held-out polygons of the third
            label set under the published U-Net v3 (the set every v3 score in the paper is on), so accuracy is the
            mix-weighted mean of producer's accuracies; a class a resample lacks drops out and the weights are renormalised.

Gate: each draw's per-block confusions, summed, must give the accuracy and kappa of logs\v3_extras.json for every map within
0.0005, or this stops (exit 2) before scoring anything.

Predictions, written 2026-11-10 19:05 after §69.96 was read and before this ran:
  P1  Pooled, U-Net minus nearest polygon, accuracy: the interval lies above 0.
  P2  Pooled, SVM minus nearest polygon, accuracy: the interval includes 0 (as F4 and F6.4).
  P3  At the 1,652 polygons' class mix, U-Net minus nearest polygon on fresh2 alone, accuracy: the interval lies above 0.
  P4  At that mix the nearest polygon's accuracy on fresh2 is at least 5 points below its 80.6 %.
  Reading: P3 and P4 held -> F6.5's miss is the draw's class mix (apron), not the U-Net's ground; P3 not held -> on
  fresh2's ground the baseline keeps up with the U-Net whatever the mix.

  "<ArcGIS Pro Python>" check_fresh_pooled.py
"""
import os, sys, json, time
import numpy as np
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import make_v3_extras as X          # sets --labels v3 before labelsets is read
B = X.B
KEYS = ["unet", "svm", "near"]
PAIRS = X.PAIRS_F


def per_block(run, shape, g):
    pack = lambda a: (a, a != 255, g)
    win = lambda r, mode=False: X.window_array(os.path.join(X.WORK, "classified", r), shape, mode)
    maps = {"unet": pack(win(run)), "svm": pack(win(run + "_svm", True)),
            "near": B.load("near", None, None, X.fc(run, "train"))}
    P = B.polys(X.fc(run, "test"))
    R = {k: B.rows(a, m, gg, P, len(X.SEVEN)) for k, (a, m, gg) in maps.items()}
    hit = np.all([r.sum((1, 2)) > 0 for r in R.values()], axis=0)
    P = [p for p, h in zip(P, hit) if h]
    blocks = sorted({p[2] for p in P})
    bi = np.array([blocks.index(p[2]) for p in P])
    return blocks, {k: np.array([R[k][hit][bi == j].sum(0) for j in range(len(blocks))]) for k in R}, len(P)


def mixacc(c, w):
    rs = c.sum(1)
    ok = rs > 0
    pa = np.where(ok, np.diag(c) / np.where(ok, rs, 1), 0)
    return float((w[ok] * pa[ok]).sum() / w[ok].sum())


def boot(draws, nboot, seed, w=None):
    """draws: list of {key: per-block confusions}; resample blocks within each draw, sum over draws."""
    rng = np.random.default_rng(seed)
    S = {k: np.empty((nboot, 2)) for k in KEYS}
    for b in range(nboot):
        ws = [np.bincount(rng.integers(0, len(d["unet"]), len(d["unet"])), minlength=len(d["unet"])).astype(float)
              for d in draws]
        for k in KEYS:
            c = sum(np.tensordot(wi, d[k], 1) for wi, d in zip(ws, draws))
            oa, _, ba = B.scores(c)
            S[k][b] = (mixacc(c, w) if w is not None else oa, ba)
    out = {k: dict(accuracy_ci95=B.ci(S[k][:, 0]), balanced_ci95=B.ci(S[k][:, 1])) for k in KEYS}
    for a, b2 in PAIRS:
        d = S[a] - S[b2]
        out["%s-%s" % (a, b2)] = dict(accuracy_ci95=B.ci(d[:, 0]), balanced_ci95=B.ci(d[:, 1]),
                                      share_above_0_accuracy=round(float((d[:, 0] > 0).mean()), 4))
    return out


def full(draws, w=None):
    out = {}
    for k in KEYS:
        c = sum(d[k].sum(0) for d in draws)
        oa, kp, ba = B.scores(c)
        out[k] = dict(accuracy=round(mixacc(c, w) if w is not None else oa, 4), kappa=round(kp, 4), balanced=round(ba, 4))
    return out


def main():
    t0 = time.time()
    ref = json.load(open(os.path.join(HERE, "logs", "v3_extras.json"), encoding="utf-8"))
    a3, m3, g = X.published(X.ARR % "v3")
    shape = a3.shape
    mix = B.rows(a3, m3, g, B.polys(X.V3_TEST), len(X.SEVEN)).sum((0, 2)).astype(float)
    w = mix / mix.sum()
    del a3, m3
    print("mix of the 1,652:", dict(zip(X.SEVEN, np.round(w, 4))), "(%.0f s)" % (time.time() - t0), flush=True)
    D, res = {}, dict(script="check_fresh_pooled.py", when=time.strftime("%Y-%m-%d %H:%M"), boot=B.NBOOT, seed=B.SEED,
                      mix=dict(zip(X.SEVEN, [round(float(x), 4) for x in w])))
    for run in ("fresh", "fresh2"):
        blocks, RB, n = per_block(run, shape, g)
        for k in KEYS:
            oa, kp, _ = B.scores(RB[k].sum(0))
            r = ref[run]["full"][k]
            ok = abs(oa - r["accuracy"]) <= 0.0005 and abs(kp - r["kappa"]) <= 0.0005
            print("%s %-4s %.4f %.4f, v3_extras.json %s %s -> %s" % (run, k, oa, kp, r["accuracy"], r["kappa"],
                                                                    "ok" if ok else "MISMATCH"), flush=True)
            if not ok or n != ref[run]["polygons"]:
                sys.exit(2)
        D[run] = RB
        res[run] = dict(blocks=blocks, polygons=n, at_mix=full([RB], w), at_mix_bootstrap=boot([RB], B.NBOOT, B.SEED, w),
                        class_pixels=dict(zip(X.SEVEN, [int(x) for x in RB["unet"].sum((0, 2))])),
                        confusions={k: RB[k].astype(int).tolist() for k in KEYS})
        print(run, "at the mix:", res[run]["at_mix"], "(%.0f s)" % (time.time() - t0), flush=True)
    both = [D["fresh"], D["fresh2"]]
    res["pooled"] = dict(full=full(both), block_bootstrap=boot(both, B.NBOOT, B.SEED),
                         at_mix=full(both, w), at_mix_bootstrap=boot(both, B.NBOOT, B.SEED, w))
    print("pooled:", res["pooled"]["full"], res["pooled"]["block_bootstrap"]["unet-near"], flush=True)
    above = lambda c: c[0] > 0
    pb, f2 = res["pooled"]["block_bootstrap"], res["fresh2"]
    v = dict(P1=above(pb["unet-near"]["accuracy_ci95"]),
             P2=pb["svm-near"]["accuracy_ci95"][0] <= 0 <= pb["svm-near"]["accuracy_ci95"][1],
             P3=above(f2["at_mix_bootstrap"]["unet-near"]["accuracy_ci95"]),
             P4=f2["at_mix"]["near"]["accuracy"] <= ref["fresh2"]["full"]["near"]["accuracy"] - 0.05)
    res["predictions"] = {k: "held" if x else "NOT held" for k, x in v.items()}
    res["seconds"] = round(time.time() - t0)
    print(res["predictions"])
    p = os.path.join(HERE, "logs", "fresh_pooled.json")
    json.dump(res, open(p, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print("->", p)


if __name__ == "__main__":
    main()
