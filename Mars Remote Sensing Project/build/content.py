# -*- coding: utf-8 -*-
"""Shared content for the Mars global mosaic project deliverables.

Every dataset, parameter, runtime, and error below was read out of the actual
project on Z:\\ on 2026-09-13 (aprx layer definitions, the file geodatabase item
table's <Process> lineage, the GpMessages logs, and the .aux.xml raster
statistics). Nothing here is invented.
"""

# Logan Edwards' own title, taken from his Presentation 1.
DECK_TITLE = "Mars Global Mosaic"
COURSE = "REMOTE SENSING 2026 OCN 4704"
AUTHOR = "Logan Edwards"

TITLE = ("Mars Global Mosaic: Mapping Lava Flows, Fluvial Channels, "
         "and Impact Craters in Visible and Infrared")

SHORT_TITLE = "Mars Global Mosaic"

INVESTIGATORS = [
    AUTHOR,
    COURSE,
    "Fall 2026",
]

# ---------------------------------------------------------------- INTRODUCTION

MISSION = (
    "Assemble a co-registered global visible and thermal-infrared mosaic of Mars in "
    "ArcGIS Pro from three existing global products, and use it to map and classify "
    "three landform families \u2014 volcanic flow units, fluvial channels and valley "
    "networks, and impact craters \u2014 producing one internally consistent global "
    "landform inventory."
)

BACKGROUND = [
    ("Three global products already cover Mars end to end at better than 250 m per "
     "pixel, in three different parts of the spectrum: Viking MDIM 2.1 colour "
     "(visible, 232 m), THEMIS Day IR (thermal infrared, 100 m), and the HRSC/MOLA "
     "blended DEM (topography, 200 m). All three are downloaded and loaded."),
    ("They are distributed separately and in two different coordinate systems, so no "
     "single product lets you interrogate morphology, thermal response, and slope at "
     "the same pixel. Building that stack is the core technical task of this project."),
    ("The three target landform families each record a different process: volcanic "
     "resurfacing, flowing water, and impact. Each is expressed differently across the "
     "three datasets, which is what makes a fused stack worth building."),
    ("The methods are the same ones used for terrestrial scenes \u2014 band compositing, "
     "gradient and slope derivatives, unsupervised and supervised classification, "
     "accuracy assessment \u2014 applied to a planetary surface with no water column "
     "and no vegetation to correct for."),
]

TASKS = [
    ("Acquire the global raster set",
     "Viking MDIM 2.1 colour (232 m), THEMIS Day IR v12 (100 m), HRSC/MOLA blended "
     "DEM (200 m). All three are on disk with statistics built. Pyramids are not "
     "built on any of them, which is worth doing before the next global run."),
    ("Build a grouped mosaic viewer",
     "One map holding three groups (Viking, IR, HRSC MOLA), each pairing the source "
     "raster with its derived product, so layers can be swapped against each other. "
     "Complete."),
    ("Harmonize the coordinate systems",
     "Three frames, not two: the DEM is in GCS_Mars_2000_Sphere (degrees, central "
     "meridian 0); Viking is SimpleCylindrical_Mars in metres on central meridian 0; "
     "THEMIS is SimpleCylindrical_Mars in metres on central meridian 180. Project "
     "everything into one frame, and check the meridian, not just the units."),
    ("Rebuild the terrain derivatives correctly",
     "Re-run Slope and Hillshade on the projected DEM so the z-factor is valid; the "
     "current versions were computed against degree units and carry WARNING 000869."),
    ("Build the visible + infrared composite",
     "Composite Bands over the co-registered Viking colour and THEMIS Day IR \u2014 "
     "four bands. Elevation stays a separate analysis layer: Iso Cluster measures "
     "distance in raw band values, so a band running \u22128,528 to +21,226 m would "
     "swamp four running 1\u2013255. Four attempts at global scale \u2014 three on "
     "9 September and one on 13 September \u2014 all cancelled before completing; the "
     "fix is to project first and run over bounded extents, which succeeds."),
    ("Derive image-gradient products",
     "Slope on the THEMIS and Viking rasters is a DN gradient, not terrain slope \u2014 "
     "an edge and texture measure that highlights flow margins and crater rims. Label "
     "and use it as such."),
    ("Classify surface units",
     "Iso Cluster unsupervised classification, then Maximum Likelihood against training "
     "polygons. The workflow has already been rehearsed end to end on the Mercury "
     "MESSENGER basemap; apply it to the Mars stack."),
    ("Digitize landform vectors",
     "Lava flow margins, channel centerlines, and crater rims as three feature classes "
     "in the project geodatabase."),
    ("Build a real crater inventory",
     "The IAU nomenclature layers already loaded are a gazetteer of 1,113 named craters, "
     "not a crater-count database. Either digitize craters in the type area or import "
     "a published catalogue."),
    ("Produce the map layouts",
     "No layouts exist in the project yet. Global sheets plus detail panels for the "
     "two saved views: the Ius Chasma type area and the Jezero context map."),
]

