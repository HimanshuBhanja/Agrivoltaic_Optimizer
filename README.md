# The Agrivoltaic Optimizer

## Academic Context

- **Program:** M.Sc. Agriculture Analytics
- **Study Area:** Jodhpur District, Rajasthan
- **Members:** K. Yaswanthi, Sathvik, Himanshu

## Large Files

Too large for normal repo storage — hosted separately on Google Drive:

- `Lulc_jodhpur(updated one).tif`
- `merged_dem.tif`
- `grid_distance.tif`
- `road_distance.tif`
- `Screen demo of the PyQGIS dashboard.mp4`

**Google Drive folder:** *Agrivoltaic Optimizer — Large Files* — **https://drive.google.com/drive/folders/1Cr6ZaOrBn4RWhjpJDDig9asa57VGeH9B?usp=sharing**

## Repository Structure

```
Agrivoltaic_Optimizer/
│
├── dem/
│   ├── merged_dem.vrt
│   ├── SRTM DEM tiles
│   └── README.md
│
├── grid_distance/
│   ├── grid-distance source/intermediate data
│   └── README/documentation
│
├── lulc/
│   ├── lulc_jodhpur.tif
│   └── README.md
│
├── road_distance/
│   ├── road-distance source/intermediate data
│   └── README/documentation
│
├── vectors/
│   ├── Jodhpur boundary
│   ├── simplified boundary
│   └── README.md
│
├── docs/
│   ├── Agrivoltaic_Optimizer_Report.docx
│   ├── Project Proposal/
│   │   ├── PROPOSAL.pdf
│   │   └── README.md
│   └── README.md
│
├── outputs/
│   ├── agrivoltaic_dashboard_.html
│   ├── K-Means Validation Elbow Method, Optimal K is 5.jpeg
│   ├── rasters/
│   │   ├── agrivoltaic_suitability.tif
│   │   └── cluster_output (1).tif
│   └── README.md
│
├── plugin/
│   ├── agrivoltaic_plugin.py
│   ├── initiating the ui.py
│   └── suitability_initiating script.py
│
├── scripts/
│   └── agrivoltaic_optimizer.ipynb
│
├── jodhpur_boundary/
│
├── smoothed_suitability.tif
├── smoothed_suitability.tfw
│
├── .gitattributes
└── .gitignore
```

## 1. Overview

Hybrid spatial-intelligence system for identifying optimal land zones for combined solar-energy and agriculture (agrivoltaic) development.

## 2–3. Objectives

1. Acquire and organize geospatial datasets.
2. Preprocess and spatially align input raster datasets.
3. Develop a Multi-Criteria Decision Analysis (MCDA) framework for agrivoltaic suitability assessment.
4. Apply unsupervised K-Means clustering to validate spatial segmentation of MCDA output.
5. Generate spatial suitability map showing agrivoltaic suitability zones.
6. Develop interactive GIS visualization via QGIS and PyQGIS.
7. Provide standalone interactive HTML visualization of results.

## 4. Research Questions

1. Which geographic locations are most suitable for agrivoltaic systems?
2. How can geospatial data and ML evaluate land suitability for dual-use solar-agriculture systems?
3. Which environmental and infrastructural factors influence agrivoltaic feasibility?
4. How can spatial intelligence support policymakers, agricultural planners and renewable-energy developers in site selection?

## 5. Study Area

**Jodhpur District, Rajasthan, India**

Selected for:
- High solar irradiance
- Dryland agricultural environment
- Availability of agricultural land
- Relevance to solar-energy development
- Potential agrivoltaic application

Validated Jodhpur district boundary: **~22,850 km²** (master AOI).

## 6. System Architecture

```text
Geospatial Data Acquisition
          ↓
Spatial Database / Data Organization
          ↓
Raster Preprocessing
          ↓
AOI Clipping & CRS Alignment
          ↓
Raster Grid Alignment
          ↓
Feature Preparation & Normalization
          ↓
MCDA Suitability Scoring
          ↓
K-Means Clustering Validation
          ↓
Suitability Classification
          ↓
GeoTIFF Output
          ↓
QGIS / PyQGIS Dashboard
          ↓
Interactive HTML Visualization
```

## 7. Data Sources

