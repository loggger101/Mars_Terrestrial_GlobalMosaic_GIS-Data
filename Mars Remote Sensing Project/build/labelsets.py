# -*- coding: utf-8 -*-
r"""Which labels a classification run trains and scores on (decision D17, KB §68; NEXT-STEPS §11.5).

  (default)      the four classes of the 512 hand-drawn labels: Landform_TrainingSamples_terrain_60_train /
                 _60_test (make_global60_classification.py's split, KB §31). Every output name as before.
  --labels v2    the seven classes after the author's review: Landform_TrainingSamples_v2_60_train / _test
                 (apply_label_review.py; the same 14 held-out blocks). Outputs carry "_v2" in their names,
                 so no four-class file is ever replaced by a seven-class one.
  --labels v2p   a rehearsal of the v2 runs before the review (KB §69.4): every proposal taken as proposed
                 (apply_label_review.py --rehearsal), Landform_TrainingSamples_v2p_60_train / _test, outputs
                 named "_v2p". Tests the pipeline and its timings; never a result, never the published map.
  --labels v3    the seven classes with the v2 polygons cut into screened pieces and a few thousand new polygons
                 from reference data (propose_v3_labels.py, KB §69.49): Landform_TrainingSamples_v3_60_train /
                 _test, the same 14 held-out blocks, outputs named "_v3". The v2 held-out set stays the
                 like-for-like score: score a v3 map with --labels v2 as well.

Class codes are fixed: 1-4 as in the hand-drawn labels, 5-7 new; a code is never renumbered (KB §68.1).
NAMES[i] is code i + 1 in either set, so a four-class map scores on v2 labels with the same indices: it simply
never predicts 5-7. The colours are the hand-drawn labels' and apply_label_review.py's.
"""
import sys

FOUR = ["Crater", "steep/windy hills", "lava tube", "Normal Ground"]
SEVEN = FOUR + ["volcanic edifice", "apron", "fluvial channel"]
COLOURS = {"Crater": (255, 0, 0), "steep/windy hills": (28, 119, 85), "lava tube": (158, 25, 147),
           "Normal Ground": (81, 51, 13), "volcanic edifice": (255, 170, 0), "apron": (115, 178, 255),
           "fluvial channel": (0, 92, 230)}

_v = sys.argv[sys.argv.index("--labels") + 1] if "--labels" in sys.argv else "four"
if _v not in ("four", "v2", "v2p", "v3"):
    raise SystemExit("--labels takes four, v2, v2p or v3, not %r" % _v)
V2 = _v in ("v2", "v2p", "v3")                  # seven classes
REHEARSAL = _v == "v2p"
NAMES = SEVEN if V2 else FOUR
TAG = "_" + _v if V2 else ""                    # inserted into every output name of a v2 (or v2p) run
TRAIN = "Landform_TrainingSamples_%s_60_train" % _v if V2 else "Landform_TrainingSamples_terrain_60_train"
TEST = "Landform_TrainingSamples_%s_60_test" % _v if V2 else "Landform_TrainingSamples_terrain_60_test"
WRITER = "propose_v3_labels.py" if _v == "v3" else "apply_label_review.py"   # the only script a split may come from