SIGNIFICANCE = [
    ("The fusion is the contribution. The three source products are individually "
     "standard, but stacking them into one analysis raster in a common projection is "
     "what allows a unit to be described by morphology, thermal response, and slope "
     "simultaneously."),
    ("Thermal infrared responds to particle size and surface coherence, which visible "
     "albedo does not. Where Mars is dust-mantled, the THEMIS layer should recover flow "
     "boundaries the Viking colour mosaic cannot \u2014 a claim this project can measure."),
    ("Discriminating volcanic from fluvial channels is a live problem: Athabasca Valles "
     "was mapped as a fluvial outflow channel for decades before being reinterpreted as "
     "flood lava. Morphology plus thermal response addresses it."),
    ("The workflow transfers terrestrial remote sensing methods to a planetary target "
     "with no water column and no vegetation, and only ~6 mbar of CO\u2082 overhead "
     "\u2014 the signal is almost entirely surface physics."),
    ("The result is testable without any privileged data. Unit boundaries can be "
     "checked against the published USGS global geologic map of Mars, and crater-rim "
     "detection against the 141 IAU-named craters above 100 km already in the "
     "geodatabase. Both are free, and neither depends on imagery this project does "
     "not hold."),
]

# -------------------------------------------------------------------- METHODS

SPECTRUM = [
    ("Visible", "0.4 \u2013 0.7 \u00b5m",
     "Viking MDIM 2.1 colour. Morphology, albedo contrast, and shadow relief; the "
     "ferric absorption edge separates bright dust from darker basaltic surfaces."),
    ("Thermal IR", "6.8 \u2013 14.9 \u00b5m",
     "THEMIS Day IR. Daytime brightness temperature carries both morphology and "
     "silicate composition through the Si\u2013O reststrahlen bands."),
    ("Thermal IR (night)", "6.8 \u2013 14.9 \u00b5m",
     "THEMIS Night IR \u2014 not yet acquired. Paired with the day mosaic it yields "
     "thermal inertia, the single best dust-versus-bedrock discriminator from orbit."),
    ("Laser altimetry", "1064 nm (active)",
     "HRSC/MOLA blended DEM. Not passive imaging, but it supplies the slope, gradient, "
     "and drainage context that separates channels from albedo streaks."),
]

SPECTRUM_NOTES = [
    ("The martian atmosphere is ~6 mbar of CO\u2082. It is effectively transparent across "
     "the visible and near-infrared; the THEMIS bands are placed to avoid the strong "
     "15 \u00b5m CO\u2082 band."),
    ("Radar sounding (SHARAD, MARSIS) is deliberately excluded: it probes the "
     "subsurface rather than surface landforms, and has no global coverage at the "
     "resolution this project needs."),
]

