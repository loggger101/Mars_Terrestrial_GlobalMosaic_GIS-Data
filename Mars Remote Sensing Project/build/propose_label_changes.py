# -*- coding: utf-8 -*-
r"""Proposals for the seven-class labels (decision D17, KB §68; NEXT-STEPS §11.2).

Reads the 512 hand-drawn labels and writes Landform_TrainingSamples_v2_proposals: every label copied
with an Action and the evidence behind it, plus new polygons for the three new classes. Nothing is
decided here: the author sets Review on every row whose Action is not "keep", and
apply_label_review.py builds the v2 labels from the accepted rows. Landform_TrainingSamples_terrain is
only read.

  python propose_label_changes.py --dry-run     evidence, actions and checks; log only, nothing written
  python propose_label_changes.py               also write the proposals class (Pro closed)
  python propose_label_changes.py --map         also the map "Labels v2: proposals" in the .aprx

Classes (KB §68.1): 1 Crater (impact only), 2 steep/windy hills, 3 lava tube, 4 Normal Ground (volcanic
plains included), 5 volcanic edifice, 6 apron (water and ice), 7 fluvial channel.

Evidence for every polygon, old and new:
  SIM 3292 unit-group shares   v + vf volcanic plains, ve edifices, apron (ANa everywhere; lAa; Aa only
                               west of 100°W, the Olympus aureole), landslide (Aa in Valles Marineris)
  CraterCover                  share of the polygon inside Robbins & Hynek crater rims (cells of the DEM
                               window, up to 4,000 sampled), and the largest crater touching it
  relief and slope             from the HRSC/MOLA blend DEM, slope on a metric grid
  ValleyKm                     Alemanno & Orofino (2017) valley length within ~6 km of the polygon
  named features               the IAU names inside and within 100 km (catenae, valles, montes, ...)

Actions on the 512 (thresholds below, as constants):
  relabel  Crater on a volcano (ve >= 0.5 or a named mons/tholus/patera inside) -> 5; hills on apron
           units -> 6, on ve -> 5; lava tube by valleys off volcanic units -> 7, on apron units with no
           catena or fossa near -> 6, large on ve -> 5, large on volcanic plains with no catena -> 4;
           a relabelled polygon loses the ground of any label inside it that keeps its own class
  check    a Crater polygon under a quarter inside catalogued craters; Normal Ground on ve or apron;
           lava tube off volcanic units (fluvial suggested if a named vallis is within 100 km, else
           asked whether it is a tectonic pit chain); ProposedClass then holds the suggestion
  clip     a training polygon that shares ground with a held-out one loses that ground (KB §68.2)
  delete   a non-Crater polygon >= 95 % inside another of its class (a crater in a basin is kept)
  fix      Classcode or colour unlike the rest of its class (label 512)
  keep     everything else
New polygons ("new"): ve units -> 5; ANa, lAa and the aureole's Aa -> 6, each cut by a 3° grid and inset
5 km; valley strips 2.4 km wide along the longest valleys -> 7, at most 8 per held-out and 4 per
training block. Every new polygon has the existing labels and the valley strips cut out of it, so no
two rows overlap.

Split, as make_global60_classification.py: the 15° block of the centroid of the polygon clipped to
±60°; the 14 held-out blocks are those of Landform_TrainingSamples_terrain_60_test; any other block is
training. The script checks that rule reproduces the existing split.

Inputs, each with a drive default and an option for a test copy:
  --gdb      labels, IAU nomenclature, Ref_SIM3292_GeologicUnits, Ref_Craters_Robbins2020 (KB §41)
  --valleys  Mars Project\Reference\Alemanno2017_valleys\Giulia Valleys.shp, from Zenodo
             10.5281/zenodo.1051038 (CC BY-SA 4.0); SHA-256 of the .shp in VALLEY_SHA
  --dem      <drive>\Mars_HRSC_MOLA_BlendDEM_Global_200mp_v2.tif
  --out-gdb  where the proposals class goes (default: the project gdb)
  --aprx     the project for --map (default: the drive's; a copy for a rehearsal)
Writes logs\label_proposals.json. A proposals class holding any Review is never replaced.
"""
import os, sys, json, math, time, shutil, hashlib, collections
sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)   # progress shows in a log
import numpy as np
import arcpy
from osgeo import gdal, ogr

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from paths import on_drive, GDB as DRIVE_GDB

def opt(name, default):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default

GDB = opt("--gdb", DRIVE_GDB)
OUT_GDB = opt("--out-gdb", GDB)
VALLEYS = opt("--valleys", on_drive(r"Mars Project\Reference\Alemanno2017_valleys\Giulia Valleys.shp"))
DEM = opt("--dem", on_drive("Mars_HRSC_MOLA_BlendDEM_Global_200mp_v2.tif"))
APRX = opt("--aprx", on_drive(r"Mars Project\Mars Project.aprx"))
LOG = opt("--log", os.path.join(HERE, "logs", "label_proposals.json"))
DRY = "--dry-run" in sys.argv
MARKER = "propose_label_changes.py"
VALLEY_SHA = "bf853acd13545d19387e83596353318912f4b598d3b274d932a2bf764e306715"

