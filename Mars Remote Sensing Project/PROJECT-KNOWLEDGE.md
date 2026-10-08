# Mars Global Mosaic — Project Knowledge Base

**Owner:** Logan Edwards · OCN 4704 Remote Sensing · Fall 2026 · Florida Tech
**File:** `Z:\Mars Remote Sensing Project\PROJECT-KNOWLEDGE.md`
**Started:** 2026-09-18 · **Last updated:** 2026-10-08 (**§39.4: the record, the plans, the build scripts, the project's layer and layout text and the GitHub page rewritten in an objective, impersonal voice**; **§39.3: the interim deck is now a living build in the Presentation 1 style with seven map slides; `verify_all.py` repaired after §37**; **§21.4 corrected: the interim deck was never blocked; the course template is now on `Z:` and both deck builders run (§39.2); §1: the interim is due mid-November; §39 added: the next-steps plan, `NEXT-STEPS.md`, and the interim plan, `INTERIM-PLAN.md`; §10: the USGS geologic map is named as a validation source but is not on disk**; **§38 added: layout 08, the mosaic itself at ±60° in four panels (visible, day IR, night IR, topography), each on its own map in the stack's native CRS**; 2026-10-07: **§37 added: everything that isn't Mars is out of the project, moved to `Z:\_removed_not_Mars\`, nothing deleted; §36.4: every classified raster's pixel values are now its class codes, the two GUI maps and `ius_sup_*` included**; earlier the same day, **§36: the ±60° landform maps recoded 0–3 → 1–4**; 2026-10-06: **§35 added: the project is backed up to a public GitHub repo, `loggger101/Mars_Terrestrial_GlobalMosaic_GIS-Data`, which is also its project page; §2.5's "no backup" is superseded**; 2026-10-03: **§32 added: the digitising map and layout 06 put the candidates and the empty digitising classes in Pro; basin layout 07; the classification smoothed 5 × 5, chosen by feature size**; earlier the same day, **§31 added: the fix. A corrected ±60° stack, a reclassification scored on held-out labels, every Mars map clipped to ±60°, a new map and layouts in the project**; 2026-10-02: **§30 added — the two GUI SVM classifications checked against the labelled polygons, the IAU craters and the DEM: the 29 Sep map follows its 4096-px processing tiles and scores below chance on its own training data; the 30 Sep map is mostly elevation**; earlier the same day, **§29.2 and §11 q23 — the two class schemas number lava tube and steep/windy hills the other way round; every labelled file follows the older one**; 2026-10-01: **§29 added — manual work in the Pro GUI, 2026-09-24 to 10-01, read from the logs and the gdb: hand training labels in four classes, a ±60° segmentation, two SVM classifications, the first two successful global Composite Bands runs, a deep-learning export — and `Landform_TrainingSamples_terrain` now holds the hand-drawn labels, which `make_typearea_supervised.py` would delete; §6, §8, §11, §13.2, §17.2, §27 reconciled**; 2026-09-19: **§28 added — the derived products move off the type area onto the mosaics' own grid; `build\grid60.py` is now the single definition of the ±60° extent, and the diurnal-contrast index exists at 15.2 bn px**; **§24 added — the day–night pair worked properly; calibrated thermal inertia is NOT derivable from the held 8-bit products, and the relative diurnal-contrast index that replaces it**; **§25 added — task 11 seeded with inferred channel candidates, and `Fill` caught flooding Ius Chasma 2,077 m deep**; earlier on 2026-09-18, a re-verification pass — most `[E]` items
promoted to `[V]`; Composite Bands attempt count corrected from three to four; laptop-vs-desktop
constraint added as §2.1; **final-deliverable date answered — 8 December 2026**; `Z:`
confirmed as the project's single home, §2.5; **§13 added — verified headless
capability, incl. working layout export**; **§14 added — deliverables read, four
defects found**; **§15 added — THEMIS Night IR acquired, verified and added to the project**; **§16 added —
analysis extent defined as ±60°**; **§17 added — audit suite repaired (12 dead paths) and
`verify_all.py` corrected from three Composite runs to four**; **§18 added — tasks 3 and 5
completed for the type area; the composite works**; **§19 added — task 7 run on Mars; the
IsoCluster→MLClassify two-step proven a no-op; task 11 scaffolded**; **§20 added — task 4
done for the type area, WARNING 000869 eliminated**; **§23 added — object-based classification; the Mercury segmentation parameters are
maximum-detail**; **§22 added — task 13 started, the project has
layouts**; **§21 added — audit round 2: q2/q8,
night-IR stretch fixed, defect 1 fixed at source, interim report rebuilt**; **§2.2 corrected — the SSD-copy recommendation
is withdrawn, the project stays on `Z:` and the real footprint is 250 GB, not 43.7 GB**)

This is the durable record of what is actually true about this project, kept so that no
deliverable ever has to be written from assumption again. It replaces guesswork, not judgment.

**How to read the confidence tags.** Every factual claim below carries one:

| Tag | Means |
|---|---|
| **[V]** | Verified directly by reading the project with `arcpy`/`gdal` on this machine — on 2026-09-18 unless the section says otherwise. |
| **[E]** | Established in an earlier session by reading file headers / gdb bytes. Not re-checked on 2026-09-18, but nothing contradicts it. |
| **[?]** | Open, conflicting, or assumed. Do not put in a deliverable without resolving it first. |

Additions to this file must be tagged. An untagged claim is worth nothing six weeks from now.

> ## ⚠ Run the heavy work on the DESKTOP, not the laptop
>
> **Noted 2026-09-18 on instruction.** The sessions producing this file have been running on
> the **laptop** (15.4 GB RAM, integrated graphics), which is not the machine for processing.
> The **desktop** is an i7-8700K / RTX 2080 Ti / 64 GB DDR4. Any global geoprocessing run,
> pyramid build, or Composite Bands retry **waits for it**. See §2.1 for what is and is not safe
> to do on the laptop.
>
> **But note §2.2:** `Z:` is a USB hard disk, and it — not either CPU — is the real bottleneck.
> **That is permanent:** the project lives on the external drive because it will outgrow both
> computers, so the I/O ceiling is a condition to plan around, not a problem to fix. Pyramids
> and internal-SSD *scratch* are the levers that remain.

---

## 1. What the project is

A global visible + thermal-infrared mosaic of Mars, used to map lava flows, fluvial channels,
and impact craters. **[E]**

The project's own title is **"Mars Global Mosaic"** — use it, don't invent one. **[E]**

> **Scope, decided 2026-09-18: the analysis extent is ±60° latitude, not the full globe.**
> Built from global products, but the co-registered stack spans ±60° — 86.6% of the surface —
> set by THEMIS night-time coverage. **See §16 before writing the word "global" anywhere.**

**Status — corrected 2026-09-18:** **Presentation 1 and the project prospectus are
BOTH delivered and presented.** Neither is a live deliverable; neither is worth correcting.
Remaining: the **interim** (report + presentation) and the **final**. **The interim is due mid-November 2026** (as stated 2026-10-08; exact day not given yet **[?]**), so it is the first deadline, about three weeks before the final. Plan: `INTERIM-PLAN.md` (§39). **[V]**

> **The standing directive, sharpened 2026-09-19: "just worry about getting data worked and
> laid out."** Work the DATA and the LAYOUTS — not the document prose. Focus on what will be
> done going forward, not on what has already been handed in. Errors found in the prospectus
> (§14.5) are only a lesson for the final — do not carry them forward, do not spend time
> repairing delivered documents.

**The final is due Tuesday 8 December 2026** — the date was given on 2026-09-18, which is
**81 days out**. **[V]** This is the schedule anchor: every desktop job in §11 has to fit
before it. Note the §8 run times are still not attributable to a machine, so plan that work
with slack rather than against those numbers.

---

## 2. How to work on this project

### 2.1 Which machine — this matters more than anything else in this section

**There are two machines. Check which one is in use before starting anything.**

| | **Laptop** (in use now) | **Desktop** (the processing machine) |
|---|---|---|
| Model | HP OmniBook 3 16-bu0xxx | — |
| CPU | Intel **Core Ultra 5 225U**, ~15 W U-series | Intel **i7-8700K**, 95 W desktop |
| Cores | 12 physical / 14 logical | 6 physical / 12 logical |
| RAM | **15.4 GB** (5.5 GB free) | **64 GB DDR4** |
| GPU | Intel integrated — none usable | **NVIDIA RTX 2080 Ti**, 11 GB |
| Internal disk | 477 GB NVMe, 346 GB free | — |

Laptop figures measured 2026-09-18 **[V]**; desktop figures as stated 2026-09-18.

**Be precise about *why* the desktop is the right machine, because the obvious reason is the
weakest one.** The i7-8700K is a 2017 six-core part. Against a modern 12-core low-power mobile
chip it wins on sustained clocks and, crucially, never thermally throttles — but in raw
multithreaded throughput the two are closer than "desktop vs laptop" suggests, and the laptop
actually has more threads. **The CPU is the least decisive of the differences.** What actually
matters:

1. **64 GB vs 15.4 GB of RAM — a 4× difference, and the laptop only has ~5.5 GB free.** This is
   the real constraint. A global geoprocessing job over a 22.8-billion-pixel raster has room to
   work on the desktop and does not on the laptop.
2. **A real GPU.** The RTX 2080 Ti (Turing, CUDA compute capability 7.5) is comfortably above
   what ArcGIS Pro's GPU-capable Surface tools ask for, so `GPU_THEN_CPU` should finally mean
   something — see §2.3.
3. **No thermal ceiling** on multi-hour runs.

### 2.2 The bottleneck is the drive — and it is permanent **[V]**

`Z:` is a **Seagate Backup Plus Slim — a portable 2.5-inch HDD connected over USB**, 1863 GB
total, **250 GB used and 1613 GB free**.

That is a spinning disk behind a USB bridge, and it is the slowest thing in this entire project.
The evidence is in the record: the full-resolution decimation reads (§8) moved THEMIS's 22.8 GB
in 204 s ≈ **112 MB/s**, which is exactly USB-3-attached-HDD sequential speed. **Those reads
were I/O-bound, not CPU-bound.** Upgrading the processor changes nothing about them.

> **Decided 2026-09-18 — the project stays on `Z:` and is not copied to internal disk.**
> Stated plainly: the project will outgrow what either computer can hold. This closes
> open question 9. **[V]**

**An earlier version of this section recommended the opposite, and it was wrong on its
numbers.** It costed the copy at "43.7 GB, about 7 minutes" — counting only the three source
GeoTIFFs and silently ignoring everything derived from them. **The real footprint is 250 GB**,
because `Mars Project.gdb` alone is **138 GB**: the F32 derivatives are far larger than the U8
imagery they came from (`Slope_Mars_M1` on the THEMIS grid is 213,390 × 106,696 × 4 bytes ≈
**91 GB** by itself). The laptop's 346 GB free would take today's 250 GB with almost nothing to
spare, and a completed Composite Bands (~68 GB) plus pyramids (~14 GB) would exhaust it.
**The constraint is correct and the old advice was an artefact of measuring the wrong thing.**

**So the I/O ceiling is a fixed condition of this project, not a problem to be solved.** Plan
around it:

- **Pyramids are now the single best available speed-up** (§11 q6) — they cut how many bytes
  cross the USB bus for every subsequent display and overview read. Previously ranked behind
  the SSD copy; with the copy off the table they are first. **Desktop job.**
- **Put geoprocessing scratch on internal SSD, not on `Z:`.** This does not conflict with the
  decision above — the *project* stays on `Z:`, but `arcpy.env.scratchWorkspace` and
  `arcpy.env.workspace` for intermediates do not have to. Temporary files are written and
  re-read many times over, and that traffic is the cheapest to move off the slow bus.
- **Confirm the drive is on a USB 3 port.** 112 MB/s says it currently is; a USB 2 port would
  cap it near 40 MB/s and quietly triple every run.
- **Keep caching decimated reads to `.npy`** (§9). Already the practice — it matters more now.
- **Never re-read a global when a cached array will do.**

**Open, and worth testing before the December deadline:** the four globals are uncompressed
and stored **one scanline per block** (§3, §9). On an I/O-bound pipeline with CPU to spare,
**internally tiled and LZW/DEFLATE-compressed copies could read materially faster** — fewer
bytes over the bus, and windowed reads that stop pulling whole 213,390-pixel rows. That trades
a plentiful resource for the scarce one. It would mean rewriting the rasters, so it is a
decision, not a tweak — see §11 q12. **[?]**

### 2.3 What the 2080 Ti does and does not buy **[?]**

ArcGIS Pro's GPU-capable Spatial Analyst surface tools (`Slope`, `Aspect`, `HillShade`,
`Viewshed2`) take an `analysis_target_device` parameter — this is the `GPU_THEN_CPU` flag
already present in the `Slope_Mars_V1` lineage (§7), which on the laptop fell straight back to
CPU with *"No compatible GPU device has been detected."* A Turing card should satisfy it.

**Verify rather than assume**, on the desktop, before planning around it: re-run a surface tool
with `GPU_THEN_CPU` and check whether the GP messages still report no compatible device. If the
message is gone, the GPU engaged.

Do not expect it everywhere. `IsoCluster`, `MLClassify`, `SegmentMeanShift` and `CompositeBands`
are **not** GPU tools — the Composite Bands retry (§8) will be CPU and I/O bound no matter what
card is installed.

**Safe on the laptop** — all cheap, all metadata-only:

- Opening the `.aprx` with `arcpy.mp`, listing maps/layers/broken sources
- Reading the gdb inventory, row counts, raster statistics, GP lineage, `GpMessages`
- Editing this file and the deliverables
- Rebuilding figures **from the cached `.npy` arrays**, and small windowed reads

**Wait for the desktop** — anything that touches every pixel:

- **Building pyramids** on the four globals (§3)
- **Retrying Composite Bands** (§8) — 2 h 22 m has already gone into this on unknown hardware
- Any global `Slope`, `SurfaceParameters`, `HillShade`, `IsoCluster` or segmentation run
- Full-resolution `GRIORA_Average` decimation — the ~11 min of reads behind the `.npy` caches

**`Z:` is an external drive, which is what makes this workable** — the project, the data and
this file all travel between the two machines. That is almost certainly why the project was
moved off `C:` in the first place (§8). Just remember the drive has to be mounted, and it is not
always (§2).

> **Open question, and it affects the schedule.** The run times in §8 were logged 9–13 Sep, but
> **nothing records which machine produced them.** If they were measured on the desktop, the
> laptop is slower still; if on the laptop, the desktop should beat them comfortably. Do not
> quote those timings as the project's processing budget until this is settled. **[?]**

### 2.4 Tooling

**The GUI is not drivable from a scripted session.** No desktop-control tools. Everything below
happens through `arcpy`, headlessly. **[V]**

**ArcGIS Pro 3.7**, arcpy reports `ProductName ArcGISPro`, Python **3.13.13**: **[V]**

```
C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe
```

`CheckExtension` returns **Available** for **3D**, **Spatial** and **ImageAnalyst**. **[V]**

**Do not use `propy.bat`.** It fails with `'C:\Program' is not recognized` — the batch file
doesn't quote its own install path. Call the `python.exe` above directly. **[V]**

**Close ArcGIS Pro before any write to the `.aprx`.** Reading a saved project while Pro has it
open is fine; saving over it is not. Check with `tasklist | findstr ArcGISPro` first.

**Two Pythons, neither does both jobs.** Re-tested 2026-09-18 — **[V]**:

| | ArcGIS Python **3.13.13** | System Python **3.14.6** |
|---|---|---|
| `osgeo.gdal` | **yes** | **no** |
| `pptx` | **no** | **yes** |
| numpy, matplotlib, PIL, lxml | yes | yes |

**GDAL and python-pptx are the only discriminators** — everything else is in both, so the rule
is simply: anything touching a raster runs on the ArcGIS interpreter, anything building a deck
runs on the system one.

**`Z:` is not always mounted.** It has been unavailable mid-session more than once. Check before
planning any run. **[E]**

**On the desktop the same drive mounts as `F:`, not `Z:`.** **[V]** — the gdb lineage of the GUI
 2026-09-29/30 runs writes to `F:\Mars Project\…` (§29.1). The `Z:\TypeArea` and `Z:\Global60`
junctions point at `Z:\Mars Project\…` (read 2026-10-01), and 50 of the 76 scripts in `build\`
contain `Z:` paths, so on the desktop neither will resolve unless the letter is changed to `Z:`
in Disk Management. Not tested there. **[?]**

---

### 2.5 `Z:` is the project's home — keep everything on it

**Stated 2026-09-18.** The `Z:` drive is the project: `Z:\Mars Project\` (the ArcGIS
project) and `Z:\Mars Remote Sensing Project\` (deliverables, this file, `build\`) should hold
**just about everything**, and new work belongs there rather than under `C:\Users\…` or
OneDrive. **Scripted sessions have a standing go-ahead to create and edit files on `Z:` for this project.**

This is also what already happened once by force: the old
`C:\Users\Loggg\OneDrive\Documents\ArcGIS\Projects\Mars Project` folder is gone, and three
referenced files did not survive the move (§3). Keeping one home is what prevents a repeat.

Two things this does **not** override:

- **Close ArcGIS Pro before writing to the `.aprx`** (§2.4). The permission is about *where*
  files may be written, not about clobbering an open project.
- **Destructive changes still get asked about** — deleting the duplicate nomenclature classes,
  clearing broken references, or overwriting a deliverable edited by hand. Open
  questions 4 and 5 stay open questions.

**This is now permanent, not a preference.** Confirmed 2026-09-18 that the project stays on
the external drive because its size will exceed what the project computers can hold — already 250 GB,
and growing (§2.2). There is no internal-disk copy and none is planned. `Z:` is the archive,
the working copy and the transport between machines, all at once.

> **Decided 2026-09-18: `Z:` is the only copy. No backup for now.** **[V]** Raised once and
> answered; it is decided and settled. Do not re-open it unasked — but do not pretend
> the exposure isn't there either, because it changes what "careful" means when working here.
>
> **Superseded 2026-10-06, on request: the irreplaceable part is now backed up to GitHub**
> (§35). The 112 MB below, the gdb's vectors and the small rasters are off the drive; the
> 300+ GB of derivatives still are not. The care rules below still apply.

**What that decision actually risks is asymmetric, and worth knowing before acting:**

| | Size | If the drive dies |
|---|---|---|
| `Mars Remote Sensing Project\` — this file, `build\` scripts, the decks and reports | **112 MB** | **Irreplaceable.** The project's own writing and code. Weeks of work. |
| The three source GeoTIFFs at `Z:\` root | 43.7 GB | Re-downloadable from USGS/NASA. Slow, not lost. |
| `Mars Project.gdb` — the F32 derivatives | 138 GB | Re-computable, but at many hours of desktop time (§8). |

**So the 112 MB is the part that matters and the 250 GB is mostly why there's no backup.**
That asymmetry is the thing to remember: the irreplaceable half would fit on anything.

**Practical consequences while this stands — these are about care, not backup:**

- **Prefer additive writes.** Write new files rather than overwriting good ones; there is no
  second copy to restore from and no version history.
- **Never delete from `Z:` without asking**, including the duplicate nomenclature classes
  (§11 q4) and the broken references (q5). Both stay open questions for exactly this reason.
- **Close Pro before writing the `.aprx`** (§2.4). A half-written project file on a
  single-copy drive is the worst case available.
- **The 69 GB in `Z:\$RECYCLE.BIN`** (measured 2026-09-18) is 4% of the drive and holds
  something large that was deleted — plausibly a failed Composite Bands output. Emptying it is a manual
  step, not a scripted one. Worth raising if space ever gets tight; it is not tight now
  (1613 GB free).

---

## 3. The data actually held

**Four** global GeoTIFFs at `Z:\` root, **~58 GB** together. Three were the original holding;
**THEMIS Night IR was added 2026-09-18** (§15). A recursive search of `Z:` for `.tif` / `.img`
/ `.jp2` returns exactly these four at the root. **[V]**

> Derived type-area rasters also now exist in `Z:\Mars Project\TypeArea\` (§18–20). They are
> products, not source imagery, and are not counted here.

| File | Size | Dimensions | Bands | Type | Cell | CRS | Central meridian | NoData |
|---|---|---|---|---|---|---|---|---|
| `Mars_Viking_MDIM21_ClrMosaic_global_232m.tif` | 11.87 GB | 92,160 × 46,080 | 3 | U8 | 231.542 m | `SimpleCylindrical_Mars` | **0°** | **0.0** |
| `Mars_MO_THEMIS-IR-Day_mosaic_global_100m_v12.tif` | 21.21 GB | 213,390 × 106,696 | 1 | U8 | 100 m | `SimpleCylindrical_Mars` | **180°** | **0.0** |
| `Mars_HRSC_MOLA_BlendDEM_Global_200mp_v2.tif` | 10.60 GB | 106,694 × 53,347 | 1 | S16 | 0.00337412° | `GCS_Mars_2000_Sphere` | geographic | **−32768** |
| `Mars_MO_THEMIS-IR-Night_mosaic_60N60S_100m_v14.tif` | 14.14 GB | 213,388 × 71,130 | 1 | U8 | 100 m | `SimpleCylindrical_Mars` | **180°** | **0.0** |

All dimensions, cell sizes, CRS, central meridians and NoData values above: **[V]**

**Pyramids are not built on any of the four.** Confirmed independently: no `.ovr` sidecar and
GDAL reports `GetOverviewCount() == 0` for every band of every file, **THEMIS Night IR
included** (checked 2026-09-18). Statistics *are* built on all four. This remains the cheapest
available speed-up. **[V]**

**All four are uncompressed, BAND-interleaved, and stored one scanline per block**
(`block = width × 1`) — Viking 92,160×1, Day IR 213,390×1, DEM 106,694×1, Night IR
213,388×1. **[V]** See §9 for what that means when reading windows.

> The night mosaic therefore inherits **every** performance property of the other three: the
> pyramid job (§11 q6) is **four files, not three**, and the tiling/compression question
> (q12) applies to it equally.

### Statistics — all values below read from the `.tif.aux.xml` sidecars and GDAL 2026-09-18 **[V]**

**DEM** (`STATISTICS_*`, skip factor 1 — i.e. computed over every pixel):

| min | max | mean | stddev | median | valid px |
|---|---|---|---|---|---|
| −8528 m | +21226 m | −720.54254 | 2976.46528 | −360.235 | 5,691,764,861 |

Total DEM pixels = 106,694 × 53,347 = 5,691,804,818, so **valid coverage is 99.9993%** — the
DEM is essentially complete. NoData is −32768.

**THEMIS Day IR:**

| min | max | mean | stddev | median | valid px |
|---|---|---|---|---|---|
| **1** | 255 | 125.74638 | 34.36466 | 125 | 22,143,880,259 |

Total = 213,390 × 106,696 = 22,767,859,440, so **valid coverage is 97.26%** — this confirms the
"22.77 bn total / 22.14 bn valid / 97.3%" figure exactly. **Note the minimum DN is 1, not 0**,
because 0 is reserved as NoData; the valid data range is 1–255.

**Viking MDIM, all three bands** (each band's valid count = 4,246,732,800 = 92,160 × 46,080,
the *full* pixel count):

| Band | min | max | mean | stddev |
|---|---|---|---|---|
| 1 | 18 | **207** | 122.83502 | 31.58019 |
| 2 | 18 | 231 | 97.26186 | 32.86124 |
| 3 | 18 | 255 | 95.77282 | 35.51307 |

**The Viking mosaic has no fill at all** — every pixel counts as valid and the minimum is 18, so
despite NoData being declared as 0 there are no 0 pixels anywhere. The band-1 maximum of **207
is a real clip**, visible as a histogram spike (bands 2 and 3 reach 231 and 255).

### Not held

CTX, CRISM, and any crater-count catalogue are **not on disk**. **[V]**

> **THEMIS Night IR was in this list until 2026-09-18 and no longer is** — it was acquired and
> added to the project (§15). Coverage is ±60°, not global, which is what set the project's
> analysis extent (§16).

**But CTX is reachable online** — `Map2` carries `Global CTX Mosaic of Mars (V01)` as a hosted
Esri service (`astro.arcgis.com/.../OnMars/CTX1/MapServer`). Not local, but usable for
validation with a network connection. **[V]**

### Dead references — do not try to re-acquire

Three files are still referenced by maps but are gone from both C: and Z:, and they are not coming
back: the **Jezero HiRISE orthomosaic**, the **Mercury MESSENGER basemap**, and the
**Enceladus DEM**. The old `C:\Users\Loggg\OneDrive\Documents\ArcGIS\Projects\Mars Project`
folder no longer exists — checked directly, it is gone — so they did not survive the move to
the external drive. **[V]**

---

## 4. The trap that has cost the most time

**The project spans three coordinate frames, not two.** **[V]**

1. THEMIS Day IR is on **central meridian 180°**, grid running 0–360°E.
2. Viking MDIM is on **central meridian 0°**, grid running −180–180°E.
3. The DEM sits in **`GCS_Mars_2000_Sphere`** — degrees, not metres — while THEMIS and Viking
   are in `SimpleCylindrical_Mars`, metres.

Consequences, all observed:

- **A THEMIS window read at face value lands half a planet away.** Always read
  `GetProjParm('Central_Meridian')` per file before windowing. **[E]**
- This is the likely reason **Composite Bands never completed** — it would misregister
  silently rather than fail. Still an inference, not a proven cause: the logs record only
  user cancellation, never a CRS error. **[?]**
- The metre/degree split is why every DEM derivative returned **WARNING 000869** with a
  default z-factor of 1. **[V]** — two logged runs carry it verbatim:
  *"WARNING 000869: Z factor: The Z units of the output geographical spatial reference are
  undefined. A default Z factor of 1 was used."* (10 Sep, 7 min 15 s; and 13 Sep, 11 min 42 s).

**To reproduce the meridian bug deliberately** (for a figure): read the window with its
longitudes shifted +180°. **[E]**

---

## 5. Project structure

Read through `arcpy.mp` on 2026-09-18. All of §5 is **[V]**.

- **11 maps, 0 layouts.**
- `defaultGeodatabase` = `Z:\Mars Project\Mars Project.gdb`
- `homeFolder` = `Z:\Mars Project`

**Zero layouts meant there was no print/export composition anywhere in the project.** Every
figure in the deliverables was matplotlib off the raw rasters. **Superseded 2026-09-18:
three layouts now exist on a new `Ius Chasma Type Area` map — see §22.** Any "export the map" request
means building a layout from scratch first.

**The two working maps:**

| Map | Layers | Spatial reference |
|---|---|---|
| `Mars High-Resolution Mosaic Viewer` | 9 | `Mars_2000_(Sphere)` |
| `Map3` | 9 (the same set) | `SimpleCylindrical_Mars` |

Both carry the Viking / HRSC-MOLA / IR groups. The other nine maps are singles and scratch.

**Map names are not unique and case collides.** Two maps named `Mars` — one
`Mars_2000_(Sphere)`, one `GCS_Mars_2000_Sphere` — plus a third named `mars`. **Never select a
map by name alone in a script.** Index, or match on spatial reference as well.

**`listBrokenDataSources()` returns 4, not 3** — three unique missing files, but the Enceladus
DEM is broken in *two* maps (`Map1` and `Enceladus`). Count instances, not files, when reporting.

**~~Oddity:~~ solved 2026-09-18.** `Jezero_CTX_BlockAdj_dd_Clip` is a **`CIMTiledServiceLayer`**
— a hosted ArcGIS Online tile service, not a local dataset. `dataSource` is not merely empty,
it **raises** *"The attribute 'dataSource' is not supported on this instance of Layer"*; whatever
read it first turned that exception into an empty string. It is not broken because there is
nothing local to break.

**It is also a duplicate.** Its service URL is
`tiles.arcgis.com/tiles/Lmcs3aS4AodOs221/arcgis/rest/services/Jezero_Crater_Clipped` —
**the same service as the `Jezero Crater Clipped` layer beside it**, under a different display
name. Nothing was stripped or lost. **[V]**

**The Perseverance map still works without local files** — rover position/path/waypoints,
Ingenuity position and Jezero Crater Clipped are all hosted ArcGIS Online services. Keep it as a
context map; it needs a network connection. **[E]**

---

## 6. Geodatabase inventory

Read with `arcpy` 2026-09-18. This is authoritative — it supersedes any byte-walk estimate.
All of §6 is **[V]**.

### Feature classes — 30 present (22 on 2026-09-18, 26 on 2026-10-01; see the rows below, §29, §31)

The IAU nomenclature layers were imported two and three times over as `_2` / `_3` duplicates,
plus two empty scratch classes. All are `Mars_2000_(Sphere)`, all Point except as noted.

| Dataset | Rows | Copies |
|---|---|---|
| `MARS_nomenclature_craters_lt100km_March2019` | **972** | ×3 |
| `MARS_nomenclature_misc_March2019` | 337 | ×3 |
| `MARS_nomenclature_classicalbedo_March2019` | 303 | ×2 |
| `MARS_nomenclature_craters_gt100km_March2019` | **141** | ×3 |
| `MARS_nomenclature_albedo_March2019` | 126 | ×3 |
| `Line` (Polyline), `Point` | 0 | empty scratch |

**Added 2026-09-18** (§19.4) — empty scaffolding for task 11, in
`Mars_Equidistant_Cylindrical_CM180`, not `Mars_2000_(Sphere)` like the rest:

| Dataset | Geometry | Rows |
|---|---|---|
| `Landform_LavaFlowMargins` | Polyline | 0 |
| `Landform_ChannelCenterlines` | Polyline | 0 |
| `Landform_CraterRims` | Polygon | 0 |

**Added 2026-09-19** (§25) — the only populated non-nomenclature class, and the only one
holding **inferred** geometry:

| Dataset | Geometry | Rows |
|---|---|---|
| `Landform_ChannelCandidates_auto` | Polyline | **2,610** |
| `Landform_CraterCandidates_auto` (§26) | Polygon | **1,685** |
| `Landform_TrainingSamples_terrain` | Polygon | ~~1,604~~ **512 since 2026-09-30 — now the hand-drawn labels, §29.3** |

**Read 2026-10-01** (§28, §29) — four more, three of them scripted ±60° work that this table had
not been reconciled with, one manual: **[V]**

| Dataset | Geometry | Rows | Made by |
|---|---|---|---|
| `Landform_BasinCandidates_auto_60` | Point | 5,144 | §28.11, coarse basin pass |
| `Landform_ChannelCandidates_auto_60_smoke` | Polyline | 5,245 | §28.11 smoke tile |
| `Landform_CraterCandidates_auto_60_smoke` | Point | 2,939 | §28.11 smoke tile |
| `TrainingSamples_202609290009589587982` | Polygon | 455 | **manual (GUI)**, 2026-09-29 (§29.2) |
| `Analysis_Extent_60` | Polygon | 1 | §31, `make_global60_classification.py`: the ±60° clip shape |
| `Landform_TrainingSamples_terrain_60_train` | Polygon | 329 | §31.3, the hand-drawn labels clipped and split |
| `Landform_TrainingSamples_terrain_60_test` | Polygon | 183 | §31.3, held out |
| `Check_Tiles_4096px_60` | Polygon | 954 | §31.1, `make_global60_maps.py`: the §30.2 tile grid |

> Both are deliberately **not** `Landform_ChannelCenterlines` / `Landform_CraterRims` — machine
> candidates must not be mixed into the manual digitising classes. Every row carries
> `Confidence='inferred'`. Deleting either costs nothing.

**No tables.**

The crater counts confirm what the deliverables already claim: **141 craters >100 km, 972
<100 km.** Note these are a **gazetteer**, not a crater inventory — they are named features,
not a complete population. Do not present them as a crater count.

The duplicates are pure clutter and safe to delete once approved.

### Rasters — 14 rasters on 2026-10-01 (8 on 2026-09-18; six added in the GUI, last rows and §29)

| Raster | Dimensions | Type | Grid | Stats (min/max/mean) |
|---|---|---|---|---|
| `Slope_Mars_H1` | 106,694 × 53,347 | F32 | DEM, degrees | 0 / 400.13 / 1.664 |
| `Slope_Mars_M1` | 213,390 × 106,696 | F32 | THEMIS, m, CM 180 | 0 / 141.99 / 7.274 |
| `Slope_Mars_V1` | 92,160 × 46,080 | F32 | Viking, m, CM 0 | 0 / 45.63 / 1.881 |
| `Surface_Mars1` | 92,160 × 46,080 | F32 | Viking, m, CM 0 | 0 / 4223.06 / 2.472 |
| `HillSha_Mars1` | 106,694 × 53,347 | U8 | DEM, degrees | 0 / 183 / 131.40 |
| `Segmented_202609081925347487376` | 106,694 × 53,347 | U8 ×3 | DEM, degrees | 62 / 251 / 183.62 |
| `…_interIndex` | 106,694 × 53,347 | S32 | DEM, degrees | 0 / 65474 / 1320.97 |
| `Mercury_MESSEN_IsoClusterUns` | 92,160 × 46,080 | S8 | Mercury, m | 1 / 10 / 5.045 |
| `Mars_MO_THEMIS_CompositeBand` | 213,388 × 71,130 | ×2 | night grid, CM 180 | GUI, 09-24 (§29) |
| `Segmented_202609290011302066080` | 213,388 × 71,130 | ×3 | night grid, CM 180 | GUI, 09-29 (§29) |
| `…_interIndex` | 213,388 × 71,130 | ×1 | night grid, CM 180 | GUI, 09-29 |
| `Classified_202609292109007048151` | 213,388 × 71,130 | ×1 | night grid, CM 180 | GUI, SVM, 4 classes |
| `CompositeBand` | 92,160 × 46,080 | ×7 | **Viking, CM 0** | GUI, 09-30 (§29.4) |
| `Classified_202609300147338582853` | 92,160 × 46,080 | ×1 | Viking, CM 0 | GUI, SVM, 4 classes |

The six rows above were read with `arcpy.Raster` on 2026-10-01 **[V]**; types and statistics not
read.

---

## 7. Derived products and what is wrong with each

### Every slope layer is PERCENT_RISE, not degrees **[V]**

The lineage is explicit:

```
Slope <dem>     -> Slope_Mars_H1   PERCENT_RISE 1 PLANAR METER CPU_ONLY
Slope <themis>  -> Slope_Mars_M1   PERCENT_RISE 1 PLANAR METER CPU_ONLY
Slope <viking>  -> Slope_Mars_V1   PERCENT_RISE 1 PLANAR METER GPU_THEN_CPU
SurfaceParameters <viking> -> Surface_Mars1  SLOPE QUADRATIC "231.5417872 Meters"
                              FIXED_NEIGHBORHOOD METER PERCENT_RISE
                              GEODESIC_AZIMUTHS NORTH_POLE_ASPECT