# What is actually on disk, measured from the files themselves.
DATA_HELD = [
    ("Mars_MO_THEMIS-IR-Day_mosaic_global_100m_v12.tif", "Mars Odyssey THEMIS",
     "Thermal IR, 1 band, 8-bit", "100 m/px",
     "213,390 \u00d7 106,696 px; 22.14 of 22.77 billion valid (97.3% coverage); "
     "DN 1\u2013255, mean 125.7, \u03c3 34.4"),
    ("Mars_Viking_MDIM21_ClrMosaic_global_232m.tif", "Viking Orbiter",
     "Visible colour, 3 bands", "232 m/px",
     "92,160 \u00d7 46,080 px; band 1 DN 18\u2013207, mean 122.8, \u03c3 31.6"),
    ("Mars_HRSC_MOLA_BlendDEM_Global_200mp_v2.tif", "Mars Express / MGS",
     "Elevation, 1 band, 16-bit", "200 m/px",
     "106,694 \u00d7 53,347 px; \u22128,528 m to +21,226 m, mean \u2212720.5 m"),
    ("MARS_nomenclature_* (5 feature classes)", "IAU / USGS, March 2019",
     "Point and polygon gazetteer", "n/a",
     "141 craters >100 km; 972 craters <100 km; 126 albedo; 303 classical albedo; "
     "337 other"),
]

DATA_NEEDED = [
    ("THEMIS Night IR global mosaic", "100 m/px",
     "The highest-value missing dataset. Same source and format as the day mosaic "
     "already held; day\u2013night pairing is what turns brightness temperature into "
     "thermal inertia."),
    ("CTX mosaic tiles (bounded, not global)", "5\u20136 m/px",
     "Needed only over the type area, to resolve channel margins and craters below "
     "the ~1 km limit of the 100 m base. A global CTX mosaic is multi-terabyte and is "
     "explicitly out of scope."),
    ("A crater catalogue or digitized crater layer", "n/a",
     "The IAU layers are named features only. Crater statistics need either a published "
     "catalogue or craters digitized in the type area."),
]

BANDS = [
    ("THEMIS Day IR (v12 mosaic)", "6.8\u201314.9 \u00b5m",
     "The global morphology and composition base; the highest-resolution global layer "
     "held, at 100 m"),
    ("Viking MDIM 2.1 band 1 (red)", "\u2248 0.59 \u00b5m",
     "Best contrast between ferric dust and darker basaltic surfaces"),
    ("Viking MDIM 2.1 bands 1/2/3", "visible RGB",
     "Natural-colour context and unit boundary confirmation; currently displayed with "
     "a 0.5% min-max stretch"),
    ("HRSC/MOLA elevation", "n/a (altimetry)",
     "Absolute elevation; the vertical reference for every channel gradient measured"),
    ("Derived: slope, percent rise", "from elevation",
     "Terrain slope for channel gradients and flow-front steepness"),
    ("Derived: hillshade 225\u00b0/45\u00b0", "from elevation",
     "Shaded relief for visual interpretation of flow lobes and crater rims"),
    ("Derived: THEMIS DN gradient", "from thermal IR",
     "Edge and texture measure \u2014 highlights thermal boundaries at flow margins"),
    ("Derived: Viking DN gradient", "from visible",
     "Edge and texture measure \u2014 highlights albedo boundaries and crater rims"),
    ("Planned: THEMIS day \u2212 night", "6.8\u201314.9 \u00b5m",
     "Thermal inertia proxy; requires the night mosaic to be acquired"),
]