LABELS = "Landform_TrainingSamples_terrain"
TEST = "Landform_TrainingSamples_terrain_60_test"
UNITS, CRATERS = "Ref_SIM3292_GeologicUnits", "Ref_Craters_Robbins2020"
OUT = "Landform_TrainingSamples_v2_proposals"
MAP = "Labels v2: proposals"

NAMES = {1: "Crater", 2: "steep/windy hills", 3: "lava tube", 4: "Normal Ground",
         5: "volcanic edifice", 6: "apron", 7: "fluvial channel"}
R_KM = 3396.19
KM_DEG = math.pi * R_KM / 180.0           # km per degree of latitude
BLOCK, LAT_MAX = 15.0, 60.0

SHARE = 0.5                # a unit group "holds" a polygon at half its area
CRATER_COVER_MIN = 0.25    # a Crater polygon less covered than this by catalogued craters is checked
LARGE_KM2 = 1000.0         # a lava-tube polygon this large is a field or an edifice, not a chain
VALLEY_NEAR_KM = 5.0       # valley length near a lava-tube polygon that suggests a fluvial origin
NESTED = 0.95
GRID_DEG, INSET_DEG, MIN_NEW_KM2 = 3.0, 0.045, 300.0   # new unit polygons: 3° cells, inset ~5 km
STRIP_DEG, STRIP_MIN_KM, STRIPS_TEST, STRIPS_TRAIN = 0.02, 20.0, 6, 2   # ~250 strips: a review, not a census
NEAR_KM = 100.0
NAMED_TYPES = {"Catena", "Cavus", "Fossa", "Vallis", "Mons", "Tholus", "Patera", "Mensa", "Sulcus",
               "Labes", "Chaos", "Collis", "Dorsum"}
VOLCANO_TYPES = {"Mons", "Tholus", "Patera"}


# ---------------------------------------------------------------------------- inputs
def block_of(geom):
    """The split's rule (make_global60_classification.make_split): the clipped polygon's centroid."""
    g = clip60(geom)
    if g is None:
        return None
    c = g.centroid
    return "%d_%d" % (math.floor(c.X / BLOCK), math.floor(c.Y / BLOCK))


_EXT60 = None
def clip60(geom):
    global _EXT60
    if _EXT60 is None:
        _EXT60 = rect(-180, -LAT_MAX, 180, LAT_MAX, geom.spatialReference)
    g = geom.intersect(_EXT60, 4)
    return g if g is not None and g.area > 0 else None


def rect(x0, y0, x1, y1, sr):
    return arcpy.Polygon(arcpy.Array([arcpy.Point(x0, y0), arcpy.Point(x0, y1), arcpy.Point(x1, y1),
                                      arcpy.Point(x1, y0), arcpy.Point(x0, y0)]), sr)


def km2(g):
    return g.getArea("GEODESIC", "SQUAREKILOMETERS")


def read_labels():
    sr = arcpy.Describe(os.path.join(GDB, LABELS)).spatialReference
    out = []
    flds = ["OID@", "Classvalue", "Classname", "Classcode", "RED", "GREEN", "BLUE", "SHAPE@"]
    with arcpy.da.SearchCursor(os.path.join(GDB, LABELS), flds) as cur:
        for oid, cv, cn, cc, r, g, b, shp in cur:
            out.append(dict(oid=oid, cls=cv, name=cn, code=cc, rgb=(r, g, b), geom=shp, km2=km2(shp)))
    with arcpy.da.SearchCursor(os.path.join(GDB, TEST), ["Block"]) as cur:
        held = sorted(set(r[0] for r in cur))
    return sr, out, held


def read_units(sr):
    units = []
    with arcpy.da.SearchCursor(os.path.join(GDB, UNITS), ["Unit", "UnitGroup", "SHAPE@"]) as cur:
        for u, grp, shp in cur:
            g = shp.projectAs(sr)
            c = g.centroid
            kind = None
            if grp in ("v", "vf"):
                kind = "volc"
            elif grp == "ve":
                kind = "ve"
            elif u in ("ANa", "lAa") or (u == "Aa" and c.X < -100):
                kind = "apron"
            elif u == "Aa":
                kind = "slide"                      # Valles Marineris landslides: not an ice apron
            units.append(dict(unit=u, group=grp, kind=kind, geom=g, ext=g.extent))
    return units


def read_craters():
    lon, lat, d = [], [], []
    with arcpy.da.SearchCursor(os.path.join(GDB, CRATERS), ["SHAPE@XY", "DiamKm"]) as cur:
        for (x, y), dk in cur:
            lon.append(x); lat.append(y); d.append(dk)
    return np.array(lon), np.array(lat), np.array(d)


def read_named(sr):
    out = []
    for fc in arcpy.ListFeatureClasses("MARS_nomenclature*") or []:
        if "crater" in fc.lower():
            continue
        with arcpy.da.SearchCursor(fc, ["clean_name", "type", "SHAPE@"]) as cur:
            for nm, ty, shp in cur:
                t = (ty or "").split(",")[0].strip()
                if shp is None or t not in NAMED_TYPES:
                    continue
                p = shp.projectAs(sr)
                out.append(dict(name=nm, type=t, pt=arcpy.PointGeometry(p.centroid, sr),
                                x=p.centroid.X, y=p.centroid.Y))
    return out


