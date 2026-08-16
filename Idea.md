# PS-02: Satellite Rooftop Heat-Vulnerability Classifier & Cool-Roof Prioritisation Engine
### Full System Design & Build Plan

---

## 1. Problem Reframed As An Engineering Task

**Input:** City Name (E.G. "Jaipur") Or A Bounding Box.
**Output:** A Ranked, Geolocated List Of Buildings That Should Get Cool-Roof Coatings First, Each With A Predicted Material, A Heat-Risk Score, Estimated Population Protected, And An Estimated Coating Cost — Exported As Geojson + CSV "Work Order."

This Is Fundamentally A **Five-Stage Pipeline**: Ingest → Segment/Align Buildings → Classify Roof Material → Fuse With Thermal Data → Score And Rank → Export. Treat Each Stage As An Independent Module With A Clean Interface, So Team Members Can Build In Parallel And Swap Components Without Breaking The Pipeline.

---

## 2. System Architecture (End-To-End)

```
┌─────────────────────────────────────────────────────────────────┐
│ STAGE 1 — DATA INGESTION                                         │
│  Google Open Buildings v3 (footprints + heights)                 │
│  Sentinel-2 L2A (RGB+NIR, 10m)  |  Landsat 8/9 (thermal, 30–100m)│
│  ECOSTRESS LST (70m, better revisit for heat)                    │
│  Census Houselisting (ward-level roof-material %)                │
│  WorldPop (population density)  |  OSM (roads, land use)         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ STAGE 2 — BUILDING-LEVEL FEATURE EXTRACTION                      │
│  Clip Sentinel-2 chip per building footprint (buffer ~5–10m)     │
│  Compute per-roof spectral indices (NDVI, NDBI, brightness,      │
│  texture/GLCM), building height & area from Open Buildings 2.5D  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ STAGE 3 — ROOF-MATERIAL CLASSIFICATION                            │
│  CNN backbone (ResNet/EfficientNet, ImageNet-pretrained)          │
│  → fine-tuned on Nacala-Roof-Material / Open Cities AI            │
│  → domain-adapted to India via ward-level Learning-from-Label-    │
│    Proportions (LLP) using Census roof-material tables as weak    │
│    supervision (no per-building labels needed)                    │
│  Output: per-building softmax over {metal/tin, asbestos-cement,   │
│  concrete/RCC, tile, thatch/tarpaulin}                            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ STAGE 4 — THERMAL CROSS-VALIDATION                                │
│  Join Landsat/ECOSTRESS LST raster to each building centroid      │
│  Aggregate day + night LST, compute diurnal amplitude             │
│  (proxy for heat retention overnight — the real killer)           │
│  Sanity-check: does predicted material's LST distribution match   │
│  known material thermal behaviour? Flag mismatches for QA.        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ STAGE 5 — HEAT-RISK SCORING                                       │
│  Weighted composite score per building (see §5 formula)           │
│  Inputs: material risk weight, LST anomaly, night retention,      │
│  building height/density, occupancy proxy (WorldPop / footprint)  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ STAGE 6 — RANKING & WORK-ORDER GENERATION                         │
│  Sort by risk score, apply budget/coverage constraint             │
│  (e.g. "coat roofs until 500,000 people are protected")           │
│  Output ranked GeoJSON + CSV: id, geometry, material, risk_score, │
│  population_protected, area_m2, estimated_cost_INR                │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. Data Pipeline Details

| Dataset | Purpose | Notes |
|---|---|---|
| Google Open Buildings V3 | Building Polygons (Footprint, Confidence, Area) | Filter Confidence > 0.7; Use 2.5D Temporal Layer For Height Where Available |
| Sentinel-2 L2A | RGB + NIR Imagery For Material Classification | 10M Resolution — One Building May Be < 1 Pixel In Dense Slums; Use Super-Resolution Or Accept Coarse Aggregation For Small Roofs |
| Landsat 8/9 TIRS | Land Surface Temperature, Both Day And Night Pass | 100M Thermal Resampled To 30M — Coarser Than Building Footprint, Join At Building Centroid |
| ECOSTRESS | Higher-Frequency LST (70M), Better For Diurnal/Night Captures | Use Where Available (Not Full Daily Global Coverage) — Fallback To Landsat |
| Census Houselisting & Housing Tables (2011, House Listing) | Ward-Level % Of Houses By Roof Material | This Is Your **Weak Supervision** Signal — No Building-Level Labels Exist, Only Ward Aggregates |
| Worldpop | Gridded Population Estimates | Used To Estimate "Population Protected" Per Roof |
| OSM | Roads, Land Use, Slum/Informal Settlement Tags Where Tagged | Useful For Context Features And QA |

**Data Engineering Pattern:** Build A Single `GeoParquet`/`PostGIS` Table Keyed By `building_id` With One Row Per Building, Columns Accumulating As Each Pipeline Stage Runs. This Avoids Repeated Joins And Lets Every Team Member Work Off The Same Table.

---

## 4. Roof-Material Classifier — The Core ML Component

### 4.1 Why This Is A Weak-Supervision Problem, Not Standard Classification
You Have **No Per-Building Ground Truth** For Indian Roofs. What You Have:
- A Handful Of Labeled Datasets From Other Countries (Mozambique's Nacala-Roof-Material, Open Cities AI — Africa/Asia Disaster-Response Imagery) — Different Roofing Styles But Transferable Low-Level Texture/Material Features.
- Ward-Level **Aggregate** Roof-Material Percentages From Census — You Know 40% Of Ward X Is Metal/Tin, 25% Asbestos, Etc., But Not Which Specific Building Is Which.

This Is Exactly The **Learning From Label Proportions (LLP)** Setting.

### 4.2 Recommended Training Strategy (In Order Of Implementation Effort)

1. **Baseline Transfer Learning** — Fine-Tune A ResNet50/Efficientnet-B0 (ImageNet-Pretrained) On Nacala-Roof-Material + Open Cities AI Labeled Chips. This Gives You A Material Feature Extractor That Generalizes Reasonably Across Geographies (Roofing Material Physics/Spectral Signature Is Somewhat Universal).
2. **Self-Supervised Pretraining On Local Imagery** — Run Simclr/DINO Or A Simpler Rotation/Jigsaw Pretext Task On Unlabeled Sentinel-2 Chips From Your Target Indian City. This Adapts The Feature Space To Local Imagery Statistics (Lighting, Resolution, Vegetation) Before You Ever See A Label.
3. **LLP Fine-Tuning With Census Ward Proportions** — Freeze/Fine-Tune The Backbone With A **Bag-Level Loss**: For Each Ward (Bag Of Buildings), Compute The Mean Predicted Class Distribution Across All Buildings In That Ward, And Penalize The KL-Divergence Between That Mean And The Known Census Ward Proportions. This Is The Key Novel Piece — Cite "Learning From Label Proportions" (Yu Et Al. And Follow-Ups) In Your Writeup, It's A Well-Established Weakly-Supervised Technique.
4. **(Stretch) Multi-Sensor Fusion** — Concatenate A Small Thermal-Derived Feature (Per-Building LST + Diurnal Amplitude) Into The Classifier's Final Layer Before Softmax, Since Certain Materials (Metal, Asbestos) Have Distinctive Thermal Signatures. This Closes The Loop Between Stage 3 And Stage 4 And Is A Nice Technical Differentiator For Judges.

### 4.3 Practical Shortcuts For A Hackathon Timeline
- Don't Train From Scratch — Everything Above Should Be Fine-Tuning, Not Full Training.
- Pick **One Mid-Size Indian City** (Or Even One District) As Your Demo AOI, Not "Any Indian City," To Keep Compute And Data Volume Tractable. State In Your Submission That The Pipeline Generalizes.
- If LLP Training Doesn't Converge In Time, Fall Back To **Pseudo-Labeling**: Use The Transfer-Learned Model's Confident Predictions, Calibrate The Overall Class Distribution To Match Ward-Level Census Proportions (A Simpler Proportion-Matching Heuristic Instead Of Full LLP Loss), And Present LLP As The "Production-Grade" Approach In Your Writeup/Roadmap Slide.

---

## 5. Heat-Risk Score — Formula Design

Judges Will Want A Legible, Defensible Formula, Not A Black Box. Propose A Transparent Weighted Sum, Normalized 0–1 Per Component:

```
RiskScore = w1·Material_Risk + w2·LST_Anomaly + w3·Night_Retention
          + w4·Density_Height + w5·Occupancy_Vulnerability
