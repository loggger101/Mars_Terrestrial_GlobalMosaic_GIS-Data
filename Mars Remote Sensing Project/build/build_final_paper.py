# -*- coding: utf-8 -*-
r"""Builds the final paper (AASTeX 7, aastex701.cls): copies its figures in, then compiles the PDF.

The prose is hand-written LaTeX in NEXT STUFF\Final\paper\mars_global_mosaic.tex, every number with its KB § in a
comment beside it; this script only gathers the figures and runs the compiler, so a figure refreshed by
make_final_figs.py, make_fig_final.py or an interim chart script reaches the paper on the next build.

  py -3.13 build_final_paper.py [--no-compile]

Needs MiKTeX (installed per-user 2026-10-22; pdflatex and bibtex under %LOCALAPPDATA%\Programs\MiKTeX), which
fetches missing packages on demand.
"""
import os, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
PAPER = os.path.join(os.path.dirname(HERE), "NEXT STUFF", "Final", "paper")
FIGS = os.path.join(PAPER, "figures")
JOB = "mars_global_mosaic"
TEX_BIN = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "MiKTeX", "miktex", "bin", "x64")

FIGURES = [   # (source under build\, name in figures\)
    (r"final_img\10_global60_locator.png", "10_global60_locator.png"),
    (r"final_img\15_athabasca_type_area.png", "15_athabasca_type_area.png"),
    (r"final_img\08_global60_mosaic.png", "08_global60_mosaic.png"),
    (r"pres1_img\global60_thermal.png", "global60_thermal.png"),     # cropped: CROP
    (r"interim_img\tes_check.png", "tes_check.png"),
    (r"final_img\depressions_vs_robbins.png", "depressions_vs_robbins.png"),
    (r"interim_img\ius_channel_candidates.png", "ius_channel_candidates.png"),   # cropped: CROP
    (r"final_img\12_global60_channels.png", "12_global60_channels.png"),
    (r"interim_img\t8_enrichment.png", "t8_enrichment.png"),
    (r"interim_img\t5_margins.png", "t5_margins.png"),
    (r"final_img\04_global60_landforms.png", "04_global60_landforms.png"),
    (r"interim_img\accuracy_200m.png", "accuracy_200m.png"),
    (r"interim_img\thermal_ablation.png", "thermal_ablation.png"),
    (r"final_img\16_x5_detections.png", "16_x5_detections.png"),
    (r"final_img\17_x5c_unet_provinces.png", "17_x5c_unet_provinces.png"),
    (r"final_img\svm_vs_unet.png", "svm_vs_unet.png"),
]
# Two deck charts carry slide furniture a paper caption replaces: a title strip naming the gdb class and the KB
# (ius_channel_candidates), a footnote citing the KB (global60_thermal). Pixels cut from the top and the bottom.
CROP = {"ius_channel_candidates.png": (80, 0), "global60_thermal.png": (0, 95)}


def run(exe, *args):
    r = subprocess.run([os.path.join(TEX_BIN, exe)] + list(args), cwd=PAPER, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    if r.returncode != 0:
        print(r.stdout[-4000:])
        sys.exit("%s failed (exit %d); see %s.log" % (exe, r.returncode, JOB))
    return r.stdout


def main():
    os.makedirs(FIGS, exist_ok=True)
    for src, name in FIGURES:
        p = os.path.join(HERE, src)
        if not os.path.exists(p):
            sys.exit("missing figure %s: run make_final_figs.py / make_fig_final.py first" % p)
        if name in CROP:
            from PIL import Image
            top, bottom = CROP[name]
            im = Image.open(p)
            im.crop((0, top, im.width, im.height - bottom)).save(os.path.join(FIGS, name), optimize=True)
        else:
            shutil.copy2(p, os.path.join(FIGS, name))
    print("copied %d figures to %s" % (len(FIGURES), FIGS))
    if "--no-compile" in sys.argv:
        return
    flags = ["-interaction=nonstopmode", "-halt-on-error", JOB + ".tex"]
    run("pdflatex.exe", *flags)
    run("bibtex.exe", JOB)
    run("pdflatex.exe", *flags)
    out = run("pdflatex.exe", *flags)
    warn = [l for l in open(os.path.join(PAPER, JOB + ".log"), encoding="latin-1")
            if "undefined" in l.lower() or "Overfull" in l]
    for l in warn:
        print("  " + l.rstrip())
    print(out.strip().splitlines()[-1])


if __name__ == "__main__":
    main()