def read_valleys(sr):
    if not os.path.exists(VALLEYS):
        sys.exit("valley map missing: %s (Zenodo 10.5281/zenodo.1051038; NEXT-STEPS §11.2)" % VALLEYS)
    h = hashlib.sha256(open(VALLEYS, "rb").read()).hexdigest()
    if h != VALLEY_SHA:
        sys.exit("valley map %s has SHA-256 %s, expected %s" % (VALLEYS, h, VALLEY_SHA))
    out = []
    with arcpy.da.SearchCursor(VALLEYS, ["Type", "Name", "Age", "SHAPE@"]) as cur:
        for ty, nm, age, shp in cur:
            g = shp.projectAs(sr)
            out.append(dict(type=ty, name=(nm or "").strip(), age=age, geom=g, ext=g.extent))
    return out


# ---------------------------------------------------------------------------- evidence
class Dem:
    def __init__(self, path):
        gdal.UseExceptions()
        self.ds = gdal.Open(path)
        self.band = self.ds.GetRasterBand(1)
        self.gt = self.ds.GetGeoTransform()
        self.nodata = self.band.GetNoDataValue()

    def cells(self, geom):
        """Elevation (m), slope (deg) and lon/lat of the DEM cells whose centres fall in geom."""
        x0, dx, _, y0, _, dy = self.gt
        e = geom.extent
        c0 = max(0, int(math.floor((e.XMin - x0) / dx)) - 1)
        c1 = min(self.ds.RasterXSize, int(math.ceil((e.XMax - x0) / dx)) + 2)
        r0 = max(0, int(math.floor((e.YMax - y0) / dy)) - 1)
        r1 = min(self.ds.RasterYSize, int(math.ceil((e.YMin - y0) / dy)) + 2)
        if c1 - c0 < 3 or r1 - r0 < 3:
            return None
        z = self.band.ReadAsArray(c0, r0, c1 - c0, r1 - r0).astype("float64")
        z[z == self.nodata] = np.nan
        mem = gdal.GetDriverByName("MEM").Create("", c1 - c0, r1 - r0, 1, gdal.GDT_Byte)
        mem.SetGeoTransform((x0 + c0 * dx, dx, 0, y0 + r0 * dy, 0, dy))
        if int(gdal.VersionInfo()) >= 3110000:     # GDAL 3.11+: MEM holds vectors; "Memory" is deprecated
            src = gdal.GetDriverByName("MEM").Create("", 0, 0, 0, gdal.GDT_Unknown)
        else:
            src = ogr.GetDriverByName("Memory").CreateDataSource("")
        lyr = src.CreateLayer("p")
        f = ogr.Feature(lyr.GetLayerDefn()); f.SetGeometry(ogr.CreateGeometryFromWkt(geom.WKT))
        lyr.CreateFeature(f)
        gdal.RasterizeLayer(mem, [1], lyr, burn_values=[1])
        mask = mem.ReadAsArray().astype(bool)
        lats = y0 + (r0 + np.arange(r1 - r0) + 0.5) * dy
        lons = x0 + (c0 + np.arange(c1 - c0) + 0.5) * dx
        ddy = abs(dy) * KM_DEG * 1000.0
        ddx = abs(dx) * KM_DEG * 1000.0 * np.cos(np.radians(lats))[:, None]
        gy, gx = np.gradient(z)
        slope = np.degrees(np.arctan(np.hypot(gx / ddx, gy / ddy)))
        ok = mask & np.isfinite(z) & np.isfinite(slope)
        if not ok.any():
            return None
        rr, cc = np.nonzero(ok)
        return dict(z=z[ok], slope=slope[ok], lon=lons[cc], lat=lats[rr])


def crater_cover(cells, clon, clat, cd, rng):
    """Share of the cells inside a catalogued crater rim, and the largest crater touching the polygon."""
    lon, lat = cells["lon"], cells["lat"]
    if lon.size > 4000:
        i = rng.choice(lon.size, 4000, replace=False); lon, lat = lon[i], lat[i]
    rdeg = cd / 2.0 / KM_DEG
    near = ((clat + rdeg >= lat.min()) & (clat - rdeg <= lat.max()) &
            (clon + rdeg / np.maximum(np.cos(np.radians(clat)), 0.05) >= lon.min()) &
            (clon - rdeg / np.maximum(np.cos(np.radians(clat)), 0.05) <= lon.max()))
    if not near.any():
        return 0.0, 0.0
    nl, nt, nd = np.radians(clon[near]), np.radians(clat[near]), cd[near]
    pl, pt = np.radians(lon)[:, None], np.radians(lat)[:, None]
    inside = np.zeros(lon.size, bool); dmax = 0.0
    for s in range(0, nd.size, 2000):
        a = (np.sin((nt[s:s + 2000] - pt) / 2) ** 2 +
             np.cos(pt) * np.cos(nt[s:s + 2000]) * np.sin((nl[s:s + 2000] - pl) / 2) ** 2)
        dist = 2 * R_KM * np.arcsin(np.sqrt(np.clip(a, 0, 1)))
        hit = dist <= nd[s:s + 2000] / 2.0
        inside |= hit.any(axis=1)
        touched = hit.any(axis=0)
        if touched.any():
            dmax = max(dmax, float(nd[s:s + 2000][touched].max()))
    return float(inside.mean()), dmax