```

| Component | How Computed | Rationale |
|---|---|---|
| Material_Risk | Lookup Table: Tin/Tarpaulin/Asbestos = High, Tile/RCC = Low, Calibrated From Literature On Roof Surface Temps | Material Is The Direct Physical Driver |
| LST_Anomaly | (Building LST − Ward Mean LST) / Ward Std | Flags Buildings Hotter Than Their Neighbourhood |
| Night_Retention | (Night LST − Day LST Minimum) Or Diurnal Amplitude | Captures "Stays Hot Overnight" — The Actual Killer Per The Problem Statement |
| Density_Height | Building Height × Neighbourhood Density (Heat-Island Proxy) | Low, Dense, Single-Storey Informal Housing Traps Heat |
| Occupancy_Vulnerability | Worldpop Density Over Footprint, Optionally Weighted By Informal-Settlement Flag | Prioritizes Where People Actually Live, Not Just Hot Pixels |

Suggested Starting Weights: Material 0.30, LST Anomaly 0.25, Night Retention 0.20, Density/Height 0.15, Occupancy 0.10 — Expose These As A Config File So Judges/Users Can Re-Weight Live (Nice Demo Feature).

---

## 6. Output: The Work Order

```json
{
  "building_id": "OB_12345",
  "geometry": {...},
  "predicted_material": "asbestos-cement",
  "material_confidence": 0.78,
  "risk_score": 0.86,
  "rank": 1,
  "population_protected_est": 6,
  "roof_area_m2": 42.3,
  "estimated_cost_inr": 6300,
  "ward": "Ward 14"
}
```
CSV Export Mirrors This Flattened, Sorted By `Rank`. This Is The Artifact A Municipal Cool-Roof Program Officer Could Actually Hand To A Contractor — Make This The Centerpiece Of Your Demo.

---

## 7. Tech Stack

| Layer | Tools |
|---|---|
| Data Access | Google Earth Engine (Sentinel-2, Landsat, Open Buildings, Worldpop All Queryable Directly), `Geemap`, `Osmnx` |
| Geospatial Processing | Geopandas, Rasterio, Shapely, Postgis/Geoparquet |
| ML | Pytorch, `Timm` (Pretrained Backbones), Scikit-Learn For The LLP Loss / Baseline Scoring |
| Thermal Fusion | `Rioxarray`, `Xarray` For Raster-Vector Joins |
| Backend/API | Fastapi Serving The Scored Geojson | 
| Frontend/Demo | Streamlit Or A Simple Leaflet/Mapbox GL Map Showing Ranked Roofs Color-Coded By Risk — This Is Your Money Shot For Judges |
| Orchestration | A Single `run_pipeline.py` Or Lightweight Prefect/Airflow DAG If Time Allows — For A Hackathon, A Script With Clear Stage Functions Is Enough |

---

## 8. Team Role Split (Assuming 4–5 People)

1. **Geo-Data Lead** — Earth Engine Queries, Open Buildings Extraction, Building-Footprint Chip Generation, Ward-Census Join.
2. **ML Lead** — Roof-Material Classifier: Transfer Learning + LLP Fine-Tuning.
3. **Thermal/Scoring Lead** — Landsat/ECOSTRESS LST Joins, Risk-Score Formula, Ranking + Cost-Estimate Logic.
4. **Full-Stack/Demo Lead** — Fastapi + Leaflet Map, Geojson/CSV Export, Polished Live Demo.
5. **(If 5Th Member) Storyteller/PM** — Problem Framing, Impact Narrative, Slide Deck, Ties To State Cool-Roof Budget Numbers For The Pitch.

---

## 9. Suggested Timeline (Mapped To Your Poster's Dates)

| Phase | Dates | Focus |
|---|---|---|
| Setup | Aug 5–8 | Earth Engine Access, Pull Open Buildings + Sentinel-2 + Census For 1 Demo City, Set Up Repo/Data Schema |
| Core Build | Aug 9–15 | Classifier Fine-Tuning + LLP, Thermal Join, Risk Scoring |
| Integration | Aug 16–19 | End-To-End Pipeline Run On Demo AOI, Generate First Work-Order Output, Build Map Demo |
| Polish & Submit | Aug 20 | Jury Review Deadline — Freeze Pipeline, Polish Deck, Record Demo Video As Backup |
| Presentation Prep | Aug 20–24 | Refine Pitch, Rehearse For Winner Announcement / World Health Summit Expert Meeting |

---

## 10. What Will Impress Judges

- **A Live Map** They Can Click Through (Ranked Roofs, Color-Coded By Risk) — Far More Persuasive Than Slides Alone.
- **The LLP Weak-Supervision Story** — Shows You Understood The Hardest Real Constraint (No Ground-Truth Labels) Instead Of Hand-Waving It.
- **A Defensible, Tunable Risk Formula** Rather Than An Opaque ML Score.
- **Concrete Impact Numbers**: "X People Protected Per ₹ Spent" Using Your Cost/Population Fields — Ties Directly To The "Measurably Efficient And Equitable" Framing In The Problem Statement.
- **Honesty About Validation** — Since You Won't Have Ground-Truth Roof Labels To Test Against, Show Your QA Approach (Thermal Cross-Validation, Spot-Checking A Handful Of Buildings Via Imagery/Street View) Rather Than Claiming An Unverifiable Accuracy Number.

---

## 11. Known Risks & Mitigations

| Risk | Mitigation |
|---|---|
| Sentinel-2 10M Resolution Too Coarse For Small Individual Roofs | Aggregate Small/Adjacent Buildings Into Clusters Where Needed; Be Upfront About Resolution Limits In The Writeup |
| LLP Training Unstable/Doesn't Converge In Time | Fall Back To Proportion-Calibrated Pseudo-Labeling (See §4.3) |
| ECOSTRESS Coverage Gaps For Chosen City/Date | Default To Landsat 8/9 Thermal As Primary, ECOSTRESS As Enhancement Where Available |
| No Ground Truth To Report Accuracy Against | Report Ward-Level Proportion Match (Predicted Vs Census Aggregate) As Your Validation Metric — Legitimate For LLP Models |
| Scope Too Large For Hackathon Window | Restrict Demo AOI To One City/District; State Clearly That Architecture Generalizes Nationally |