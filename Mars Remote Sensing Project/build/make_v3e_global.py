# -*- coding: utf-8 -*-
r"""The edifice retraining's model (run edf, tag v3e; make_v3_edf.py, D37) over all of ±60°, in two passes.

To be run ONLY if make_v3_edf.py --report gives E1-E5 all held (D39, the author 2026-11-11, KB §69.109: "Yes, classify
and lead"). Otherwise the retraining is reported as a test (D40) and this script is not used.

It is make_dl_pixels.py's --classify-global and --mosaic --two-pass with three things changed and nothing else:
  the model    edf's newest .emd (make_v3_extras.emd("edf")), not the published v3 model
  the scratch  C:\MarsScratch\x5c_v3e\global (tiles\, tiles_b\), so no v3 tile is read or replaced
  the names    global60_landforms_unet_v3e_200m_seamfix.tif and logs\dl_unet_v3e_global_mosaic_seamfix.json
The classes, the stack, the tiles, the two passes and the mosaic rule are the published v3 map's (KB §66.8, §69.80).
mosaic() refuses to replace a file in Global60, as always.

  "<ArcGIS Pro Python>" make_v3e_global.py --plan                      prints the paths and the model; runs nothing
  "<ArcGIS Pro Python>" make_v3e_global.py --classify [--pass B] --tiles N    (run_v3e_lead.ps1, chunks of 60 tiles)
  "<ArcGIS Pro Python>" make_v3e_global.py --mosaic
Then verify_global60_classification.py --cell 200 --labels v3 | v2 --raster <the map> scores it like the v3 map.
"""
import os, sys
sys.argv += ["--labels", "v3"]                    # seven classes; read by labelsets.py when it is first imported
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import make_v3_extras as X
import make_dl_pixels as D
import labelsets as L

TAG = "_v3e"
assert L.NAMES == L.SEVEN
L.TAG = TAG                                       # mosaic()'s log name
D.WORK = r"C:\MarsScratch\x5c" + TAG
D.GLOBAL = os.path.join(D.WORK, "global")
D.UNET_MAP = "global60_landforms_unet%s_200m.tif" % TAG
D.UNET_SEAMFIX = "global60_landforms_unet%s_200m_seamfix.tif" % TAG
V3_GLOBAL = r"C:\MarsScratch\x5c_v3\global"
assert os.path.normcase(D.GLOBAL) != os.path.normcase(V3_GLOBAL)


def model():
    m = X.emd("edf")
    assert "x5c_v3e_" in m, m
    return m


if __name__ == "__main__":
    if "--plan" in sys.argv:
        import glob
        print("scratch ", D.GLOBAL)
        print("map     ", os.path.join(D.G.OUTDIR, D.UNET_SEAMFIX), "exists" if os.path.exists(os.path.join(D.G.OUTDIR, D.UNET_SEAMFIX)) else "not yet")
        print("stack   ", D.STACK, os.path.exists(D.STACK))
        print("tiles   ", len(D.tiles()))
        root = os.path.join(X.WORK, "models", "global60_unet_x5c_v3e_*")
        print("model   ", sorted(glob.glob(os.path.join(root, "*.emd"))) or "no .emd yet under %s" % root)
    elif "--classify" in sys.argv:
        os.makedirs(D.GLOBAL, exist_ok=True)
        sys.argv += ["--emd", model()]
        D.classify_global()
    elif "--mosaic" in sys.argv:
        sys.argv += ["--two-pass"]
        D.mosaic()
    else:
        sys.exit(__doc__)