RESOLUTION = [
    ("Spatial",
     ["The global base is set by what is held: 100 m (THEMIS), 200 m (DEM), 232 m "
      "(Viking). The composite can be no finer than the coarsest input unless the "
      "others are resampled up.",
      "Working rule: roughly ten pixels across a feature are needed to map its margin "
      "reliably. At 100 m that means features \u2265 1 km \u2014 adequate for flow lobes "
      "and trunk valleys, but sub-kilometre tributaries will not resolve.",
      "That limit is the argument for bounded CTX windows at 5\u20136 m over the type "
      "area rather than a finer global sheet. No sub-metre imagery is held, so "
      "everything below about a kilometre is a stated limit of the mapping rather "
      "than something this project can resolve."]),
    ("Spectral",
     ["Held: one thermal band (THEMIS day) plus three visible bands (Viking). That is "
      "four bands total \u2014 enough to discriminate broad unit types, not enough to "
      "identify minerals.",
      "Adding THEMIS Night IR is the single highest-value spectral addition, because it "
      "converts the existing day mosaic into a thermophysical measurement rather than "
      "just an image.",
      "Mineral identification would require CRISM, which ArcGIS Pro cannot process as "
      "hyperspectral cubes. Out of scope; noted as a limitation rather than a plan."]),
    ("Radiometric",
     ["THEMIS and Viking are both 8-bit as distributed \u2014 adequate for morphology and "
      "for the visual mosaic, and the practical constraint on how finely surface units "
      "can be separated by DN alone.",
      "The DEM is the exception: it carries a real physical range of \u22128,528 m to "
      "+21,226 m, a relief of 29,754 m, which is where the quantitative measurements in "
      "this project will come from.",
      "Deriving true thermal inertia would require calibrated radiance rather than the "
      "8-bit mosaic. The day\u2013night difference approach is therefore a proxy, and "
      "will be described as one."]),
    ("Temporal",
     ["Martian landforms do not change on human timescales, so temporal resolution is "
      "not about change detection here.",
      "It matters diurnally: day and night IR of the same ground is the entire basis of "
      "the planned thermal inertia product.",
      "It matters seasonally in the source mosaics, which are already composited from "
      "many orbits selected for low dust opacity \u2014 an upstream decision inherited "
      "rather than controlled.",
      "The one genuinely time-varying layer is the Perseverance traverse feature "
      "service in the Jezero context map, which updates as the rover drives. It is a "
      "hosted web service rather than held data, so it needs a network connection."]),
]

# Recovered verbatim from the geodatabase lineage and GpMessages logs.
WORKFLOW_LOG = [
    ("Sep 8, 18:34", "Iso Cluster + ML Classify",
     "Mercury MESSENGER MDIS 166 m, 10 classes",
     "Succeeded \u2014 method rehearsal on another body"),
    ("Sep 9, 03:35", "Segment Mean Shift",
     "Spectral detail 20, spatial detail 20, min segment 5 px",
     "Succeeded"),
    ("Sep 9, 11:52", "Composite Bands", "Global extent",
     "Failed \u2014 cancelled after 47 min 57 s"),
    ("Sep 9, 12:43", "Composite Bands", "Retry",
     "Failed \u2014 cancelled after 1 min 41 s"),
    ("Sep 9, 12:44", "Composite Bands", "Retry",
     "Failed \u2014 cancelled after 1 h 14 min 51 s"),
    ("Sep 10, 19:44", "Slope \u2192 Slope_Mars_H1",
     "HRSC/MOLA DEM, percent rise, z-factor 1, planar",
     "Succeeded in 7 min 15 s \u2014 WARNING 000869 (Z units undefined)"),
    ("Sep 11, 12:03", "Slope \u2192 Slope_Mars_M1",
     "THEMIS Day IR, percent rise, z-factor 1, planar", "Succeeded"),
    ("Sep 11, 12:24", "Surface Parameters \u2192 Surface_Mars1",
     "Viking MDIM, slope, quadratic, 231.54 m fixed neighborhood",
     "Succeeded in 1 h 26 min 45 s"),
    ("Sep 11, 20:34", "Slope \u2192 Slope_Mars_V1",
     "Viking MDIM, percent rise, GPU then CPU",
     "Succeeded in 1 h 05 min 01 s \u2014 no compatible GPU detected, ran on CPU"),
    ("Sep 13, 03:03", "Hillshade \u2192 HillSha_Mars1",
     "HRSC/MOLA DEM, azimuth 225\u00b0, altitude 45\u00b0, shadows",
     "Succeeded in 11 min 42 s \u2014 WARNING 000869 (Z units undefined)"),
    ("Sep 13, 14:48", "Composite Bands", "Global extent, first input Slope_Mars_V1",
     "Did not complete \u2014 output registered, no raster data written"),
]