def unit_shares(geom, units):
    """Shares of the tracked unit kinds, and the unit covering most of the polygon."""
    e, a = geom.extent, km2(geom)
    sh, by_unit = collections.Counter(), collections.Counter()
    for u in units:
        ue = u["ext"]
        if ue.XMax < e.XMin or ue.XMin > e.XMax or ue.YMax < e.YMin or ue.YMin > e.YMax:
            continue
        if u["geom"].disjoint(geom):
            continue
        if u["geom"].contains(geom):
            x_km2 = a
        else:
            x = u["geom"].intersect(geom, 4)
            x_km2 = km2(x) if x is not None and x.area > 0 else 0.0
        if x_km2 > 0:
            by_unit[u["unit"]] += x_km2 / a
            if u["kind"]:
                sh[u["kind"]] += x_km2 / a
    top = by_unit.most_common(1)
    top = "%s %.2f" % top[0] if top else "no unit"
    return {k: round(min(v, 1.0), 3) for k, v in sh.items()}, top


def valley_km(geom, valleys):
    b = geom.buffer(0.1)
    e = b.extent
    total = 0.0
    for v in valleys:
        ve = v["ext"]
        if ve.XMax < e.XMin or ve.XMin > e.XMax or ve.YMax < e.YMin or ve.YMin > e.YMax:
            continue
        if b.disjoint(v["geom"]):
            continue
        x = b.intersect(v["geom"], 2)
        if x is not None:
            total += x.getLength("GEODESIC", "KILOMETERS")
    return total


def named_near(geom, named):
    inside, near = [], []
    c = geom.centroid
    for f in named:
        if abs(f["y"] - c.Y) > 20 or abs(f["x"] - c.X) > 40:
            continue
        if geom.contains(f["pt"]):
            inside.append((f["type"], f["name"], 0.0))
        else:
            d = geom.distanceTo(f["pt"]) * KM_DEG
            if d <= NEAR_KM:
                near.append((f["type"], f["name"], round(d)))
    return inside, sorted(near, key=lambda t: t[2])


def evidence(geom, ctx, rng):
    sh, top = unit_shares(geom, ctx["units"])
    cells = ctx["dem"].cells(geom)
    ev = dict(shares=sh, top_unit=top, km2=round(km2(geom), 1),
              eqd_km=round(2 * math.sqrt(km2(geom) / math.pi), 1),
              elong=round(geom.length ** 2 / (4 * math.pi * geom.area), 2) if geom.area > 0 else None)
    if cells is not None:
        cover, dmax = crater_cover(cells, *ctx["craters"], rng)
        p5, p50, p95 = np.percentile(cells["z"], [5, 50, 95])
        ev.update(cover=round(cover, 3), dmax_km=round(dmax, 1), relief_m=round(float(p95 - p5)),
                  elev_m=round(float(p50)), slope_med=round(float(np.median(cells["slope"])), 2),
                  slope_p90=round(float(np.percentile(cells["slope"], 90)), 2), cells=int(cells["z"].size))
    ev["valley_km"] = round(valley_km(geom, ctx["valleys"]), 1)
    ev["inside"], ev["near"] = named_near(geom, ctx["named"])
    return ev


def evidence_text(ev):
    s = ev["shares"]
    parts = ["unit %s; volc %.2f ve %.2f apron %.2f slide %.2f" % (ev["top_unit"], s.get("volc", 0), s.get("ve", 0),
                                                                   s.get("apron", 0), s.get("slide", 0))]
    if "cover" in ev:
        parts.append("craters cover %.2f, largest %.0f km (eq. diameter %.0f km)" % (ev["cover"], ev["dmax_km"],
                                                                                      ev["eqd_km"]))
        parts.append("relief %d m, slope median %.1f° p90 %.1f°" % (ev["relief_m"], ev["slope_med"], ev["slope_p90"]))
    parts.append("valleys %.0f km" % ev["valley_km"])
    nm = ["%s (in)" % n for _, n, _ in ev["inside"][:3]] + ["%s %d km" % (n, d) for _, n, d in ev["near"][:3]]
    if nm:
        parts.append("named: " + ", ".join(nm))
    return "; ".join(parts)[:254]