```

The stored statistics agree with percent, not degrees: H1 reaches 400.13 (= 400% rise = 76°,
entirely sane) and M1 reaches 141.99, which is impossible in degrees.

> **Never describe these layers as degrees in a deliverable.** A figure of
> "0–90°, mean 89.74° (saturated)" was previously attached to them in project notes. That
> pairing is wrong — it must have come from a separate windowed recomputation in degrees.
> The underlying z-factor defect is real; it just cannot be quoted in degrees off these rasters.

`Slope_Mars_V1` was submitted `GPU_THEN_CPU` while the others were `CPU_ONLY`. There is no
compatible GPU on this machine, so it would have fallen back. **[V]**

### `Slope_Mars_M1` and `Slope_Mars_V1` are not terrain slope

They are `Slope` run on **imagery**, so they are DN gradient. They have already been renamed in the
maps to **`Gradient_Mars_V1`** and **`Gradient_Mars_M1`**, which is correct — but the underlying
gdb dataset names still say `Slope_*`. `Slope_Mars_H1` (DEM-derived) keeps its name correctly.
**[V]**

`Surface_Mars1` has the same problem: `SurfaceParameters SLOPE` run on the Viking **imagery**,
not the DEM. Its max of 4223 is the tell. **[V]**

### `HillSha_Mars1` carries the same defect as the slopes

`HillShade <dem> -> HillSha_Mars1 225 45 SHADOWS 1` — azimuth 225, altitude 45, shadows on,
**z-factor 1 on a degree grid**. Compromised in exactly the same way as the slope layers. **[V]**

### An undocumented segmentation run

`SegmentMeanShift` (spectral detail 20, spatial detail 20, min segment size 5) on **2026-09-08**
produced `Segmented_202609081925347487376` and its `_interIndex` — **65,474 segments** on the
DEM grid. This is the day before the Composite Bands attempts. **Nothing in any deliverable
mentions it.** Decide whether it belongs in the record. **[V]**

### The Mercury Iso Cluster rehearsal succeeded

`IsoClusterUnsupervisedClassification <mercury> 10 <out> 20 10` — 10 classes, min class size 20,
sample interval 10. **10 requested, 10 delivered**, every class populated: **[V]**

```
class  1   6.78%      class  6  17.87%
class  2   6.17%      class  7  14.55%
class  3   8.92%      class  8   6.87%
class  4  15.45%      class  9   2.69%
class  5  19.69%      class 10   1.01%
```

`MLClassify` was then run with the saved `.gsg` and EQUAL priors to the **same output name**.

> **Corrected 2026-09-18 (§19.2): that second step changed nothing.**
> `IsoClusterUnsupervisedClassification` already runs IsoCluster *then* MLClassify internally,
> so re-running MLClassify with its own signature file and EQUAL priors reproduces the identical
> raster — proven by matching checksums on the Mars run. **This raster is not "the
> maximum-likelihood result as distinct from the ISODATA assignment." They are the same
> thing.** **[V]**

> **Do not carry the "2 classes per 3 requested" collapse rule to this project.** That is a
> property of a specific WorldView scene from other coursework (87% zero fill, spectrally
> tight ocean). The Mercury basemap has neither problem, and nothing collapsed. Check fill
> fraction and class dominance before ever warning about cluster collapse.

---

## 8. Processing history

### CORRECTION: Composite Bands was attempted **four** times, not three **[V]**

Read from the eight `GpMessages\` XML records on 2026-09-18. The full logged history — every
GP operation the project kept a message file for:

| # | Started | Ended | Elapsed | Result | Notes |
|---|---|---|---|---|---|
| 1 | 09 Sep 11:52:35 | 12:40:32 | **47 m 57 s** | FAILED | CompositeBands, `Operation cancelled by user` |
| 2 | 09 Sep 12:43:02 | 12:44:44 | **1 m 41 s** | FAILED | CompositeBands, cancelled |
| 3 | 09 Sep 12:44:51 | 13:59:43 | **1 h 14 m 51 s** | FAILED | CompositeBands, cancelled |
| 4 | 10 Sep 19:44:24 | 19:51:39 | **7 m 15 s** | ok | **WARNING 000869** — Slope on the DEM |
| 5 | 11 Sep 12:24:33 | 13:51:19 | **1 h 26 m 45 s** | ok | SurfaceParameters on Viking |
| 6 | 11 Sep 20:34:10 | 21:39:12 | **1 h 05 m 01 s** | ok | *"No compatible GPU device has been detected."* |
| 7 | 13 Sep 03:03:23 | 03:15:06 | **11 m 42 s** | ok | **WARNING 000869** — DEM derivative, likely HillShade |
| 8 | **13 Sep 14:30:59** | **14:48:27** | **17 m 28 s** | FAILED | **CompositeBands, cancelled — the fourth attempt** |
| 9 | 24 Sep 15:57:04 | 16:07:05 | 10 m 01 s | FAILED | CompositeBands, cancelled — **a fifth attempt** (§29) |
| 10 | 24 Sep 16:07:30 | 18:59:55 | 2 h 52 m 25 s | ok | CompositeBands night + day IR — **the first global composite to succeed** (§29) |
| 11 | 29 Sep 22:08:58 | 30 Sep 01:19:39 | 3 h 10 m 40 s | ok | CompositeBands, 7 bands on the Viking grid (§29.4) |

> **Rows 9–11 were added 2026-10-01 from the three newer `GpMessages\` files.** **[V]** Their only
> message besides start and end is "Building Pyramids..."; the gdb lineage ends each composite
> within 3 s of the log's end, so each log is the composite run itself, pyramids included. **The
> count below is "four" as of 13 Sep; there are now five cancelled attempts and two successes.**

**Attempt 4 was four days after the other three**, on 13 Sep, and earlier notes missed it.
All four log the same sequence: `A raster error has occurred` → `Operation cancelled by user`
→ `Failed to execute (CompositeBands)`. So "failed" still overstates it — every one was
cancelled, not errored — but the problem was revisited once more than the record showed.

**Total time spent on Composite Bands: about 2 h 22 m**, all of it discarded.

> **A trap worth naming.** A previous session invented a phantom fourth Composite Bands run by
> regex-scraping deleted rows out of `.gdbtable` (see §9), and that error was correctly
> retracted — which then hardened "three" into the record. But there really *were* four
> attempts; the GpMessages log is independent of the gdb and shows it plainly. **A retracted
> claim being wrong for the right reason does not make its opposite true.** Re-derive from the
> authoritative source rather than from the correction.

**Run 6 is the direct confirmation that there is no usable GPU** — `Slope_Mars_V1` was
submitted `GPU_THEN_CPU` (§7) and the log answers *"No compatible GPU device has been
detected."* It then took 1 h 05 m on CPU. **[V]**

**The lineage dates the drive move precisely.** The Mercury, Segment, `Slope_Mars_H1`,
`Slope_Mars_M1` and `SurfaceParameters` runs all wrote to
`C:\Users\Loggg\OneDrive\Documents\ArcGIS\Projects\Mars Project\`; `Slope_Mars_V1` and
`HillSha_Mars1` wrote to `Z:\Mars Project\`. **Those last two are the only post-move outputs.**
**[V]**

### Measured run times — effectively the project schedule, but see the caveat

> **Which machine ran these is not recorded** (§2.1). Treat them as order-of-magnitude until
> that is settled, not as a budget. **[?]**

No compatible GPU — confirmed in the log, not assumed — so every global run is CPU-bound:

- Slope on the 200 m DEM — **7 min 15 s** **[V]**
- Slope on the Viking mosaic — **1 h 05 min 01 s** **[V]**
- Surface Parameters on the Viking mosaic — **1 h 26 min 45 s** **[V]**
- A DEM derivative on 13 Sep (likely HillShade) — **11 min 42 s** **[V]**
- Full-resolution averaged decimation (`GRIORA_Average`): Viking 355 s, THEMIS 204 s, DEM 96 s
  — **[E]**, measured in an earlier session; re-verifying would mean re-running them, so this
  is the one timing left unconfirmed.

---

## 9. Reading the data without opening Pro

**Prefer `arcpy`.** `arcpy.mp.ArcGISProject(r"Z:\Mars Project\Mars Project.aprx")` opens in
seconds with Pro closed and gives `listMaps()`, `listLayers()`, `listBrokenDataSources()`,
`listLayouts()`, and per-layer `dataSource` / `isBroken` / `isGroupLayer`. **[V]**

**The byte-level route is the fallback** — for when `Z:` is unmounted, and for the one question
arcpy cannot answer: what was **deleted**.

- The `.aprx` is a **zip of CIM JSON** — layer names, data connections, renderers, saved extents.
- GP lineage with full tool parameters and timestamps: `Mars Project.gdb\a00000004.gdbtable`,
  decode latin-1, regex for `<Process ...>`. **[V]** — this is how §7 was resolved.
- Elapsed times and warnings: the `GpMessages\` XML files.
- Raster statistics: the `.tif.aux.xml` sidecars.
- Row counts: byte offset 4 of each `.gdbtable`.

> **Never scrape `.gdbtable` bytes with a plain regex for *inventory*.** Free space holds
> deleted rows, and dead datasets get reported as live — a phantom Composite Bands run was
> once invented exactly this way, out of a deleted `Slope_Mars_V1_CompositeBands` item. Walk the
> matching `.gdbtablx`: 16-byte header, then one 5-byte little-endian entry per ObjectID,
> value 0 = deleted, non-zero = row offset. **[E]**
>
> Note the coincidence trap this set up — **there genuinely were four Composite Bands attempts**
> (§8), just not for the reason the bad regex suggested. Two independent sources, one unreliable
> and one authoritative, happened to point at the same number.

Regex over `<Process ...>` in `a00000004.gdbtable` is still fine for **lineage** — tool
parameters and flags — because a stale record there is a record of something that really ran.
It is *inventory* questions ("does this dataset exist?") that the free-space problem ruins.

Figures read from the rasters directly: the TIFFs are **stripped one scanline per block** —
GDAL reports `block = width × 1` for all three, uncompressed and BAND-interleaved **[V]** — so a
windowed read still pulls whole rows, and narrowing a window horizontally buys nothing. Windows
take seconds; a global decimation ~45 s. Cache to `.npy`. **`ReadAsArray` decimates by nearest
neighbour unless told otherwise** — at 1:71 that turns THEMIS into aliased speckle and Syrtis
Major vanishes. Pass `resample_alg=gdal.GRIORA_Average`. **[E]**

---

## 10. Validation

There is **no ground truth and no sub-metre imagery** for this project. Validation rests on:

- the published **USGS global geologic map** (**not on disk**, checked 2026-10-08: no geologic unit layer in the gdb or on `Z:`. Acquiring it is §39's D5(a)) **[V]**
- the **IAU crater gazetteer** already in the gdb (§6)
- the hosted **CTX mosaic** service (§3), network permitting

The deliverables already say so. Keep it that way. **[E]**

---

## 11. Open questions

1. ~~Final-deliverable date is unknown.~~ **Answered 2026-09-18: the final is due
   Tuesday 8 December 2026** (§1). **[V]**
2. ~~`Jezero_CTX_BlockAdj_dd_Clip` — empty dataSource, not flagged broken.~~ **Answered
   2026-09-18: a hosted tile service, and a duplicate of `Jezero Crater Clipped`** (§5).
   Nothing wrong with it. **[V]**
3. ~~Does the `SegmentMeanShift` run belong in the record?~~ **Answered 2026-09-18: it is
   already in the interim report — but attributed to Mercury when it actually ran on the
   Mars DEM** (§14.5). Not a dead end; a misattribution to correct. **[V]**
4. Should the 10 duplicate nomenclature feature classes be deleted? **[?]**
5. Broken references (§3) — clear them out of the maps? Needs a write, so Pro must be closed. **Answered 2026-10-07 for the non-Mars ones (§37):** the Enceladus and Mercury maps are out of the project. The one broken link left is the Jezero HiRISE mosaic, which is Mars and stays. **[V]**
6. **Build pyramids on the four globals?** With the SSD copy ruled out (§2.2) this is now the
   **best speed-up available to the project**, not merely the cheapest. **Desktop job.** **[?]**
7. **Run Composite Bands / CRS harmonisation at ±60°.** **No longer a risk — a task.**
   The type-area run proves the recipe (§18): project first, snap to the day grid, bounded
   extent. It is `build\make_typearea_stack.py` pointed at a bigger window. Scale is
   **411×**, so plan hours and run it once. **Desktop job.** **[?]**
   **Overtaken 2026-10-03 (§31):** the classification runs on `global60_svm_stack_200m.tif`, a
   7-band 8-bit ±60° composite at 200 m. The 100 m Composite Bands run of `make_global_stack.py`
   is still unbuilt (only its smoke windows exist) and nothing now waits on it, so it is left off
   the README's next steps. **[V]**
8. **Which machine produced the §8 run times?** **Partly deduced 2026-09-18, and the logs
   answer it for at least one run.** Run 6 (`Slope_Mars_V1`, 11 Sep, 1 h 05 m) was submitted
   `GPU_THEN_CPU` and logged *"No compatible GPU device has been detected."* **An RTX 2080 Ti
   would have been detected** (Turing, CC 7.5, comfortably above what the Surface tools ask),
   **so run 6 cannot have been on the desktop.** It was the laptop.

   The chain has one untested link — q10, whether `GPU_THEN_CPU` really engages on that card.
   Settle q10 and this follows. If run 6 was on the laptop, the desktop should beat those
   timings, though §2.2 argues the USB bus caps the gain either way. **[?]**
9. ~~Copy the rasters to the desktop's internal SSD?~~ **Answered 2026-09-18: no. The project
   stays on `Z:` permanently — it will outgrow both computers** (§2.2). The old framing also
   undercounted the footprint by 5×. **[V]**
10. **Does `GPU_THEN_CPU` actually engage on the 2080 Ti?** One test run settles it (§2.3). **[?]**
11. ~~What internal disk does the desktop have, and how much free space?~~ **Moot** — it was
    only needed to plan the copy in q9, which is now settled. Still worth knowing for **scratch
    space** (§2.2), which is a far smaller ask. **[?]**
12. **Rewrite the globals as internally tiled, compressed copies?** On a permanently I/O-bound
    pipeline this trades spare CPU for scarce bandwidth and would also fix the whole-row read
    penalty (§2.2, §9). Needs a test on one raster before committing — and space for the
    copies, which `Z:` has. **Desktop job.** **[?]**
13. ~~Acquire the THEMIS Night IR global mosaic.~~ **Done 2026-09-18 on instruction** —
    `Mars_MO_THEMIS-IR-Night_mosaic_60N60S_100m_v14.tif`, 14.14 GB, on `Z:` and added to the
    project. **There is no *global* night mosaic; coverage is ±60°** (§15). **[V]**
14. ~~Fix the deliverable defects before resubmission.~~ **Largely overtaken 2026-09-19:**
    the prospectus is delivered and cannot be changed; **defect 1 is fixed at the source**
    in `content.py` and the interim report rebuilt (§21.3); and **the documents have been deprioritised
    entirely — "just worry about getting data worked and laid out"** (§1).
    Left open only as housekeeping: the interim **deck** still disagrees with the report
    (it was built 13 Sep, before the fix), and the segmentation date discrepancy
    (§14.5 #3) is unresolved. **[?]** **Corrected 2026-10-08 (§39.2): the deck was never blocked by
    the template**; a rebuild carries the fix. Not rebuilt, because the interim is to be
    rewritten anyway (`INTERIM-PLAN.md`). **[V]**
15. **Should segmentation ever run at ±60°?** Measured, not guessed: **~92 h** at the
    recommended 14/14/30, ~37 h even assuming the desktop is 2.5× faster (§23.6). The
    honest position is that **object-based classification is a type-area technique for this
    project**. If a global classified layer is wanted, per-pixel Iso Cluster is hours.
    **Do not commit desktop days to this without asking first.** **[?]**
    **Overtaken 2026-09-29: one was run manually on the desktop** — one raster-function input,
    15.5 / 15 / 20 px, about 19 h, then an SVM over it (§29.5). Whether it de-speckles is not
    measured. **[?]**
16. **Digitising is now the critical path and it needs manual judgement — but it is seeded.**
    **§25 (2026-09-19)** put **2,610 inferred candidate centrelines** in a *separate* class,
    each carrying the thermal index, so the blank canvas is gone. **The judgement is not.**
    The three
    `Landform_*` feature classes exist and are empty (§19.4); the **supervised half of
    task 7 cannot start without training polygons** (§19.2). No desktop needed. **[?]**
    **Started 2026-09-29 (§29.2): 512 hand-drawn training polygons in four classes, used for
    two SVM classifications and a deep-learning export.** The three `Landform_*` classes are
    still empty. **[V]**

17. **Should the plateau candidates be kept at all?** **§25.2:** 64% of the 2,610 candidates
    sit on ground under 2° of slope, where flow routing is finding paths in a 200 m DEM
    resampled to 100 m. The routing rasters are cached, so **raising `THRESH` or filtering on
    slope costs ~2 min**, not a rebuild. Open decision: whether to prune them or leave them as
    prompts. **[?]**
18. **Does any hydrology belong at ±60° at all?** Every closed basin in the band — Valles
    Marineris, Hellas, every crater — has §25.1's `Fill` problem, and the mask that solves it
    at type-area scale has not been tested at 411×. **Do not start this without asking.** **[?]**
19. **Rebuild the 7-band composite on the night grid with the valid slope?** The GUI `CompositeBand`
    sits on Viking's CM 0 grid at 231.54 m and carries `Slope_Mars_H1` (§29.4). Open decision. **[?]**
20. ~~Retarget `build\make_typearea_supervised.py` before it is ever re-run.~~ **Done
    2026-10-01 on request** (§29.8): it writes `Landform_TrainingSamples_terrain_auto` and
    refuses to delete any class holding a row it did not write. **[V]**
21. ~~`verify_all.py` fails 1 of 38.~~ **Fixed 2026-10-01 on request** (§29.8): the count is
    dated per log, four by 13 Sep plus the fifth on 24 Sep. **39 / 39.** **[V]**
22. **The drive is `F:` on the desktop** (§2.4). Junctions and `build\` paths assume `Z:`. **[?]**
    **The project's layers are safe since 2026-10-03 (§34.1):** 12 that read through the
    `Z:\Global60` junction were repointed, so the `.aprx` opens whole on `F:`. The scripts still
    assume `Z:`.
23. **Which class schema is kept?** `Composite Object Classes.ecs` (1 Oct) numbers lava tube 2 and
    steep/windy hills 3; the hand-drawn labels, both SVM definitions and the deep-learning export use the
    reverse (§29.2). Settle it before training a model on the export or drawing samples under
    the newer schema. **[?]**
24. **What in `ClassifyRaster` made the 29 Sep map blocky?** The IR input and the segmentation are
    seamless; only the classified output has the 4096-px seams (§30.2). Needs the `.afr` and the
    tool's settings from the desktop. Until then, do not use that map as a result. **[?]**
25. **Fix the 7-band stack before training a deep-learning model on it?** Elevation alone
    reproduces 62% of the SVM made from it, and bands 6–7 are empty past ±60° (§30.3, §30.5). Open decision. **[?]** **Done 2026-10-03, adoption is an open decision (§31):** corrected stack,
    re-export, reclassification.
26. **Boxes or pixel labels for the deep-learning export?** PASCAL VOC boxes around area classes
    (Normal Ground, hills) are often a whole chip; `Classified_Tiles` fits those classes (§31.4). Open decision. **[?]**
27. **How much smoothing to publish?** Held-out scores rise with every majority window, from 70.5 %
    raw to 75.1 % at 9 × 9, because the labelled polygons are large. 5 × 5 was chosen by feature size (§32.2).
    Open decision. **[?]**

---

## 12. Working conventions

- **Read the project before writing anything about it.** Deliverables written from assumption were rejected, correctly. That is the origin of this file.
- **"Restyle" means a visible redesign**, not consistency fixes. A conservative
  tidy-up has been rejected in those exact terms.
- **The school SharePoint is not synced to this machine.** Ask for an export or download; the
  link hits a Microsoft sign-in wall.
- The work is done in **ArcGIS Pro only**, on CPU-only hardware.
---

### 12.1 File and record conventions — follow these

Added 2026-09-18 after an audit of this file found four stale claims and six dead script
references. **The failure mode is writing a new section without reconciling the old one.**

**This file.** Sections are numbered and sequential; every claim carries `[V]` / `[E]` / `[?]`;
cross-references use `§N`. **When a new section supersedes an older claim, edit the older one**
— do not leave it to be contradicted later. §3 said "these three files are the whole of the
held imagery **[V]**" for as long as it took to notice; a false claim wearing a `[V]` is worse
than no claim.

**Scripts in `build\`.** The existing convention is verb-first, and new scripts follow it:

| Prefix | Purpose |
|---|---|
| `make_*` | produces data, rasters or figures (`make_fig_*` for figures specifically) |
| `build_*` | produces a deliverable (`.pptx` / `.docx`) |
| `audit_*` | inspects the deliverables |
| `verify*` | checks claims against the project files |
| bare noun | a module, not a script — `content.py`, `le_theme.py`, `marsfig.py` |

**Every figure must have a script that regenerates it.** `ius_day_night_diff.png` briefly
existed without one; it is reproducible again.

**Derived data.** Type-area products are `ius_*` in `Z:\Mars Project\TypeArea\`, reached as
`Z:\TypeArea` for Spatial Analyst (§19.1). Every warped raster gets the **named** Esri WKT
`Mars_Equidistant_Cylindrical_CM180` (§20.2), which the stack script now applies itself.

**Python gotcha that has bitten repeatedly in this project.** Windows paths in non-raw Python
strings silently corrupt — `\f` is a formfeed, `\t` a tab, `\v` a vertical tab, and
`\(` escapes the parenthesis. All four have bitten this project: two find-and-replace
passes silently matched nothing, and one wrote a vertical tab into this very file.
**Use raw strings or `os.path.join` for every path, including in throwaway one-liners.**

**`build\audit_record.py` checks all of the above** — section numbering, § cross-references,
script names, control characters, table shape, the record's counts against the actual gdb and
disk, every figure having a script, and the memory files' frontmatter, links and index.
**Run it after editing this file.** It exits non-zero on failure, and it is what caught the four
stale claims and six dead references that prompted writing it.

---

## 13. What scripted sessions can actually do to this project — verified 2026-09-18

Everything in this section was **run on this machine today**, not reasoned about. Timings are
real, from the laptop, with `Z:` on USB. **[V]**

### 13.1 The channel

**Headless `arcpy` is the only channel, and it is enough.** Re-confirmed 2026-09-18: this
session has **no desktop-control tools** — a tool search returns only browser automation. The
Pro GUI cannot be clicked, so nothing here depends on it. What replaces it:

```
"C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe"  script.py
```

`import arcpy` costs **7.3 s** — pay it once per script, not once per question. ArcGISPro
**3.7**, Python **3.13.13**, and **Spatial / 3D / ImageAnalyst all `Available`**. Pro was
**not running** during these tests, which is the state to work in (§2.4).

### 13.2 Verified capability matrix

| Operation | Cost | Notes |
|---|---|---|
| `arcpy.mp.ArcGISProject(...)` | **0.1 s** | Opens with Pro closed. Free. |
| `listMaps` / `listLayers` / `listBrokenDataSources` | instant | 11 maps, 0 layouts, 4 broken — all reconfirmed today |
| `ListRasters` / `ListFeatureClasses` on the gdb | instant | 8 rasters, 22 feature classes on 2026-09-18; 14 rasters, 26 feature classes on 2026-10-01; **14 rasters, 30 feature classes on 2026-10-03** — matches §6 |
| **`p.saveACopy(tmp)`** | **0.7 s** | **The safety primitive — see §13.3** |
| `p.createLayout(w,h,"INCH")` | instant | The project's 0 layouts is not a barrier |
| `lyt.createMapFrame(geom, map)` | instant | |
| `mf.camera.scale = …` | instant | |
| **`lyt.exportToPNG(out, resolution=72)`** | **11.7 s** | **Global extent, real raster render** |

### 13.3 The safe-edit pattern — use this for anything that writes

`saveACopy` costs 0.7 s and makes the single-copy drive (§2.5) survivable. **Never edit the original
`.aprx` in place when a copy would do:**

```python
p = arcpy.mp.ArcGISProject(r"Z:\Mars Project\Mars Project.aprx")
p.saveACopy(scratch_aprx)          # 0.7 s
p2 = arcpy.mp.ArcGISProject(scratch_aprx)   # work here, never on the original file
```

Layouts, symbology experiments and exports all belong on the copy. Only write the real
`.aprx` when a change has been asked to persist — and then only with Pro closed (§2.4).

### 13.4 Real map exports are available, and this changes the figure strategy

**§5 says the project has zero layouts, and that has been read as "map export is out of
reach." It is not.** A layout built from scratch over `Map3`, rendering the Viking mosaic at
global extent, exported to PNG in **11.7 seconds** — the project's own layers, symbology and
own coordinate system, correctly rendered.

**Why this matters for the deliverables (§1, due 8 December):** every figure so far has been
matplotlib drawn off the raw rasters (§5), which reproduces the data but not the cartography —
no renderers, no layer stack, no legend, no scale bar, no graticule. Those are exactly the
things a remote-sensing deliverable is marked on. Both routes now exist:

- **matplotlib / `build\`** (§13.5) — full control, dark theme, cached `.npy`, no Pro needed
- **`arcpy.mp` layout export** — genuine ArcGIS cartography, legends and scale bars, at ~12 s
  a frame

Neither is obsolete. Use matplotlib for designed figures inside the deck's visual language;
use layout export when the deliverable should show the GIS itself. **Ask which is wanted
before building a figure set — don't assume matplotlib because that is what exists.**

### 13.5 What this makes possible without opening Pro

Read and report anything: inventories, statistics, lineage, extents, row counts, CRS.
Build figures both ways. Draft and rebuild the decks and reports from `build\`
(§[deck pipeline], system Python for `pptx`). Audit deliverables against the project's actual
numbers. Prepare, parameterise and stage geoprocessing — **but run the global ones on the
desktop** (§2.1), because capability is not the constraint there, RAM and the USB bus are.

### 13.6 Limits worth stating plainly

- **No GUI.** Anything that exists only as a Pro dialog is out of reach. Nothing so far has.
- **Global GP runs still wait for the desktop** (§2.1) — `arcpy` will happily start a job the
  laptop cannot finish.
- **Writes to the `.aprx` need Pro closed**; check `tasklist | findstr ArcGISPro` first.
- **`osgeo.gdal` here, `pptx` on system Python** (§2.4). Raster work and deck work are
  separate interpreters, always.
- **Deletions need the author's approval** (§2.5), single-copy drive, no backup.
---

## 14. The deliverables — what they claim, and four defects found in them

Read directly out of the `.docx` files on 2026-09-18. Until now this file recorded the
*project*; this section records **what has been written about it**, because the two have
drifted. **[V]**

### 14.1 The plan, in the prospectus's own words

**Full title:** *"Mars Global Mosaic: Mapping Lava Flows, Fluvial Channels, and Impact Craters
in Visible and Infrared."* Use the full title on deliverables; "Mars Global Mosaic" is the
short form (§1).

**The stated goal:** assemble a **co-registered** global visible + thermal-IR mosaic from the
three held products and use it to map three landform families — volcanic flow units, fluvial
channels and valley networks, impact craters — producing **one internally consistent global
landform inventory**.

**The prospectus carries a 10-task plan**; the interim report re-cuts it as **14 tasks with
percent-complete**, reporting **~42% overall**. Fully complete: raster acquisition, the grouped
mosaic viewer. Near: type-area selection 90%, DEM derivatives 80%. **At zero: landform
digitizing, crater inventory, map layouts.** CRS harmonization sits at **15%** and the band
composite at **5%** — and those two gate everything below them.

**Task 3 (harmonize the coordinate systems) is explicitly "the gate."** The prospectus's own words. It is
§4's trap stated as project structure, and nothing downstream of task 5 moves until it closes.

### 14.2 Two design decisions that are easy to get wrong

**The composite is four bands: Viking RGB + THEMIS Day IR. Elevation is deliberately
excluded.** The reasoning is correct: Iso Cluster measures distance in **raw band
values**, so a DEM band running −8,528 to +21,226 would swamp four bands running 1–255.
Elevation stays a separate analysis layer. **Do not "helpfully" add the DEM to the composite.**

**The prospectus's own fix for the failed composite: project first, then run over bounded extents rather
than the globe.** Both documents say it. This matches §4's diagnosis and §2's I/O reality, and
it is the plan to execute — not something to redesign.

### 14.3 The type area is Ius Chasma — be specific

The mosaic viewer is parked over **western Valles Marineris, ~271–286°E, 6–13°S — Ius Chasma
and the Louros Valles tributaries on its south wall.** That is the type area for detail work
and figures. The **Jezero** map is a second saved view and is **context only**: hosted
Perseverance services, no local imagery (§5).

### 14.4 The scientific hook, worth keeping in the writing

**Athabasca Valles was mapped as a fluvial outflow channel for decades before being
reinterpreted as flood lava.** Discriminating volcanic from fluvial channels is a live problem,
and morphology + thermal response is the project's answer to it. That is the argument the
deliverables are built on — it is stronger than "combine three datasets."

**THEMIS Night IR is named as the single highest-value missing dataset**, in both documents.
Day−night pairing converts brightness temperature into **thermal inertia**, the best
dust-versus-bedrock discriminator from orbit. Same source and format as the day mosaic already
held. **The plan depends on acquiring it** — see §11 q13.

> **Qualified by §24 (2026-09-19):** the file was acquired, but **the held products cannot
> yield calibrated thermal inertia** — both are 8-bit DN, independently stretched, with no
> scaling to Kelvin. The hook survives intact; what carries it is the **relative
> diurnal-contrast index**, which §24.3 shows is a material discriminator and not a
> restatement of topography. **Write the hook, not the word "inertia".**

### 14.5 Four defects to fix before resubmission **[V]**

> These are provable, not stylistic. Fix them before either document is sent again.

1. **The Composite Bands attempt count is wrong in both documents — and the interim report
   contradicts itself.** The prospectus says *"failed three times"* and *"Three attempts at
   global scale on 9 September."* The interim's own processing table lists **four rows**,
   including `Sep 13, 14:48 — Global extent, first input Slope_Mars_V1`, yet its narrative
   still says *"Composite Bands has failed three times."* **The table and the prose disagree
   inside the same document.** The truth is four attempts totalling ~2 h 22 m (§8).

2. **The interim report attributes Segment Mean Shift to the wrong planet.** It states the
   segmentation *"ran successfully end to end on the Mercury MESSENGER MDIS basemap."*
   It did not. Verified by reading the output raster directly on 2026-09-18:

   | Raster | Dimensions | CRS | Extent |
   |---|---|---|---|
   | `Segmented_2026090819253…` | 106,694 × 53,347 | **`GCS_Mars_2000_Sphere`** | −180…180°, −90…90° |
   | `Mercury_MESSEN_IsoClusterUns` | 92,160 × 46,080 | `SimpleCylindrical_Mercury_2015` | metres |

   The segmentation output is on the **Mars DEM grid, in Mars degrees**. Only Iso Cluster and
   ML Classify were rehearsed on Mercury. **This closes §11 q3**: the segmentation is already
   in the record — it is simply attributed to the wrong body.

3. **The segmentation date disagrees with itself.** The interim report logs it *"Sep 9,
   03:35"*, but the output name `Segmented_202609081925347487376` encodes **2026-09-08
   19:25:34**, and §7 dates it 08 Sep. An ~8-hour offset, plausibly UTC-vs-local. Worth
   settling before it is quoted again. **[?]**

4. **Scope: both documents call for a *global* night mosaic, and describe a global analysis
   stack. Neither exists.** No global night product is published, and **the project has since defined
   the project's analysis extent as ±60°** (§16). Both documents need the scope restated —
   not as an apology, as a definition. §16.5 has the wording. **[V]**

**What this says about method, and it is the point of §12:** all three defects were found by
reading the project rather than the prose. Every one is checkable in seconds against a raster
header or a log. **Audit the deliverables against the project's own numbers before any
resubmission** — that is now a standing task, not a one-off.
---

## 15. THEMIS Night IR — sourced and verified 2026-09-18

§11 q13 acted on. **The file was chosen by reading product labels, not by name-matching**, and
the choice turns on co-registration. **[V]**

### 15.1 The file

```
https://asc-pds-services.s3.us-west-2.amazonaws.com/mosaic/
    Mars_MO_THEMIS-IR-Night_mosaic_60N60S_100m_v14.tif
```

**14.14 GB** · MD5 `39a50397e05e078258083be88cee0714` · ProductId `thm_night_ir_v14`, ASU Mars
Space Flight Facility. Downloaded to `Z:\` beside the other globals, with its `.lbl` and
`.md5` kept alongside for provenance.

`planetarymaps.usgs.gov/mosaic/` redirects to this S3 bucket, and the bucket is **where the
existing source files came from** — `Mars_MO_THEMIS-IR-Day_…v12.tif` (21.21 GB) and
`Mars_Viking_MDIM21_ClrMosaic_global_232m.tif` (11.87 GB) are present at byte-identical sizes
to the copies on `Z:`. Provenance for the whole holding is therefore settled. **[V]**

### 15.2 Why this file and not the other one

There are two THEMIS night products. **They are not interchangeable**, and the wrong one
would reintroduce the §4 trap:

| | **`…Night_mosaic_60N60S_100m_v14`** ✅ | `THEMIS_NightIR_ControlledMosaics_100m_v2_oct2018` |
|---|---|---|
| Size | 14.14 GB | 15.32 GB (+ 5.13 GB `.ovr`) |
| Dimensions | 213,388 × 71,130 | 213,389 × 77,058 |
| **Central meridian** | **180 — matches the day mosaic** | **0 — mismatched** |
| Latitude | ±60° | ±65° |
| ULX | −10,669,400.0 | −10,669,445.554 |
| **Aligns with the day grid?** | **Yes, exact integer offset** | **No — 0.544 px** |

The controlled mosaic buys 5° of latitude and costs a reprojection plus a resample, on the
exact axis that has already cost this project four cancelled runs. Not worth it.

### 15.3 The grids are pixel-aligned — verified by arithmetic, not assumed **[V]**

| | Day v12 | Night v14 |
|---|---|---|
| Size | 213,390 × 106,696 | 213,388 × 71,130 |
| ULX / ULY | −10,669,500.0 / 5,334,800.0 | −10,669,400.0 / 3,556,500.0 |
| X extent | ±10,669,500 | ±10,669,400 |
| Y extent | ±5,334,800 | ±3,556,500 |

**X origin offset = exactly 1.00 pixel. Y origin offset = exactly 17,783.00 pixels.** Both
integers, both at the same 100 m resolution and the same `SimpleCylindrical` / CM 180.

**So the night raster is an exact integer-pixel sub-window of the day grid.** Day − night
needs **no resampling and no reprojection** — set the day raster as snap raster, intersect the
extents, and subtract. This is the cleanest join in the entire project, and the only one of
the four rasters that is natively aligned to another.

> **Do not reproject this file "to be safe."** Any resample would destroy the exact alignment
> that makes the difference image meaningful.

### 15.4 The coverage limit is a real constraint — and a fourth deliverable defect

**There is no global THEMIS night mosaic. It does not exist.** Night IR stops at **±60°**
because the poles lack usable night-time thermal coverage.

Both deliverables call for *"the THEMIS Night IR **global** mosaic"* (§14.4). **That product
cannot be acquired, and the wording has to change** — add it to the §14.5 list as **defect 4**.

What it actually costs the project:

- **Thermal inertia is derivable only between 60°N and 60°S** — about **87% of Mars by
  surface area**, but the polar layered deposits and both ice caps are out.
- **The type area is safe.** Ius Chasma sits at **6–13°S** (§14.3), comfortably inside.
- State it as a **stated limit of the mapping**, exactly as the prospectus already does for
  sub-kilometre features — that framing is the prospectus's and it is the right one.
### 15.5 Verified in the data, and the first real result **[V]**

Added to the project 2026-09-18: `.aprx` backed up to `.backups\Mars Project
20260918-194853.aprx` first, statistics built (**242 s**, a streaming low-RAM read — safe on
the laptop, unlike the RAM-bound jobs in §2.1), then inserted into the **`IR` group of both
working maps** (`Mars High-Resolution Mosaic Viewer` and `Map3`). MD5 verified against the
published checksum: **match**.

**Night IR statistics:** min 1, max 255, mean **124.60**, σ **32.79** — against the day
mosaic's mean 125.75, σ 34.36. NoData 0, valid range 1–255, exactly as the day mosaic (§3).

**The predicted alignment held exactly.** A windowed read over the Ius Chasma type area
(271–286°E, 13–6°S) computed the offsets independently from each file's own geotransform:

```
day   window  col=160634.975  row=56904.482   8891 x 4149
night window  col=160633.975  row=39121.482
offset        dcol=-1.000     drow=-17783.000     <- exact integers
valid overlap 100.00%
```

**No resampling, no reprojection, 100% overlap.** Figure at
`build\pres1_img\ius_day_night_diff.png`, built by `build\make_fig_daynight.py` — which recomputes
the offsets from each file's own geotransform every run, so the alignment is re-proven rather
than remembered.

> ### The result worth putting in the report
>
> **Pearson r between day and night over the type area is 0.098 — essentially uncorrelated.**
>
> That is not a registration failure; registration is proven above. **It is the entire
> justification for the night mosaic, measured on the project's own type area.** The day image reads as
> shaded relief — sun-facing slopes bright — because daytime IR is dominated by solar heating
> and slope orientation. The night image does not: it shows **material properties**, because
> overnight the signal is governed by thermal inertia, with rock and bedrock still warm while
> dust has cooled.
>
> **The two carry almost independent information. If they were correlated, the night mosaic
> would add nothing.** r ≈ 0.1 is the quantitative version of the prospectus claim that
> *"thermal infrared responds to particle size and surface coherence, which visible albedo does
> not"* — and it is now measured rather than asserted.
>
> In the difference image: broad **red** = warm day, cool night = **low thermal inertia, dust
> mantle**. **Blue** = relatively warm at night = **higher thermal inertia, bedrock or coarse
> material** — and it traces the canyon walls and the Louros Valles tributaries. That is
> exactly the dust-versus-bedrock discrimination the project was built to do.

**Caveat to keep honest in the writing:** this is a **DN difference on two 8-bit mosaics**, not
calibrated thermal inertia. The prospectus already says the day−night approach is a proxy
requiring calibrated radiance for the real quantity — keep that sentence.

> **§24 (2026-09-19) turned that caveat from a hedge into a proof, and two things here now
> need reading with it:**
>
> - **The caveat is stronger than stated.** It is not only that the mosaics are 8-bit — they
>   are **independently stretched** (day p2/p98 = 35/205, night = 58/203), so a raw subtraction
>   differences two unrelated scales. **Calibrated thermal inertia is not derivable from these
>   products at all.** The night ISIS label settles it: `Base=0.0, Multiplier=1.0`.
> - **`ius_day_night_diff.png` captioned its third panel "thermal-inertia proxy"** over the raw
>   difference. That is the overclaim §24.1 disproves; **relabelled and rebuilt 2026-09-19.**
>
> **The r = 0.098 result above is unaffected** — a correlation does not care about the
> stretch. But for the dust-versus-bedrock reading, **use `ius_thermal_contrast.tif` (§24.2),
> not the raw difference.**
---

## 16. The project's analysis extent is ±60° latitude — decided 2026-09-18

**The decision, verbatim: the basis for the project, while built from global products,
covers only ±60° of latitude.** This supersedes "global" wherever that word describes the
*analysis stack*. **[V]**

### 16.1 Why it is the right call and not merely a concession

The night mosaic forces it (§15.4) — but the result is better than a compromise, because
**it is the first time all four inputs share one latitude range.** A stack whose bands stop at
different latitudes is not a stack; every downstream product would have had a ragged edge and
a different denominator. ±60° makes the whole thing rectangular and consistent.

### 16.2 What it costs, measured **[V]**

| Dataset | Full grid | At ±60° | Rows kept |
|---|---|---|---|
| Viking MDIM (232 m) | 92,160 × 46,080 | 92,160 × **30,720** | 66.7% |
| THEMIS Day IR (100 m) | 213,390 × 106,696 | 213,390 × **71,130** | 66.7% |
| HRSC/MOLA DEM (200 m) | 106,694 × 53,347 | 106,694 × **35,565** | 66.7% |
| THEMIS Night IR (100 m) | 213,388 × 71,130 | unchanged | 100% |

**Total band-pixels fall from 56.38 bn to 42.64 bn — a 24.4% reduction** (33.3% on each
raster that gets clipped).

> **The trade is favourable, and this is the sentence for the report: clipping to ±60° removes
> a third of the rows but only 13.4% of the surface area.**
>
> Simple cylindrical massively oversamples high latitudes — a row near the pole spans the same
> pixel count as one at the equator while covering a fraction of the ground. **86.6% of Mars
> lies within ±60°.** So the cut is cheap in science and expensive in pixels, which is exactly
> the right direction on an I/O-bound pipeline (§2.2).

### 16.3 The science survives it — verified, not assumed **[V]**

Checked against the cached decimated DEM:

| | Value | Location | Inside ±60°? |
|---|---|---|---|
| DEM minimum | −8,263 m | 32.8°S, 62.1°E — **Hellas Planitia** | **yes** |
| DEM maximum | +21,080 m | 17.3°N, 227°E — **Olympus Mons** | **yes** |

**Relief within ±60° is identical to global relief: 29,343 m.** The project loses **no**
elevation dynamic range — and the quantitative measurements come from the DEM (§14).

**What is actually lost:** the polar layered deposits, both ice caps, and the north polar erg.
**None of these belongs to the three target landform families** — lava flows, fluvial
channels, impact craters. A minor bonus: the cut also removes the high-latitude Viking MDIM
zones worst affected by seasonal frost and low illumination.

### 16.4 Consequences to act on

- **Composite Bands gets a third smaller.** Stacked with the prospectus's own fix — project first, run over
  bounded extents (§14.2) — the retry is now materially more tractable than the four runs that
  were cancelled. **This is the strongest argument yet that the retry will succeed.**
- **Clip or snap everything to the night raster's extent**, since it is the binding one and
  the day grid aligns to it exactly (§15.3). Use it as the template.
- **Terrain derivatives should be rebuilt inside ±60°**, not globally — task 4 in the
  prospectus already calls for rebuilding them on a projected DEM (§14.1), so do both at once
  and pay the run cost only once.
- **Pyramids (§11 q6) are still worth it**, and now cheaper.

### 16.5 How to say it in the deliverables

**Keep the title.** *"Mars Global Mosaic"* remains accurate: the source products are global,
and the visible mosaic genuinely is. What is ±60° is the **co-registered analysis stack**.
Distinguish the two explicitly and early rather than quietly redefining "global" —

> built from global products; the co-registered four-band analysis stack spans ±60° latitude,
> set by THEMIS night-time coverage, and covers 86.6% of the surface.

State it once in scope, repeat it in limitations, and **give the 86.6% figure** — a stated,
quantified limit reads as rigour. This replaces defect 4 in §14.5: the fix is not an apology
for missing data, it is a definition of scope.
---

## 17. The audit suite — was dead, now works. Run it. 2026-09-18 **[V]**

### 17.1 It had been broken since the move off `C:`

**Twelve scripts in `build\` pointed at `C:\Users\Loggg\Downloads\Mars Remote Sensing
Project`, which does not exist.** The whole audit and several figure generators had been
silently dead since the project moved to `Z:` (§8 dates that move to ~11 Sep). Nothing
reported this, because nobody ran them.

Fixed 2026-09-18 — originals kept in `build\.py_backup_20260918\` (45 files):

- **Repathed all 12** to `Z:\Mars Remote Sensing Project`.
- **Remapped the deliverable filenames**, which had drifted too: the interim deck and report
  now live in `NEXT STUFF\`, and `Mars Global Mosaic - Presentation 1.pptx` is now
  **`ocean first pres LE.pptx`** (`ocean` = the OCN course code, not the other project).
- **Added a UTF-8 stdout shim** to all 10 audit/verify scripts. They were crashing with
  `UnicodeEncodeError` on a cp1252 console the moment output contained `→` or `−`. They now
  run anywhere.
- Made the new `NEXT STUFF\…` paths raw strings; `"\M"` is not a valid escape.

**Run them with the ArcGIS interpreter** (§2.4) from `build\`:

```
"C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe" verify_all.py
```

### 17.2 `verify_all.py` was enforcing the retracted error — corrected

This is the §8 trap caught in the act. The script asserted:

```python
check("Exactly three Composite Bands runs are logged",
      msgs.count("Failed to execute (CompositeBands)") == 3, ...)
...
("Four attempts",          "the fourth composite run was never real"),
("fourth on 13 September", "the fourth composite run was never real"),
```

**It hard-coded "three" and would have flagged any deliverable that correctly said "four" as
an error.** The retraction of the phantom-run claim had been frozen into the verifier, so the
tool meant to catch mistakes was enforcing one.

Counted from the logs directly: **8 GpMessages files, 4 `Failed to execute (CompositeBands)`,
2 `WARNING 000869`.** The fourth is `929130196400` — 13 Sep 14:30:59 → 14:48:27, 17 min 28 s.
§8 was right.

Corrected to `== 4`, added a positive check for the 17 min 28 s run, and deleted the two
inverted phrase checks. **`verify_all.py` now passes 38 / 38.**

> **2026-10-01: 37 / 38, then fixed.** The `== 4` check failed because a fifth was cancelled
> attempt on 24 Sep (§8 row 9): a whole-folder count encodes the day it was written. It now dates
> each log and checks four by 13 Sep plus the fifth, so later runs cannot break it. **39 / 39**
> (§29.8). **[V]**

> A caution for anyone editing these scripts: **a check that encodes a belief is not evidence
> for it.** Re-derive from `GpMessages\` or the raster headers, never from what the verifier
> expects.

### 17.3 What the working suite immediately found

`audit_consistency.py` pulls every sentence carrying a key number across all four documents.
On its first successful run it confirmed **§14.5 defect 1 in all three live documents**:

```
COMPOSITE ATTEMPTS
  [PROS      ] Three attempts at global scale on 9 September, all cancelled...
  [PROS      ] Three attempts on 9 September, cancelled after 47 min 57 s, 1 min 41 s,
               and 1 h 14 min 51 s — the tool logs record all three
  [IDECK,IREP] Three attempts on 9 September, abandoned after 47 min 57 s, ...
```

**The prospectus does not merely undercount — it asserts "the tool logs record all three."
The logs record four.** That is the most directly falsifiable sentence in either document and
the first thing to fix.

Minor, and not worth changing: the prospectus rounds hillshade to "12 min" where the interim
gives "11 min 42 s".

### 17.4 `verify2.py` — 16 failures, and they are stale by design

`verify2.py` checks the **pre-restyle** Presentation 1, which no longer exists. Pointed at
`ocean first pres LE.pptx` it reports 16 failures. **These are not defects to fix** —
Presentation 1 is delivered and is no longer a live deliverable (§1).

Two observations from it are still worth knowing, confirmed by independent extraction:

- **The restyled deck has 20 slides and `0` speaker notes.** The rebuild dropped every note.
  If they are ever wanted back, they exist only in the pre-restyle file or in `content.py`.
- **`Ius Chasma`, `Louros Valles`, `Type Areas for the Mosaic`, `mosaic seams` and
  `hosted rover services` are all absent from the delivered deck.** The type-area material
  did not survive the restyle. Historical now — but the type area is task 1 at 90% (§14.1),
  so it should certainly appear in the interim and final.

**Retarget `verify2.py`'s deck checks at the interim deck**, or retire them. As written they
will report 16 failures forever and train the eye to ignore the suite.
---

## 18. Tasks 3 and 5 are DONE for the type area — 2026-09-18 **[V]**

**The Composite Bands run that failed four times globally, burning 2 h 22 m, completed in
8.8 seconds over the type area.** Whole harmonise-plus-composite pipeline: **~44 s on the
laptop.** The prospectus's own fix — project first, bounded extents — was correct.

Outputs in **`Z:\Mars Project\TypeArea\`**, built by `build\make_typearea_stack.py`.

### 18.1 The target grid, and why

**`eqc / lon_0=180 / R=3396190 / 100 m`, snapped to the day mosaic's own pixel edges.**
Extent 271–286°E, 13–6°S → **8891 × 4150 px**.

Chosen so **the day–night pair is never resampled** (§15.3) — only Viking and the DEM are, and
they must be at any target. The alternative (reprojecting onto CM 0, as Presentation 1
proposed) would have resampled the two finest and only natively-aligned layers. **Do not do
that.**

| Output | Source | Resample | Time |
|---|---|---|---|
| `ius_viking.tif` (3 band) | Viking 232 m, CM 0 | cubic | 9.7 s |
| `ius_day.tif` | THEMIS day 100 m, CM 180 | **none needed** | 2.3 s |
| `ius_night.tif` | THEMIS night 100 m, CM 180 | **none needed** | 2.5 s |
| `ius_dem.tif` | HRSC/MOLA, degrees | cubic | 6.4 s |
| `ius_composite_4band.tif` | Viking RGB + day | — | 8.8 s |
| `ius_composite_5band.tif` | + night | — | 13.8 s |

All four land on an identical 8891 × 4150 grid — **task 3 satisfied for this extent.**
DEM over the type area: −4,592 m to +5,805 m, relief 10,397 m.

### 18.2 Two composites, because the night mosaic changes the design

The written plan is **4 bands** (Viking RGB + day IR), with the DEM excluded because Iso
Cluster measures distance in raw values and −8,528…+21,226 would swamp 1…255 (§14.2).

**That reasoning admits THEMIS night as a fifth band** — it is 8-bit, DN 1–255, exactly like
the others. So both were built. **The 5-band is the better classification input** and the
choice is open; the 4-band exists so the written plan still has its artefact.

### 18.3 The band statistics justify the whole project — put this in the interim **[V]**

**100.00% of pixels are valid in all five bands simultaneously.** No gaps, no fill, nothing to
mask. Correlation over the type area:

| | Vik R | Vik G | Vik B | Day IR | Night IR |
|---|---|---|---|---|---|
| **Viking R** | 1.000 | 0.960 | 0.925 | −0.486 | −0.121 |
| **Viking G** | 0.960 | 1.000 | 0.993 | −0.496 | −0.085 |
| **Viking B** | 0.925 | 0.993 | 1.000 | −0.488 | −0.068 |
| **Day IR** | −0.486 | −0.496 | −0.488 | 1.000 | 0.105 |
| **Night IR** | −0.121 | −0.085 | −0.068 | 0.105 | 1.000 |

Three things fall straight out of it, and all three are report material:

1. **The three Viking bands are one dimension, not three** (r = 0.925–0.993). Visible colour
   is largely redundant with itself. A 3-band visible mosaic is not a 3-band measurement.
2. **Day IR is moderately *anti*-correlated with visible (−0.49).** Bright in visible means
   cool in daytime IR — the dust signature: fine, bright, low thermal inertia. **This is the
   measured form of the prospectus claim that thermal IR carries what albedo does not.**
3. **Night IR is the most independent band in the stack** (|r| ≤ 0.12 against everything).
   It contributes information no other layer holds. **The acquisition paid for itself.**

> **Effective dimensionality of the stack is about three: visible albedo, day IR, night IR.**
> That is the quantitative case for the fusion, and it is now measured rather than asserted.

### 18.4 Figure

`build\pres1_img\ius_fusion.png` — natural colour / HSV fusion / day−night, three panels,
in the deck's dark theme. Built by `build\make_fig_fusion.py`. The day−night panel shows canyon
walls, wall-rock spurs and the Louros Valles tributary fans in **blue** (high thermal inertia,
bedrock and coarse debris) against a **red** plateau (dust). **That is the project's target
discrimination, working, on its type area.**

A first attempt used per-band percentile stretches and came out as unreadable neon — on
decorrelated bands that maximises chroma. The HSV version (hue from the false colour at half
saturation, value from day IR) keeps relief legible while colour carries the thermal signal.
**Use the HSV form for any future fusion figure.**

### 18.5 What this unblocks

Task 5 was **5%** and task 3 **15%** (§14.1). For the type area both are now done. Next, in
order, and all of it laptop-sized at this extent:

- **Iso Cluster + ML Classify on `ius_composite_5band.tif`** — task 7, rehearsed on Mercury,
  never run on Mars. Now runnable in minutes rather than hours.
- **Digitizing flow margins / channel centerlines / crater rims** — task 11, still 0%.
- **Rebuild slope and hillshade from `ius_dem.tif`** — it is a projected metric grid, so
  **WARNING 000869 will not recur** and the z-factor is finally valid (§7).
- **Scale the same script to ±60°** when the desktop is available (§16).
---

## 19. Task 7 run on Mars for the first time — and a method correction 2026-09-18 **[V]**

`build\make_typearea_classes.py`, on `ius_composite_5band.tif`. Same parameters as rehearsed on
Mercury: **10 classes, min class size 20, sample interval 10.**

**IsoCluster 12.5 s · MLClassify 7.2 s.** Ten classes requested, **ten delivered, every one
populated** — 25.25 / 15.21 / 12.39 / 10.21 / 9.34 / 6.31 / 6.29 / 5.95 / 5.64 / 3.41 %.
No collapse, as expected: fill is 100% and the stack is not spectrally tight.

### 19.1 A trap: legacy Spatial Analyst rejects spaces in paths **[V]**

`IsoClusterUnsupervisedClassification` failed on `Z:\Mars Project\TypeArea\…` with:

```
ERROR 010328: Syntax error at or near symbol SPACE.
ERROR 010267: Syntax error in parsing grid expression.
```

The legacy grid-expression parser cannot handle the space in **"Mars Project"**. 8.3
short-name generation is **disabled on this volume**, so `GetShortPathNameW` returns the long
path unchanged and is no help.

**The fix, already in place: a directory junction.**

```
mklink /J Z:\TypeArea "Z:\Mars Project\TypeArea"
```

Data stays where it belongs; the tools get a space-free path. `Z:\TypeArea` **is not a copy** —
it is the same folder, so it costs nothing on the single-copy drive (§2.5).
**Use `Z:\TypeArea\…` for every Spatial Analyst call.** Expect the same failure from any other
legacy SA tool run against the project path — and note the whole project lives under a folder
with a space, so this will recur.

### 19.2 The Iso Cluster → ML Classify two-step is a no-op as run **[V]**

The two outputs are **the same raster**:

| | |
|---|---|
| differing pixels, 1,023,371-px sample | **0** |
| GDAL band checksum, full raster | **62066 = 62066** |
| class counts | identical to the pixel across all 10 |

Re-checkable any time with `build\verify_typearea.py`, which also prints the band statistics
and the correlation matrix in §18.3.

**`IsoClusterUnsupervisedClassification` already performs IsoCluster followed by MLClassify
internally.** Re-running `MLClassify` with the signature file it just wrote and EQUAL priors
reproduces its own output exactly. It adds nothing.

> **This applies retroactively to the Mercury rehearsal** (§7), which was run the same way —
> so that raster is not "the maximum-likelihood result as distinct from the ISODATA
> assignment". The two are the same thing. **Correct that in §7 and do not repeat the claim.**
>
> **What makes the supervised step real is training polygons**, which is what task 7 actually
> says — *"Iso Cluster unsupervised classification, then Maximum Likelihood against training
> polygons."* None exist yet. **The supervised half of task 7 has not been done**, and cannot
> be until landform polygons are digitised (§19.4). Do not report task 7 as complete.

### 19.3 The classification is geologically coherent

`build\pres1_img\ius_classification.png` (built by `build\make_fig_classification.py`), classes over day-IR
relief. It is not noise:

- **Classes 1–3 (cyan/blue, 24.0% together)** track the **canyon walls, wall-rock spurs and
  the Louros Valles tributary fans** — high thermal inertia, bedrock and coarse debris.
- **Classes 4–6 (orange/red, 50.7%)** blanket the **plateau** — the dust mantle.
- **Classes 7, 8, 10 (purple/magenta)** pick out crater ejecta and intermediate plateau
  texture.

**That is the dust-versus-bedrock discrimination the project exists to make, and it falls out
of the unsupervised run without any training data.** It is per-pixel and therefore speckled —
the remedy is the `SegmentMeanShift` already rehearsed (§7), applied to the composite
rather than to the bare DEM.

### 19.4 Task 11 scaffolded — the three landform feature classes exist

`build\make_landform_fcs.py` created them in `Mars Project.gdb`, empty and ready:

| Feature class | Geometry | Fields |
|---|---|---|
| `Landform_LavaFlowMargins` | POLYLINE | 10 |
| `Landform_ChannelCenterlines` | POLYLINE | 11 |
| `Landform_CraterRims` | POLYGON | 11 |

Common schema: `UnitName`, `Confidence` (certain/probable/inferred), `Evidence` (which band
the boundary came from), `Notes`, `MappedBy`, `MappedOn`. Plus per-class fields — channels
carry **`Origin` (fluvial / volcanic / indeterminate)**, which is the Athabasca Valles
question (§14.4) made into an attribute; craters carry `DiameterKm` and `Preservation`.

All three are in **`Mars_Equidistant_Cylindrical_CM180`**, matching the analysis stack (§18.1)
so lengths and areas are measured on the grid the mapping is done on. Equirectangular is
neither equal-area nor conformal, but across 6–13°S the scale error is under 2%. **[V]**

**These are empty scaffolding, not data.** The schema is a proposal — change it freely before
digitising starts, and it costs nothing to drop them.
---

## 20. Task 4 done for the type area — the z-factor defect is FIXED 2026-09-18 **[V]**

Prospectus task 4: *"Re-run Slope and Hillshade on the projected DEM so the z-factor is valid;
the current versions were computed against degree units and carry WARNING 000869."*

`build\make_typearea_terrain.py`, on `ius_dem.tif` — a **projected metric grid**
(`Mars_Equidistant_Cylindrical_CM180`, 100 m cells, linear unit Meter).

| Output | Time | min | max | mean | WARNING 000869 |
|---|---|---|---|---|---|
| `ius_slope_deg.tif` | 21.9 s | 0.000 | **71.792°** | 6.539° | **no** |
| `ius_slope_pct.tif` | 21.7 s | 0.000 | 304.001% | 12.028% | **no** |
| `ius_aspect.tif` | 19.4 s | −1.000 | 359.931 | 159.387 | **no** |
| `ius_hillshade.tif` | 7.0 s | 0.000 | 254.000 | 175.482 | **no** |

**The warning does not recur on any of the four.** It was never a quirk to live with — it was
the degree grid, exactly as §4 diagnosed, and projecting first removes it.

**These are the first terrain derivatives in this project with a valid z-factor.**

### 20.1 The numbers are physical, and they cross-check

Maximum slope **71.792° = 304.001% rise** — `atan(3.04001) = 71.792°` to three decimals.
The two independent runs agree exactly, which is a free internal validation.

Mean slope **6.54°** over the type area: gentle plateau, very steep chasma walls. Entirely
plausible for western Valles Marineris.

**Contrast with the broken global layer.** `Slope_Mars_H1` reports max **400.13** — percent
rise computed on a degree grid with z-factor 1. That number is not a slope in any unit; it is
an artefact. §7's rule stands for the *global* layers, but **the type-area layers supersede
them and may be quoted in degrees.**

> **Slope is now available in BOTH units, correctly.** Use `ius_slope_deg.tif` for anything a
> reader will interpret (channel gradients, flow-front steepness) and quote degrees. The
> percent version exists only so the old global layers have a like-for-like comparison.

### 20.2 A fix worth keeping: the rasters had no named CRS

`gdal.Warp` wrote a PROJ-derived WKT that **ArcGIS read as `spatialReference.name =
"unknown"`**. The coordinates were right, but an unnamed CRS makes tools, layouts and the
`Landform_*` feature classes disagree on paper.

**`build\make_typearea_stack.py` now does this itself**, immediately after the warp: it
relabels every output with an equivalent **named Esri WKT**,
`Mars_Equidistant_Cylindrical_CM180` — the same string the feature classes use (§19.4).
**This only renames; no pixel or coordinate is touched.**

The step began as a standalone script for the one-time repair, then was folded into the
stack script so **a warp can never again leave an unnamed CRS behind**. GDAL and ArcGIS
agree on the maths and disagree on the label, and the label is what ArcGIS keys on.
---

## 21. Audit round 2 — 2026-09-18 **[V]**

### 21.1 Two open questions closed

**q2 answered.** `Jezero_CTX_BlockAdj_dd_Clip` is a `CIMTiledServiceLayer` pointing at
`tiles.arcgis.com/.../Jezero_Crater_Clipped` — **the same service as the `Jezero Crater
Clipped` layer beside it**. Its `dataSource` does not return empty, it *raises*
`"not supported on this instance of Layer"`; whatever read it first swallowed the exception.
Nothing is broken or stripped: it is a duplicate of a hosted layer. See §5.

**q8 partly deduced.** Run 6 logged *"No compatible GPU device has been detected"* — an RTX
2080 Ti would have been detected, **so run 6 was the laptop, not the desktop**. The chain
depends on q10 (untested), so it is strong but not closed.

### 21.2 A display defect introduced by a scripted edit, caught by `audit_layers.py`

Adding the night mosaic with `addDataFromPath` gave it ArcGIS's **default**
`PercentMinimumMaximum 0.5/0.5`, while the day mosaic uses `StandardDeviations n=5, 2/2`.

**Flipping between day and night to judge thermal response would then be reading a stretch
artefact as much as the data** — and that comparison is the project's core method. The two
bands are near-identically distributed (day mean 125.75 σ 34.36, night 124.26 σ 32.79), so
there was no reason for them to differ.

Fixed by `build\fix_night_stretch.py` in **both working maps**; `.aprx` backed up first.

**Lesson: a layer added programmatically inherits defaults, not its neighbour's symbology.**
Check the stretch whenever a raster joins an existing comparison group.

*Still inconsistent, lower priority:* the DEM is `StandardDeviations n=2` in the viewer and
`Map3` but `PercentMinimumMaximum` in the `Mars` scratch map. Different maps, different
purposes — harmless unless those maps get used for comparison. **[?]**

### 21.3 Defect 1 fixed at the source, and the interim report rebuilt

`content.py` carried the wrong Composite Bands count in **three** places:

| Section | Feeds | Was |
|---|---|---|
| `TASKS` | prospectus (delivered) | "Three attempts at global scale" |
| `PROBLEMS` | prospectus (delivered) | "the tool logs record all three" |
| `ISSUES` | **interim (live)** | "Composite Bands has failed three times" |

All three corrected to **four attempts, ~2 h 22 m**, with the 13 Sep 17 min 28 s run named.
The prospectus is delivered and cannot be changed, but **`content.py` also feeds the interim
and the final**, so leaving a known-false fact in the source would propagate it forward.

`ISSUES` now also records the resolution — the bounded composite completing in 8.8 s with
100% co-valid pixels (§18) — so the interim reports a solved problem rather than an open one.

**The interim report was rebuilt** from the corrected source. Diff against the backup
(`NEXT STUFF\.backup_20260918\`) shows exactly **two** changes: the intended correction, and
*"crater inventory … in the type area"* → *"in sample windows"*. **The second was pre-existing
drift** — `content.py` had been edited after the 13 Sep build, so the shipped document was
already stale against its own source. Worth knowing that the built documents are not
automatically in step with `content.py`.

### 21.4 Blocked: the interim deck cannot be rebuilt **[?]**

`build_interim_deck.py` takes a **course-supplied `.pptx` template** as `sys.argv[1]` — it
reads `prs.slides[0]` and `[1]` and fills a skeleton whose bold labels and banner it
preserves. **That template is not on `Z:`.** A search finds `.pptx` files only inside
`Z:\$RECYCLE.BIN`.

So the interim **report** now carries the fix and the interim **deck** does not. Options, all
open decisions: recover the template from the Recycle Bin (a manual step, not a scripted one — §2.5), fetch it
again from SharePoint (not synced — §12), or edit the two affected slides by hand.

**Until then the deck and the report disagree about the attempt count.** That is worse than
both being wrong, so it should not be left.

> **⚠ Corrected 2026-10-08 (§39.2): this section blamed the wrong builder.** The deck in
> `NEXT STUFF\` (12 slides, the Presentation 1 style) was built by **`build_interim_le.py`**, which
> needs **no template**; it covers the template's headings in its own design. A test rebuild into
> scratch reproduces its 12 slide titles exactly and differs in exactly two lines, the defect-1 fix
> and "in sample windows". So the deck was rebuildable all along. The template-filling builder,
> `build_interim_deck.py`, is the alternative, and **the template is now on `Z:`** (placed in
> `NEXT STUFF\` on 2026-10-08). **[V]**
---

## 22. Task 13 started — the project has layouts now 2026-09-18 **[V]**

**§5 has said "11 maps, 0 layouts" since this file was written. That is no longer true.**
`build\make_typearea_layouts.py` builds a new map, **`Ius Chasma Type Area`**, holding the six
type-area products, and three 11 × 8.5 in layouts off it:

| Layout | Layer shown | Export |
|---|---|---|
| `01_visible` | Viking MDIM 2.1 | 2.4 MB |
| `02_night_ir` | THEMIS Night IR | 1.4 MB |
| `03_classification` | Iso Cluster, 10 classes, **with legend** | 0.8 MB |

PNGs at 150 dpi in `Z:\Mars Project\TypeArea\layouts\`, **~1.3 s each**. Each carries title,
subtitle, metric scale bar, north arrow, and a credit block naming the projection, sphere
radius, cell size and extent.

### 22.1 Four things that had to be got right, none of them obvious

**`arcpy.mp` has no `createTextElement` in Pro 3.x.** Titles and credits are built through the
CIM: a `CIMTextGraphic` (text + `CIMSymbolReference` wrapping a `CIMTextSymbol`, `shape` set to
an `arcpy.Point`) wrapped in a `CIMGraphicElement`, appended to `layout.getDefinition("V3")
.elements`, then `setDefinition`. `CIMPointGeometry` is **not** a creatable class — pass an
`arcpy.Point`.

**`createMapSurroundElement` wants a StyleItem OBJECT, not its name.** Passing the string
`"ArcGIS North 1"` fails silently-ish with the name echoed back as the error. Get it from
`p.listStyleItems("ArcGIS 2D", "NORTH_ARROW")` and match on `.name`.

**Match the frame to the data aspect or get white bands.** The stack is 8891 × 4150 = **2.14:1**;
a 10.1 × 6.30 in frame is 1.60:1 and left thick white margins top and bottom. The frame is now
`FR_W / DATA_AR` tall and computed from the data.

**A 10-class legend does not fit at default settings.** `el.isOverflowing` reports it
truthfully — worth asserting on. Fixed with `columnCount = 4`, headings and title suppressed
through the CIM, and the full band height under the frame.

### 22.2 A real cartographic defect in the default symbology **[V]**

**Iso Cluster's default colours gave class 2 and class 10 both pure red** — indistinguishable
on the map *and* in the legend, which makes the map wrong rather than ugly.
`recolour_classes()` applies a 10-colour qualitative set, ordered so wall-rock and debris
classes read cool and plateau dust reads warm. The map is now interpretable at a glance:
**blues and teals trace the chasma walls and the Louros Valles fans, oranges and reds blanket
the plateau** — the same structure §19.3 found in the statistics.

### 22.3 No graticule, and why **[?]**

**Three attempts to build `CIMGraticule` through the CIM rendered nothing.** The object accepts
`gridLines` carrying `gridLineOrientation` and a `CIMGridPattern` (`interval`/`start`/`stop`)
without raising, and still draws no lines; it also wants `mapGridEdges` and label components
whose classes are not creatable here — `CIMGraticuleLine` and `CIMSimpleMapGridEdge` both raise
`LookupError`.

**Rather than leave an invisible dead element on every sheet, there is none.** The credit block
states the extent instead. Adding a graticule in the Pro GUI takes seconds, so this is a
limitation of the *scripted* route, not of the project. Worth revisiting only if the sheets
need coordinate ticks.

### 22.4 What this changes

Every figure until now was matplotlib off the raw rasters — the data without the cartography.
**Both routes now exist and they are complementary:** `build\make_fig_*.py` for designed
figures in the deck's dark theme, and these layouts when a sheet should show the GIS itself,
with a scale bar and a legend. Ask which is wanted before building the next figure set.

`§5`'s "0 layouts" line and `§13.4`'s "the project has zero layouts" both now read against
this section.
---

## 23. Object-based classification — two method corrections 2026-09-19 **[V]**

The per-pixel classification (§19.3) is geologically coherent but speckled. Fixing that
turned up two things worth knowing before anyone repeats the workflow.

### 23.1 Measure the speckle, don't eyeball it

`build\verify_segmentation.py` reports, over one identical full-resolution window
(3200 × 2200 px across the chasma wall and the plateau):

- **boundary pixels** — the fraction with at least one 4-neighbour of a different class.
  High = salt-and-pepper.
- **mean run length** — the horizontal distance travelled before the class changes.

Both are cheap and make "did that help?" answerable instead of arguable.

### 23.2 The legacy tool classifies per pixel even when fed segments **[V]**

Running `IsoClusterUnsupervisedClassification` on a `SegmentMeanShift` output **cut speckle
only 11.1%**. It never treated the segments as objects — it just saw a smoother image.

The Image Analyst pair does respect them:

```
SegmentMeanShift -> TrainIsoClusterClassifier -> ClassifyRaster
```

Same segmentation, same 10 classes: **18.3% less speckle, runs 1.38× longer.** Better, and the
right tool — but still not the step change object-based classification should give, which
pointed at the parameters.

| method | boundary px | mean run (px) |
|---|---|---|
| per-pixel | 43.13% | 5.0 |
| segmented image, legacy classifier | 38.35% | 6.3 |
| **object-based, Image Analyst** | **35.22%** | **6.9** |

### 23.3 The Mercury segmentation parameters are the WORST case for de-speckling **[V]**

**In `SegmentMeanShift`, `spectral_detail` and `spatial_detail` run 1–20 and HIGHER MEANS MORE
DETAIL.** The parameters rehearsed on Mercury and carried over here — **spectral 20, spatial
20, minimum segment 5 px** — are the **maximum-detail setting**: the smallest segments the tool
can make. For de-speckling that is exactly backwards.

It also explains §7's Mercury run producing **65,474 segments**: not a property of the data,
a property of asking for maximum detail.

> **Do not treat 20/20/5 as "the project's segmentation settings."** They were a rehearsal
> default. Lower detail and a larger minimum segment give the coherent objects the landform
> mapping actually needs.

### 23.4 Two arcpy traps hit here **[V]**

**`TrainIsoClusterClassifier` returns the `.ecd` path, not a Raster.** Calling `.save()` on it
is wrong; `ClassifyRaster` returns the Raster.

**`ClassifyRaster(...).save(out)` holds a lock.** Reading the output back with a
`SearchCursor` in the same breath fails with *"Failed to open raster dataset … No such file or
directory"* even though the file is on disk. `del` the Raster first.

**And the recurring one:** `ds = gdal.Open(p); ds.GetRasterBand(1)` — chaining
`gdal.Open(p).GetRasterBand(1)` frees the dataset before the band is read and raises
*"argument 1 of type GDALRasterBandShadow *"*. Hold the dataset in a name.


### 23.5 The parameter sweep, measured — and it is not close **[V]**

Three segmentations over the same stack, each classified with Image Analyst, each measured on
the same window:

| method | params | cost | boundary px | mean run | vs per-pixel |
|---|---|---|---|---|---|
| per-pixel | — | — | 43.13% | 5.0 px | baseline |
| legacy classifier on segments | 20/20/5 | — | 38.35% | 6.3 px | −11.1% |
| object-based | **20/20/5** | 103 + 52 s | 35.22% | 6.9 px | −18.3% |
| object-based | **14/14/30** | 712 + 93 s | **12.99%** | 18.6 px | **−69.9%** |
| object-based | **9/9/80** | 817 + 87 s | **6.36%** | 37.3 px | **−85.3%** |

> **The parameters matter far more than the classifier.** Switching tools bought 7 points;
> changing detail bought another 52. Carrying the Mercury settings over was costing roughly
> **67 percentage points of de-speckling.**

**Recommended: 14 / 14 / min 30 px.** Not because it is the smoothest — 9/9/80 is — but
because of the project's own resolution rule. The prospectus states that **~10 pixels across a
feature are needed to map its margin, so at 100 m the limit is ~1 km** (§14). Medium gives a
mean run of **18.6 px ≈ 1.9 km**, just above that limit. Coarse gives **37.3 px ≈ 3.7 km**,
which is *below the project's own stated resolving power* — and it shows: in
`build\pres1_img\ius_segmentation_sweep.png` the coarse panel flattens the whole plateau into
one unit, losing structure that medium keeps, while still resolving the Louros Valles
tributary fans individually.

**Coarser is also slower, which is counter-intuitive.** 9/9/80 took **8× longer** than 20/20/5
(817 s vs 103 s) — lower detail means the mean shift merges across larger neighbourhoods and
iterates more. Do not assume "less detail" means "cheaper".

### 23.6 Segmentation does not scale to ±60° on this hardware **[V]**

The type area is **36.9 M px**; the ±60° stack is **15.18 bn px — 411× larger** (§16).

| params | type area | extrapolated to ±60° | desktop at an assumed 2.5× |
|---|---|---|---|
| 20/20/5 | 155 s | 17.7 h | ~7 h |
| **14/14/30** | 805 s | **92 h (3.8 days)** | **~37 h (1.5 days)** |
| 9/9/80 | 904 s | 103 h | ~41 h |

Even generously assuming the desktop is 2.5× faster — and §2.2 argues the USB bus caps that —
**the recommended parameters mean roughly a day and a half of continuous run.** That is a
serious claim on the calendar before 8 December, and it competes with pyramids and the global
Composite Bands retry (§11).

> **So object-based classification is a type-area technique for this project, not a global
> one.** That is a defensible methodological position, not a shortfall: the type area is where
> the landform mapping and validation happen (§14.3), and the global product is the
> co-registered mosaic itself. **Say so explicitly rather than implying a global classified
> map is coming.**
>
> If a global classified layer *is* wanted, the honest options are per-pixel Iso Cluster
> (already proven, hours not days) or segmentation at 20/20/5 (~7 h) accepting that it barely
> de-speckles. **Ask before committing desktop days to this.** **[?]**

---

## 24. The day–night pair, worked properly — 2026-09-19 **[V]**

§14.4 makes the project's strongest claim: day–night pairing converts brightness temperature
into **thermal inertia**, the best dust-versus-bedrock discriminator from orbit. Until now
that sat in the prose with one number behind it (§15.5's r = 0.098). This section turns it
into a layer, and corrects what it may be called.

Built by `build\make_typearea_thermal.py` (56 s, laptop) and
`build\make_fig_thermal.py` → `build\pres1_img\ius_thermal_contrast.png`.

### 24.1 Calibrated thermal inertia is NOT derivable from the held products **[V]**

The night mosaic's own ISIS label states it plainly:

```
Group = Pixels
  Type       = UnsignedByte
  Base       = 0.0
  Multiplier = 1.0
```

`Base 0 / Multiplier 1` on an unsigned byte means **there is no scaling to radiance or to
Kelvin**. The day mosaic is the same — its histogram runs 0–255 across 256 buckets. Both are
8-bit display products, **independently stretched by ASU**, and the stretches are provably
different:

| | mean | sd | p2 | p98 |
|---|---|---|---|---|
| day DN | 125.56 | 34.86 | **35** | 205 |
| night DN | 124.26 | 33.97 | **58** | 203 |

A 23-DN difference in the lower tie point alone. **So a raw `day − night` subtraction is not a
temperature difference and not thermal inertia** — it is the difference of two unrelated
stretches. It is kept as `ius_dn_diff.tif` (mean 1.30, sd 46.06) because a reader expects to
see it, labelled for what it is.

> `content.py` already says this correctly ("would require calibrated radiance … therefore a
> proxy, and will be described as one"). **The data now proves it rather than asserting it.**

### 24.2 What IS derivable: a relative diurnal-contrast index **[V]**

Scale each band by its own 2–98 percentile to [0,1] **first**, then difference. The result is
dimensionless, bounded [−1,1], and measures relative diurnal contrast *within the type area*
rather than an artefact of two stretches.

`ius_thermal_contrast.tif` — mean **+0.0757**, sd **0.2790**, p2/p50/p98 = −0.62/+0.11/+0.57.

- **HIGH (red)** = swings hard = low thermal inertia = **dust / fines**
- **LOW (blue)** = damped = high thermal inertia = **bedrock / coarse**

### 24.3 It is a material discriminator, not a restatement of topography **[V]**

This is the result worth defending, because the obvious objection is "you have just remapped
the canyon."

| against | r |
|---|---|
| day IR | +0.605 |
| night IR | −0.719 |
| Viking red | −0.237 |
| **elevation** | **+0.108** |
| **slope** | **−0.248** |

**|r| ≤ 0.25 against both terrain layers.** The index is built from the two IR bands, so the
first two rows are arithmetic, not information. What matters is the bottom two: the index is
very nearly independent of position on the slope and of elevation.

Per object-based class (`ius_obj_medium`, 14/14/30 per §23.5), sorted by index:

| class | % area | contrast | slope° | elev m | read as |
|---|---|---|---|---|---|
| 3 | 2.6 | **−0.467** | 13.3 | +2785 | wall outcrop, rocky |
| 5 | 3.8 | **−0.443** | 9.2 | +1105 | lower wall / floor bedrock |
| 2 | 5.2 | −0.268 | **21.5** | +1983 | the steep wall itself |
| 6 | 16.9 | −0.030 | 3.1 | +2987 | mixed plateau |
| 7 | 11.6 | +0.096 | 5.1 | +3291 | plateau |
| 1 | 3.7 | +0.134 | 11.3 | +951 | |
| 8 | 9.4 | +0.197 | **17.0** | **+43** | chasma floor, mantled |
| 9 | 43.4 | +0.202 | 2.1 | +3381 | dust-mantled plateau |
| 4 | 3.4 | **+0.261** | 5.3 | +3883 | highest, dustiest |

> **The argument in one line: classes 2 and 8 are the two steepest units in the scene, 4.4°
> apart in mean slope — and 0.46 apart in the index, at opposite signs.** Same steepness,
> opposite material. Terrain cannot produce that; material can.

Visually the map confirms it — the chasma walls, the Louros Valles tributary fans and the
**ejecta rings of fresh craters** come out blue against a red plateau. Ejecta blankets are the
control case: they are topographically trivial and thermally obvious.

### 24.4 Why this matters to the Athabasca hook

§14.4 frames the project around discriminating **volcanic from fluvial** channels, where
morphology alone has failed historically. The index is the second axis. `Landform_ChannelCenterlines` already carries an **`Origin`** field (§19.4); the index gives an evidence value
to put in it that is not morphology and not visible albedo.

### 24.5 A defect fixed at the source **[V]**

`build\make_fig_daynight.py` titled its third panel **"Day − Night — thermal-inertia proxy"**
over the *raw DN difference*. That is the exact overclaim §24.1 disproves. Relabelled to
"raw DN difference, not thermal inertia" and the figure rebuilt.

### 24.6 Two stale entries in `content.py` **[?]**

The risk register still carries *"Thermal inertia is not yet possible — only the THEMIS day
mosaic is held"* (~line 385) and *"Thermal inertia is blocked on a missing dataset"* (~line
500). **The night mosaic was acquired 2026-09-18** (§15). Both entries are now false. They are
document prose rather than data, so they are flagged here rather than edited — **an open decision**.

---

## 25. Candidate channel centrelines — task 11 seeded, with one large trap 2026-09-19 **[V]**

Digitising is the critical path and it needs manual judgement, but it should not start from a blank
canvas. `build\make_channel_candidates.py` derives **candidate** centrelines from the DEM by
flow routing and attributes each one with the diurnal-contrast index (§24), so every candidate
arrives pre-triaged on the axis that bears on the Athabasca question.

**They go to a separate feature class, `Landform_ChannelCandidates_auto`.**
`Landform_ChannelCenterlines` was left untouched — machine candidates must not be mixed into
the manual digitising class. Every row is `Confidence='inferred'`, `Origin='indeterminate'`,
`MappedBy='auto-candidate (flow accumulation)'`.

### 25.1 The trap: `Fill` floods Ius Chasma, and half the network was artefact **[V]**

Ius Chasma is a **closed basin**. `Fill` does what it is designed to do and floods it into a
flat synthetic lake, and `FlowAccumulation` then routes happily across that surface. Measured
on `fill − dem`:

| | |
|---|---|
| scene raised at all (>1 m) | **21.8%**, 80,238 km² |
| raised > 100 m | 9.1% |
| **maximum raise** | **2,077 m** |
| mean elevation of raised ground | +1,218 m (scene mean +2,620 m) — i.e. the chasma floor |
| **stream cells sitting on filled ground** | **56.1%** |

> **Over half of the first candidate network was a routing artefact across a surface that does
> not exist.** It looked entirely plausible on screen — long, smooth, dendritic trunk lines
> down the middle of the chasma. Nothing about the output announced it.

The fix is a mask, not a parameter: keep only cells where `fill − dem ≤ 1 m`. The script now
measures the discard on every run and prints it, and carries `FillDepthM` per segment as an
audit field — it reads **mean 0.073 m, max 0.889 m** across the kept set, as designed.

**This generalises.** Any hydrology tool run on Valles Marineris, Hellas, or any crater
interior has the same problem. `Fill` also flooded **every crater in the scene** — the bright
dots in panel B of `build\pres1_img\ius_channel_candidates.png`.

### 25.2 What came out, and which part of it is worth the time **[V]**

2,610 candidates, **15,428 km**, mean 5.9 km, median 4.2 km, longest 58.2 km. Threshold:
> 5,000 upslope cells (50 km² catchment), segments < 2 km dropped (twice the project's own
~1 km resolving limit, §23.5).

| mean slope | n | km | mean thermal index |
|---|---|---|---|
| **< 2° (plateau)** | **1,661** | 10,072 | +0.122 |
| 2–5° | 253 | 1,180 | +0.128 |
| 5–10° | 308 | 1,725 | +0.026 |
| **> 10° (wall)** | **388** | 2,451 | −0.033 |

> **Be honest about this: 64% of the candidates sit on plateau under 2° of slope.** The source
> DEM is a 200 m HRSC/MOLA blend resampled to 100 m; on a near-flat dust-mantled surface, flow
> routing finds paths in DEM noise. Seven of the eight longest candidates are on slopes under
> 0.7° — length is not evidence here. **The plateau set is a prompt to look, not a result.**

The subset worth attention is the steep one. **188 candidates, 1,037 km, on slopes ≥ 5°
with a thermal index < −0.15** — steep *and* rock-floored. Those are the best lava-channel
candidates in the scene, and the query that finds them is one `SelectLayerByAttribute` away.

Removing the fill artefacts also **doubled the rock-floored share of the network, 7.0% → 11.0%** —
the artefacts were flooring the chasma with mantled-signature lines.

### 25.3 Schema and cost

Fields: `UnitName`, `Origin`, `Confidence`, `Evidence`, `StrahlerOrd`, `LengthKm`, `ThermIdx`,
`ThermSd`, `SlopeDeg`, `FillDepthM`, `Notes`, `MappedBy`, `MappedOn` — a superset of §19.4's
channel schema, so accepted rows copy straight across.

**Cost: 4.5 min cold, 2.2 min warm** on the laptop. `Fill` / `FlowDirection` /
`FlowAccumulation` are cached to `ius_fill/fdr/fac.tif` and reused; only the threshold and
downstream steps re-run, so **sweeping `THRESH` is cheap.** Strahler order tops out at 3
because the network is truncated at the chasma rim — that is correct, channels do end there.

### 25.4 What this unblocks

The candidates give the supervised half of task 7 (§ task plan) something to select against,
and they give task 11 a starting geometry. **They are not a landform map and must not be
reported as one** — `Confidence='inferred'` on every row is the guard.

---

## 26. Task 12 from zero — a crater inventory, and an honest detection limit 2026-09-19 **[V]**

The project's only crater data is the IAU gazetteer, and §14/§25 already say what is wrong
with it: **141 named craters >100 km and 972 <100 km, planet-wide, is a name list, not an
inventory**, and size-frequency dating cannot be done from it.

The detector falls straight out of §25.1. **`Fill` floods every closed depression — which is
what a crater is, topographically.** `ius_filldepth.tif` was therefore already a crater
raster; it needed thresholding, shape-filtering and measuring, not new processing.
`build\make_crater_candidates.py`, **49 s**, laptop.

### 26.1 The gazetteer is empty over the type area — which is the argument for doing this **[V]**

**There are ZERO named craters in 271–286°E, 6–13°S.** The nearest are **Oudemans** (124.2 km,
268.23°E 9.84°S) and **Perrotin** (82.8 km, 282.06°E 2.82°S), both just outside the box.

> So over the type area the gazetteer contributes **nothing at all** — not a sparse sample, an
> empty one. Any crater statement about Ius Chasma has to come from measurement. **That is the
> case for task 12, and it is stronger than "the gazetteer is incomplete."**

It also means the detector cannot be validated in place, which is why §26.3 goes to the
craters instead.

### 26.2 What came out **[V]**

10,164 closed depressions deeper than 20 m; **1,685 survive the filters**, each of which has a
reason:

| filter | value | why | dropped |
|---|---|---|---|
| min depth | 20 m | below this is noise in a 200 m blend | — |
| min diameter | 1.0 km | the project's own resolving limit (§23.5) | 7,551 |
| max aspect | 2.0 | craters are round; the chasma is not | 529 |
| min fill ratio | 0.55 | area / bbox; a perfect circle gives π/4 = 0.785 | 1,116 |

Diameters: min 1.00, **median 1.46**, max 31.4 km. **1–2 km: 1,233 · 2–5 km: 364 · 5–10 km: 61
· 10–20 km: 22 · 20–50 km: 5.** Median depth/diameter **0.0453** (p10 0.0265, p90 0.1035) —
low against a fresh simple crater's ~0.2, as it must be: the detector measures **depth below
the lowest rim pass**, not true crater depth, and most of these are degraded and infilled.

Each candidate also carries the §24 thermal index. **Candidates average +0.124 against a scene
mean of +0.0757** — crater interiors are dust-mantled relative to their surroundings, which is
what a sediment trap should look like.

### 26.3 Validated on two named craters — one hit, one instructive failure **[V]**

`build\verify_crater_detection.py` builds two ~25–30 Mpx windows around Oudemans and Perrotin
and runs the **identical** detector. 179 s including both DEM warps and both `Fill` runs.

| | IAU | detected | centre error | verdict |
|---|---|---|---|---|
| **Perrotin** | 82.8 km | **77.0 km** | 1.95 km | **hit, −7.1%**, rank **1 of 1,321** |
| **Oudemans** | 124.2 km | — | — | **MISS** |

**Perrotin is recovered as the single largest candidate in its window**, aspect 1.03, fill
ratio 0.71. On a well-preserved crater the method is good to better than 10% on diameter.

**Oudemans is not found at any filter setting, and the reason is physical, not a tuning
problem.** Measured directly on the DEM:

- fill depth inside the crater: **mean 4.76 m**, only **5.56%** of pixels over 20 m
- rim elevations around the circle: min **2,145 m**; crater floor (p2) **2,178 m**
- **the lowest rim point sits 33 m BELOW the floor**, and **35 of 360 rim samples** are within
  100 m of floor level

**Oudemans is breached into the canyon system. It is not a closed depression, so `Fill` has
nothing to fill and the detector cannot see it.**

> ### The limit, stated plainly
>
> **This method finds closed depressions. A crater whose rim is breached is invisible to it** —
> and in a canyon type area that is exactly the population of most interest, because a breached
> rim is itself evidence of fluvial or collapse modification. **Breached craters must be
> digitised by hand.** Do not report the candidate count as a complete inventory; report it as
> a complete inventory *of closed depressions* ≥ 1 km.

### 26.4 The filters were tuned on the evidence, not by eye **[V]**

The sweep, each row the same detector at a different setting:

| aspect ≤ | fill ≥ | Perrotin error / rank | Oudemans |
|---|---|---|---|
| 2.5 | 0.45 | −7.1%, rank 2 / 1,779 | miss |
| 2.2 | 0.50 | −7.1%, rank 2 / 1,566 | miss |
| **2.0** | **0.55** | **−7.1%, rank 1 / 1,321** | miss |
| 1.8 | 0.60 | −7.1%, rank 1 / 1,037 | miss |
| 1.5 | 0.65 | −7.1%, rank 1 / 693 | miss |

**2.0 / 0.55 is the chosen point:** it is the loosest setting at which the truth crater is the
top-ranked candidate. It also removes a **140.9 km "crater"** (aspect 2.39) that the original
2.5 / 0.45 admitted — a fragment of the chasma, not an impact structure. Tightening further
buys nothing and starts discarding real craters.

### 26.5 Where it lives

`Landform_CraterCandidates_auto` (polygon, 1,685 rows) — **separate from `Landform_CraterRims`,
which stays manual**, exactly as §25 did for channels. Fields: `DiameterKm`, `DepthMaxM`,
`DepthMeanM`, `Aspect`, `FillRatio`, `ThermIdx`, `CenterLon`, `CenterLat`, `IAUName`,
`Preservation`, plus the common schema. Every row is `Confidence='inferred'`,
`MappedBy='auto-candidate (fill-depth detection)'`.

Figure: `build\pres1_img\ius_crater_candidates.png` — the map, the size-frequency
distribution, and **both validation windows including the failure**. Showing the miss is the
point; a validation figure that only shows the hit is advertising.

---

## 27. Task 7 supervised — the project's first accuracy assessment 2026-09-19 **[V]**

> **⚠ 2026-10-01: the 1,604 terrain polygons below are no longer in the gdb.**
> `Landform_TrainingSamples_terrain` now holds the 512 hand-drawn labels. The script that built this
> section used to delete that class; **since 2026-10-01 it writes
> `Landform_TrainingSamples_terrain_auto` and refuses to delete what it did not write** (§29.8).
> The figures below stand as measured; a re-run rebuilds the 1,604 polygons in the new class.

§19.2 established that Iso Cluster → ML Classify is a **no-op**: re-classifying auto-generated
signatures teaches nothing. The supervised half needs labels the classifier did not invent.
`build\make_typearea_supervised.py`, ~17 min on the laptop for three runs.

### 27.1 Two design choices that decide whether the number means anything **[V]**

**Labels come from TERRAIN ALONE** — slope, elevation, and §26's crater mask. Not one of the
five spectral bands touches a label. The obvious alternative, seeding from the object-based
classification, would score a classifier against labels it generated. With terrain labels the
number answers a real question: **how much of the landform structure is visible spectrally?**

**Train and test are SPATIAL BLOCKS**, a 10 × 6 checkerboard, not random pixels. A random
pixel split in remote sensing sits a test pixel next to its own training pixel; neighbouring
pixels are not independent samples and the accuracy inflates badly. Class cores are eroded 2 px
so no label sits on a mixed boundary pixel. **1,604 training polygons**, in
`Landform_TrainingSamples_terrain`; **13,901,945 held-out test pixels.**

### 27.2 The headline, and it is honest **[V]**

| stack | overall accuracy | kappa | |
|---|---|---|---|
| **the 5-band composite** | **62.7%** | **0.406** | the clean number |
| + diurnal-contrast index | 63.1% | 0.409 | **+0.4 pt** — also clean |
| + index **and** slope | 82.6% | 0.682 | **circular**, upper bound only |

Against a 16.7% random baseline for six classes, **62.7% / κ 0.41 is a real result**: the
spectral stack alone recovers terrain-defined geomorphic units with moderate agreement.

> **The third row must never be quoted as a result.** Slope is both a band in that stack and an
> input to the class definitions, so it is partly predicting its own labels. It is in the table
> to show the ceiling, and to be honest that the ceiling is unearned.

### 27.3 The uncomfortable one: the thermal index adds +0.4 points **[V]**

On this task the diurnal-contrast index — the product §24 was built for, and the reason the
night mosaic was acquired — is worth **four tenths of a point.**

**That is not a failure of the index. It is a confirmation of §24.3, and the two results agree
exactly.** §24.3 measured the index at **r = +0.108 against elevation and −0.248 against
slope** and concluded it is a *material* discriminator, nearly independent of terrain. §27's
classes are *terrain* classes. **A band that is orthogonal to terrain cannot help predict
terrain, and it didn't.** The prediction and the measurement were made independently and match.

> **So the real conclusion is methodological: terrain-derived labels cannot price the thermal
> index, by construction.** Measuring what the night mosaic bought requires **material**
> labels — dust versus bedrock versus flow — and those cannot be generated from a DEM. They
> require photo-interpretation.
>
> **This is the strongest argument yet for hand digitising** (§25, task 11): it is not
> merely the remaining task, it is the only way to demonstrate the project's central claim.

### 27.4 Per-class, where the failures are informative **[V]**

Spectral stack, producer / user accuracy:

| class | producer | user | n test | read as |
|---|---|---|---|---|
| wall_steep | **74.2%** | 74.2% | 1,601,902 | the walls are spectrally distinct |
| chasma_floor | **72.3%** | 39.2% | 2,021,560 | found, but over-predicted |
| plateau | 62.8% | **92.2%** | 9,462,727 | when it says plateau, it is right |
| crater_interior | 16.1% | 8.2% | 567,459 | **craters are topographic, not spectral** |
| plateau_flank | 19.7% | 3.5% | 169,192 | thin transitional band |
| wall_moderate | 2.4% | 3.4% | 79,105 | thin transitional band, 28,718 training px |

**`crater_interior` at 16.1% is a result, not a defect.** A 1–2 km crater interior is made of
the same material as the plateau around it — §26 found exactly this, that candidates sit only
+0.05 above the scene mean on the thermal index. **Craters are a topographic class. Do not
expect a spectral classifier to find them, and do not present the crater candidates as
spectrally derived.**

The two thin transitional classes fail because they are narrow bands: erosion at 4 px had left
`wall_moderate` just **1,918 training pixels of 540,901**, which is why the core erosion was
reduced to 2 px. Even at 28,718 they are too thin to learn. **Either widen them or drop them.**

### 27.5 Two silent traps, and a 2.1% that was a bug **[V]**

The first run reported **2.1% overall accuracy** — *below* the 16.7% random baseline, with
`plateau` (63% of test pixels) never predicted once. **Below-random with an unpredicted
majority class is a bug signature, not a weak model.** Both causes:

- **`ClassifyRaster` writes VALUE 0…n−1, not the class codes.** The real class is in the
  output raster's **VAT `Classvalue`** column. Comparing raw VALUE against labels 1–6 shifts
  every class by one. **Always build the VALUE→Classvalue map from the VAT.**
- **`BuildVRT(..., separate=True)` inherits a different NoData from every source.** Stacking
  the composite (NoData 0), the index (−9999) and slope (−3.4e38) produced a raster with three
  NoData values; that classifier collapsed to one class across **98.6%** of pixels and wrote a
  meaningless `nodata=3.0`. **Build a mixed-type stack by hand with one sentinel no band can
  legitimately take.**

Figure: `build\pres1_img\ius_supervised.png`.

---

## 28. The products move to the analysis extent — `Global60` 2026-09-19 **[V]**

> **Read §28.10 first if this section is being used for anything about thermal
> discrimination.** Building the index at ±60° is what made it testable against known
> geology, and it failed: the THEMIS mosaics are locally normalised, so the index is a
> local contrast field and not a material map.

**Instruction, verbatim: the data produced must be for the global mosaic, not just a
specific type area, and it must sit "in the same content area as the mosaics I've downloaded
and the data mosaics that live with them."**

Correct, and §18–26 had drifted. Every derived product in this project was `ius_*` — the
Ius Chasma box, 8891 × 4150, **0.24% of the analysis extent**. The type area was the correct
place to prove each method and a wrong place to leave them.

### 28.1 One grid, read from the night mosaic rather than written down **[V]**

§16.4 already said *"clip or snap everything to the night raster's extent."* That is now code,
in **`build\grid60.py`**, and it **reads the grid off the file** every time instead of
hardcoding a table — so a product built through it is co-registered by construction and cannot
silently drift, which is §4's whole lesson.

| | **G100** | **G200** |
|---|---|---|
| size | 213,388 × 71,130 | 106,694 × 35,565 |
| cell | 100 m | 200 m |
| pixels | **15.178 bn** | 3.795 bn |
| origin | −10,669,400 , +3,556,500 | identical |
| footprint | ±60.0003° lat, 359.9985° lon | identical |
| CRS | `Mars_Equidistant_Cylindrical_CM180`, R = 3,396,190 m | identical |
| vs type area | **411×** | 103× |

`G200` is an exact 2 × 2 aggregation of `G100` — same origin, same footprint, every 200 m cell
edge falling on a 100 m cell edge. The two overlay without a reproject.

Outputs go to **`Z:\Mars Project\Global60\`**, beside `TypeArea\`, with **`Z:\Global60`** as
the junction for the legacy Spatial Analyst tools that reject the space (§19.1). A `README.md`
in the folder states the grid and the two caveats below.

### 28.2 Two measurements that made a 15-billion-pixel product tractable on the laptop **[V]**

**The day and night mosaics are pixel-aligned to the integer.** Re-verified: the day mosaic
sits at exactly **+1 px in x and +17,783 px in y** from the night grid, both exact integers.
So on G100 the THEMIS pair is a plain **window read** — no warp, no interpolation, no
temporary copy. §15.3 said the grids align; this says what that is worth, which is the
difference between a 36-minute job and an impossible one.

**The DEM is already on G200, to 10 microns.** HRSC/MOLA's 0.0033741208° is **199.999990 m**
on this sphere — drifting **0.005 px across the full 106,694-column width**. Tested rather
than assumed, on a 512 × 512 window near Ius:

| warp to G200 | pixels identical to source | max difference |
|---|---|---|
| **nearest neighbour** | **262,144 / 262,144 = 100.0000%** | **0 m** |
| cubic | 63.74% | 28 m (mean 1.7 m over altered pixels) |

> **So the ±60° terrain derivatives are computed on the real MOLA/HRSC elevations, and the
> type-area ones are not.** `ius_dem.tif` had to cubic-resample to reach 100 m, which altered
> 36% of its pixels by up to 28 m; `ius_slope_deg.tif` is a slope of that interpolation. This
> is not a defect in §20 — at a 100 m target it was unavoidable — but it is a reason to prefer
> the ±60° products for any *quantitative* terrain claim.

**The rule this settles: imagery products at 100 m, DEM products at 200 m.** Running terrain
at 100 m costs 4× and manufactures detail that was never measured.

### 28.3 The diurnal-contrast index at ±60° — built, 36.3 minutes **[V]**

`build\make_global_thermal.py`. **`global60_thermal_contrast.tif`**, Int16 × 10000,
nodata −32768, **25.57 GB** (1.19× compression).

It is tractable because the index is a **byte lookup**: both inputs are uint8 and the index
depends only on the two byte values, so two 256-entry tables compute it exactly with no float
array anywhere. Peak RAM is one 512-row strip.

| | ±60° (G100) | Ius type area (§24.2) |
|---|---|---|
| co-valid pixels | **14,776,942,885 / 15,178,288,440 = 97.36%** | 100.00% |
| mean | +0.0597 | +0.0757 |
| sd | 0.2905 | — |
| p2 / p50 / p98 | −0.613 / +0.075 / +0.626 | — |

> **The two are NOT comparable.** The stretch is computed over ±60° here and over the type
> area there. Quoting a value from one against the other is a mistake waiting to happen —
> which is why the README says so and this table pairs them once, explicitly.

**It is not a latitude artefact — checked, because it had to be. [V]** If a day−night index
scaled across a hemisphere were tracking illumination or season rather than material, it would
show as a latitude gradient. Sampled over 31.5 Mpx in 40 latitude bands × 12 longitudes:

- correlation of band mean with |latitude|: **r = −0.237**
- spread of band means **0.1455**, against a within-band sd of **0.286**

**Latitude explains about half as much as the scatter inside any one band**, so there is no
illumination gradient masquerading as signal.

> **⚠ This section originally concluded that the dust/bedrock reading therefore "survives
> the scale-up" and justified using the index planet-wide. That was WRONG and is
> retracted — see §28.10.** Ruling out one suspected artefact is not evidence of signal.
> Tested against actual geology, the index separates dusty from rocky provinces by
> **−0.0009**, because both THEMIS mosaics are locally contrast-normalised.

### 28.4 What is built, what is staged, and the reason for the split

Decided 2026-09-19: run the cheap tier on the laptop, stage the rest for the desktop.

| script | product | grid | where |
|---|---|---|---|
| `make_global_thermal.py` | diurnal-contrast index | G100 | **done, 36.3 min** |
| `make_global_terrain.py` | DEM, slope°, aspect, hillshade | G200 | **done, ~27 min (§28.8)** |
| `make_global_landforms.py` | crater + channel candidates | G200 | **smoke-tested; coarse pass DONE, fine pass ~7 h (§28.11)** |
| `make_global_stack.py` | harmonised bands + Composite Bands | G100 | **smoke-tested; ~150 GB (§28.11)** |
| `verify_global60.py` | co-registration gate | — | seconds |
| `make_fig_global60.py` | ±60° figure, and pyramids | — | after the above |

**`verify_global60.py` is the thing that makes "same content area" checkable rather than
claimed.** It tests every product's four corners to the millimetre, its cell size, its shape,
its CRS name and central meridian, and — for 200 m products — that it nests on the 100 m grid.
Non-zero exit on any failure. Run it after every ±60° job.

### 28.5 Segmentation is still out, and that has not changed **[V]**

§23.6 measured that segmentation does not scale to ±60° on this hardware. Nothing here
changes that. **`make_global_landforms.py` deliberately contains no segmentation step** — the
±60° landform work is flow routing and fill-depth detection, which tile; segmentation does not.

### 28.6 Two limits that get bigger at ±60°, not smaller

Both are §25.1 and §26.3, and scaling the extent scales the problem:

- **`Fill` floods closed basins**, and at ±60° the closed basins are Valles Marineris, **Hellas,
  Argyre, Isidis** and every crater interior — not one canyon. The fill-depth mask is applied
  per tile and the discard fraction is measured and printed per tile, because at this extent
  nobody can eyeball whether it worked.
- **The detector finds closed depressions, so breached craters stay invisible.** Oudemans is
  the worked example (§26.3). At ±60° the honest description of the output is unchanged:
  *a complete inventory of closed depressions ≥ 1 km*, never *a crater inventory*.

`make_global_landforms.py` therefore runs **two scales**: the whole extent decimated 8× to
1600 m and filled in one piece, to catch basins ≥ 20 km with no tile seams at all, plus 8192 px
tiles with a **1024 px (205 km) halo** for everything smaller. Only candidates whose centroid
lands in a tile core are kept, so seams neither duplicate nor drop. It checkpoints every
tile and skips completed ones on re-run — a crash in hour six costs one tile.

### 28.7 A bug worth recording, because testing is what caught it **[V]**

`Grid.warp_kwargs()` already sets `resampleAlg`, and **three call sites passed it a second
time** — `TypeError: got multiple values for keyword argument 'resampleAlg'`. Every one of
them would have died at its first warp, minutes into a run. They were found by warping a
512 × 512 test window before launching anything, not by reading the code.

> **The lesson, sharpened: on jobs measured in hours, test the call on a window first.**
> A 3-second test caught what would otherwise have been three separate failed runs.

### 28.8 Terrain at ±60° — task 4 done at analysis-extent scale **[V]**

`build\make_global_terrain.py`, on G200. All four pass `verify_global60.py`.

| product | type | size | min | max | mean | sd |
|---|---|---|---|---|---|---|
| `global60_dem.tif` | Int16 | 3.21 GB | — | — | — | — |
| `global60_slope_deg.tif` | Float32 | 7.04 GB | 0.000° | **52.698°** | **2.186°** | 3.457 |
| `global60_aspect.tif` | Float32 | 8.03 GB | 0.000° | 359.944° | 177.157° | 106.896 |
| `global60_hillshade.tif` | Byte | 1.30 GB | 1 | 255 | 180.055 | 9.099 |

**Slope is in DEGREES on a projected metric grid, so it may be quoted** — unlike the global
`Slope_Mars_*` layers in the gdb, which are PERCENT_RISE computed on a degree grid (§7).
`WARNING 000869` cannot arise here: `gdaldem` is used, not the legacy Spatial Analyst tool,
and the grid is metric.

> **Mean slope over ±60° is 2.19°, against 6.54° over the Ius type area (§20).** That is the
> expected direction and a useful sanity check: the type area is a canyon system and is three
> times steeper than the band as a whole. **Maximum slope is 52.7° at 200 m, against 71.8° at
> 100 m over Ius** — also expected, because slope is resolution-dependent and a 200 m cell
> averages across what a 100 m cell resolves. **Do not quote the two maxima against each
> other**; they are measurements at different support.

### 28.9 A timing trap: the scripts report WALL CLOCK, and the laptop sleeps **[V]**

`make_global_terrain.py` printed **`done in 9:15:10`**, of which the DEM warp claimed
**8:53:32**. That is not the cost of the job. Measured directly afterwards, by warping a real
full-width slice of the same job and extrapolating:

| | measured | implied whole job |
|---|---|---|
| DEM warp, 106,694 × 2,048 slice (5.76% of the job) | 18.8 s | **0.09 h ≈ 5.5 min** |
| same-CRS control, night mosaic, same pixel count | 10.4 s | — |
| **cost of the CM 0 → CM 180 roll** | **1.8×** | — |

**So the real terrain cost is about 27 minutes — 5.5 for the warp and 21 for the three
derivatives — and the other 8.7 hours were the laptop asleep.** The run started 03:06 and
finished 12:21 unattended.

Two things follow, and the second is the one that matters:

1. **An elapsed time printed by any script here includes suspend time.** §8 already warned
   that the logged run times are not attributable to a machine; this is the concrete
   mechanism. **Never quote a script's own elapsed figure as a cost without a rate check.**
2. **A first reading of this log said the scanline-blocked source made the warp pathological,
   and that was wrong.** The roll costs 1.8×, not 100×. It was retracted within the hour
   because the slice test was run instead of the explanation being believed. **This is exactly
   the failure mode §4 is about — a plausible story that fits the numbers and is not true.**

**Before any multi-hour run on the laptop, disable sleep** (Windows power settings, or the
desktop app's keep-awake preference). Otherwise an overnight job's timing is uninterpretable
even when its output is perfect — which here it was: all five products pass co-registration.

### 28.10 The THEMIS mosaics are LOCALLY NORMALISED — the thermal index does not scale **[V]**

**This is the most important finding of 2026-09-19 and it constrains the project's central
claim. Read it before writing anything about thermal discrimination.**

Building the index at ±60° made it testable against known geology for the first time, and it
failed that test. Sampled over seven provinces whose thermal-inertia contrast is textbook:

| province | index mean | sd |
|---|---|---|
| Arabia Terra — bright, **dusty**, low TI | +0.0597 | 0.193 |
| Amazonis — **dustiest** on the planet | +0.0574 | 0.131 |
| Tharsis dust | +0.0578 | 0.146 |
| Syrtis Major — dark, **rocky**, high TI | +0.0633 | 0.204 |
| Acidalia — dark, rocky | +0.0607 | 0.231 |
| Hellas floor | +0.0539 | 0.228 |
| Valles Marineris — bedrock walls | +0.0590 | 0.234 |

> **Separation of dusty from rocky provinces: −0.0009.** Zero, and faintly the wrong sign,
> against within-province scatter of 0.13–0.23. **Syrtis Major and Arabia Terra — one of the
> strongest thermal-inertia contrasts on Mars — are indistinguishable in this index.**

**The cause is in the source mosaics, not in the index.** Reading the *identical* boxes from
all three products, with Viking as the control:

| | day IR | night IR | **Viking red** |
|---|---|---|---|
| dusty provinces | 125.61 | 124.50 | 123.50 |
| rocky provinces | 125.80 | 124.49 | 75.82 |
| **difference** | **−0.19** | **+0.02** | **+47.67** |

Viking, from the same boxes, separates the provinces by **47.67 DN** — so the sampling is
correct and the geography is right. That is the control that makes this conclusive.

And the signature is unmistakable once the spread is included:

| | day DN | night DN | Viking R |
|---|---|---|---|
| Arabia Terra | 125.6 ± 34.1 | 124.4 ± 30.9 | 122.1 ± 20.3 |
| Amazonis | 125.5 ± 31.1 | 124.5 ± 29.2 | 124.9 ± 14.0 |
| Syrtis Major | 125.6 ± 32.6 | 124.2 ± 32.6 | **67.3** ± 23.3 |
| Acidalia | 126.0 ± 34.1 | 124.7 ± 32.8 | **84.3** ± 25.9 |
| *whole mosaic (§3)* | *125.75 ± 34.36* | — | *122.84 ± 31.58* |

**Every province reproduces the mosaic-wide mean AND the mosaic-wide spread in both THEMIS
products.** A region cannot do that unless it was stretched to fill the range independently.
**Both THEMIS mosaics are locally contrast-normalised: their DN is local contrast, not
radiance.** Viking is not normalised that way and keeps its real albedo differences.

*(The spatial unit of the normalisation — per image strip, per tile, per mosaic sheet — is
not measured here. It does not need to be for the conclusion, but it is worth knowing before
choosing a window size for any local work. **[?]**)*

#### What this does and does not break

- **§24.3 stands.** Within the type area the stretch is approximately constant, so DN
  differences there *are* meaningful and the index *is* a material discriminator at that
  scale. The measured type-area result is not retracted.
- **§24 must not be extrapolated.** The index is a **local** contrast field. Two values from
  different parts of the planet are not comparable, and neither are the type area and ±60°
  (§28.3 said that for the stretch; this says it for the physics).
- **`global60_thermal_contrast.tif` is correctly computed and still useful** — as local
  texture, for per-object attribution inside a window, exactly as
  `make_global_landforms.py` uses it. **It is not a material map and must never be published
  as one.**
- **§28.3's latitude check was right but its conclusion was too strong.** There is no latitude
  gradient — that part holds. But "the dust/bedrock reading survives the scale-up" was
  inferred from the absence of one artefact, not demonstrated against geology. It is wrong,
  and the province test is what a real check looks like. **Absence of a suspected artefact is
  not evidence of signal.**

#### What to do instead, for anything planet-scale

1. **Visible albedo carries the regional material signal and is already on disk.** Viking
   separates dusty from rocky terrain by 47.67 DN. **For ±60° material discrimination, lead
   with Viking**, not with the thermal pair. This raises the value of
   `make_global_stack.py` considerably.
2. **Calibrated thermal products would be needed to do this thermally** — ASU's TES or THEMIS
   thermal-inertia maps, not the 8-bit display mosaics held here. Not on disk (§3), and
   acquiring one is a decision, not a tweak. **[?]**
3. **Reframe the hook honestly** (§14.4). Day–night pairing as *the* planet-scale dust/bedrock
   discriminator is not supportable with these products. As a *local* discriminator, measured
   and validated on the type area, it is — and the Athabasca argument was always local.

### 28.11 The staged scripts are smoke-tested, and the basin pass is already done **[V]**

§28.7's lesson, applied to the two scripts that had never been run. Both now carry a
`--smoke` mode that retargets them at a small window over Ius Chasma with separately named
outputs, so the desktop run is not their first execution.

```
python make_global_landforms.py --smoke --skip-coarse --max-tiles 1
python make_global_stack.py --smoke
```

**`make_global_stack.py --smoke`: 20 s.** Harmonise ×3, both composites, CRS relabel. Checked
rather than assumed: all five outputs land on the target grid with the named CRS, nest on
G100, and **band 4 of the composite is bit-identical to the standalone day raster** — the VRT
stacking is not silently reordering or resampling anything.

**`make_global_landforms.py --smoke`: 9 min**, of which **8.5 min was the one-off 200 m
thermal resample**, now cached. The tile itself took 37 s and every downstream step ran:
Fill → FlowDirection → FlowAccumulation → fill mask → StreamLink → StreamOrder →
StreamToFeature → zonal statistics → checkpoint → merge → two feature classes → thermal
attribution.

Two numbers from it that are results, not diagnostics:

- **Fill-artefact discard 46.2% of stream cells**, against 56.1% at Ius (§25.1). The mask is
  doing the same job at this scale and is not optional.
- **Crater density 4.85 × 10⁻³ /km², against 4.56 × 10⁻³ /km² for the type-area run at 100 m**
  — within 6%, despite half the resolution. The 200 m detector is not finding a different
  population.

#### The full run costs 7 hours, measured rather than extrapolated

| tile | pixels | time |
|---|---|---|
| 2560 × 2560 | 6.55 Mpx | 37.0 s |
| 5120 × 5120 | 26.2 Mpx | 123.4 s |

4× the pixels for **3.34×** the time — slightly sub-linear, so `Fill` is behaving. Projecting
to the real 10240 × 10240 tile gives ~6.9 min, and with the short bottom row of tiles the 70
tiles come to **≈ 7.0 h on the laptop**. The earlier 6–8 h estimate was right; it is now
measured. Desktop should be faster, but §8's warning stands — do not assume a factor.

#### The coarse basin pass is finished, and it is a product **[V]**

**48 seconds** for the whole extent at 1600 m, one `Fill`, no tile seams: **217,622 closed
depressions, 5,144 of them ≥ 20 km.** Written to **`Landform_BasinCandidates_auto_60`** —
its own class, so nobody mistakes it for the ≥1 km inventory the fine pass will produce.
Thermal index attached to every row.

It recovers the big basins unprompted:

| detected | IAU | |
|---|---|---|
| 2,697 km at 71.9°E −41.0°, **7,857 m deep** | Hellas, ~70°E −42.4°, the deepest basin on Mars | ✓ |
| 2,093 km at 113.5°E +44.5° | Utopia, ~118°E +45° | ✓ |
| 1,026 km at 87.6°E +12.5° | Isidis, ~88°E +13° | ✓ |

#### The project's first planet-scale accuracy figure for the detector **[V]**

Against **all 117 named IAU craters ≥ 100 km inside ±58°** — not one crater, as §26.3 had:

| | | |
|---|---|---|
| a closed depression found near the centre | 88 / 117 | **75%** (positional) |
| …**and** diameter within ±50% | 79 / 117 | **68%** (usable) |
| diameter error on those | median **+2.2%** | p10 −12.6%, p90 +20.8% |

> **Quote the 68%, not the 75%.** The gap is real: a degraded crater's *closed* part is only
> its deepest pocket, so the detector can find something in the right place that is far too
> small. Positional recall alone flatters it.
>
> **Match to the LARGEST candidate near the centre, not the nearest.** Taking the nearest
> gives spurious matches — Greeley, 457 km, "matched" to a 24.6 km pocket inside it. That
> choice moved the diameter agreement from poor to a median of +2.2%, so it is a real
> methodological point and not bookkeeping.

**Median +2.2% at basin scale corroborates §26.3's −7.1% on Perrotin at type-area scale.**
Two independent checks at very different sizes now agree that the method is good to better
than ~10% on diameter *when it sees the crater at all*.

**The 32% it misses is the §26.3 limitation, unchanged and now quantified planet-wide.**
Breached craters are invisible to a closed-depression detector. **So the honest headline is:
this recovers about two-thirds of large named craters with good diameters, and the third it
misses is a population — the breached ones — not a random sample.** That population is
precisely the fluvially modified one, so it must be digitised by hand.

---

## 29. Manual work in the Pro GUI — 2026-09-24 to 10-01, read 2026-10-01 **[V]**

**None of this was scripted.** It is manual work in the GUI, recorded so the next session does not plan against
the 2026-09-19 picture. Read-only, from `GpMessages\`, the gdb lineage (`a00000004.gdbtable`,
regex over `<Process>` — lineage only, never inventory, §9), `arcpy` (`Describe`, `GetCount`,
search cursors, `arcpy.Raster`) and the files' own metadata. Nothing was changed.

### 29.1 What was run **[V]**

| End (local) | Tool | Output |
|---|---|---|
| 24 Sep 16:07 | Composite Bands, cancelled after 10 m 01 s — the **fifth** cancelled attempt | none |
| 24 Sep 18:59 | Composite Bands, Night IR + Day IR, 2 h 52 m 25 s | `Mars_MO_THEMIS_CompositeBand`: 2 bands (night, day), 213,388 × 71,130, 100 m, CM 180 — exactly the night grid (§28.1) |
| 29 Sep 00:09 | Training samples saved | `TrainingSamples_202609290009589587982`, 455 polygons |
| 29 Sep 19:22 | `SegmentMeanShift` 15.5 / 15 / min 20 px, on a raster-function input (`.afr` in the desktop's Temp, not readable from here) | `Segmented_202609290011302066080`, 3 bands, night grid |
| 29 Sep 21:53 | `ClassifyRaster`, support vector machine, over the segments plus Night IR | `Classified_202609292109007048151`, 4 classes, night grid |
| 30 Sep 01:19 | Composite Bands, 7 bands, 3 h 10 m 40 s | `CompositeBand`, 92,160 × 46,080, 231.54 m, CM 0, global (§29.4) |
| 30 Sep 04:28 | `ClassifyRaster`, SVM, on `CompositeBand` | `Classified_202609300147338582853`, 4 classes, Viking grid |
| 30 Sep 08:03 | Training samples exported | `Z:\new training.shp`, 511 polygons |
| 1 Oct 19:56 | Export Training Data For Deep Learning, from `CompositeBand` | `Z:\Mars Project\LabeledObjects\CompositeBand\202610011907318762216\` (§29.6) |

**The lineage time is the end time:** for both composites it falls within 3 s of the
`GpMessages` end (18:59:53 vs 18:59:55; 01:19:36 vs 01:19:39). Pro stamps an output's name with
its creation time, so the segmentation ran from 00:11:30 to 19:22:17 — **about 19 h 11 m**.
That pairing of two timestamps is an inference. **[E]**

**Which machine.** The 29–30 Sep lineage carries `C:\Users\Owner\AppData\Local\Temp\…` and
`F:\Mars Project\…`: the Windows account `Owner`, not the laptop's `Loggg`, so the desktop, with
the drive as `F:` (§2.4). The 24 Sep composite wrote to `Z:\Mars Project\…`, so probably the
laptop. **[?]**

### 29.2 The labels — four classes, hand-drawn, planet-wide **[V]**

| Set | Crater | steep/windy hills | lava tube | Normal Ground | Total |
|---|---|---|---|---|---|
| `TrainingSamples_202609290009589587982` (29 Sep) | 275 | 39 | 44 | 97 | 455 |
| `Z:\new training.shp` (30 Sep) | 301 | 44 | 44 | 122 | 511 |
| `Landform_TrainingSamples_terrain` (now) | 302 | 44 | 44 | 122 | 512 |

The class schemas are `THERMAL NIGHT.ecs` (29 Sep) and `Composite Object Classes.ecs` (1 Oct),
both at `Z:\Mars Project\`. Both `.ecd` files name `SupportVector` and `new training.shp`.

**The two schemas number two of the classes differently — read 2026-10-02.** **[V]** Every file
that holds labels or a model uses **steep/windy hills = 2, lava tube = 3**: all three sets in the
table above (the two gdb classes read with `arcpy`, `new training.dbf` read directly), both
`.ecd` files, `THERMAL NIGHT.ecs` (and `THERMAL NIGHT1.ecs`, byte-identical), and the
deep-learning export's `esri_model_definition.emd` and `stats.txt` (§29.6). Only
`Composite Object Classes.ecs`, saved 1 Oct 19:33, 26 minutes after the export, has
**Lava Tube = 2, Windy/Steep Hills = 3**, with both names respelled. Crater = 1 and
Normal Ground = 4 agree everywhere. So a model trained on the export and read through the newer
schema, or new samples drawn under it and merged with these, would swap those two classes
without any error. Which schema is kept is an open decision (§11 q23). **[?]**
The polygons span **166.2°W to 94.9°E and 43.8°S to 62.1°N** (`Mars_2000_(Sphere)`): planet-wide,
not Ius, and a few reach north of the ±60° analysis extent (§16), where the night bands are empty.

**These are what §27.3 said the project lacked: labels drawn by eye, not generated from a DEM.**
Note that they are **landform and terrain** classes, not the **material** classes (dust versus
bedrock) that §27.3 says could price the thermal index. Whether "Normal Ground" against "steep/windy
hills" can test that claim is open. **[?]**

### 29.3 ⚠ The §27 terrain labels are gone, and that script would delete the hand-drawn labels

`Landform_TrainingSamples_terrain` held the **1,604** terrain-derived polygons of §27.1. It now
holds **the 512 hand-drawn polygons**, with Pro's training-sample schema (`Classcode`, `Classname`, `Classvalue`, …,
`ImageURI`, `IShape`) in `Mars_2000_(Sphere)`. The §27 accuracy (62.7%, κ 0.41) stands as measured,
but its training set is no longer in the gdb. **[V]**

> **As found on 2026-10-01, `build\make_typearea_supervised.py` set `overwriteOutput = True`,
> then deleted and rewrote `Landform_TrainingSamples_terrain` (lines 137–140). Run as it stood,
> it would have destroyed the hand-drawn labels.** `new training.shp` is a near copy (511: one Crater fewer),
> not a backup to rely on. **Fixed the same day on request: §29.8.** **[V]**

### 29.4 The 7-band composite, and where it departs from §18 and §28 **[V]**

Band order, from the lineage and the export's per-band statistics: **1–3 Viking RGB**, **4 DEM**
(−5,611 to 18,305 m over the tiles), **5 `Slope_Mars_H1`** (0 to 111.6), **6 Night IR**
(mean 124.34), **7 Day IR** (mean 125.78).

A design decision taken in the GUI. Where it differs from what this file built:

- **The grid is Viking's** (CM 0, 231.54 m, global extent). Both THEMIS bands were rolled 180°
  and resampled from 100 m, where §18.1 and §28.1 keep the day–night pair on its native grid
  because it is the only pair that aligns exactly (§15.3). Outside ±60° bands 6–7 are empty while
  1–5 are not. That follows from §15.4; it was not read. **[E]**
- **Band 5 is `Slope_Mars_H1`**, which is percent rise computed on a degree grid with z-factor 1
  (§7). The valid slope is `Global60\global60_slope_deg.tif` (§28.8), on the 200 m grid.
- **The DEM is a band.** §14.2 left it out of the Iso Cluster composite because raw elevation
  swamps 8-bit bands in a distance measure. Whether Pro's SVM rescales its inputs was not
  checked. **[?]**
- At 231.54 m the §23.5 rule (~10 px across a feature) puts the resolving limit near **2.3 km**,
  against ~1 km on the 100 m stack.

### 29.5 The ±60° segmentation

§23.6 measured ~92 h for 14 / 14 / 30 at ±60° on the laptop and said to ask first. A GUI run used
 15.5 / 15 / 20 on the desktop in about 19 h (§29.1): **higher detail and a smaller minimum segment
than §23.5 recommends**, so the segments are smaller and the de-speckling is likely weaker.
`build\verify_segmentation.py` measures speckle on the type area only; this run has not been
measured. **[?]**
**The SVM over it (29 Sep) is blocky on the 4096-px tile grid and scores below chance on its own
training polygons (§30.2). The segmentation itself is seamless and is not implicated.**

### 29.6 The deep-learning export **[V]**

**4,507 tiles of 256 × 256 px × 7 bands** from `CompositeBand`, metadata `PASCAL_VOC_rectangles`
(object-detection boxes), **6,808 labelled objects**:

| Class | Images | Objects |
|---|---|---|
| Crater | 2,094 | 3,152 |
| Normal Ground | 1,998 | 2,691 |
| steep/windy hills | 300 | 539 |
| lava tube | 210 | 426 |

A polygon crossing tiles is counted once per tile, 1.51 objects per image on average. The largest
object is **3.51 × 10⁹ m², which is a whole tile** ((256 × 231.54 m)²), so some boxes are the
tile itself. Boxes that size teach a detector nothing about boundaries. **[V]** for the
arithmetic, **[?]** for the consequence. The next tool, Train Deep Learning Model, is the first
in this project that would use the 2080 Ti, so §11 q10 (does the GPU engage?) now matters.
The export's class values follow `THERMAL NIGHT.ecs`, not the newer
`Composite Object Classes.ecs` (§29.2, §11 q23). **[V]**
The SVM made from the same stack is mostly an elevation map (§30.3), which is a warning for any
model trained on these tiles (§11 q25). **Redone from the corrected stack in §31.4.**

### 29.7 What this section changed elsewhere

§2.4 (the `F:` letter), §6 (26 feature classes, 14 rasters), §8 (rows 9–11), §11 (q15, q16
updated; q19–q22 added), §13.2 (counts), §17.2 (`verify_all.py` 37 / 38), §27 (the warning).
**`build\audit_record.py` passes again** with the counts reconciled. Backup of this file before
the edit: `Z:\Mars Remote Sensing Project\.backup_20261001\PROJECT-KNOWLEDGE.md`.

### 29.8 Two scripts fixed on request, 2026-10-01 **[V]**

Originals kept in `build\.py_backup_20261001\`. Both files keep their CRLF line endings.

**`build\make_typearea_supervised.py` can no longer delete the hand-drawn labels.** `TRAIN_FC` is now
**`Landform_TrainingSamples_terrain_auto`**, an `_auto` class like the other machine products
(§25), and a new `safe_to_replace()` runs before any `Delete`. It allows the replace only when
the class is absent or every row's `MappedBy` is the script's own marker. Otherwise it stops with
`REFUSING: … Nothing deleted`. An empty class counts as replaceable, since there is nothing to
lose. The script was **not** re-run, so its outputs are unchanged.

**`build\verify_all.py` dates each cancelled run.** `composite_cancellations()` reads the start
time and elapsed time per `GpMessages` log. The single `== 4` check became three: exactly four
cancelled by 13 Sep, the fourth on 13 Sep at 17 min 28 s, and the fifth on 24 Sep at 10 min 01 s.
**39 / 39.**

**Both were proved on planted defects**, with the functions extracted from the files by `ast`
and every fixture in a scratch directory on `C:`, never on this drive:

| Planted | Expected | Result |
|---|---|---|
| a copy of `GpMessages\` without the 13 Sep log | count 3, so the check fails | 3 |
| a copy without the 24 Sep log | fifth not found | not found |
| a copy plus a cancelled run dated 20 Oct | count still 4 | 4 |
| `safe_to_replace` on the hand-drawn `Landform_TrainingSamples_terrain` | refuse | refused |
| a scratch class, every row script-made | replace | allowed |
| the same plus one row `MappedBy = "manual, by hand"` | refuse | refused |
| a scratch class with no `MappedBy` field | refuse | refused |

---

## 30. The two GUI SVM classifications, checked — 2026-10-02 **[V]**

**No geoprocessing was run.** Read-only on the laptop, pyramid levels only, nothing in the gdb
or the `.aprx` written. `build\verify_svm_classifications.py` reproduces every number here in
about a minute and writes `build\logs\svm_check.json`; `build\make_fig_svm_check.py` draws
`pres1_img\svm_check.png` from it. The rasters are the two `Classified_*` of §29.1:
**the 29 Sep map** (SVM over the ±60° segments plus Night IR, night grid) and **the 30 Sep map**
(SVM over the 7-band `CompositeBand`, Viking grid). Both carry the RAT
Value 0–3 = Crater, steep/windy hills, lava tube, Normal Ground, which follows `THERMAL NIGHT.ecs` (§29.2).

### 30.1 Four independent checks **[V]**

| Check | 29 Sep map | 30 Sep map |
|---|---|---|
| Area shares at ±60°, area-weighted (Crater / hills / lava tube / Normal) | 51 / 45 / 1.4 / 2.7 % | 40 / 3.5 / 24 / 33 % |
| The 512 labelled polygons scored on the map (training-set score, an **upper** bound) | **19.5 %, κ −0.01** | **65.1 %, κ 0.47** |
| — polygons whose own class wins: Crater / hills / lava tube / Normal | 224/301, 26/44, **0/44, 0/122** | 204/301, 38/44, 35/44, 45/122 |
| IAU named craters ≥ 5 km, not near any training polygon: 'Crater' inside 0.7 R vs a 1.5–2.5 R ring | 0.59 vs **0.67** (n 817) | 0.62 vs 0.53 (n 898) |
| — craters where inside > ring | 45 % | 61 % |

**The two maps agree on 24.0 % of the ±60° band, against 21.6 % by chance: κ 0.03.** As maps
of the same four classes they are close to independent.

**A map that said Normal Ground everywhere would score 55 % on the labelled polygons.** The 29 Sep map
scores 19.5 %, which is below that and below chance, on the data it was trained on.

### 30.2 The 29 Sep map follows its processing tiles, not the terrain **[V]**

The map is a patchwork of uniform rectangles. Every vertical class edge that stands out is a
whole number of **4096-pixel tiles** (4096 × 100 m = 6.91°) from the last, counted from 0°E and
60°N on the night grid. That is the tile grid, not a property of Mars.

**The seams are made in the classification step.** Across tile boundaries against across ordinary
columns and rows, on pyramid level 4 (32× decimated, one tile = 128 px):

| Raster | jump at tile columns / elsewhere | at tile rows |
|---|---|---|
| `Mars_MO_THEMIS_CompositeBand`, both bands | 1.00 | 1.00 |
| `Segmented_202609290011302066080`, all 3 bands | 1.01 | 1.01 |
| `Classified_202609292109007048151` | **2.77** | **3.14** |

So the IR input and the segmentation are seamless and the classified output is not. **What inside
`ClassifyRaster` does this is not known.** The segment IDs in `_interIndex` are a single global
range (0 to 467,797) and do not restart per tile, so the obvious guess is not confirmed. The
raster-function `.afr` it ran over sits in the desktop's Temp and cannot be read from here (§29.1). **[?]**

**Not a misregistration.** Shifting the map by 0, ±2, 90, 180 and 270° of longitude never lifts
the training-set κ above 0.14, and that at a meaningless 270°. The 30 Sep map peaks at 0°
(κ 0.47), so the method finds registration when it is there. **[V]**

**Consequence:** the 29 Sep map cannot be used as a result. Its "Crater" class is *less* common
inside named craters than around them. The ±60° segmentation under it (§29.5) is not
implicated by this test and may still be usable.

### 30.3 The 30 Sep map is mostly an elevation map **[V]**

It has real skill on the hand-drawn labels (κ 0.47 on its own training set) and a weak crater signal
(0.62 inside vs 0.53 around). But:

- **Elevation alone reproduces 62.1 % of it at ±60°**: put each pixel in a 500 m DEM bin and
  give it the bin's majority class. The largest class alone gets 36.7 %. Below −2 km it is
  60–68 % Normal Ground (the northern lowlands). From 0 to +4 km it is 60–62 % lava tube (the
  southern highlands). Above +4 km it is 84 % Crater (the Tharsis volcanoes). This is the effect
  §14.2 and §29.4 warned about: an unscaled DEM band in metres dominating 8-bit bands.
- **Even shifted 180° in longitude it still scores κ 0.35 on the labelled polygons.** Most of its skill
  is "which elevation and latitude band", not "which feature".
- **Outside ±60° the thermal bands are empty** (§29.4), and **91 % of the region south of 60°S
  comes out Crater**, 40 % north of 60°N. Those are artefacts of the empty bands, outside the
  analysis extent (§16).

### 30.4 The metrics were proved on planted maps first **[V]**

`training_score` and `crater_score` were extracted from the script by `ast` and run on synthetic
global maps at 0.02°/px:

| Planted | Expected | Result |
|---|---|---|
| IAU crater disks painted Crater, all else Normal | inside ≈ 1, ring ≈ 0 | 0.998 / 0.046, inside > ring 98.5 % |
| the same rolled 180° | inside ≈ ring | 0.029 / 0.030 |
| the labelled polygons painted with their own class | 1.0, κ 1.0 | 1.000, κ 1.000 |
| the same rolled 180° | ≈ Normal share, κ 0 | 0.554, κ −0.001 |
| Normal Ground everywhere | Normal share, κ 0 | 0.555, κ 0.000 |

### 30.5 What this changes

- **The deep-learning export (§29.6) is built from the 30 Sep stack, with its unscaled DEM band and
  its empty thermal bands past ±60°.** A detector trained on it can learn elevation, and any tile
  north of 60°N (the labelled polygons reach 62.1°N) has blank bands 6–7. Worth settling before Train Deep
  Learning Model spends GPU hours (§11 q25). **[?]**
- **For a defensible classification:** drop the DEM band or rescale it, keep `global60_slope_deg.tif`
  in place of `Slope_Mars_H1` (§28.8), clip to ±60°, and score it on held-out polygons, not
  training polygons. §27's spatial-block split is the method already in `build\`. Open decision. **[?]**
- §29.5's open question about speckle in the segmentation is still open. This section measured the
  classification over the segments, not the segments themselves.

---

## 31. The fix: a corrected ±60° stack, a reclassification scored on held-out labels, and the work put into the project — 2026-10-02/03 **[V]**

**On request: "ensure the work is in the parts I can see when I open the project in ArcGIS Pro,
properly clip everything to the 60° limit, and fix the parts you find issues with."** Run on the
laptop. Every number below is printed by a script in `build\` and stored in `build\logs\`.

### 31.1 What now shows in Pro **[V]**

`build\make_global60_maps.py` wrote these into `Mars Project.aprx` with Pro closed, after a copy
went to `Z:\Mars Project\.backups\` (§13.3):

- **Every Mars map is clipped to ±60°** with `Map.clipLayers`, using the `Analysis_Extent_60`
  polygon: `Mars` (both), `Mars High-Resolution Mosaic Viewer`, `Map2`, `Map3`, `Perseverance Map`, and the five new maps (two Ius maps, inside ±60° anyway). Clipping is display-only: nothing is deleted, and `clipLayers(None)`
  in Python, or Map Properties → Clip Layers in Pro, undoes it. The Earth, Enceladus and Mercury
  maps, the broken HiRISE map `mars` and the Ius map (already inside ±60°) are left alone.
- **New map "Mars ±60° Analysis"**: the corrected classification over hillshade, the hand-drawn labels split
  into the training and held-out sets (outlined in the class colours), the inputs (stack RGB, thermal
  contrast index, slope, DEM, hillshade), a group holding the 29 and 30 Sep GUI SVMs marked superseded,
  and IAU craters and basin candidates for reference.
- **New maps "Check — 29 Sep SVM" and "Check — 30 Sep SVM"**, one per check frame, so each frame
  in Pro shows its own layer live.
- **New layouts `04_global60_landforms` and `05_svm_checks`**, exported to
  `Z:\Mars Project\Global60\layouts\`.
- **Layouts `01_visible` and `02_night_ir` were showing the classification in Pro.** All three Ius
  sheets framed one map, so each showed whichever layer was on last (§22). They now have a map each
  ("Ius Chasma — visible", "Ius Chasma — night IR"), and 03 keeps the original map.

### 31.2 The corrected stack **[V]**

`build\make_global60_svm_stack.py` → `Z:\Mars Project\Global60\global60_svm_stack_200m.tif`:
G200 (§28.1), 106,694 × 35,565, 7 bands, U8, nodata 0, **97.33 % co-valid**, overviews, statistics,
the named CM 180 WKT. Every defect of §29.4 and §30.3 is addressed:

| `CompositeBand` (30 Sep) | this stack |
|---|---|
| global; bands 6–7 empty past ±60° | ±60° exactly, the night mosaic's own extent |
| THEMIS rolled 180° and resampled to 231.5 m | THEMIS 2 × 2-averaged on its own grid, never warped |
| raw DEM in metres beside 8-bit bands | **no elevation band**; 9 × 9 local relief (1.8 km) in its place |
| `Slope_Mars_H1`, percent rise on a degree grid | slope in degrees, `global60_slope_deg.tif` |
| F32, ranges 0–255 beside −5,611–18,305 | every band U8, p1/p99 → 1–255 over ±60° |

Bands: Viking R, G, B (bilinear 231.5 → 200 m); Night IR; Day IR; slope; relief. The p1/p99 limits
are in the file's `STRETCH` metadata.

**Registration checked.** At the 1.6 km overview, Viking red against Day IR correlates at
**r −0.147 at zero shift, the strongest of any shift within ±19 km, and +0.001 when rolled 180°**.
Bright dust is cool by day, so the sign is the physical one. Slope against relief: r 0.989 at
zero shift. **[V]**

**Cost, measured.** Viking warp 24.6 min; 70 strips ~1 h of compute. The script reported
5 h 26 min of wall clock because **the laptop slept at least twice** (§28.9). `SetThreadExecutionState`
keeps it awake while idle but cannot stop a lid close.

### 31.3 The classification, scored on labels it never saw **[V]**

`build\make_global60_classification.py`:

- `Analysis_Extent_60`: one polygon, ±60.0003°, the night mosaic's edge.
- **The 512 labelled polygons, clipped to ±60° and split by whole 15° × 15° blocks**: 39 blocks, 14 to test;
  **329 training, 183 held out**. Held out per class: Crater 124/302, steep/windy hills 16/44,
  lava tube 21/44, Normal Ground 22/122. A held-out polygon never shares a block with a training
  polygon (the §27 rule). Seed 60, so the split is reproducible. Written as
  `Landform_TrainingSamples_terrain_60_train` / `_60_test`. **The original `Landform_TrainingSamples_terrain`
  was only read**, and the delete guard (§29.8) passed six planted cases first.
- Train Support Vector Machine, 1,000 samples per class, on the 200 m stack: 25.4 min →
  `Global60\global60_landforms_svm.ecd`.
- **Classified at 400 m, not 200 m.** A smoke window timed 200 m at 14 µs/px, ~15 h for ±60° on
  the laptop: a desktop job by §2.1. At 400 m it took about 3 h of compute: 21 tiles, 00:18–10:45 wall clock including a ~7 h sleep (§31.5). `--cell 200` runs the 200 m
  version on the desktop. Output: `Global60\global60_landforms_svm_400m.tif`.

`build\verify_global60_classification.py`, at 400 m:

| | this map | 30 Sep map | 29 Sep map |
|---|---|---|---|
| **Held-out polygons** (never trained on) | **70.5 %, κ 0.54** | — | — |
| Training polygons | 82.8 %, κ 0.67 | 65.1 %, κ 0.47 | 19.5 %, κ −0.01 |
| One class everywhere, on the held-out set | 58.6 % | | |
| Elevation bins alone reproduce | **54.6 %** | 62.1 % | |
| Tile-seam ratio, 4096 px at 100 m (1.00 = none) | 1.00 | | 2.77 |
| 'Crater' inside IAU craters vs ring, n | 52 vs 44 %, n 817 | 62 vs 53 % | 59 vs 67 % |

Held-out producer's accuracy: Crater 55 %, steep/windy hills 61 %, lava tube 39 %, Normal Ground 99 %. Held-out polygons won by their own class: Crater 103/124, steep/windy hills 14/16, lava tube 4/21, Normal Ground 20/22.
Area shares at ±60°: Crater 33.0 %, steep/windy hills 2.3 %, lava tube 10.7 %, Normal Ground 54.0 %.

**Verdict.** It is the first map in this project scored on labels it never saw, and it is better
than both GUI maps on accuracy, seams and elevation. It is not better on the crater test: its
'Crater' signal (+8 points inside against outside) matches the 30 Sep map's (+9). Held out it scores **70.5 %, κ 0.54**, against 58.6 % for one class everywhere.
The 30 Sep GUI map managed 65.1 % (κ 0.47) on its *own* training labels. There are no tile seams
(1.00). Elevation explains it barely better than a constant (54.6 % against 53.9 %), so it is no
longer an elevation map. **[V]**

**What it is not:** a map of the landforms the class names suggest. Held out, class by class
(producer's / user's):

- **Normal Ground** (smooth plains) is solid: 99 / 78 %.
- **'Crater'** is right when it says Crater (user's 92 %) but finds only 55 % of crater ground. It
  behaves as *cratered terrain*: 52 % inside named craters against 44 % around them.
- **Steep/windy hills** is middling: 61 / 47 %.
- **Lava tube is not usable.** It covers 10.7 % of the map, and only 1.8 % of what it marks inside
  held-out polygons is lava tube. It sits over Tharsis, Elysium and Hellas, and its main confusion
  is with crater ground. 44 polygons (21 held out) is too few for a planet-scale class.

The night mosaic's coverage gaps show as nodata stripes poleward of about 40°. **[V]** for the
numbers, **[?]** for any geological reading.

### 31.4 The deep-learning export, redone **[V]**

`build\make_global60_dl_export.py` → `Z:\Mars Project\LabeledObjects\global60_svm_stack_200m\`.
The GUI export's settings: 256 × 256 chips, PASCAL VOC rectangles, the class values. Stride 128, because the GUI export's
stride is not recorded. **5,480 chips × 7 bands, 7,884 objects** (Crater 3,575, Normal Ground 3,241,
steep/windy hills 610, lava tube 458), 10.5 min. Every chip is inside ±60° and every band is
8-bit. The 1 Oct export is untouched.
**Not fixed, and not fixable by a re-export:** boxes for area classes. The largest box is still
a whole chip (2.62 × 10⁹ m² = (256 × 200 m)²). For Normal Ground or hills, `Classified_Tiles`
(pixel labels) fits better than boxes. That is a change of method, so it is an open decision (§11 q26). **[?]**

### 31.5 Two traps hit on the way, recorded so they cost nothing next time

- **A full-extent `ClassifyRaster` from a script hands off to `LocalWorker.exe` processes**, which
  appeared about 90 s later, one every 1.5 s. Until then the Python process sits at 0 % CPU and
  0 MB/s, and looks hung. It was stopped as hung, wrongly. The script now classifies in 21 tiles of
  16,384 px, each checkpointed with a `.done` marker on the internal SSD, then mosaics them on one
  400 m lattice (asserted per tile). Progress shows, and a sleep or crash costs one tile.
- **`Map.moveLayer` inside a group layer DELETES layers** (two vanished in a rehearsal). Group members
  are placed with `addLayerToGroup(..., "BOTTOM")`, added top to bottom, and `moveLayer` is used
  only at the top level. **The first real run left the classification under the opaque hillshade**:
  Pro auto-arranges added layers and puts new groups on top. It was caught on layout 04's export
  and fixed by ordering explicitly.
- **cp1252 console**: printing `≥` crashed the map script mid-run. It now reconfigures stdout to UTF-8.
- **The first "dry run" of `make_global60_maps.py` wrote the real project.** The `sed` edit meant
  to add `--aprx` silently matched nothing. The backup step ran first
  (`.backups\Mars Project 20261003-015853.aprx`), Pro was closed, and the changes were the ones
  asked for, so nothing was lost. But check that an edit landed before relying on it. Rehearsals
  since then use a copy **beside** the real `.aprx`: it stores relative paths, so a copy elsewhere
  breaks every layer.
- **`gdal.Open(p).GetRasterBand(1)` in one expression** lets the dataset be collected and crashes
  the next read. The stack reader pins its datasets.

**How the run actually went.** The laptop ran on battery, slept from ~02:40 to ~10:00, and both
processes survived the sleep. The classification started at 00:18 and finished at 10:45 wall clock;
tiles took 9–24 min (row 0–1) and ~2 min (row 2). `build\logs\global60_finish.ps1` waited on it, then
ran the scoring and the map script unattended (log: `global60_finish.log`).

### 31.6 What this changes elsewhere

§11 q24 stays open: the cause of the 29 Sep blocks is not known. Missing raster statistics on the
raster-function input is the leading guess **[?]**: this stack has statistics, and the new map's
seam ratio is 1.00. q25 is **answered by §31.2–31.4**, adoption is an open decision.
q26 is new.

---

## 32. The digitising map, the basin layout, and a smoothed classification — 2026-10-03 **[V]**

Laptop, Pro closed, `.aprx` backed up before each write (`Z:\Mars Project\.backups\`), every write
rehearsed on a copy beside the real file first (§31.5).

### 32.1 What digitising needs is now in the project

Digitising is the critical path (§11 q16), but none of its inputs were in any map. The empty
target classes weren't, and neither were the candidates (§25, §26, §28.11).
`build\make_candidate_maps.py` adds:

- **Map "Ius Chasma — digitising"**, layout **`06_ius_digitising`**. On top, the three empty
  classes, ready to edit: `Landform_ChannelCenterlines` (blue), `Landform_CraterRims` (yellow),
  `Landform_LavaFlowMargins` (orange). Under them, the candidates:
  - **Channels: steep and rock-floored (188)**, a definition query (`SlopeDeg >= 5 AND ThermIdx < -0.15`)
    on `Landform_ChannelCandidates_auto`, in cyan. It reproduces §25's 188 and 1,037 km.
  - Channels: other (2,422), the complement, switched off.
  - Craters: closed depressions ≥ 1 km (1,685), in magenta.
  - Under those, the Ius rasters (hillshade on; Viking, slope and the diurnal index off). Within this
    one window the index is valid (§28.10).

  The layout's notes say what the candidates cannot do: 64 % sit on plateau under 2°, and breached
  craters are missing (Oudemans, §26). **Accepting a candidate is still a manual act: a copy into the
  class.**
- **Map "Mars ±60° — basins"**, layout **`07_global60_basins`**. `Landform_BasinCandidates_auto_60`
  (5,144) is drawn as graduated symbols on `DiameterKm`, in five classes from 20–41 km to
  1,027–2,697 km. Red rings mark the IAU named craters over 100 km. The notes quote §26's planet-scale
  accuracy: 68 % of the 117 named craters ≥ 100 km recovered within ±50 % in diameter, median
  error +2.2 %.

Two arcpy traps hit and fixed: labels set on a graduated renderer's `classBreaks` through
`arcpy.mp` do not stick, so they are set on the CIM's `renderer.breaks`. And legend items repeat
the layer name, so legends for single-symbol layers run with `names=False`.

### 32.2 A 5 × 5 majority filter, chosen by feature size, not by score

`build\make_global60_landforms_clean.py --size n` applies a mode filter to the 400 m map. Nodata
never votes, and ties keep the original class. Each version was scored by
`verify_global60_classification.py --raster …`:

| window | pixels changed | held out | training | 'Crater' inside / ring |
|---|---|---|---|---|
| none (raw) | — | 70.5 %, κ 0.54 | 82.8 %, κ 0.67 | 52 / 44 % |
| 3 × 3 (1.2 km) | 7.3 % | 72.3 %, κ 0.56 | 84.7 %, κ 0.70 | 55 / 46 % |
| **5 × 5 (2 km)** | **11.2 %** | **73.5 %, κ 0.58** | **85.9 %, κ 0.73** | **57 / 47 %** |
| 7 × 7 (2.8 km) | 13.5 % | 74.3 %, κ 0.59 | 86.8 %, κ 0.74 | 58 / 47 % |
| 9 × 9 (3.6 km) | 15.1 % | 75.1 %, κ 0.60 | 87.5 %, κ 0.75 | 60 / 48 % |

**Every score rises with every window, on both label sets,** because the labelled polygons are large
(median 107–652 km² outside lava tube). A polygon score rewards smoothing well past the point
where small landforms are erased. **So the window cannot be chosen from these scores,** and
choosing it on the held-out set would spend the held-out set. It was fixed by feature size
instead: half the ~4 km resolving limit of a 400 m map (the ~10 px rule, §23.5). That gives
**5 × 5**, which is the version on the map and in layout 04. The raw map stays in the map,
switched off. Seam ratio 0.99; elevation alone 54.8 % against 54.1 % for one class alone. All four
filtered rasters are in `Global60\` (`…_mode3/5/7/9.tif`, ~100 MB each). How much smoothing to
publish is an open decision (§11 q27). **[V]** numbers, **[?]** the choice.

### 32.3 Caveats that §31 left out

- **The stack's night and day bands are locally contrast-normalised too** (§28.10). The diurnal
  index fails planet-wide for that reason, and the same mosaics are bands 4–5 of
  `global60_svm_stack_200m.tif`. In the classifier they therefore carry local contrast and texture,
  not radiance that can be compared across the planet. This suits landform classes, and is a
  further reason the map should never be read as a material (dust/bedrock) map. **[E]**
- **The ±60° diurnal index is in the analysis map, switched off,** and is now labelled "compare
  within one area only (KB §28.10)", so the caveat is visible in Pro.

---

## 33. Every layout exported and read; five presentation defects fixed — 2026-10-03 **[V]**

Laptop, Pro closed. No layout had been looked at as a whole sheet since it was built, so all seven
were exported to PNG and read one by one. Five defects turned up. `build\polish_layouts.py` fixes
them in the `.aprx` (backed up first, rehearsed on a copy beside the real file, idempotent: a
second run reports "no change" on every sheet). The real project then exported **byte-identical**
to the rehearsal. Fresh PNGs are in `TypeArea\layouts\` (01–03) and `Global60\layouts\` (04–07).
`verify_all.py` still passes 39 / 39.

1. **Fonts.** The builders asked for **Aptos** (titles, notes) and the legend style brought
   **Tahoma**. **Neither is installed on the laptop**, so Pro substituted a different fallback for
   each, and the legends on 03–07 came out in a serif face beside sans-serif text. Every font on
   every sheet is now **Arial** (146 font references). The scale bars were Arial already. The "N"
   of the north arrow is a glyph of the arrow symbol and was left alone.
2. **Sheet 02's caption contradicted §24 and §28.10.** It said *"Bright = high thermal inertia:
   bedrock and coarse debris."* The THEMIS mosaics are locally contrast-normalised 8-bit DN, so
   bright means warmer at night **than its surroundings**. Now: *"Bright = warmer at night than its
   surroundings, as rock and coarse debris are. Local contrast, not calibrated thermal inertia
   (KB §28.10)."* It is corrected at the source in `make_typearea_layouts.py` too.
3. **Sheet 04's grey streaks were unexplained.** Measured on `…_400m_mode5.tif` (nodata 255),
   they are no-data: **2.6 %** of the ±60° band and **19 %** of the rows south of 48°S. These are
   gaps between THEMIS orbits, with the hillshade showing through. The checks note now says so.
4. **Sheet 04's legend** printed "Analysis extent ±60°" twice, as a heading and as the label. The
   heading is off. In Arial, the 16 pt legend headings wrapped "(±60°, 400 m)" so that "m" stood on
   a line of its own. **All legend headings are now capped at 11 pt.**
5. **Sheet 07's legend** split the five basin size classes across two columns, with the last two
   under the IAU entry. Basins are now in column 1 and IAU craters in column 2 (manual columns).

The three builders now say "run `polish_layouts.py` afterwards" in their docstrings, and
`layoutkit.py` and `make_typearea_layouts.py` ask for Arial. Re-running a builder therefore
reintroduces only the legend fixes, and the polish pass restores them.

**Seen and left alone:**
- On sheet 06, the north arrow's "N" sits just right of the legend box. This was already the case.
- Sheet 04's subtitle runs ~0.2 in past the map frame's right edge, though it stays inside the page.
- Sheet 04's classification is drawn at 30 % transparency over hillshade, so its swatches look
  paler than the same classes on sheet 05. The hues match the RAT colours on both sheets.

---

## 34. Twelve layers would have broken on the desktop; two more layout nudges — 2026-10-03 **[V]**

Laptop, Pro closed, `.aprx` backed up before each write, every write rehearsed on a copy beside the
real file first.

### 34.1 No layer reads through a junction any more

`Z:\Global60` and `Z:\TypeArea` are directory junctions for the legacy Spatial Analyst tools that
reject the space in "Mars Project" (§19.1). Read with `fsutil reparsepoint query`, both store an
**absolute** target: `\??\Z:\Mars Project\Global60` and `\??\Z:\Mars Project\TypeArea`. On the
desktop the drive mounts as `F:` (§2.4), so `F:\Global60` points at a `Z:` that isn't there.

A sweep of every layer in every map found **12 layers reading through `Z:\Global60`**:
- 7 in "Mars ±60° Analysis", including the classification on layout 04
- the hillshade in "Mars ±60° — basins", under layout 07
- 4 in the manual group `60Drasters` in "Mars High-Resolution Mosaic Viewer"

**All 12 would have opened broken on the desktop.** The `.aprx` stores relative paths, so a layer
that reads `Mars Project\Global60\…` directly survives the change of drive letter.
`build\repoint_junction_layers.py` repoints them to the real folder. The files are the same, so only
the path changes. Every layout then rendered **pixel-identical** to before the change. A second run
finds 0 layers. No layer used `Z:\TypeArea`.

At the source, `make_global60_maps.py` and `make_candidate_maps.py` now add layers from
`grid60.OUTDIR` (the real folder), not `OUTDIR_NOSPACE`. **Rule: scripts may use the junctions for
geoprocessing; layers in the project must not.**

Not done: the 4 broken layers the sweep also found are the non-Mars ones (Enceladus, Mercury, a
Jezero HiRISE file missing from the drive). Clearing them is still q5, an open decision. (2026-10-07: the non-Mars ones are gone, §37.)

### 34.2 Two layout nudges left over from §33

- Sheet 04's subtitle is rewrapped so it ends inside the map frame.
- Sheet 06's north arrow moved 0.3 in right, clear of the legend box.

Both are in `polish_layouts.py` and in the builders' source. PNGs refreshed.

---

## 35. Backed up to GitHub, which is also the project page — 2026-10-06 **[V]**

**On request: a public repo named `Mars_Terrestrial_GlobalMosaic_GIS-Data` that backs up as
much as it can and acts as the project page.** `https://github.com/loggger101/Mars_Terrestrial_GlobalMosaic_GIS-Data`.
This supersedes §2.5's "no backup" for the part that matters. `Z:` stays the working copy and the
only home of the large derivatives.

**Licensing, chosen 2026-10-06:** code (`.py`, `.ps1`) under **MIT** (`LICENSE`); everything else
(this file, documents, figures, layouts, the `.aprx`, vectors, release rasters) under
**CC BY 4.0** (`LICENSE-CC-BY-4.0.txt`, the official legal code). The source mosaics and IAU
nomenclature keep their producers' terms. The README's License section says so. **[V]**

### 35.1 What went where **[V]**

| | where | size |
|---|---|---|
| `Mars Remote Sensing Project\` (this file, `build\`, logs, figures, deliverables, the `.backup_*` folders) | repo, same folder name | ~100 MB |
| `Mars Project\`: `.aprx`, `.atbx`, `.ecd`/`.ecs`, `GpMessages`, `ImportLog`, every sidecar, RAT, model and layout PNG in `Global60\` and `TypeArea\`, `LabeledObjects\` metadata | repo, same folder name | ~25 MB |
| `Z:\` root: the globals' `.aux.xml`, the night mosaic's `.lbl`/`.md5`, the `new training` shapefile, the screenshot | repo, `drive-root\` | 14 MB |
| The gdb's 19 feature classes (all but `Line`, `Point` and the `_2`/`_3` nomenclature duplicates), incl. the 512 labels and the empty `Landform_*` classes | repo, `exports\mars_project_vectors.gdb`; release, GeoPackage | 60 MB |
| `TypeArea\` whole, Global60's classification maps + model + smoke rasters, the `.npy` caches, the two GUI SVM maps from the gdb | release `data-2026-10-06`, originals zipped byte for byte, `SHA256SUMS.txt` | ~4 GB |
| The four source globals | **not copied**; the README links them. All four checked by HTTP HEAD 2026-10-06: byte-identical sizes at the USGS S3 bucket, the DEM under `mosaic/Mars/HRSC_MOLA_Blend/` | 62 GB |
| Global60's derivatives, the gdb rasters, `.backups\`, DL chips, the five `*_ov400.npy` | **not backed up** on 2026-10-06 at first; re-computable by `build\`. Most of it followed the same evening (§35.3) | ~300 GB |

Every feature class's row count was checked against the source after export (19/19). Re-encoding
the rasters as DEFLATE GeoTIFFs only saved 8–35 %, so the release ships the original files. **[V]**

### 35.2 Keeping it current

Three scripts in `build\`, each finding the drive from its own path, so they work on `F:` too:

- `build\github_sync.py --commit` (either Python, stdlib): mirrors what changed into the clone at
  `~\OneDrive\Documents\GitHub\Mars_Terrestrial_GlobalMosaic_GIS-Data`, commits, pushes. Files over
  95 MB are reported and skipped. Files deleted on the drive are removed from the mirror; git
  history keeps them. **Only reads `Z:`.**
- `build\github_export_gdb.py --rasters` (ArcGIS Python): re-exports the gdb vectors into the
  repo's `exports\`, and the GeoPackage and the two GUI SVM maps to the release staging folder
  (`%LOCALAPPDATA%\Temp\mars_github_dist`). **Run after digitising** — manual edits live only in the gdb.
  It also writes the layer catalog, `exports\README.md`. **A re-export rewrites every gdb file
  (new internal UUIDs) even when no feature changed**, ~60 MB of history per run, so run it only
  when layers have changed; `--catalog-only` rewrites just the catalog. It builds in staging and
  refills the repo's `.gdb` folder file by file: deleting that folder failed with *Access is
  denied* because OneDrive held it (2026-10-06). **[V]**
- **Repo-only files** (not on `Z:`, so the mirror leaves them alone): `restore.py` rebuilds the drive
  from a clone and both releases (verify, unzip, rejoin split rasters, never overwrite without
  `--force`); **tested 2026-10-07: the 2-piece `global60_dem.tif` came back byte-identical, 3.2 GB in
  352 s** **[V]**. `tools\check_repo.py` (page links, Python syntax, file sizes, `CITATION.cff`) runs
  in GitHub Actions on every push; each check failed on a planted defect first. `CITATION.cff`
  gives the name as **Logan M Edwards**, the standard since 2026-10-07 (the author's own commit to the
  LICENSE and README).
- `build\github_catalog_rasters.py` (ArcGIS Python, headers only, seconds) writes the repo's
  `docs\rasters.md`: all 63 backed-up rasters with grid, type, NoData and size **read from GDAL**,
  a description, and the release asset holding each. An undescribed raster is printed as
  "(not described)". It found that **the landform maps' pixel values were 0–3, not the class
  codes 1–4** (only the RAT mapped them). **Fixed the same day, §36.** **[V]** The README's backup and restore
  detail now lives in `docs\backup.md`; the front page keeps a "Using the data" section.
- `github_sync.py` also regenerates `docs\scripts.md` in the repo: every build script grouped by
  purpose, with its docstring's first line and the interpreter it needs, followed through local
  imports (`le_theme` → `pptx` makes every deck builder "system").
- `build\github_release_bundle.py --upload data-YYYY-MM-DD`: zips the release groups (parts under
  1.9 GB) and publishes them.

The repo stores files byte-exact (`.gitattributes`: `* -text`). The clone is in OneDrive, so check
for `*-DESKTOP-PJS73RO.*` conflict copies before committing; `.gitignore` excludes them.

### 35.3 The large products followed, as a second release — 2026-10-06

Work continued on request. The first release uploaded at **~10 MB/s** (1.0 GB in 101 s, read from the
asset timestamps), so the slow-to-recompute products fit in about two hours. **[V]**

- `Mars Project\.backups\`, the 31 `.aprx` snapshots (2026-09-18 to 10-03, 11 MB), now go to the
  repo: they are the project file's history from before git. `github_sync.py` no longer skips them.
- `build\github_release_large.py derivatives-YYYY-MM-DD` (ArcGIS Python) publishes release
  `derivatives-2026-10-06`: the seven ±60° derivatives (`global60_svm_stack_200m`,
  `_thermal_contrast`, `_thermal_contrast_200m`, `_dem`, `_slope_deg`, `_aspect`, `_hillshade`; 67.6 GB)
  as their original bytes cut into 1.9 GB `.partNNN` pieces, their sidecars, both `LabeledObjects`
  exports, and the GUI ±60° segmentation `Segmented_202609290011302066080` out of the gdb. One
  `SHA256SUMS` hashes every piece and every reassembled file. Resumable; stages one piece at a time;
  keeps the machine awake. Log: `build\logs\github_release_large.log`.
- **Finished 2026-10-07 11:39 EDT: 46 assets, 74.4 GB.** Every asset's SHA-256 as GitHub records it
  matches the hash taken from the drive (45/45, plus the sums file). **[V]** It took ~16 h, not 2:
  the first run died on a DNS failure (now retried, up to 6 times); the laptop went into Modern
  Standby twice on battery ("Austerity Battery Drain Budget Exceeded", 20:21–21:51 and from 21:56),
  which `SetThreadExecutionState` does not prevent; and the uplink fell from ~10 MB/s to 0.7–1.4 MB/s
  overnight (home Wi-Fi, then `fit.edu`). One piece needed 4 retries on the campus network. A resumed
  run takes each uploaded asset's SHA-256 from GitHub's `digest` field instead of rebuilding it.
  **Big uploads: on AC, lid open, wired if possible.**
- **Still not backed up:** the `.ovr` pyramids (~22 GB, Build Pyramids re-creates them) and the
  other gdb rasters. Most are what §7 and §29–30 find defective and superseded: the percent-rise
  slopes, `HillSha_Mars1`, `Surface_Mars1`, and the global composites `CompositeBand` and
  `Mars_MO_THEMIS_CompositeBand`. Two are neither: the undocumented 8 Sep segmentation (§7) and the
  Mercury Iso Cluster rehearsal, which is not Mars. The two GUI SVM maps are in the first release.
  Say so if any of these should go too. **[V]**

---

## 36. The landform maps' pixel values are now the class codes — 2026-10-07 **[V]**

**On request,** after the raster catalog (§35.2) showed the trap. `ClassifyRaster` writes
pixel values 0..n−1 and keeps the class codes only in the attribute table's `Classvalue`, so on all
five ±60° landform maps pixel **0 was Crater (code 1) … 3 was Normal Ground (code 4)**. Pro read
them correctly through the table; anyone reading raw pixels (GDAL, numpy, QGIS without the RAT) got
every class off by one, against training labels that use 1–4.

### 36.1 What changed

- `global60_landforms_svm_400m.tif` and `_mode3/5/7/9.tif` in `Global60\` now hold **1 Crater,
  2 steep/windy hills, 3 lava tube, 4 Normal Ground, 255 no class**. Same grid, NoData, colours (each
  moved with its class), overviews, projection and statistics; the RAT now has Value = Classvalue.
- **The originals were moved, not deleted**, to `Global60\_0based_originals\` (30 files), and
  release `data-2026-10-06` held them until its `global60-classification.zip` was replaced the same day.
- `build\landform_codes.py` does the recode, taking pixel → code from the raster's own table.
  `build\fix_landform_values.py` applied it (idempotent; skips a map already coded).
- **The sources can't bring 0–3 back:** `make_global60_classification.py` recodes after the
  mosaic, and `make_global60_landforms_clean.py` reads the class values from the table instead of
  hard-coding 0–3 (`range(4)`, `np.minimum(a, 3)`), and takes `--out`.
- **The `.aprx` needed no change.** All seven landform layers (the five maps and the two GUI maps)
  key their unique-value symbology on `Class_name`, not the pixel value.

### 36.2 Proved, not assumed

- Rehearsed on a copy of `_mode9` first. Then on `Z:`: **every pixel of all five maps equals the old
  value + 1** (old ≠ 255), counted by an independent GDAL check, which on an un-recoded file reports
  923,742,337 mismatches, so it is not vacuous.
- The updated mode filter, run 5 × 5 on the recoded raw map, reproduces the recoded `_mode5`
  **exactly** (0 of 948,669,701 pixels; 11.17 % changed, as in §32.2).
- The classifier's new mosaic step, run on the 21 finished 400 m tiles still in scratch, rebuilds a
  raw map **identical** to the recoded one on `Z:`.
- Rescored with `verify_global60_classification.py`: raw **70.5 %, κ 0.540**; 5 × 5 **73.5 %,
  κ 0.578**. All 46 score fields of both logs match the logs from before the recode; only the `rat`
  field (pixel → name) moved by one.
- The replaced `global60-classification.zip` was restored through `restore.py` from GitHub and
  compared with `Z:`: identical.

### 36.3 The same convention elsewhere: also recoded, §36.4 **[V]**

The other ClassifyRaster outputs kept 0-based pixels with codes in their tables: the two GUI SVM
maps in the gdb and the type-area classifications (`ius_sup_*`: 0–5 for codes 1–6). **Those were requested
too the same day ("continue updating the old 0-based numbering"), and they are done:
§36.4.**

### 36.4 The rest recoded: `ius_sup_*` and the two GUI maps — 2026-10-07 evening **[V]**

Every classified raster in the project now has **pixel value = class code**. Done by
`build\fix_classified_values.py` (idempotent, uses `landform_codes.py` as §36.1; Pro closed).

| Raster | Before → after | NoData | Original kept as |
|---|---|---|---|
| `TypeArea\ius_sup_spectral.tif` | 0–5 → **1 crater interior, 2 steep wall, 3 moderate wall, 4 chasma floor, 5 plateau flank, 6 plateau** | 255 | `TypeArea\_0based_originals\` (moved, with sidecars) |
| `TypeArea\ius_sup_thermal.tif`, `_augmented.tif` | same | 15 (theirs, kept) | same folder |
| gdb `Classified_202609292109007048151` (29 Sep) | 0–3 → **1 Crater, 2 steep/windy hills, 3 lava tube, 4 Normal Ground** | 255 | gdb `…_0based` (renamed) |
| gdb `Classified_202609300147338582853` (30 Sep) | same | 255 (none masked) | gdb `…_0based` |

- **The GUI maps had no NoData value, only a mask,** and under the 29 Sep map's mask the stored
  pixels read 0, which was Crater. Its 401,286,036 masked pixels are now NoData 255. The originals
  were renamed `<name>_0based` in the gdb, not deleted, and the recode copied in under the old name,
  so the five `.aprx` layers on them still resolve and keep their colours (unique values keyed on
  `Class_name`; checked by reading the project after the run).
- **Checked:** 29 Sep **14,777,002,404** valid pixels, 30 Sep **4,246,732,800**: every one equals
  old + 1, masks identical, tables Value = Classvalue, pyramids 9 and 8 levels as before. The type-
  area maps: per-class counts and NoData counts identical before and after.
- **A false alarm first, fixed:** the generalised check reported a mismatch because numpy 2 keeps
  `np.where(mask, 256, uint8_array)` as uint8, so 256 wraps to 0 and NoData was counted as Crater.
  `landform_codes.py` now casts to int16 first. The §36.1 results don't depend on it (their checks
  were the independent GDAL count).
- **`Z:` dropped off USB at 14:55** (System log: "Delayed Write Failed") while `CopyRaster` was
  writing the 29 Sep recode straight into the gdb on the drive, 40+ minutes in. The renamed original
  was intact (re-read in full, 0 mismatches); the partial copy was unreadable. The script now
  **builds the gdb raster on internal disk and copies the finished dataset to `Z:` in one step**,
  and **resumes**: if `<name>_0based` exists, it drops an unreadable or un-recoded `<name>` and
  recodes from the `_0based` original. Both paths were rehearsed in scratch gdbs before the rerun.
- **The copy onto `Z:` then failed once more** (16:37, ERROR 000260 file read/write; nothing in
  the System log). It cleaned up after itself. The same copy into a scratch gdb on `Z:` worked, so
  `build\fix_classified_finish.py` retried just that step (up to three tries): the first worked.
- **Reading two gdb rasters in full-width 2048-row strips thrashes GDAL's cache:** the first
  independent check read 58 GB off `Z:` in 2.5 h for a ~600 MB raster. Strips one block (128 rows)
  high with a 2 GB cache: the 30 Sep map in 79 s.
- **Release:** `github_export_gdb.py --rasters-only` re-exports the two maps as GeoTIFF with 255
  written under the mask and declared NoData (the gdb stores 0 or 255 under it, which a reader that
  ignores masks would take for data). `Classified_*.tif` and `typearea-part*.zip` in release
  `data-2026-10-06` are replaced; `docs/rasters.md` gives the class codes.

## 37. Everything that isn't Mars is out of the project — 2026-10-07 **[V]**

**Instruction, verbatim:** "anything that isnt part of MARS is not relevent tho so please remove it."
`build\remove_non_mars.py`, rehearsed on a copy of the `.aprx` first, Pro closed. **Nothing was
deleted**: every item went to `Z:\_removed_not_Mars\` (with a README), which can be deleted manually.

| What | Where it went |
|---|---|
| Map **"Map"**: World Topographic + World Hillshade, Web Mercator (Earth) | `Map.mapx` |
| Map **"Map1"**: the Enceladus Cassini DEM (a broken link) | `Map1.mapx` |
| Map **"Enceladus"**: the Enceladus DEM + Earth basemaps | `Enceladus.mapx` |
| Map **"Mercury"**: the MESSENGER basemap (a broken link) | `Mercury.mapx` |
| gdb raster `Mercury_MESSEN_IsoClusterUns` (the Mercury Iso Cluster rehearsal, §7) | `removed_not_Mars.gdb` (copied, dimensions checked, then removed from the project gdb) |
| `build\aprx_live\`, the 2026-09-18 unpacked `.aprx` snapshot | `aprx_live_snapshot_2026-09-18\` (moved whole); `build\audit_aprx.py` then re-extracted the current project into `build\aprx_live\` |

- Each map was removed only if its coordinate system is not Mars and no layout uses it; each was
  exported to `.mapx` first (import one to get it back), and the `.aprx` was backed up to
  `Mars Project\.backups\Mars Project 20261007-203644.aprx`. The four held only non-Mars layers.
- **After:** **15 maps, all in Mars coordinate systems; 7 layouts**, unchanged. The gdb holds
  **15 rasters** (14 − Mercury + the two `_0based` originals of §36.4) and 30 feature classes. One
  broken link is left, the Jezero HiRISE mosaic (Mars, §3). Every web layer left is a Mars service
  (Esri OnMars MDIM, CTX, MOLA/HRSC) or the Perseverance/Jezero feeds. Nothing else on `Z:` is named
  for another body; `Z:\new training.shp` (511 features) is in Mars 2000.
- **Not removable, so left:** the `.aprx`'s geoprocessing history still records the Mercury Iso
  Cluster run, and its metadata keeps one orphan entry titled "Mercury". The record's own history
  (§3, §7, §23) still describes the Mercury tutorial settings: that is where the segmentation
  parameters came from, so it stays.
- `Z:\_recode_probe\` (a scratch gdb from §36.4's copy test) and the internal-disk temp folders
  `%LOCALAPPDATA%\Temp\mars_github_dist` and `mars_scratch` were sent to the Recycle Bin on
  request, 2026-10-07. `mars_scratch` held the 400 m classification tiles and `viking_g200.tif`;
  `make_global60_svm_stack.py` rebuilds the latter if it is missing, and the scripts recreate the folder.

## 38. The mosaic itself, as a layout — 2026-10-08 **[V]**

The project is the Mars Global Mosaic, and no layout showed the mosaic: 01–03 are the Ius type area,
04–07 are products made from it. `build\make_mosaic_layout.py` adds **layout `08_global60_mosaic`**
and four one-layer maps, one per panel so each frame shows its own layer live in Pro (§31.1):

| panel | map | layer |
|---|---|---|
| A | "Mosaic ±60° — visible" | Viking MDIM 2.1 colour, bands 1–3 of `global60_svm_stack_200m.tif` |
| B | "Mosaic ±60° — day IR" | THEMIS Day IR, stack band 5 (`day_ir`) |
| C | "Mosaic ±60° — night IR" | THEMIS Night IR, stack band 4 (`night_ir`) |
| D | "Mosaic ±60° — topography" | `global60_dem.tif`, Elevation #1 ramp, 35 % transparent over `global60_hillshade.tif` |

- **Why the stack and not the sources:** it is G200, already stretched p1/p99 → 1–255 over ±60°
  (§31.2), and has overviews, so the image panels draw linear (no second stretch) from one file
  rather than three 14 GB sources without pyramids. The sheet exports in about a second.
- **The diurnal-contrast index is deliberately not a panel.** At ±60° it is local texture, never a
  material map (§28.10). The captions say the THEMIS panels are locally contrast-normalised and are
  compared within a region only, and that Viking albedo carries the regional material signal.
  That is also why panels B and C look near-uniform grey at this scale: it is the data, not a
  rendering fault.
- **The four maps draw in the stack's own CRS** (`Mars_Equidistant_Cylindrical_CM180`), centred on
  180°E, not the GCS of the other ±60° maps. Reprojected, the raster's 0°/360° edge left a **white
  seam down the middle of each small frame** (layout 07's larger frame does not show it). Native,
  the edges are the frame edges and nothing is resampled. **[V]**
- **NoData draws black,** not the page's white: the 2.7 % of the band without THEMIS cover, streaks
  in the south. The stack keeps only pixels valid in every band (97.33 %, §31.2), so the Viking panel
  shows them too.
- **`Map.moveLayer(reference, moved, …)`:** the reference layer comes first. Written the other way
  round, it put the hillshade over the elevation colours. Caught on the first rehearsal export.
- Rehearsed twice on a copy beside the `.aprx`, every export read. Then on the project: backup
  `Mars Project\.backups\Mars Project 20261008-010943.aprx`; `polish_layouts.py` found nothing to
  change on any of the eight sheets. PNG in `Global60\layouts\08_global60_mosaic.png`.
- **After:** 19 maps, all Mars; **8 layouts**. Captions quote only figures already in this record:
  47.67 DN Viking province separation (§28.10), r −0.49 and |r| ≤ 0.12 at Ius (§18), r −0.147 at
  ±60° (§31.2), DEM −8,528 to +21,226 m (the file's statistics).

## 39. Next steps, brainstormed — 2026-10-08

**The plan lives in `Z:\Mars Remote Sensing Project\NEXT-STEPS.md`**, on request: where the
project stands against its own goal, ten open decisions (D1–D10) with a recommendation each,
laptop work, desktop jobs, the manual digitising, a week-by-week schedule to 8 December with a data
freeze on 20 November, risks, and what has been ruled out. This file stays the authority on what
is true; that one is the plan. Facts found while writing it:

- **Lava flows have no product at any scale.** The ±60° "lava tube" class is 39 % / 2 % (§31.3) and
  the three `Landform_*` classes are empty. The only reference that could score a lava-flow result,
  the USGS geologic map, is not held (§10). **[V]**
- **58 of the 100 scripts in `build\` hard-code `Z:`** (a grep for the literal), so §11 q22 blocks
  every desktop job, where the drive is `F:`. **[V]**
- **Athabasca Valles is inside the analysis extent:** IAU 153.2–156.8°E, 7.2–10.0°N, centre
  155.0°E 8.5°N, beside Cerberus Fossae (154.4–174.7°E, 6.2–16.2°N); read from
  `MARS_nomenclature_misc_March2019`. The hook of §14.4 can be a second type area. **[V]**
- **The thermal claim has never been tested with the hand-drawn labels.** §27.3's +0.4 pt used terrain labels;
  the 512 labelled polygons and the §31 split make a band ablation possible. **[?]** until run.

### 39.1 Expanded the same day: the interim date, and two plan files

**The interim's due date was given: mid-November** (§1). The plan was reworked around two deadlines:

- **`NEXT-STEPS.md`** now carries a session-start checklist, D1–D10 (D1 answered; D10 new: *review* candidates with a `Review` field instead of drawing everything), the reference
  downloads checked on the web (D5), eight tests T1–T8 each with a prediction written before it
  runs, a figure list for both deadlines, an outline for the final, and a schedule with an
  **interim data cut on 2 November**, a **digitising checkpoint on 1 November** (if the digitising classes are
  still empty, both documents present machine products as candidates with measured recall),
  the interim ~13 November, and the **data freeze moved to 22 November**.
- **`INTERIM-PLAN.md`**: the interim drafts were built 13 and 18 September and every section of
  `content.py` they use is stale; a section-by-section map from old claim to current fact; the
  14 progress rows with facts (percentages left open); the results the interim can show, each
  with its sheet; wording traps; and a timeline.
- **The interim's four hypotheses and six questions had not been tracked since September.**
  Status read from this record: H1 and H2 untested (both need a volcanic type area), H3 partly
  answered (§19.3), H4 answered by a different method (fill depth, not DN gradient: §28.11);
  Q1, Q2 and Q4 answered, Q3 overtaken by §28.10, Q5 partly (Strahler order tops out at 3, §25),
  Q6 unexamined. **[V]** for the statuses; the tests that would close them are **[?]**.
- **Reference data, checked 2026-10-08 (web, not downloaded):** the USGS geologic map (SIM 3292,
  doi 10.3133/sim3292) is public domain and ships as a file geodatabase **in a Robinson
  projection**; the TES thermal-inertia maps (Putzig & Mellon 2007) are 20 px/°, ~50 MB, with
  interpolation masks; the Robbins & Hynek 2012 crater database is in research-data repositories
  (its ≥ 1 km count is quoted inconsistently online: read it from the file); **no public download
  was found for the Hynek et al. 2010 valley networks**. Nothing was downloaded: each is an open decision. **[E]**

### 39.2 The interim folder, read 2026-10-08 — the template is back, and the deck was never blocked

`NEXT STUFF\` holds the interim material; confirmed: **the exact due date is not known, only "mid-November"**.
The folder now holds **`2 Interim Presentation Template.pptx`** (put there 2026-10-08 01:31), the
13 Sep deck, the 18 Sep report and `.backup_20260918\`. **[V]**

- **The template is two slides of headings, nothing else:** slide 1 *Project Title*, *Project
  Investigators*, *Project Goals*; slide 2 *Relevant Spectral Bands*, *List of Project Tasks and
  Percent Complete*, *Preliminary Results (if available)*, *Project issues and Hurdles*, under the
  banner "Remote Sensing Project – Interim Presentation". Those seven headings are what the course
  asks of the interim. **[V]**
- **Both builders run** (test builds into scratch only; the originals untouched):
  `build_interim_le.py` → 12 slides in the Presentation 1 style, no template needed, and the
  source of the existing deck (§21.4 corrected); `build_interim_deck.py <template>` → 11 slides on
  the course template's banner and background. Both rendered through PowerPoint and read. Which
  one is submitted is an open decision (`NEXT-STEPS.md` D11). **[V]**
- **Neither deck, nor the report, contains a single map or figure.** Every slide is text or a
  table, while eight layouts exist (§38). `le_theme.py` already has picture helpers (`picture`,
  `picture_h`, `picture_box`, used by Presentation 1); `build_interim_docx.py` has none. Putting the
  layout PNGs into *Preliminary Results* is the largest single improvement available to the
  interim. **[V]**

### 39.3 The interim deck, rebuilt as a living build in the Presentation 1 style — 2026-10-08 **[V]**

**Decided:** the Presentation 1 style with graphics, no fixed slide count, and the interim "is dynamic and will
likely change largely as we gather and process the task data". Built the same night:

- `build\interim.py` (all slide text, each number with its §), `build\make_interim_figs.py` (layouts
  re-exported at 200 dpi with the sheet prose hidden in memory and trimmed; legends split out) and
  `build\build_interim_live.py` (the `le_theme.py` design). Output: `NEXT STUFF\Mars Global Mosaic -
  Interim Presentation.pptx`, **16 slides, seven of them maps or figures**; the 13 Sep deck is in
  `NEXT STUFF\.backup_20261008\`. Every slide rendered through PowerPoint and read. How to rebuild,
  and the open polish items, are in `INTERIM-PLAN.md`, its section 0.
- **Whole layout sheets on a slide failed**: their captions shrank to fine print and the maps to a
  third of the slide. Hiding the prose elements for the export (never saving the project) fixed it.
- **A legend exports blank once its map frame is hidden**, so legends are cut out as the difference
  between the sheet exported with and without them.
- **Two layer names in the project were worded in the third person** and showed in the deck's legend; renamed
  "Hand-drawn labels — …" in the `.aprx` (`build\fix_label_names.py`, backup first) and in
  `make_global60_maps.py`; layout 05's title likewise ("The first two SVM classifications, checked").
- **`verify_all.py` had been crashing since §37**: it counted the Mercury Iso Cluster VAT in the
  project gdb, which §37 moved out. It now reads the VAT in `Z:\_removed_not_Mars\removed_not_Mars.gdb`
  (`a00000010`, fields Value/Count, 10 rows), and falls back to the lineage alone if that
  folder. **39 / 39**; planting a wrong table makes that check fail. It still checks `content.py`,
  not `interim.py` (`INTERIM-PLAN.md`, its section 0, item 6).
- **Found while choosing figures:** `pres1_img\global60_thermal.png` quotes Viking's dusty–rocky
  separation as **54.4 DN over five boxes**; §28.10 gives **47.67 DN over seven provinces**. Not a
  contradiction, two box sets; quote the set with the number. `pres1_img\ius_fusion.png` still says
  "thermal-inertia proxy" on the image (§24 retired the term).

### 39.4 The project's text, rewritten in an objective, impersonal voice — 2026-10-08 **[V]**

**Request (2026-10-08):** remove the personal phrasing from the GitHub repo; everything is to be
written from an objective, impersonal point of view.

The record, both plan files and the build scripts had been written as third-person notes about
one person (possessives on the labels, the requests, the decisions; a group named in the second
person), and the public
repo mirrors all of them. Changed:

- **`build\neutral_voice.py`**: ordered phrase rules (specific before generic, each anchored at a word
  start; without the anchor a possessive rule also matched inside "this file"), whitespace kept so list
  indentation survives. `--check` exits 1 if any third-person pronoun is left. Applied to this file,
  `NEXT-STEPS.md`, `INTERIM-PLAN.md`, `Global60\README.md` and every build script that had one;
  all report **0** afterwards. Verbatim quotations of instructions keep their wording. The tool
  itself lists the phrases it removes, so it is kept off the project page.
- **The `.aprx`**: `build\fix_label_names.py` now applies the same rules to every layer name and
  layout text element (6 changes: the digitising group, the superseded-SVM group, layout 04's
  subtitle, layout 05's two score blocks, layout 06's subtitle). A renamed layer keeps the
  internal file it was created under, so `build\rebuild_groups.py` recreated the two groups under
  the new names: children copied in order, symbology byte-identical (compared as CIM JSON), the
  layout legends unchanged, rehearsed on a copy first. The builders write the new names too.
- **Figures and sheets**: `svm_check.png` regenerated from its cached arrays (its title and a caption
  carried the old wording); layout sheets 04–06 re-exported; the interim deck rebuilt.
- **The project page**: `github_sync.py` no longer mirrors the dated snapshot folders
  (`.backup_*`, `.py_backup_*`: history, kept on the drive and in git history) or `neutral_voice.py`.
  The README's reader-facing lines and the citation message were reworded in the repo itself.
- **Not changed, deliberately:** generic "you" inside the text of documents already delivered
  (Presentation 1, the prospectus) and the CC BY legal text. Rebuilding those would no longer match
  what was handed in.
- **Rule from now on:** everything written into this record, the plans, the scripts, the project
  and the repo uses the objective, impersonal voice. Run `neutral_voice.py --check` on any edited
  text before it is mirrored.