SCHEDULE = [
    ("1\u20132", "Aug 24 \u2013 Sep 4", "Scoping; target selection and mapping extent",
     "Target list"),
    ("3", "Sep 7 \u2013 Sep 11",
     "Global raster acquisition; first derivatives (slope, surface parameters)",
     "Three global rasters loaded"),
    ("4", "Sep 14 \u2013 Sep 18",
     "Project all layers to SimpleCylindrical_Mars; rebuild DEM derivatives with a "
     "valid z-factor", "Single-CRS layer stack"),
    ("5", "Sep 21 \u2013 Sep 25",
     "Composite Bands over bounded extents; acquire THEMIS Night IR",
     "Visible + IR composite raster"),
    ("6", "Sep 28 \u2013 Oct 2", "Day\u2013night thermal difference; training polygons",
     "Thermal inertia proxy"),
    ("7\u20138", "Oct 5 \u2013 Oct 16",
     "Iso Cluster and Maximum Likelihood classification of the Mars stack",
     "Interim presentation; classified raster"),
    ("9\u201310", "Oct 19 \u2013 Oct 30",
     "Digitize lava flow margins, channel centerlines, crater rims",
     "Landform feature classes"),
    ("11\u201312", "Nov 2 \u2013 Nov 13",
     "Crater inventory and size-frequency distributions in sample windows",
     "Crater database"),
    ("13", "Nov 16 \u2013 Nov 20", "Accuracy assessment against a published geologic map",
     "Confusion matrix"),
    ("14", "Nov 23 \u2013 Nov 27",
     "Map layouts and figure production (Thanksgiving week \u2014 front-load into "
     "week 13)", "Map sheets"),
    ("15", "Nov 30 \u2013 Dec 4", "Final presentation and written report",
     "Final deliverables"),
]

# ------------------------------------------------------------ EXPECTED RESULTS

HYPOTHESES = [
    ("H1",
     "In dust-mantled regions, the THEMIS Day IR layer will delineate volcanic flow "
     "boundaries that are not visible in the Viking colour mosaic, because thermal "
     "response depends on particle size and surface coherence while visible albedo is "
     "dominated by the dust veneer. Measured as mapped flow area from the IR layer "
     "versus the visible layer over the same extent."),
    ("H2",
     "Channel segments classed as fluvial will show shallower longitudinal gradients in "
     "the HRSC/MOLA DEM than segments classed as volcanic, and the two populations will "
     "separate when gradient is plotted against thermal DN."),
    ("H3",
     "A four-band composite (Viking R/G/B + THEMIS day) will produce more stable Iso "
     "Cluster classes than any single input, measured by how many of the requested "
     "classes survive with a meaningful pixel count."),
    ("H4",
     "Crater rim detection from the DN gradient products will recover a large majority "
     "of the 141 IAU-named craters larger than 100 km, giving an independent check on "
     "the gradient method before it is trusted on unnamed craters."),
]

QUESTIONS = [
    "Does projecting the DEM into SimpleCylindrical_Mars on a common central "
    "meridian, and re-running Slope with a valid z-factor, change the slope values "
    "enough to alter any interpretation?",
    "Once the three frames are harmonised onto one meridian, does Composite Bands "
    "complete at global scale, or is a tiled, bounded-extent workflow still the only "
    "viable path on this hardware?",
    "How much does the 8-bit depth of the THEMIS and Viking mosaics limit how finely "
    "surface units can be separated?",
    "Is the day-only THEMIS mosaic sufficient to separate flows from dust, or is the "
    "night mosaic genuinely required?",
    "At 100 m, how many orders of tributary in a valley network are recoverable, and "
    "where does the count saturate?",
    "The DN gradient reproduces Viking mosaic seams as false edges. Setting those "
    "aside, does it reveal any unit boundary the source image does not already "
    "show \u2014 or is its only real use as an edge mask?",
]