# ---------------------------------------------------------------------------- rules
def decide(lab, ev):
    """(action, proposed class, reason) for one of the 512, from its evidence alone."""
    s, c = ev["shares"], lab["cls"]
    volc, ve, apron = s.get("volc", 0), s.get("ve", 0), s.get("apron", 0)
    types_in = {t for t, _, _ in ev["inside"]}
    near = {t for t, _, d in ev["near"] if d <= 50} | types_in
    if c == 1:
        if ve >= SHARE or types_in & VOLCANO_TYPES:
            return "relabel", 5, "Crater means impact only: on a volcano (ve %.2f%s)" % (
                ve, ", " + ", ".join(n for t, n, _ in ev["inside"] if t in VOLCANO_TYPES) if types_in & VOLCANO_TYPES else "")
        if ev.get("cover", 1) < CRATER_COVER_MIN:
            return "check", 1, "under a quarter inside catalogued impact craters (%.2f): impact?" % ev.get("cover", 0)
    elif c == 2:
        if apron >= SHARE:
            return "relabel", 6, "hills on apron units (%.2f): aprons are their own class" % apron
        if ve >= SHARE:
            return "relabel", 5, "hills on a volcanic edifice (ve %.2f)" % ve
    elif c == 3:
        if ev["valley_km"] >= VALLEY_NEAR_KM and volc + ve < SHARE:
            return "relabel", 7, "by mapped valleys (%.0f km) off volcanic units (%.2f): fluvial" % (
                ev["valley_km"], volc + ve)
        if apron >= SHARE:
            if near & {"Catena", "Fossa", "Cavus"}:
                return "check", 6, "on apron units (%.2f) but a catena or fossa lies near: lava tube or apron?" % apron
            return "relabel", 6, "on apron units (%.2f), no catena or fossa near: lava tube is not apron" % apron
        if ve >= SHARE and ev["km2"] >= LARGE_KM2:
            return "relabel", 5, "large (%.0f km2) and on a volcanic edifice (ve %.2f)" % (ev["km2"], ve)
        if volc >= SHARE and ev["km2"] >= LARGE_KM2 and not near & {"Catena", "Cavus"}:
            return "relabel", 4, "large (%.0f km2) on volcanic plains (%.2f), no catena: volcanic plains are Normal Ground" % (
                ev["km2"], volc)
        if volc + ve < SHARE:
            vn = [(n, d) for t, n, d in ev["near"] if t == "Vallis"]
            if vn:
                return "check", 7, "off volcanic units (on %s), no mapped valley within 6 km, %s %d km: fluvial?" % (
                    ev["top_unit"], vn[0][0], vn[0][1])
            fos = [(n, d) for t, n, d in ev["near"] if t in ("Fossa", "Catena")]
            return "check", 3, "off volcanic units (on %s)%s: a tectonic pit chain rather than a lava tube? keep, relabel or reject" % (
                ev["top_unit"], ", %s %d km" % fos[0] if fos else "")
    elif c == 4:
        if ve >= SHARE:
            return "check", 5, "Normal Ground on a volcanic edifice (ve %.2f)" % ve
        if apron >= SHARE:
            return "check", 6, "Normal Ground on apron units (%.2f)" % apron
    return "keep", c, ""


def integrity(labels, held):
    """Nested duplicates, cross-split overlaps, odd attributes. Returns {oid: [(action, reason, geom)]}.
    Classes are the proposed ones (l["final"]): a polygon nested in one that changes class is no duplicate."""
    out = collections.defaultdict(list)
    codes = collections.Counter((l["cls"], l["code"], l["rgb"]) for l in labels)
    usual = {}
    for (c, code, rgb), n in codes.items():
        if n > usual.get(c, (None, None, 0))[2]:
            usual[c] = (code, rgb, n)
    for l in labels:
        u = usual[l["cls"]]
        if (l["code"], l["rgb"]) != (u[0], u[1]):
            out[l["oid"]].append(("fix", "Classcode %r colour %s, the class uses %r %s" % (l["code"], l["rgb"], u[0], u[1]), None))
    for i, a in enumerate(labels):
        for b in labels[i + 1:]:
            if a["geom"].disjoint(b["geom"]):
                continue
            x = a["geom"].intersect(b["geom"], 4)
            if x is None or x.area <= 0:
                continue
            k = km2(x)
            if a["final"] != b["final"]:
                # the relabelled, broader polygon gives way: a chain inside a flow field stays a chain
                movers = [p for p in (a, b) if p["final"] != p["cls"]]
                if len(movers) == 1:
                    p = movers[0]; q = b if p is a else a
                    out[p["oid"]].append(("cut", "label %d (%s) inside it keeps its class: %.1f km2 cut out" % (
                        q["oid"], NAMES[q["final"]], k), q["geom"]))
                else:
                    for p, q in ((a, b), (b, a)):
                        out[p["oid"]].append(("check", "shares %.1f km2 with label %d of another class" % (k, q["oid"]), None))
            sa, sb = a.get("split"), b.get("split")
            if sa != sb:
                tr, te = (a, b) if sa == "train" else (b, a)
                out[tr["oid"]].append(("clip", "shares %.1f km2 with held-out label %d" % (k, te["oid"]), te["geom"]))
            if a["final"] == b["final"] and a["final"] != 1:
                p, q = (a, b) if (a["km2"], -a["oid"]) <= (b["km2"], -b["oid"]) else (b, a)   # the smaller goes
                if k / p["km2"] >= NESTED:
                    out[p["oid"]].append(("delete", "%.0f %% inside label %d of the same class" % (100 * k / p["km2"], q["oid"]), None))
    return out


PRECEDENCE = ["delete", "relabel", "clip", "check", "fix", "keep"]