| Dataset | Source | Resolution / Type | Purpose |
|---|---|---|---|
| SRTM DEM | USGS EarthExplorer | 30 m | Elevation, slope, aspect |
| LULC | ESA WorldCover 2021 | 10 m | Agricultural land classification |
| GHI Solar Data | NASA POWER API | Point/Grid | Solar irradiance |
| Roads & Infrastructure | OpenStreetMap | Variable | Infrastructure proximity |
| District Boundary | GADM Level 2 | Vector | AOI definition |

## 8. Input Spatial Layers

### 8.1 LULC
Binary agricultural mask derived from ESA WorldCover:
```
Agricultural pixel     → 1
Non-agricultural pixel → 0
```

### 8.2 GHI
Global Horizontal Irradiance — indicator of solar-energy potential. Source: NASA POWER.

### 8.3 DEM
30 m SRTM DEM used as terrain reference; derives Elevation, Slope, Aspect. Also serves as the reference raster grid for spatial alignment.

### 8.4 Road Distance
Infrastructure-accessibility criterion, inverse-normalized:
```
Smaller distance → Higher suitability
Larger distance   → Lower suitability
```

### 8.5 Grid Distance
Initially considered, but **excluded** from final model — delivered raster showed zero spatial variance (cannot meaningfully discriminate locations). Its weight was redistributed proportionally among remaining variables.

### 8.6 Terrain Slope
Derived from DEM. Flatter terrain favored:
```
Lower slope  → Higher suitability
Higher slope → Lower suitability
```

### 8.7 Terrain Aspect
Directional orientation of terrain; used to derive a south-facing directional suitability score.

## 9. Raster Preprocessing

- AOI clipping
- CRS alignment
- Raster grid alignment
- Resampling
- Feature preparation
- Agricultural masking
- Normalization

DEM used as reference raster for the common processing grid.

## 10. Raster Alignment

Input layers differ in resolution, extent, CRS, and pixel grid — aligned to a common spatial reference based on the DEM.

**Resampling strategy:**
- Continuous variables (GHI, Slope, Distance surfaces) → continuous resampling
- Categorical variables (LULC) → categorical-preserving resampling (prevents invalid land-cover classes from interpolation)

## 11. MCDA Framework

Multiple spatial criteria combined into one composite suitability score. Each criterion normalized to a comparable scale, multiplied by its weight, combined via weighted linear combination:

```
Suitability Score =
    Weighted LULC
  + Weighted GHI
  + Weighted Road Proximity
  + Weighted Slope
  + Weighted Aspect
```

## 12. Final MCDA Weight Matrix

| Variable | Description | Weight | Normalization |
|---|---|---|---|
| LULC Binary | Agricultural pixel classification | 38% | Binary (0/1) |
| GHI Solar | Global Horizontal Irradiance | 25% | Min-Max |
| Road Proximity | Distance to road network | 17% | Min-Max inverse |
| Terrain Slope | Slope derived from DEM | 13% | Min-Max inverse |
| Terrain Aspect | South-facing directional score | 7% | Min-Max |

**Total: 38 + 25 + 17 + 13 + 7 = 100%**

Grid distance excluded (zero spatial variance); weight redistributed proportionally across remaining five variables.

## 13. Normalization

**Standard Min-Max** (higher values preferred):
```
Normalized Value = (X - Xmin) / (Xmax - Xmin)   → range 0–1
```

**Inverse Normalization** (lower values preferred — used for Road distance, Slope):
```
Normalized Value = (Xmax - X) / (Xmax - Xmin)
```

## 14. Composite Suitability Score

```
Suitability =
    0.38 × LULC
  + 0.25 × GHI
  + 0.17 × Road Proximity
  + 0.13 × Slope
  + 0.07 × Aspect
```

## 15. K-Means Machine Learning

Unsupervised validation step to check whether MCDA suitability values show meaningful spatial segmentation. No labeled ground-truth parcels were available, so supervised classification was not used as the primary model — K-Means investigates structure of the MCDA output instead.

## 16. Elbow Method

Tested K = 2–7, computed Within-Cluster Sum of Squares (WCSS) for each. Elbow point identified at:

**K = 5** — aligns with the five intended suitability tiers.

## 17. Suitability Classification

| Class | Label | Score Range | Description |
|---|---|---|---|
| 1 | Unsuitable | 0.00–0.20 | Physically or legally ineligible |
| 2 | Low Suitability | 0.20–0.40 | Marginal zones, significant investment needed |
| 3 | Moderate Suitability | 0.40–0.60 | Viable, standard infrastructure requirements |
| 4 | High Suitability | 0.60–0.80 | Prime development zones, high ROI potential |
| 5 | Prime Agrivoltaic Zone | 0.80–1.00 | Optimal dual-use locations |

