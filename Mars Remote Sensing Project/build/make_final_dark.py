# -*- coding: utf-8 -*-
r"""Navy-ground copies of the final deck's charts and layouts (D24, the author's yes of 2026-11-03; KB §69.65)
-> final_img\dark\.

The final deck is drawn in the interim's mars_theme since D24, so its figures need the navy-ground copies the
interim's have (make_interim_dark.py, KB §69.13). This reuses that script's recolouring unchanged, pointed at
final_img\dark\: each chart script runs with matplotlib's savefig wrapped, and each layout the final deck shows
(final.FIGURES, exported to final_img\ by make_final_figs.py) has its white page turned navy. The white originals,
which the paper and the README use, are never overwritten.

    "<ArcGIS Pro Python>" make_final_dark.py     (make_fig_channels.py reads a raster with GDAL)
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import make_interim_dark as D                                     # noqa: E402  (its __main__ does not run)

D.OUT = os.path.join(HERE, "final_img", "dark")
D.CHARTS = ["make_fig_final.py", "make_fig_t5_traced.py", "make_fig_baselines.py", "make_fig_checks.py", "make_fig_tes.py", "make_fig_t8.py",
            "make_fig_t1_pro.py", "make_fig_tests567.py", "make_fig_global60.py", "make_fig_channels.py",
            "make_fig_crater_sfd.py", "make_fig_t4.py"]    # the size-frequency slide (KB 69.112)


def layouts():
    import final
    names = [r for f in final.FIGURES for k, r in f.get("images", []) if k == "layout"]
    for name in names:
        for suffix, legend in (("", False), ("__map", False), ("__legend", True)):
            p = os.path.join(HERE, "final_img", name + suffix + ".png")
            if os.path.exists(p):
                D.layout(p, legend)


if __name__ == "__main__":
    os.makedirs(D.OUT, exist_ok=True)
    D.charts()
    layouts()
