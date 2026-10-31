# -*- coding: utf-8 -*-
"""Hand-worked confusion matrices through build/score_metrics.py's metrics() (NEXT-STEPS §13.1 P9).

    python tools/test_score_metrics.py

The paper's Table 3 columns (balanced accuracy, macro F1, quantity and allocation disagreement) rest on
metrics(); the agreement check in check_repo.py only shows it is stable, not that it is right. Each case
below was worked by hand before it was written down; the arithmetic is in its comment. Rows are the
labels, columns the map, as in the scorer's logs. Run by check_repo.py in CI. Stdlib only.
"""
import sys, unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "Mars Remote Sensing Project" / "build"))
from score_metrics import metrics  # noqa: E402


def log(cm, names, accuracy, kappa, key="confusion_area_weighted"):
    """A scorer output holding one held-out confusion matrix and the accuracy and kappa it claims."""
    return {"held_out": {key: cm, "producers": {n: None for n in names}, "accuracy": accuracy,
                         "kappa": kappa, "polygons": 0}}


class HandWorked(unittest.TestCase):
    def check(self, got, **want):
        for k, v in want.items():
            self.assertAlmostEqual(got[k], v, places=4, msg=k)

    def test_perfect(self):
        # every pixel right: all scores 1, no disagreement of either kind
        m = metrics(log([[50, 0], [0, 50]], "ab", 1.0, 1.0))
        self.check(m, accuracy=1, kappa=1, balanced_accuracy=1, macro_f1=1,
                   quantity_disagreement=0, allocation_disagreement=0)

    def test_two_classes(self):
        # n 100; labels a 0.5, b 0.5; map a 0.6, b 0.4. OA 0.70; pe 0.5*0.6 + 0.5*0.4 = 0.50; kappa 0.2/0.5 = 0.40.
        # producers 40/50 = 0.8, 30/50 = 0.6 -> balanced 0.70. users 40/60, 30/40 = 0.75.
        # F1 a 2(0.8)(2/3)/(0.8 + 2/3) = 0.727273, b 2(0.6)(0.75)/1.35 = 0.666667 -> macro 0.696970.
        # Q = (|0.5-0.6| + |0.5-0.4|)/2 = 0.10; A = 1 - 0.70 - 0.10 = 0.20.
        m = metrics(log([[40, 10], [20, 30]], "ab", 0.70, 0.40))
        self.check(m, accuracy=0.70, kappa=0.40, balanced_accuracy=0.70, macro_f1=0.696970,
                   quantity_disagreement=0.10, allocation_disagreement=0.20)
        self.check(m["per_class"]["a"], producers=0.8, users=0.666667, f1=0.727273)
        self.check(m["per_class"]["b"], producers=0.6, users=0.75, f1=0.666667)

    def test_one_class_everywhere(self):
        # the map says a everywhere; labels a 0.9, b 0.1. OA 0.90 but pe 0.9*1.0 = 0.90 -> kappa 0.
        # producers 1.0 and 0.0 -> balanced 0.50; b's user's accuracy is undefined (never mapped) and its F1 is 0,
        # not left out: a class in the labels that the map never names counts against it.
        # F1 a 2(1)(0.9)/1.9 = 0.947368 -> macro (0.947368 + 0)/2 = 0.473684. Q 0.10, A 0: all of it is quantity.
        m = metrics(log([[90, 0], [10, 0]], "ab", 0.90, 0.0))
        self.check(m, accuracy=0.90, kappa=0.0, balanced_accuracy=0.50, macro_f1=0.473684,
                   quantity_disagreement=0.10, allocation_disagreement=0.0)
        self.assertIsNone(m["per_class"]["b"]["users"])
        self.assertEqual(m["per_class"]["b"]["f1"], 0.0)

    def test_class_absent_from_labels(self):
        # c is mapped (0.2) but has no held-out area: it has no producer's accuracy and no F1, and it is left
        # out of the balanced accuracy and the macro F1, yet its mapped area still counts as quantity error.
        # labels a 0.4, b 0.6, c 0; map a 0.3, b 0.5, c 0.2. OA 0.70; pe 0.4*0.3 + 0.6*0.5 = 0.42;
        # kappa 0.28/0.58 = 0.482759. producers 0.75, 2/3 -> balanced 0.708333. users 1.0, 0.8, 0.0.
        # F1 a 2(0.75)(1)/1.75 = 0.857143, b 2(2/3)(0.8)/(2/3 + 0.8) = 0.727273 -> macro 0.792208.
        # Q = (0.1 + 0.1 + 0.2)/2 = 0.20; A = 1 - 0.70 - 0.20 = 0.10.
        m = metrics(log([[30, 10, 0], [0, 40, 20], [0, 0, 0]], "abc", 0.70, 0.482759))
        self.check(m, accuracy=0.70, kappa=0.482759, balanced_accuracy=0.708333, macro_f1=0.792208,
                   quantity_disagreement=0.20, allocation_disagreement=0.10)
        self.assertIsNone(m["per_class"]["c"]["producers"])
        self.assertIsNone(m["per_class"]["c"]["f1"])

    def test_unrounded_matrix_preferred(self):
        # with both present, the unrounded matrix is the one scored (the rounded one here would give OA 1)
        r = log([[50, 0], [0, 50]], "ab", 0.70, 0.40)
        r["held_out"]["confusion_unrounded"] = [[40, 10], [20, 30]]
        m = metrics(r)
        self.check(m, accuracy=0.70, kappa=0.40)
        self.assertEqual(m["source"], "confusion_unrounded")

    def test_log_that_disagrees_with_itself(self):
        # a log whose stated accuracy is not its matrix's is refused, not scored
        with self.assertRaises(ValueError):
            metrics(log([[40, 10], [20, 30]], "ab", 0.75, 0.40))
        with self.assertRaises(ValueError):
            metrics(log([[40, 10], [20, 30]], "ab", 0.70, 0.45))


if __name__ == "__main__":
    unittest.main(verbosity=1)
