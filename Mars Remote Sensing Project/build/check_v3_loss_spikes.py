# -*- coding: utf-8 -*-
r"""The validation loss of every U-Net trained, and the verdicts of S1 (KB §69.88) and R3 (make_v3_extras.py) on it.

Every v3 training on the third label set's added polygons (base, fresh, noth) had its validation loss rise far late in
training while its training loss and validation-chip accuracy held; cut, without them, and every earlier U-Net did not
(§69.88, §69.90). The ArcGIS training tool writes one row per epoch (epoch, train loss, valid loss, accuracy, dice) to
training_messages.txt beside each model in DLModels; this reads them all.

  S1 (registered 2026-11-09 07:45, before add_train): add's validation loss rises above 5 at some epoch after the 15th ->
     "held"; stays below 2 throughout -> "not held"; otherwise "not decided".
  R3 (registered 2026-11-09 09:00, before rep_export): rep's validation loss rises above 5 at some epoch after the 15th.

Reads only; writes logs\v3_loss_spikes.json.   py -3 check_v3_loss_spikes.py   (standard library only)
"""
import os, re, json, glob, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from paths import on_drive
MODELS = on_drive(r"Mars Project\DLModels")
ROW = re.compile(r"^(\d+)\s+([0-9.]+(?:e[-+]?\d+)?)\s+([0-9.]+(?:e[-+]?\d+)?)\s+([0-9.]+(?:e[-+]?\d+)?)")
RUNS = {"add": "global60_unet_x5c_v3a_*", "rep": "global60_unet_x5c_v3r_*"}


def epochs(path):
    seen = {}
    for line in open(path, encoding="utf-8", errors="replace"):
        m = ROW.match(line.strip())
        if m:
            seen[int(m.group(1))] = (float(m.group(2)), float(m.group(3)), float(m.group(4)))
    return [(e,) + seen[e] for e in sorted(seen)]


def rule(rows):
    late = [v for e, _, v, _ in rows if e > 15]
    if any(v > 5 for v in late):
        return "held"
    if all(v < 2 for _, _, v, _ in rows):
        return "NOT held"
    return "not decided"


def main():
    res = dict(script="check_v3_loss_spikes.py", models={})
    for d in sorted(glob.glob(os.path.join(MODELS, "global60_unet_*"))):
        f = os.path.join(d, "training_messages.txt")
        if not os.path.exists(f):
            continue
        rows = epochs(f)
        if not rows:
            continue
        v = [r[2] for r in rows]
        best = min(rows, key=lambda r: r[2])
        over = [r[0] for r in rows if r[2] > 2]
        res["models"][os.path.basename(d)] = dict(
            epochs=len(rows), best_epoch=best[0], best_valid_loss=round(best[2], 4), best_accuracy=round(best[3], 4),
            max_valid_loss=round(max(v), 3), first_epoch_above_2=over[0] if over else None,
            train_loss_last5=[round(r[1], 3) for r in rows[-5:]], accuracy_last5=[round(r[3], 3) for r in rows[-5:]])
        m = res["models"][os.path.basename(d)]
        print("%-36s best %2d %.3f  max %9.2f  first>2 %s" % (os.path.basename(d), m["best_epoch"], m["best_valid_loss"],
                                                             m["max_valid_loss"], m["first_epoch_above_2"]))
    for p, (run, pat) in (("S1", ("add", RUNS["add"])), ("R3", ("rep", RUNS["rep"]))):
        hit = sorted(glob.glob(os.path.join(MODELS, pat, "training_messages.txt")))
        rows = epochs(hit[-1]) if hit else []
        res[p] = rule(rows) if len(rows) >= 30 else "waiting for %s (%d epochs)" % (run, len(rows))
        print(p, res[p])
    out = os.path.join(HERE, "logs", "v3_loss_spikes.json")
    json.dump(res, open(out, "w", encoding="utf-8"), indent=1)
    print("->", out)


if __name__ == "__main__":
    main()