# ---------------------------------------------------------------------------- new polygons
def grid_pieces(geom, sr):
    e = geom.extent
    out = []
    for gx in np.arange(math.floor(e.XMin / GRID_DEG) * GRID_DEG, e.XMax, GRID_DEG):
        for gy in np.arange(math.floor(e.YMin / GRID_DEG) * GRID_DEG, e.YMax, GRID_DEG):
            if gy >= LAT_MAX or gy + GRID_DEG <= -LAT_MAX:
                continue
            cell = rect(gx, max(gy, -LAT_MAX), gx + GRID_DEG, min(gy + GRID_DEG, LAT_MAX), sr)
            if cell.disjoint(geom):
                continue
            x = geom.intersect(cell, 4)
            if x is not None and x.area > 0:
                out.append(x)
    return out


def subtract(g, cutters):
    for c in cutters:
        if g is None or g.area <= 0:
            return None
        if not g.disjoint(c):
            g = g.difference(c)
    return g if g is not None and g.area > 0 else None


def new_polygons(sr, ctx, labels, held):
    keep_geoms = [l["geom"] for l in labels]
    # 7: valley strips, longest first, capped per block
    per_block = collections.Counter()
    strips = []
    for v in sorted(ctx["valleys"], key=lambda v: -v["geom"].getLength("GEODESIC", "KILOMETERS")):
        g60 = v["geom"].intersect(_EXT60, 2)
        if g60 is None or g60.length <= 0 or g60.getLength("GEODESIC", "KILOMETERS") < STRIP_MIN_KM:
            continue
        c = g60.centroid if g60.centroid else g60.firstPoint
        b = "%d_%d" % (math.floor(c.X / BLOCK), math.floor(c.Y / BLOCK))
        cap = STRIPS_TEST if b in held else STRIPS_TRAIN
        if per_block[b] >= cap:
            continue
        g = subtract(g60.buffer(STRIP_DEG), keep_geoms)
        if g is None or km2(g) < 20:
            continue
        per_block[b] += 1
        sub = "valley network" if v["type"] == "Valley Network" else "valley"
        strips.append(dict(cls=7, geom=g, subtype=sub,
                           reason="strip along a mapped %s%s (Alemanno & Orofino 2017, %s), 2.4 km wide: check it sits on the floor" % (
                               v["type"].lower(), " (%s)" % v["name"] if v["name"] else "", v["age"])))
    cutters = keep_geoms + [s["geom"] for s in strips]
    # 5 and 6: unit polygons cut to a 3° grid, inset, existing labels and strips removed
    units = []
    for u in ctx["units"]:
        if u["kind"] not in ("ve", "apron"):
            continue
        cls = 5 if u["kind"] == "ve" else 6
        what = {"ANa": "mid-latitude apron unit (lobate debris aprons)", "lAa": "Tharsis fan-shaped deposit",
                "Aa": "Olympus Mons aureole (origin open)"}.get(u["unit"], "volcanic edifice unit")
        for piece in grid_pieces(u["geom"], sr):
            g = piece.buffer(-INSET_DEG)
            g = subtract(g, cutters) if g is not None and g.area > 0 else None
            if g is None or km2(g) < MIN_NEW_KM2:
                continue
            units.append(dict(cls=cls, geom=g, subtype="",
                              reason="SIM 3292 %s %s, a 3° piece inset 5 km: a 1:20 M unit holds mesas and plains "
                                     "too; trim to the %s itself before accepting" % (
                                         u["unit"], what, "apron lobes" if cls == 6 else "edifice")))
    return strips + units


# ---------------------------------------------------------------------------- output
FIELDS = [("OldOID", "LONG", None), ("OldClass", "SHORT", None), ("OldName", "TEXT", 24),
          ("Action", "TEXT", 8), ("ProposedClass", "SHORT", None), ("ProposedName", "TEXT", 24),
          ("Subtype", "TEXT", 24), ("Reason", "TEXT", 254), ("Evidence", "TEXT", 254),
          ("Split", "TEXT", 5), ("Block", "TEXT", 8), ("KM2", "DOUBLE", None), ("ShareVolc", "DOUBLE", None),
          ("ShareVE", "DOUBLE", None), ("ShareApron", "DOUBLE", None), ("CraterCover", "DOUBLE", None),
          ("MaxCraterKm", "DOUBLE", None), ("ReliefM", "DOUBLE", None), ("SlopeMed", "DOUBLE", None),
          ("ValleyKm", "DOUBLE", None), ("Review", "TEXT", 6), ("ReviewNote", "TEXT", 60), ("MappedBy", "TEXT", 40)]