Documented continuous MCDA composite score range: **0.000 → 0.760**

## 18. Final Outputs

- **Suitability GeoTIFF:** `outputs/rasters/agrivoltaic_suitability.tif`
- **K-Means Cluster Raster:** `outputs/rasters/cluster_output (1).tif`
- **Elbow Method Plot:** `outputs/K-Means Validation Elbow Method, Optimal K is 5.jpeg`
- **Interactive HTML Dashboard:** `outputs/agrivoltaic_dashboard_.html`
- **PyQGIS Plugin:** `plugin/` — `agrivoltaic_plugin.py`, `initiating the ui.py`, `suitability_initiating script.py`

Dashboard provides interactive suitability visualization with slider-based exploration.

## 19. Results

- Study Area: ~22,850 km²
- High Suitability: 40.3% (~9,213 km²)
- Low Suitability: 59.7% (~13,637 km²)
- Optimal K-Means: K = 5
- High-suitability zones concentrated mainly in eastern Jodhpur District

Stronger suitability associated with combinations of agricultural land, favorable terrain, high solar irradiance, and favorable road proximity.

## 20. Key Model Observations

- **LULC (38%)** — highest weight; agricultural land eligibility is the dominant criterion.
- **GHI (25%)** — Jodhpur has generally high irradiance, so less spatial discrimination than more variable factors.
- **Road Proximity (17%)** — closer roads → higher suitability (inverse normalization).
- **Slope (13%)** — flatter terrain → higher suitability.
- **Aspect (7%)** — south-facing directional suitability score.
- **Grid Distance** — excluded (zero spatial variance); a data-integrity/model-design decision, not an unjustified removal.

## 21. Technology Stack

- **Programming:** Python, NumPy
- **Geospatial Processing:** Rasterio, GeoPandas, QGIS, PyQGIS
- **Machine Learning:** scikit-learn, K-Means Clustering
- **Spatial Database:** PostgreSQL, PostGIS, SQLAlchemy, psycopg2
- **Visualization:** QGIS, PyQGIS, HTML5, Leaflet.js

## 22. Reproducibility

Organized for reproduction using provided input datasets, processing notebook, spatial boundary, raster outputs, plugin source code, and documentation. Methodology is district-agnostic in concept — swap the AOI boundary to adapt to another region with equivalent datasets.

## 23. Future Work

- Integration of labeled field data
- Random Forest classification
- Multi-district analysis across Rajasthan
- Live API-based data updates
- Additional agricultural constraints
- Environmental sensitivity and protected-area constraints
- More detailed infrastructure variables
- Economic feasibility criteria
- Dynamic suitability recalculation

Future ML stage can use labeled field data to move from unsupervised validation toward supervised prediction.

## 24. Real-World Applications

- **Renewable Energy Developers** — spatial screening of potential agrivoltaic development zones
- **Agricultural Planners** — identify agricultural areas where solar infrastructure may coexist with farming
- **District Administration** — spatial planning and identification of potential development corridors
- **Agricultural Extension** — support farmers/planners evaluating dual-use areas
- **Sustainable Energy Planning** — balance renewable energy expansion with agricultural land preservation

## 25. Project Significance

```
Agriculture + Geospatial Intelligence + Machine Learning
```

Demonstrates how spatial data and ML can support sustainable land-use decisions — evaluating locations where solar development and agriculture can coexist rather than treating them as mutually exclusive.

## 36. References and Data Sources

- GADM — Global Administrative Boundaries
- USGS EarthExplorer — SRTM 1 Arc-Second Global DEM
- ESA WorldCover — Global Land Cover
- NASA POWER — Solar and climate data
- OpenStreetMap — Roads and infrastructure
- PostgreSQL, PostGIS
- QGIS
- scikit-learn
- Rasterio



## 27. Conclusion

```
Geospatial Data → Raster Preprocessing → Normalization → MCDA Suitability Scoring
→ K-Means Validation → Suitability Classification → GeoTIFF → Interactive GIS Visualization
```

The Jodhpur case study produced a suitability framework with five suitability tiers and an optimal K-Means cluster count of five — demonstrating the potential of combining GIS, remote sensing, MCDA, and machine learning to support sustainable land allocation between agricultural production and renewable-energy generation.

## License

Academic project developed for educational, analytical, and research purposes.
