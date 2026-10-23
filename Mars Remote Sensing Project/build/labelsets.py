# -*- coding: utf-8 -*-
r"""Which labels a classification run trains and scores on (decision D17, KB §68; NEXT-STEPS §11.5).

  (default)      the four classes of the 512 hand-drawn labels: Landform_TrainingSamples_terrain_60_train /
                 _60_test (make_global60_classification.py's split, KB §31). Every output name as before.
  --labels v2    the seven classes after the author's review: Landform_TrainingSamples_v2_60_train / _test
                 (apply_label_review.py; the same 14 held-out blocks). Outputs carry "_v2" in their names,
                 so no four-class file is ever replaced by a seven-class one.

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
if _v not in ("four", "v2"):
    raise SystemExit("--labels takes four or v2, not %r" % _v)
V2 = _v == "v2"
NAMES = SEVEN if V2 else FOUR
TAG = "_v2" if V2 else ""                       # inserted into every output name of a v2 run
TRAIN = "Landform_TrainingSamples_v2_60_train" if V2 else "Landform_TrainingSamples_terrain_60_train"
TEST = "Landform_TrainingSamples_v2_60_test" if V2 else "Landform_TrainingSamples_terrain_60_test"