PROBLEMS = [
    ("Three coordinate frames in one project",
     "The HRSC/MOLA DEM and its derivatives sit in GCS_Mars_2000_Sphere (degrees); "
     "Viking and THEMIS both sit in SimpleCylindrical_Mars (metres) but on different "
     "central meridians \u2014 Viking on 0\u00b0, THEMIS on 180\u00b0, so the THEMIS grid runs "
     "0\u2013360\u00b0E while the other two run \u2212180\u2013180\u00b0E. A stack built without fixing "
     "that would be half a planet out and would misregister silently rather than "
     "fail. Mitigation: project everything to one frame and verify the meridian. "
     "This is the root cause of the next two problems."),
    ("Invalid z-factor on the terrain derivatives",
     "Both DEM-derived runs returned WARNING 000869 \u2014 vertical units in metres "
     "against horizontal units in degrees, with a default z-factor of 1. The existing "
     "Slope_Mars_H1 and HillSha_Mars1 are usable for display but not for measurement. "
     "Mitigation: rebuild them on the projected DEM."),
    ("Composite Bands does not complete at global scale",
     "Four attempts \u2014 47 min 57 s, 1 min 41 s and 1 h 14 min 51 s on 9 September, "
     "and a fourth on 13 September abandoned after 17 min 28 s \u2014 about 2 h 22 min in "
     "total. The tool logs record all four as cancelled by the user, "
     "not as tool errors. The visible + IR composite is the centrepiece of the project "
     "and it does not yet exist. Mitigation: project to a common CRS and cell size "
     "first, then run over bounded extents rather than the full globe."),
    ("Processing time is the schedule",
     "Measured runtimes on this machine: 7 min for slope on the 200 m DEM, 12 min for "
     "hillshade on the same DEM, 1 h 05 min for slope on the 232 m Viking mosaic, "
     "1 h 27 min for surface parameters. ArcGIS Pro reported no compatible GPU on the "
     "one run that requested one, so every tool runs on CPU. Mitigation: budget whole "
     "evenings for global runs and prototype on subsets."),
    ("The crater layers are a gazetteer, not an inventory",
     "The IAU nomenclature holds 141 craters above 100 km and 972 below \u2014 1,113 "
     "named features in total, against the hundreds of thousands of craters on Mars "
     "larger than 1 km. Crater size-frequency dating cannot be done from these layers. "
     "Mitigation: digitize craters in the type area or import a published catalogue."),
    ("\u201cSlope\u201d on imagery is not slope",
     "Slope_Mars_M1 and Slope_Mars_V1 were computed from THEMIS and Viking brightness "
     "values, not elevation. They are DN gradient \u2014 a legitimate edge and texture "
     "measure, but not terrain. Mitigation: rename and describe them as gradient "
     "products so no reader mistakes them for topography."),
    ("Thermal inertia is not yet possible",
     "Only the THEMIS day mosaic is held. Without the night mosaic there is no diurnal "
     "difference, and the dust-versus-bedrock argument rests on a single daytime image. "
     "Mitigation: acquire the night mosaic \u2014 same source and format, so this is an "
     "afternoon of downloading, not a redesign."),
    ("No pyramids on the global rasters",
     "None of the three source TIFFs carries overviews \u2014 one image level each, "
     "and no .ovr sidecar. Every redraw and every global tool pass therefore reads "
     "full resolution, including a 22.8-billion-pixel thermal mosaic. Mitigation: "
     "build pyramids once, before the next global run; it is the cheapest speed-up "
     "available on CPU-only hardware."),
    ("8-bit source depth",
     "Both image mosaics are 8-bit, so subtle DN differences between dusty units may "
     "simply not be recorded. Mitigation: treat classification boundaries as coarse and "
     "do not over-interpret single-DN differences."),
    ("Unsupervised classification may collapse",
     "Iso Cluster tends to return far fewer classes than requested when a large "
     "background or nodata region dominates the histogram. Mitigation: mask nodata "
     "first, run over bounded windows, and over-request classes."),
    ("No ground truth, and no sub-metre imagery",
     "Validation is against published interpretations, not field data, and the finest "
     "imagery held is 100 m. Nothing in this project can confirm a landform below "
     "about a kilometre. Mitigation: assess accuracy against the published USGS "
     "global geologic map and the IAU crater gazetteer, and state the resolution "
     "limit as a limit rather than working around it."),
]

# ------------------------------------------------------------------- INTERIM

