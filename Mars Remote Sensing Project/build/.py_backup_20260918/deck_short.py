# -*- coding: utf-8 -*-
"""Short forms of the content blocks, for the spoken deck only.

content.py holds the full prose, and the written prospectus and interim report
are built from it. Those documents are meant to be read, so they should stay
long. A slide is not read, it is glanced at while someone talks over it, so the
deck gets its own shorter copies here.

Nothing in content.py is modified or removed by this module. The rule applied
to every block below: state a fact once in full, on the slide that owns it, and
reference it in a clause everywhere else.

  fact                          full statement lives on
  ----------------------------  ------------------------------------------
  three coordinate frames       Potential Problems (it is the root problem)
  DN gradient is not slope      the gradient figure (the picture proves it)
  THEMIS Night IR is needed     Data Sources - Still Required
  the three products + specs    Data Sources - Acquired (panels show them)
  Composite Bands failed x3     Potential Problems

Before: 2,491 body words over 15 content slides.
After:  ~1,560.
"""

# The mission sentence is unchanged -- it is the thesis of the whole talk.

# -- Significance -------------------------------------------------------------
# Was 5 bullets. The first restated Background and is cut; the rest keep the
# claim and drop the justification, which is what the speaker is for.
SIGNIFICANCE_DECK = [
    ("Thermal infrared responds to particle size and surface coherence; visible "
     "albedo does not. Where Mars is dust-mantled, the THEMIS layer should "
     "recover flow boundaries the Viking mosaic cannot — a claim this project "
     "can measure."),
    ("Discriminating volcanic from fluvial channels is a live problem: Athabasca "
     "Valles was mapped as a fluvial outflow channel for decades before being "
     "reinterpreted as flood lava. Morphology plus thermal response addresses "
     "it."),
    ("Terrestrial remote sensing methods, applied to a surface with no water "
     "column, no vegetation and ~6 mbar of CO₂ overhead — the signal is almost "
     "entirely surface physics."),
    ("Testable without privileged data: unit boundaries against the published "
     "USGS global geologic map, crater rims against the 141 IAU-named craters "
     "above 100 km already in the geodatabase. Both are free."),
]

# -- Data sources still required ----------------------------------------------
# The CTX out-of-scope point was stated twice on this slide -- once in the table
# and again in the note underneath. It is kept in the table only.
DATA_NEEDED_DECK = [
    ("THEMIS Night IR global mosaic", "100 m/px",
     "The highest-value missing dataset. Day–night pairing is what turns "
     "brightness temperature into thermal inertia."),
    ("CTX mosaic tiles (bounded, not global)", "5–6 m/px",
     "Bounded close-ups only, to resolve margins and craters below the ~1 km limit of "
     "the 100 m base. A global CTX mosaic is multi-terabyte — out of scope."),
    ("A crater catalogue or digitized crater layer", "n/a",
     "The IAU layers are named features only. Crater statistics need a "
     "catalogue or digitized craters."),
]

# -- Spectral bands -----------------------------------------------------------
# Same five rows the deck already sliced; the third column is cut to the reason
# alone, since the band and wavelength columns already say what it is.
BANDS_DECK = [
    ("THEMIS Day IR (v12 mosaic)", "6.8–14.9 µm",
     "The morphology and composition base, and the finest global layer held"),
    ("Viking MDIM 2.1 band 1 (red)", "≈ 0.59 µm",
     "Best contrast between ferric dust and darker basalt"),
    ("Viking MDIM 2.1 bands 1/2/3", "visible RGB",
     "Natural-colour context and unit boundary confirmation"),
    ("HRSC/MOLA elevation", "n/a (altimetry)",
     "The vertical reference for every channel gradient measured"),
    ("Planned: THEMIS day − night", "6.8–14.9 µm",
     "Thermal inertia proxy; needs the night mosaic"),
]

# -- Background ---------------------------------------------------------------
# Was 4 bullets. The product list is cut (the Data Sources slide shows all three
# with panels and specs) and the methods bullet is cut (it restates Significance).
BACKGROUND_DECK = [
    ("Three global products cover Mars end to end, in three parts of the "
     "spectrum — but in three different coordinate frames. No single product "
     "lets you interrogate morphology, thermal response, and slope at the same "
     "pixel; building that stack is the core technical task."),
    ("Each target landform family records a different process — volcanic "
     "resurfacing, flowing water, impact — and each is expressed differently "
     "across the three datasets. That is what makes fusing them worth doing."),
]