def write(rows, sr):
    fc = os.path.join(OUT_GDB, OUT)
    if arcpy.Exists(fc):
        names = [f.name for f in arcpy.ListFields(fc)]
        if "Review" in names:
            with arcpy.da.SearchCursor(fc, ["Review"]) as c:
                if any((r[0] or "").strip() for r in c):
                    sys.exit("REFUSING: %s holds reviews; nothing replaced" % fc)
        if "MappedBy" not in names:
            sys.exit("REFUSING: %s was not written by this script" % fc)
        with arcpy.da.SearchCursor(fc, ["MappedBy"]) as c:
            if not all(r[0] == MARKER for r in c):
                sys.exit("REFUSING: %s holds rows this script did not write" % fc)
        arcpy.management.Delete(fc)
    arcpy.management.CreateFeatureclass(OUT_GDB, OUT, "POLYGON", spatial_reference=sr)
    for n, t, ln in FIELDS:
        arcpy.management.AddField(fc, n, t, field_length=ln)
    if "ReviewDecision" not in [d.name for d in arcpy.da.ListDomains(OUT_GDB)]:
        arcpy.management.CreateDomain(OUT_GDB, "ReviewDecision", "Candidate review: accept, reject or unsure",
                                      "TEXT", "CODED")
        for c in ("accept", "reject", "unsure"):
            arcpy.management.AddCodedValueToDomain(OUT_GDB, "ReviewDecision", c, c)
    arcpy.management.AssignDomainToField(fc, "Review", "ReviewDecision")
    names = ["SHAPE@"] + [n for n, _, _ in FIELDS]
    with arcpy.da.InsertCursor(fc, names) as cur:
        for r in rows:
            ev = r["ev"]; s = ev["shares"]
            cur.insertRow([r["geom"], r.get("old_oid"), r.get("old_cls"), NAMES.get(r.get("old_cls"), None),
                           r["action"], r["cls"], NAMES[r["cls"]], r.get("subtype", ""), r["reason"][:254],
                           evidence_text(ev), r["split"], r["block"], ev["km2"], s.get("volc", 0), s.get("ve", 0),
                           s.get("apron", 0), ev.get("cover"), ev.get("dmax_km"), ev.get("relief_m"),
                           ev.get("slope_med"), ev["valley_km"], None, None, MARKER])
    n = int(arcpy.management.GetCount(fc)[0])
    assert n == len(rows), "wrote %d rows, expected %d" % (n, len(rows))
    print("wrote %s: %d rows" % (fc, n))


def add_map():
    """The proposals in their own map: one layer per Action, the new polygons by class."""
    if "--aprx" not in sys.argv:
        bkdir = os.path.join(os.path.dirname(APRX), ".backups")
        os.makedirs(bkdir, exist_ok=True)
        bk = os.path.join(bkdir, "Mars Project %s.aprx" % time.strftime("%Y%m%d-%H%M%S"))
        shutil.copy2(APRX, bk); print("backup", bk)
    p = arcpy.mp.ArcGISProject(APRX)
    for m in p.listMaps(MAP):
        p.deleteItem(m)
    m = p.createMap(MAP, "MAP")
    m.spatialReference = arcpy.Describe(os.path.join(OUT_GDB, OUT)).spatialReference
    fc = os.path.join(OUT_GDB, OUT)
    for title, q in (("Kept as they are", "Action = 'keep'"),
                     ("Attributes to fix", "Action = 'fix'"),
                     ("To check", "Action = 'check'"),
                     ("To clip (shares ground with a held-out label)", "Action = 'clip'"),
                     ("To delete (nested duplicate)", "Action = 'delete'"),
                     ("To relabel", "Action = 'relabel'"),
                     ("New: fluvial channel (7)", "Action = 'new' AND ProposedClass = 7"),
                     ("New: apron (6)", "Action = 'new' AND ProposedClass = 6"),
                     ("New: volcanic edifice (5)", "Action = 'new' AND ProposedClass = 5")):
        lyr = m.addDataFromPath(fc)
        lyr.name = title
        lyr.definitionQuery = q
        if title.startswith("Kept"):
            lyr.visible = False
    p.save()
    print("map %r: %d layers" % (MAP, len(m.listLayers())))