GOALS_SHORT = [
    "Build one co-registered global visible + thermal-infrared mosaic of Mars in ArcGIS Pro.",
    "Map and classify lava flow units, fluvial channels, and impact craters from it.",
    "Test whether thermal infrared recovers flow boundaries that visible imagery misses "
    "under dust mantle.",
    "Assess accuracy against the published USGS global geologic map and the IAU "
    "crater gazetteer \u2014 the only independent references available.",
]

PROGRESS = [
    ("Scope, targets, and type-area selection", 90),
    ("Global raster acquisition \u2014 THEMIS, Viking, HRSC/MOLA", 100),
    ("Statistics and display stretches built (pyramids still not built)", 70),
    ("Grouped mosaic viewer assembled (Viking / IR / HRSC MOLA)", 100),
    ("DEM terrain derivatives \u2014 slope and hillshade built", 80),
    ("Image-gradient products from THEMIS and Viking", 70),
    ("Jezero context map \u2014 hosted rover services only, no held imagery", 20),
    ("Classification workflow \u2014 rehearsed on Mercury, not yet on Mars", 20),
    ("CRS harmonization to one projected frame", 15),
    ("Visible + infrared band composite", 5),
    ("Landform digitizing \u2014 flows, channels, crater rims", 0),
    ("Crater inventory beyond the IAU gazetteer", 0),
    ("Map layouts and figure production", 0),
    ("Written report and presentations", 25),
]

PRELIM = [
    ("Three global rasters loaded and characterized",
     "THEMIS Day IR v12 at 100 m (22.14 billion valid pixels, DN 1\u2013255, mean 125.7, "
     "\u03c3 34.4), Viking MDIM 2.1 colour at 232 m (92,160 \u00d7 46,080), and the "
     "HRSC/MOLA blended DEM at 200 m. 43.7 GB of source imagery, with statistics built "
     "on all three; pyramids are not built on any of them."),
    ("Global relief measured directly from the DEM",
     "Elevation ranges from \u22128,528 m to +21,226 m \u2014 a total relief of 29,754 m "
     "\u2014 with a mean of \u2212720.5 m and \u03c3 of 2,976 m. The extremes fall where "
     "expected, at the Hellas basin floor and the Olympus Mons summit, which is a first "
     "confirmation that the DEM is correctly georeferenced."),
    ("Terrain derivatives built",
     "Slope (percent rise) and hillshade (azimuth 225\u00b0, altitude 45\u00b0, shadows on) "
     "from the DEM, in 7 min 15 s and 11 min 42 s. Both currently carry WARNING 000869 "
     "and will be rebuilt on a projected DEM before any measurement is taken from them."),
    ("Gradient products built from both image mosaics",
     "Slope was run on the THEMIS and Viking rasters, giving DN gradient rather than "
     "terrain slope \u2014 an edge and texture measure. Surface Parameters was also run "
     "on the Viking mosaic with a quadratic fit over a 231.54 m fixed neighborhood, "
     "taking 1 h 26 min 45 s."),
    ("Classification workflow proven on another body",
     "Iso Cluster with 10 classes followed by Maximum Likelihood, plus Segment Mean "
     "Shift (spectral 20, spatial 20, minimum segment 5 px), ran successfully end to end "
     "on the Mercury MESSENGER MDIS basemap. The method is proven; it has not yet been "
     "applied to the Mars stack."),
    ("One type area set up",
     "The mosaic viewer is parked over western Valles Marineris (about 271\u2013286\u00b0E, "
     "6\u201313\u00b0S) \u2014 Ius Chasma and the Louros Valles tributaries on its south "
     "wall. A second map covers Jezero Crater, but it carries only hosted "
     "Perseverance rover services; no imagery of Jezero is held locally."),
]

PRELIM_NOTE = ("Every figure above was read from the project files themselves \u2014 raster "
               "statistics, geoprocessing lineage, and tool logs on Z:.")