# -- Tasks --------------------------------------------------------------------
# Was 401 words of full paragraphs in the third column. One clause each now;
# the detail is in the speaker notes and in full in the written prospectus.
TASKS_DECK = [
    ("Acquire the global raster set",
     "Done. All three on disk with statistics built; pyramids still to build."),
    ("Build a grouped mosaic viewer",
     "Done. One map, three groups, each source raster paired with its derived "
     "product."),
    ("Harmonize the coordinate systems",
     "The gate. Three frames and two meridians into one. Check the meridian, "
     "not just the units."),
    ("Rebuild the terrain derivatives",
     "Re-run Slope and Hillshade on the projected DEM for a valid z-factor."),
    ("Build the visible + infrared composite",
     "Composite Bands over Viking colour and THEMIS day — four bands. Project "
     "first, then run over bounded extents."),
    ("Derive image-gradient products",
     "Edge and texture from DN, labelled as gradient rather than as terrain "
     "slope."),
    ("Classify surface units",
     "Iso Cluster, then Maximum Likelihood on training polygons. Already "
     "rehearsed on the Mercury MESSENGER basemap."),
    ("Digitize landform vectors",
     "Flow margins, channel centerlines and crater rims as three feature "
     "classes."),
    ("Build a real crater inventory",
     "The IAU layers are a gazetteer of 1,113 named craters. Digitize a "
     "sample area or import a catalogue."),
    ("Produce the map layouts",
     "None exist yet. Global sheets at 60°N–60°S plus detail panels."),
]

# -- Resolution ---------------------------------------------------------------
# Was 236 words. All four kinds are kept because the template names all four,
# but each is cut to the two lines that carry a number or a consequence.
RESOLUTION_DECK = [
    ("Spatial",
     ["Set by what is held: 100 m (THEMIS), 200 m (DEM), 232 m (Viking). The "
      "composite can be no finer than its coarsest input.",
      "Ten pixels across a feature to map its margin reliably — so features "
      "of about a kilometre and up. Sub-kilometre tributaries will not "
      "resolve."]),
    ("Spectral",
     ["Four bands held: one thermal, three visible. Enough to separate broad "
      "unit types, not enough to identify minerals.",
      "THEMIS Night IR is the highest-value addition — it turns the day "
      "mosaic into a measurement rather than an image."]),
    ("Radiometric",
     ["Both image mosaics are 8-bit as distributed — the practical limit on "
      "how finely units can be separated by DN alone.",
      "The DEM is the exception, carrying a real range of −8,528 m to "
      "+21,226 m. The quantitative measurements come from there."]),
    ("Temporal",
     ["Martian landforms do not change on human timescales, so this is not "
      "change detection.",
      "It matters diurnally: day and night IR of the same ground is the entire "
      "basis of the planned thermal inertia product."]),
]

# -- Hypotheses ---------------------------------------------------------------
# Only H1 is cut: its "because" clause restated the Significance slide. Each
# hypothesis keeps its stated measurement, which is the point of the slide.
HYPOTHESES_DECK = [
    ("H1",
     "In dust-mantled regions, the THEMIS Day IR layer will delineate volcanic "
     "flow boundaries that are not visible in the Viking colour mosaic. "
     "Measured as mapped flow area from the IR layer against the visible layer "
     "over the same extent."),
    ("H2",
     "Channel segments classed as fluvial will show shallower longitudinal "
     "gradients in the DEM than segments classed as volcanic, and the two "
     "populations will separate when gradient is plotted against thermal DN."),
    ("H3",
     "A four-band composite will produce more stable Iso Cluster classes than "
     "any single input, measured by how many requested classes survive with a "
     "meaningful pixel count."),
    ("H4",
     "Crater rim detection from the DN gradient products will recover a large "
     "majority of the 141 IAU-named craters larger than 100 km — an "
     "independent check before the method is trusted on unnamed craters."),
]

# -- Potential problems -------------------------------------------------------
# Was 364 words, five problems each with a narrative and a mitigation sentence.
# This slide owns the coordinate-frame and Composite Bands facts in full; every
# other slide now refers to them in a clause.
PROBLEMS_DECK = [
    ("Three coordinate frames in one project",
     "The DEM is in degrees; Viking and THEMIS are in metres but on central "
     "meridians 0° and 180°. A stack built without fixing that is half a planet "
     "out, and misregisters silently rather than failing. Fix: one frame, and "
     "verify the meridian. Root cause of the next two."),
    # exact runtimes, not rounded: the prospectus and interim report quote these
    # to the second, and audit_consistency.py compares the four documents
    ("Composite Bands does not complete at global scale",
     "Three attempts on 9 September, all cancelled — after 47 min 57 s, "
     "1 min 41 s, and 1 h 14 min 51 s. The centrepiece of the project does not "
     "yet exist. Fix: common CRS and cell size first, then bounded extents "
     "rather than the full globe."),
    ("Processing time is the schedule",
     "7 min for slope on the DEM, 1 h 05 min on the Viking mosaic, 1 h 27 min "
     "for surface parameters — and no compatible GPU, so everything runs on "
     "CPU. Fix: budget whole evenings, and prototype on subsets."),
    ("“Slope” on imagery is not slope",
     "Slope_Mars_M1 and Slope_Mars_V1 were computed from brightness values, not "
     "elevation. Fix: rename and describe them as gradient products so no "
     "reader mistakes them for topography."),
    ("No ground truth, and no sub-metre imagery",
     "Validation is against published interpretations, not field data, and the "
     "finest imagery held is 100 m. Fix: assess against the USGS geologic map "
     "and the IAU gazetteer, and state the ~1 km floor as a limit."),
]