# ---------------------------------------------------------------------------- main
def main():
    t0 = time.time()
    if not DRY and OUT_GDB == DRIVE_GDB:
        assert not any("ArcGISPro" in l for l in os.popen("tasklist").read().splitlines()), "close ArcGIS Pro first"
    arcpy.env.workspace = GDB
    rng = np.random.default_rng(68)
    sr, labels, held = read_labels()
    print("labels %d; held-out blocks %d: %s" % (len(labels), len(held), " ".join(held)))
    # the split, reproduced
    split_now = {}
    with arcpy.da.SearchCursor(os.path.join(GDB, TEST), ["SHAPE@"]) as c:
        test_geoms = [r[0] for r in c]
    for l in labels:
        l["block"] = block_of(l["geom"])
        l["split"] = None if l["block"] is None else ("test" if l["block"] in held else "train")
    mism = [l["oid"] for l in labels if l["split"] == "test" and not any(not l["geom"].disjoint(t) for t in test_geoms)]
    print("split reproduced by the centroid rule: %d test, %d train, %d outside ±60°, %d mismatches %s" % (
        sum(l["split"] == "test" for l in labels), sum(l["split"] == "train" for l in labels),
        sum(l["split"] is None for l in labels), len(mism), mism[:10]))
    ctx = dict(units=read_units(sr), craters=read_craters(), named=read_named(sr), valleys=read_valleys(sr),
               dem=Dem(DEM))
    print("units %d, craters %d, named %d, valleys %d (%.0f s)" % (len(ctx["units"]), ctx["craters"][0].size,
                                                                 len(ctx["named"]), len(ctx["valleys"]), time.time() - t0))
    for i, l in enumerate(labels):
        l["ev"] = evidence(l["geom"], ctx, rng)
        l["act"], l["prop"], l["why"] = decide(l, l["ev"])
        l["final"] = l["prop"] if l["act"] == "relabel" else l["cls"]
        if (i + 1) % 100 == 0:
            print("   %d labels (%.0f s)" % (i + 1, time.time() - t0))
    issues = integrity(labels, held)
    rows = []
    for l in labels:
        ev, act, cls, why = l["ev"], l["act"], l["prop"], l["why"]
        acts = [(act, why, None)] if act != "keep" else []
        acts += issues.get(l["oid"], [])
        geom = l["geom"]
        for a, w, cutter in acts:
            if a in ("clip", "cut") and cutter is not None:
                geom = geom.difference(cutter)
                ev["km2"] = round(km2(geom), 1)
        best = min([a if a != "cut" else act for a, _, _ in acts] or ["keep"], key=PRECEDENCE.index)
        if best == "delete":
            cls = l["cls"]
        reason = "; ".join(w for _, w, _ in acts)
        rows.append(dict(geom=geom, old_oid=l["oid"], old_cls=l["cls"], action=best, cls=cls, reason=reason,
                         ev=ev, split=l["split"] or "", block=l["block"] or "",
                         subtype="valley" if cls == 7 and l["cls"] != 7 else ""))
    news = new_polygons(sr, ctx, labels, held)
    print("new polygons: %d (%.0f s)" % (len(news), time.time() - t0))
    for n in news:
        b = block_of(n["geom"])
        rows.append(dict(geom=n["geom"], action="new", cls=n["cls"], reason=n["reason"], subtype=n["subtype"],
                         ev=evidence(n["geom"], ctx, rng), split="test" if b in held else "train", block=b or ""))
    # checks on the proposals as they would stand if every proposal were accepted
    live = [r for r in rows if r["action"] != "delete"]
    clash, cross = [], []
    for i, a in enumerate(live):
        ea = a["geom"].extent
        for b in live[i + 1:]:
            eb = b["geom"].extent
            if ea.XMax < eb.XMin or eb.XMax < ea.XMin or ea.YMax < eb.YMin or eb.YMax < ea.YMin:
                continue
            if a["geom"].disjoint(b["geom"]):
                continue
            x = a["geom"].intersect(b["geom"], 4)
            if x is None or x.area <= 0 or km2(x) < 0.01:
                continue
            if a["cls"] != b["cls"]:
                clash.append((a.get("old_oid"), b.get("old_oid"), a["cls"], b["cls"], round(km2(x), 2)))
            if a["split"] != b["split"]:
                cross.append((a.get("old_oid"), b.get("old_oid"), round(km2(x), 2)))
    tally = collections.Counter((r["action"], r["cls"]) for r in rows)
    per = collections.defaultdict(lambda: dict(train=0, test=0, train_blocks=set(), test_blocks=set()))
    for r in live:
        if r["split"]:
            d = per[r["cls"]]; d[r["split"]] += 1; d[r["split"] + "_blocks"].add(r["block"])
    print("\nproposals by action and class:")
    for (a, c), n in sorted(tally.items(), key=lambda kv: (PRECEDENCE.index(kv[0][0]) if kv[0][0] in PRECEDENCE else 9, kv[0][1])):
        print("   %-8s %d %-18s %4d" % (a, c, NAMES[c], n))
    print("\nif every proposal were accepted (minimum: 10 held out in 2 blocks, 20 training in 3):")
    for c in sorted(per):
        d = per[c]
        ok = d["test"] >= 10 and len(d["test_blocks"]) >= 2 and d["train"] >= 20 and len(d["train_blocks"]) >= 3
        print("   %d %-18s train %4d in %2d blocks, held out %4d in %2d blocks  %s" % (
            c, NAMES[c], d["train"], len(d["train_blocks"]), d["test"], len(d["test_blocks"]), "ok" if ok else "SHORT"))
    print("\noverlaps between classes: %d %s" % (len(clash), clash[:10]))
    print("overlaps across the split: %d %s" % (len(cross), cross[:10]))
    log = dict(made=time.strftime("%Y-%m-%d %H:%M"), held_out_blocks=held, split_mismatches=mism,
               tally={"%s %d" % k: v for k, v in tally.items()},
               minimum={NAMES[c]: dict(train=d["train"], test=d["test"], train_blocks=sorted(d["train_blocks"]),
                                       test_blocks=sorted(d["test_blocks"])) for c, d in per.items()},
               class_overlaps=clash, split_overlaps=cross,
               rows=[dict(old_oid=r.get("old_oid"), old_cls=r.get("old_cls"), action=r["action"], cls=r["cls"],
                          subtype=r.get("subtype", ""), reason=r["reason"], split=r["split"], block=r["block"],
                          ev={k: v for k, v in r["ev"].items()}) for r in rows])
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    json.dump(log, open(LOG, "w", encoding="utf-8"), indent=1, ensure_ascii=False, default=str)
    print("log", LOG)
    if clash or cross:
        print("NOT WRITTEN: the proposals overlap across classes or across the split")
        sys.exit(1)
    if DRY:
        print("dry run: nothing written (%.0f s)" % (time.time() - t0))
        return
    write(rows, sr)
    if "--map" in sys.argv:
        add_map()
    print("done in %.0f s" % (time.time() - t0))


if __name__ == "__main__":
    main()
