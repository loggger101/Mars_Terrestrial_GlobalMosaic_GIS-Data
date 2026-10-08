# -*- coding: utf-8 -*-
r"""Exports the project's layouts to build\interim_img\ for the living interim deck (KB §39.3).

The deck is rebuilt as the data moves, so it must never show a stale sheet: this re-exports
every layout named in interim.py from Mars Project.aprx, at 200 dpi.

A whole sheet shrunk onto a slide turns its title and captions into unreadable fine print, and
the slide's takeaways say the same things anyway. So the sheet's prose is HIDDEN for the
export (the elements in DROP; short panel headings stay), and the picture is trimmed to what is
left: map frames, legends, scale bars, north arrows. This happens in memory only: the .aprx is
opened, never saved, so the layouts are untouched and Pro may be open.

  "C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe" make_interim_figs.py
"""
import os, sys, time
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import arcpy
from PIL import Image, ImageChops

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import interim as I

APRX = os.path.join(os.path.splitdrive(HERE)[0] + os.sep, "Mars Project", "Mars Project.aprx")
OUT = os.path.join(HERE, "interim_img")
DPI = 200
PAD = 12                                   # px of white kept round the trimmed content
# The sheet's prose, by element name as the three layout builders write them. Headings
# (hA-hD on 08, h29/h30 on 05) stay: they label panels the slide cannot label for them.
DROP = {"title", "subtitle", "credit", "notes", "checks", "acc_head", "acc_body",
        "cA", "cB", "cC", "cD", "s29", "s30", "t29", "t30"}


def trim(path):
    im = Image.open(path).convert("RGB")
    box = ImageChops.difference(im, Image.new("RGB", im.size, (255, 255, 255))).getbbox()
    if box:
        l, t, r, b = box
        im = im.crop((max(0, l - PAD), max(0, t - PAD), min(im.width, r + PAD), min(im.height, b + PAD)))
    im.save(path, optimize=True)
    return im.size


def main():
    os.makedirs(OUT, exist_ok=True)
    p = arcpy.mp.ArcGISProject(APRX)
    have = {l.name: l for l in p.listLayouts()}
    wanted = sorted({img for f in I.FIGURES for kind, img in f["images"] if kind == "layout"})
    missing = [n for n in wanted if n not in have]
    if missing:
        sys.exit("layouts not in the project: %s" % missing)
    for n in wanted:
        t = time.time()
        lyt = have[n]
        hidden = [e for e in lyt.listElements() if e.name in DROP]
        for e in hidden:
            e.visible = False
        out = os.path.join(OUT, n + ".png")
        lyt.exportToPNG(out, resolution=DPI)
        size = trim(out)
        print("  %-24s %5.1f s  %d hidden  %d x %d px" % (n, time.time() - t, len(hidden), size[0], size[1]))
        # A sheet with a legend also gets the map without it and the legend alone, so the deck
        # can run the map full width and set the legend beside the takeaways.
        legends = [e for e in lyt.listElements("LEGEND_ELEMENT") if e.visible]
        if not legends:
            continue
        # A legend draws nothing once its map frame is hidden, so it is found as the difference
        # between the sheet with and without it, and cut from the first.
        whole = os.path.join(OUT, n + "__with_legend.png")
        lyt.exportToPNG(whole, resolution=DPI)
        for e in legends:
            e.visible = False
        m = os.path.join(OUT, n + "__map.png")
        lyt.exportToPNG(m, resolution=DPI)
        a, b = Image.open(whole).convert("RGB"), Image.open(m).convert("RGB")
        box = ImageChops.difference(a, b).getbbox()
        if box is None:
            sys.exit("%s: the legend drew nothing" % n)
        l, t_, r, b_ = box
        a.crop((max(0, l - PAD), max(0, t_ - PAD), r + PAD, b_ + PAD)).save(
            os.path.join(OUT, n + "__legend.png"), optimize=True)
        a.close(); b.close(); os.remove(whole)
        trim(m)
        print("  %-24s + __map, __legend (%d x %d px)" % ("", r - l + 2 * PAD, b_ - t_ + 2 * PAD))
    print("exported %d layouts at %d dpi to %s (the project was not saved)" % (len(wanted), DPI, OUT))


if __name__ == "__main__":
    main()