ISSUES = [
    ("The project spans three coordinate frames",
     "The DEM and its derivatives are in GCS_Mars_2000_Sphere (degrees). Viking and "
     "THEMIS are both SimpleCylindrical_Mars in metres, but on central meridians 0\u00b0 "
     "and 180\u00b0 respectively \u2014 the THEMIS grid runs 0\u2013360\u00b0E, the other two "
     "\u2212180\u2013180\u00b0E. Read at face value the THEMIS window lands half a planet from "
     "the others. This is the root cause of both problems below. Fix: project "
     "everything into one frame and check the meridian, not just the units."),
    ("Terrain derivatives carry an invalid z-factor",
     "Both DEM runs returned WARNING 000869 \u2014 metres of elevation against degrees of "
     "horizontal distance, default z-factor 1. Slope_Mars_H1 and HillSha_Mars1 are fine "
     "for display, not for measurement. They will be rebuilt after projection."),
    ("Composite Bands failed four times globally, and now completes bounded",
     "Four attempts, not three: 47 min 57 s, 1 min 41 s and 1 h 14 min 51 s on "
     "9 September, then a fourth on 13 September abandoned after 17 min 28 s \u2014 about "
     "2 h 22 min in total, every one cancelled by the user rather than failing as a tool "
     "error. Bounding the extent resolves it: over the Ius Chasma type area the same "
     "composite completes in 8.8 s and yields a four-band stack with 100% of pixels valid "
     "in every band. The global composite itself still does not exist. "
     "Plan: project to a common CRS and cell size, then run over "
     "bounded extents instead of the full globe."),
    ("No GPU acceleration on this machine",
     "The Viking slope run requested GPU_THEN_CPU and logged 'No compatible GPU device "
     "has been detected', completing on CPU in 1 h 05 min. Every global run is CPU-bound, "
     "so processing time is effectively the project schedule."),
    ("Thermal inertia is blocked on a missing dataset",
     "Only the THEMIS day mosaic is held. The dust-versus-bedrock argument needs the "
     "night mosaic for a diurnal difference. Same source and format as the day mosaic, "
     "so this is a download rather than a redesign \u2014 but it has not been done."),
    ("The crater layers cannot support crater dating",
     "The IAU nomenclature gives 141 named craters above 100 km and 972 below. That is a "
     "gazetteer, not a crater-count inventory, and size-frequency dating cannot be done "
     "from it. Craters must be digitized in the type area or a catalogue imported."),
    ("Three dead raster references",
     "The Jezero HiRISE orthomosaic, the Mercury MESSENGER basemap, and the Enceladus "
     "DEM are still referenced by their maps, but none of those files is on the drive. "
     "The three global rasters are the whole of the held imagery. None of the three "
     "is needed for the plan as scoped; they should be removed so the project opens "
     "clean."),
    ("Housekeeping",
     "The nomenclature layers were imported more than once \u2014 14 feature classes "
     "where five would do (_2 and _3 duplicates of four of them, _2 of the fifth) "
     "\u2014 and no map layouts exist in the project yet. Neither blocks analysis, "
     "but both need clearing before the final deliverables."),
]

NEXT_STEPS = [
    "Project all three global rasters into one SimpleCylindrical_Mars frame at a "
    "common cell size and a common central meridian \u2014 THEMIS is on 180\u00b0 and the "
    "other two on 0\u00b0. This unblocks everything else.",
    "Rebuild Slope and Hillshade on the projected DEM so the z-factor is valid.",
    "Retry Composite Bands over a bounded extent rather than the globe, and confirm the "
    "four-band stack is usable before scaling up.",
    "Download the THEMIS Night IR global mosaic and difference it against the day mosaic.",
    "Apply the Mercury classification workflow \u2014 Iso Cluster then Maximum Likelihood "
    "\u2014 to the Mars composite.",
    "Rename the DN gradient products so they are not mistaken for terrain slope.",
    "Delete the duplicate _2 and _3 nomenclature imports.",
    "Build pyramids on the three global TIFFs \u2014 none of them has overviews, so "
    "every pass reads them at full resolution.",
    "Remove the three dead raster references (HiRISE, Mercury, Enceladus) so the "
    "project opens without broken layers.",
    "Start digitizing flow margins and channel centerlines in the Valles Marineris window.",
]
