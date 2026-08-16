/**
 * PARoo - Production Frontend Application Controller
 * Complete 6-Dataset Analytics, 3-Satellite Ingestion, Interactive Map Drawing, And Work-Order Studio
 */

// Global Application State
const State = {
  CurrentCity: "Jaipur",
  ActiveLayer: "CompositeRisk",
  GeojsonData: null,
  PipelineData: null,
  SelectedFeature: null,
  Map: null,
  GeojsonLayer: null,
  DrawnAOILayer: null,
  SatelliteBaseLayer: null,
  DarkBaseLayer: null,
  IsSatelliteBaseActive: false,
  Charts: {},
  ActiveWeights: {
    MaterialWeight: 0.30,
    LSTAnomalyWeight: 0.25,
    NightRetentionWeight: 0.20,
    DensityHeightWeight: 0.15,
    OccupancyWeight: 0.10
  },
  BudgetCapINR: 1000000.0,
  PreferredCoating: "High-Albedo Elastomeric Cool Roof Coating (Dual Coat)"
};

// Material Color Palette
const MATERIAL_COLORS = {
  "Metal / Tin": "#06B6D4",         // Cyan
  "Asbestos / Cement": "#8B5CF6",    // Purple
  "Concrete / RCC": "#64748B",       // Slate Grey
  "Clay / Tile": "#EA580C",          // Terracotta
  "Thatch / Tarpaulin": "#F59E0B"    // Amber
};

// Initialize Application On DOM Loaded
document.addEventListener("DOMContentLoaded", () => {
  console.log("Initializing PARoo Production Geospatial Controller...");
  InitMap();
  InitEventListeners();
  LoadCityData("Jaipur");
});

/**
 * Initialize Leaflet Geospatial Map Canvas With Interactive Drawing
 */
function InitMap() {
  console.log("Setting Up Leaflet Geospatial Map & Satellite Layers...");
  State.Map = L.map("LeafletMapInstance", {
    center: [26.9124, 75.7873],
    zoom: 14,
    zoomControl: false
  });

  L.control.zoom({ position: "bottomright" }).addTo(State.Map);

  // 1. Dark Matter Vector Base Layer
  State.DarkBaseLayer = L.tileLayer("https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png", {
    attribution: "&copy; OpenStreetMap contributors &copy; CARTO",
    subdomains: "abcd",
    maxZoom: 19
  });
  State.DarkBaseLayer.addTo(State.Map);

  // 2. High-Resolution Optical Satellite Hybrid Base Layer
  State.SatelliteBaseLayer = L.tileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}", {
    attribution: "Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community",
    maxZoom: 19
  });

  // Feature Group For Drawn Bounding Boxes
  State.DrawnAOILayer = new L.FeatureGroup();
  State.Map.addLayer(State.DrawnAOILayer);

  // Listen To Leaflet Draw Creation Events
  State.Map.on(L.Draw.Event.CREATED, (event) => {
    const Layer = event.layer;
    State.DrawnAOILayer.clearLayers();
    State.DrawnAOILayer.addLayer(Layer);

    const Bounds = Layer.getBounds();
    const MinLat = Bounds.getSouth();
    const MinLon = Bounds.getWest();
    const MaxLat = Bounds.getNorth();
    const MaxLon = Bounds.getEast();

    const AOILabel = `Custom AOI [${MinLat.toFixed(3)}°N, ${MinLon.toFixed(3)}°E]`;
    console.log(`Captured Custom Map AOI: [${MinLon.toFixed(4)}, ${MinLat.toFixed(4)}, ${MaxLon.toFixed(4)}, ${MaxLat.toFixed(4)}] -> ${AOILabel}`);
    RunCustomAOIPipeline([MinLon, MinLat, MaxLon, MaxLat], AOILabel);
  });
}

/**
 * Show / Hide Floating Geospatial Processing HUD Banner With Live Progress Bar
 */
function ShowMapLoader(Title = "Analyzing Satellite Rooftops", Subtitle = "Extracting Multispectral Bands & Thermal Signatures...", Percent = 15) {
  const Loader = document.getElementById("MapRadarLoader");
  const TextEl = document.getElementById("RadarLoaderText");
  const StepEl = document.getElementById("RadarStepBadge");
  const BarEl = document.getElementById("RadarProgressBar");
  const PercentEl = document.getElementById("RadarProgressPercent");

  if (Loader) {
    if (TextEl) {
      TextEl.innerHTML = `<i data-lucide="satellite" style="width: 14px; height: 14px; color: var(--accent-cyan);"></i><span>${Title}</span>`;
      if (window.lucide) lucide.createIcons();
    }
    if (StepEl) StepEl.textContent = Subtitle;
    if (BarEl) BarEl.style.width = `${Math.min(100, Math.max(0, Percent))}%`;
    if (PercentEl) PercentEl.textContent = `${Math.round(Percent)}%`;
    Loader.classList.add("active");
  }
}

function SetMapProgress(Percent, Title, Subtitle) {
  const TextEl = document.getElementById("RadarLoaderText");
  const StepEl = document.getElementById("RadarStepBadge");
  const BarEl = document.getElementById("RadarProgressBar");
  const PercentEl = document.getElementById("RadarProgressPercent");

  if (Title && TextEl) {
    TextEl.innerHTML = `<i data-lucide="satellite" style="width: 14px; height: 14px; color: var(--accent-cyan);"></i><span>${Title}</span>`;
    if (window.lucide) lucide.createIcons();
  }
  if (Subtitle && StepEl) StepEl.textContent = Subtitle;
  if (BarEl) BarEl.style.width = `${Math.min(100, Math.max(0, Percent))}%`;
  if (PercentEl) PercentEl.textContent = `${Math.round(Percent)}%`;
}

function HideMapLoader() {
  const Loader = document.getElementById("MapRadarLoader");
  if (Loader) {
    SetMapProgress(100, null, "Pipeline Complete (100%)");
    setTimeout(() => {
      Loader.classList.remove("active");
    }, 450);
  }
}

/**
 * Run Real Pipeline For Custom AOI Bounding Box
 */
async function RunCustomAOIPipeline(BBox, CustomName = "Custom AOI") {
  const [MinLon, MinLat, MaxLon, MaxLat] = BBox;
  State.CurrentCity = CustomName;

  // Update Header Municipality Pill
  document.getElementById("HeaderCityName").textContent = CustomName;

  // Add & Select In Dropdown If Not Present
  const CityDropdown = document.getElementById("CitySelector");
  if (CityDropdown) {
    let Option = Array.from(CityDropdown.options).find(o => o.value === CustomName);
    if (!Option) {
      Option = document.createElement("option");
      Option.value = CustomName;
      Option.textContent = `📍 ${CustomName}`;
      CityDropdown.appendChild(Option);
    }
    CityDropdown.value = CustomName;
  }

  try {
    ShowMapLoader(`Ingesting Custom AOI: ${CustomName}`, "Stage 1: Google Open Buildings v3 Ingestion", 15);
    await new Promise(r => setTimeout(r, 120));

    SetMapProgress(35, `Ingesting Custom AOI: ${CustomName}`, "Stage 2: Copernicus Sentinel-2 L2A Optical Reflectance");
    await new Promise(r => setTimeout(r, 120));

    SetMapProgress(60, `Ingesting Custom AOI: ${CustomName}`, "Stage 3: USGS Landsat 8/9 & NASA ECOSTRESS Thermal Inversion");

    const Response = await fetch("/Api/Footprints/CustomAOI", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        MinLon, MinLat, MaxLon, MaxLat,
        AOIName: CustomName
      })
    });

    if (!Response.ok) throw new Error("Custom AOI Pipeline Failed");

    SetMapProgress(85, `Ingesting Custom AOI: ${CustomName}`, "Stage 4: Weakly Supervised LLP Classifier & Knapsack Work-Order");
    const Data = await Response.json();
    State.PipelineData = Data;
    State.GeojsonData = Data.GeoJSON;

    UpdateHeaderSummaryMetrics(Data);
    RenderGeoJSONLayer();
    UpdateWorkOrderTable();
    UpdateExecutiveBriefing(Data);

    // Fit Map View To Custom AOI Polygon
    State.Map.fitBounds([[MinLat, MinLon], [MaxLat, MaxLon]], { padding: [40, 40], duration: 1.0 });

    SetMapProgress(100, `Complete: ${CustomName}`, `Loaded ${Data.GeoJSON.features.length} Building Footprints`);
  } catch (Err) {
    console.error(`Custom AOI Error: ${Err.message}`);
    ShowMapLoader("Error In Processing AOI", Err.message, 100);
  } finally {
    setTimeout(() => HideMapLoader(), 600);
  }
}

/**
 * Fetch And Render Geospatial Data For Chosen Target City
 */
async function LoadCityData(CityName, ForceRefresh = false) {
  try {
    console.log(`Fetching Geospatial Pipeline Data For: ${CityName}`);
    ShowMapLoader(`Ingesting Satellite Layers For ${CityName}`, "Stage 1: Google Open Buildings v3 & 2.5D Footprints", 15);
    
    State.CurrentCity = CityName;
    document.getElementById("HeaderCityName").textContent = CityName;

    // Update Dropdown Selection
    const CityDropdown = document.getElementById("CitySelector");
    if (CityDropdown && CityDropdown.value !== CityName) {
      CityDropdown.value = CityName;
    }

    SetMapProgress(35, `Processing ${CityName}`, "Stage 2: Sentinel-2 L2A Multispectral Optics (B02-B11)");
    await new Promise(r => setTimeout(r, 80));

    SetMapProgress(65, `Processing ${CityName}`, "Stage 3: Landsat 8/9 & NASA ECOSTRESS Thermal Inversion");

    const Response = await fetch(`/Api/Footprints/${encodeURIComponent(CityName)}`);
    if (!Response.ok) {
      throw new Error(`Failed To Load Footprints For ${CityName}`);
    }

    SetMapProgress(85, `Processing ${CityName}`, "Stage 4: Census 2011 LLP Classifier & Knapsack Pareto Solver");
    const Data = await Response.json();
    State.PipelineData = Data;
    State.GeojsonData = Data.GeoJSON;

    UpdateHeaderSummaryMetrics(Data);
    RenderGeoJSONLayer();
    UpdateWorkOrderTable();
    UpdateExecutiveBriefing(Data);

    // Fetch And Render 6-Dataset Analytics
    FetchAndRenderAll6DatasetAnalytics(CityName);

    // Zoom Map To City Centroid
    if (State.GeojsonData && State.GeojsonData.features.length > 0) {
      const FirstCoords = State.GeojsonData.features[0].properties;
      State.Map.flyTo([FirstCoords.CentroidLat, FirstCoords.CentroidLon], 14, { duration: 1.0 });
    }

    SetMapProgress(100, `Complete: ${CityName}`, `Loaded ${Data.GeoJSON.features.length} Rooftops Successfully`);
    console.log("City Data Successfully Loaded And Rendered.");
  } catch (Error) {
    console.error(`Error In LoadCityData: ${Error.message}`);
  } finally {
    HideMapLoader();
  }
}

/**
 * Render Vector Footprint Polygons With Dynamic Choropleth Shaders
 */
function RenderGeoJSONLayer() {
  if (!State.GeojsonData || !State.Map) return;

  if (State.GeojsonLayer) {
    State.Map.removeLayer(State.GeojsonLayer);
  }

  State.GeojsonLayer = L.geoJSON(State.GeojsonData, {
    style: Feature => GetFeatureStyle(Feature),
    onEachFeature: (Feature, Layer) => {
      const Props = Feature.properties;
      
      // Hover Tooltip
      const TooltipContent = `
        <div style="font-family: 'Inter', sans-serif; font-size: 11px;">
          <div style="font-weight: 700; color: #06B6D4;">${Props.BuildingId} • Rank #${Props.Rank}</div>
          <div>Material: <b>${Props.PredictedMaterial}</b> (${Math.round(Props.MaterialConfidence * 100)}%)</div>
          <div>Risk Score: <b style="color: ${Props.HeatRiskAnalysis?.RiskColorHex || '#EF4444'}">${Props.RiskScore}</b></div>
          <div>Area: <b>${Props.RoofAreaSquareMeters} m²</b> | Est. Cost: <b>₹${Props.EstimatedCostINR?.toLocaleString()}</b></div>
        </div>
      `;
      Layer.bindTooltip(TooltipContent, { sticky: true, opacity: 0.95 });

      // Click Event To Select Building In Dossier
      Layer.on({
        click: () => SelectBuildingFeature(Feature, Layer),
        mouseover: (e) => {
          const TargetLayer = e.target;
          TargetLayer.setStyle({ weight: 3, color: "#FFFFFF", fillOpacity: 0.9 });
        },
        mouseout: (e) => {
          State.GeojsonLayer.resetStyle(e.target);
        }
      });
    }
  }).addTo(State.Map);
}

/**
 * Determine Polygon Styling Based On Active Visualization Layer
 */
function GetFeatureStyle(Feature) {
  const Props = Feature.properties;
  const IsFunded = Props.IncludedInCurrentBudget !== false;

  let FillColor = "#06B6D4";
  let FillOpacity = IsFunded ? 0.75 : 0.25;
  let BorderColor = IsFunded ? "rgba(255, 255, 255, 0.4)" : "rgba(255, 255, 255, 0.1)";

  switch (State.ActiveLayer) {
    case "CompositeRisk":
      FillColor = Props.HeatRiskAnalysis ? Props.HeatRiskAnalysis.RiskColorHex : "#EF4444";
      break;

    case "Material":
      FillColor = MATERIAL_COLORS[Props.PredictedMaterial] || "#64748B";
      break;

    case "DayLST":
      const DayLST = Props.ThermalObservations?.DayLSTCelsius || 45.0;
      FillColor = GetThermalGradientColor(DayLST, 30.0, 52.0);
      break;

    case "NightRetention":
      const NightLST = Props.ThermalObservations?.NightLSTCelsius || 30.0;
      FillColor = GetThermalGradientColor(NightLST, 22.0, 38.0);
      break;

    case "Population":
      const Pop = Props.PopulationProtectedEst || 5;
      FillColor = GetPopulationGradientColor(Pop, 2, 150);
      break;
  }

  return {
    fillColor: FillColor,
    weight: 1.2,
    opacity: 0.9,
    color: BorderColor,
    fillOpacity: FillOpacity
  };
}

/**
 * Color Interpolation Utilities
 */
function GetThermalGradientColor(Val, MinVal, MaxVal) {
  const Norm = Math.max(0, Math.min(1, (Val - MinVal) / (MaxVal - MinVal)));
  if (Norm < 0.25) return "#3B82F6";  // Cool Blue
  if (Norm < 0.50) return "#EAB308";  // Yellow
  if (Norm < 0.75) return "#F97316";  // Orange
  return "#EF4444";                  // Hot Red
}

function GetPopulationGradientColor(Val, MinVal, MaxVal) {
  const Norm = Math.max(0, Math.min(1, (Val - MinVal) / (MaxVal - MinVal)));
  if (Norm < 0.3) return "#10B981";   // Emerald
  if (Norm < 0.6) return "#F59E0B";   // Amber
  return "#EF4444";                  // High Density Red
}

/**
 * Building Dossier Inspector Selection
 */
function SelectBuildingFeature(Feature, Layer) {
  State.SelectedFeature = Feature;
  const Props = Feature.properties;

  document.getElementById("InspectorEmptyState").style.display = "none";
  document.getElementById("InspectorCardContent").style.display = "flex";

  document.getElementById("InspBuildingId").textContent = Props.BuildingId;
  document.getElementById("InspWardName").textContent = Props.WardName || Props.WardId;
  document.getElementById("InspRankBadge").textContent = `Rank #${Props.Rank}`;
  document.getElementById("InspMaterial").textContent = Props.PredictedMaterial;
  document.getElementById("InspMaterial").style.color = MATERIAL_COLORS[Props.PredictedMaterial] || "#FFFFFF";
  document.getElementById("InspConfidence").textContent = `${Math.round(Props.MaterialConfidence * 100)}%`;
  document.getElementById("InspRiskScore").textContent = Props.RiskScore;
  document.getElementById("InspRoofArea").textContent = `${Props.RoofAreaSquareMeters} m²`;
  document.getElementById("InspDayLST").textContent = `${Props.ThermalObservations?.DayLSTCelsius || 45.0} °C`;
  document.getElementById("InspNightLST").textContent = `${Props.ThermalObservations?.NightLSTCelsius || 30.0} °C`;
  document.getElementById("InspCoating").textContent = Props.RecommendedCoatingType || "High-Albedo Elastomeric";
  document.getElementById("InspCost").textContent = `₹${Props.EstimatedCostINR?.toLocaleString()}`;
  document.getElementById("InspPop").textContent = `${Props.PopulationProtectedEst} Residents`;

  RenderMaterialRadarChart(Props.MaterialSoftProbabilities);
}

/**
 * Render Material Soft-Probability Radar Chart
 */
function RenderMaterialRadarChart(SoftProbs) {
  const Canvas = document.getElementById("MaterialRadarChart");
  if (!Canvas) return;

  const Labels = ["Metal / Tin", "Asbestos", "Concrete", "Clay Tile", "Thatch / Tarps"];
  const KeyMap = {
    "Metal / Tin": SoftProbs?.["Metal / Tin"] || 0.2,
    "Asbestos": SoftProbs?.["Asbestos / Cement"] || 0.2,
    "Concrete": SoftProbs?.["Concrete / RCC"] || 0.2,
    "Clay Tile": SoftProbs?.["Clay / Tile"] || 0.2,
    "Thatch / Tarps": SoftProbs?.["Thatch / Tarpaulin"] || 0.2
  };
  const Values = Labels.map(L => KeyMap[L]);

  if (State.Charts.MaterialRadarChart) {
    State.Charts.MaterialRadarChart.destroy();
  }

  State.Charts.MaterialRadarChart = new Chart(Canvas, {
    type: "radar",
    data: {
      labels: Labels,
      datasets: [{
        label: "Confidence Probability",
        data: Values,
        backgroundColor: "rgba(6, 182, 212, 0.25)",
        borderColor: "#06B6D4",
        pointBackgroundColor: "#06B6D4",
        pointBorderColor: "#FFFFFF",
        borderWidth: 2
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        r: {
          min: 0,
          max: 1,
          ticks: { display: false },
          grid: { color: "rgba(148, 163, 184, 0.15)" },
          angleLines: { color: "rgba(148, 163, 184, 0.15)" },
          pointLabels: {
            font: { size: 8.5, family: "Inter" },
            color: "#94A3B8"
          }
        }
      },
      plugins: {
        legend: { display: false }
      }
    }
  });
}

/**
 * Fetch And Render Analytics Graphs For All 6 Datasets
 */
async function FetchAndRenderAll6DatasetAnalytics(CityName) {
  try {
    console.log(`Fetching 6-Dataset Deep Analytics For ${CityName}...`);
    const Response = await fetch(`/Api/Datasets/Analytics/${encodeURIComponent(CityName)}`);
    if (!Response.ok) return;

    const Data = await Response.json();

    // 1. Dataset 1: Google Open Buildings Area & Height
    RenderDS1Charts(Data.Dataset1_OpenBuildings);

    // 2. Dataset 2: Sentinel-2 Multispectral Radar
    RenderDS2RadarChart(Data.Dataset2_Sentinel2);

    // 3. Dataset 3: Landsat Day vs Night Scatter
    RenderDS3ScatterChart(Data.Dataset3_Landsat);

    // 4. Dataset 4: ECOSTRESS 24-Hour Diurnal Cycle
    RenderDS4DiurnalChart(Data.Dataset4_Ecostress);

    // 5. Dataset 5: Census 2011 LLP Proportions
    RenderDS5CensusChart(Data.Dataset5_Census);

    // 6. Dataset 6: WorldPop Pareto Shielding Frontier
    RenderDS6WorldPopChart(Data.Dataset6_WorldPop);

    console.log("All 6 Dataset Analytics Graphs Successfully Rendered.");
  } catch (Ex) {
    console.error(`Error In FetchAndRenderAll6DatasetAnalytics: ${Ex.message}`);
  }
}

/**
 * Render Dataset 1: Google Open Buildings Charts
 */
function RenderDS1Charts(DS1) {
  if (!DS1) return;

  // Roof Area Distribution (Binning)
  const AreaCanvas = document.getElementById("ChartDS1Area");
  if (AreaCanvas) {
    if (State.Charts.DS1Area) State.Charts.DS1Area.destroy();

    const Areas = DS1.AreasM2 || [];
    const Bins = ["< 50 m²", "50-150 m²", "150-300 m²", "300-600 m²", "> 600 m²"];
    const Counts = [
      Areas.filter(a => a < 50).length,
      Areas.filter(a => a >= 50 && a < 150).length,
      Areas.filter(a => a >= 150 && a < 300).length,
      Areas.filter(a => a >= 300 && a < 600).length,
      Areas.filter(a => a >= 600).length
    ];

    State.Charts.DS1Area = new Chart(AreaCanvas, {
      type: "bar",
      data: {
        labels: Bins,
        datasets: [{
          label: "Number of Buildings",
          data: Counts,
          backgroundColor: "rgba(6, 182, 212, 0.7)",
          borderColor: "#06B6D4",
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: { grid: { color: "rgba(148, 163, 184, 0.1)" }, ticks: { color: "#94A3B8" } },
          x: { grid: { display: false }, ticks: { color: "#94A3B8", font: { size: 9 } } }
        },
        plugins: { legend: { display: false } }
      }
    });
  }

  // Building Heights
  const HeightCanvas = document.getElementById("ChartDS1Height");
  if (HeightCanvas) {
    if (State.Charts.DS1Height) State.Charts.DS1Height.destroy();

    const Heights = DS1.HeightsMeters || [];
    const HeightBins = ["1-3m (1 Storey)", "3-6m (2 Storey)", "6-12m (3-4 Storey)", "> 12m (High-Rise)"];
    const HeightCounts = [
      Heights.filter(h => h < 3.5).length,
      Heights.filter(h => h >= 3.5 && h < 6.5).length,
      Heights.filter(h => h >= 6.5 && h <= 12.0).length,
      Heights.filter(h => h > 12.0).length
    ];

    State.Charts.DS1Height = new Chart(HeightCanvas, {
      type: "bar",
      data: {
        labels: HeightBins,
        datasets: [{
          label: "Count by Height Tier",
          data: HeightCounts,
          backgroundColor: "rgba(245, 158, 11, 0.7)",
          borderColor: "#F59E0B",
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: { grid: { color: "rgba(148, 163, 184, 0.1)" }, ticks: { color: "#94A3B8" } },
          x: { grid: { display: false }, ticks: { color: "#94A3B8", font: { size: 9 } } }
        },
        plugins: { legend: { display: false } }
      }
    });
  }
}

/**
 * Render Dataset 2: Sentinel-2 Multispectral Radar Chart
 */
function RenderDS2RadarChart(DS2) {
  const Canvas = document.getElementById("ChartDS2Radar");
  if (!Canvas || !DS2) return;

  if (State.Charts.DS2Radar) State.Charts.DS2Radar.destroy();

  const Metrics = ["NDVI", "NDBI", "Albedo", "Brightness", "Texture"];
  const Materials = Object.keys(DS2);

  const Datasets = Materials.map(Mat => {
    const Values = Metrics.map(M => DS2[Mat][M] || 0.3);
    const Color = MATERIAL_COLORS[Mat] || "#06B6D4";
    return {
      label: Mat,
      data: Values,
      borderColor: Color,
      backgroundColor: "transparent",
      borderWidth: 2,
      pointRadius: 3,
      pointBackgroundColor: Color
    };
  });

  State.Charts.DS2Radar = new Chart(Canvas, {
    type: "radar",
    data: {
      labels: ["Vegetation (NDVI)", "Built-Up (NDBI)", "Solar Albedo", "Visual Brightness", "GLCM Texture"],
      datasets: Datasets
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        r: {
          min: -0.1,
          max: 1.0,
          grid: { color: "rgba(148, 163, 184, 0.18)" },
          angleLines: { color: "rgba(148, 163, 184, 0.18)" },
          ticks: { display: false },
          pointLabels: { color: "#F8FAFC", font: { size: 10.5, family: "Inter", weight: "600" } }
        }
      },
      plugins: {
        legend: { labels: { color: "#F8FAFC", font: { size: 10, family: "Inter" } } }
      }
    }
  });
}

/**
 * Render Dataset 3: Landsat Thermal Scatter With Material-Grouped Colored Points
 */
function RenderDS3ScatterChart(DS3) {
  const Canvas = document.getElementById("ChartDS3Scatter");
  if (!Canvas || !DS3) return;

  if (State.Charts.DS3Scatter) State.Charts.DS3Scatter.destroy();

  // Group Scatter Points By Roof Material For Physical Visual Separation
  const MaterialGroups = {};
  DS3.forEach(Pt => {
    const M = Pt.mat || "Concrete / RCC";
    if (!MaterialGroups[M]) MaterialGroups[M] = [];
    MaterialGroups[M].push({ x: Pt.x, y: Pt.y });
  });

  const Datasets = Object.keys(MaterialGroups).map(Mat => ({
    label: Mat,
    data: MaterialGroups[Mat],
    backgroundColor: MATERIAL_COLORS[Mat] || "#EF4444",
    borderColor: "rgba(255, 255, 255, 0.6)",
    borderWidth: 1,
    pointRadius: 4.5,
    pointHoverRadius: 6
  }));

  State.Charts.DS3Scatter = new Chart(Canvas, {
    type: "scatter",
    data: { datasets: Datasets },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: {
          title: { display: true, text: "Landsat 8/9 Daytime LST (°C)", color: "#94A3B8", font: { size: 11, weight: "600" } },
          grid: { color: "rgba(148, 163, 184, 0.12)" },
          ticks: { color: "#94A3B8" }
        },
        y: {
          title: { display: true, text: "Night Surface Temp (°C)", color: "#94A3B8", font: { size: 11, weight: "600" } },
          grid: { color: "rgba(148, 163, 184, 0.12)" },
          ticks: { color: "#94A3B8" }
        }
      },
      plugins: {
        legend: {
          display: true,
          labels: { color: "#F8FAFC", font: { size: 9.5, family: "Inter" } }
        }
      }
    }
  });
}

/**
 * Render Dataset 4: ECOSTRESS 24-Hour Diurnal Heat Cycle
 */
function RenderDS4DiurnalChart(DS4) {
  const Canvas = document.getElementById("ChartDS4Diurnal");
  if (!Canvas || !DS4) return;

  if (State.Charts.DS4Diurnal) State.Charts.DS4Diurnal.destroy();

  const Hours = DS4.TimeHours || ["00:00", "03:00", "06:00", "09:00", "12:00", "15:00", "18:00", "21:00"];

  State.Charts.DS4Diurnal = new Chart(Canvas, {
    type: "line",
    data: {
      labels: Hours,
      datasets: [
        {
          label: "Metal / Tin Sheet (Rapid Solar Heat Spike)",
          data: DS4.Metal_Tin,
          borderColor: "#06B6D4",
          backgroundColor: "rgba(6, 182, 212, 0.1)",
          tension: 0.35,
          borderWidth: 2.5,
          pointRadius: 3
        },
        {
          label: "Concrete / RCC (Nocturnal Thermal Trap)",
          data: DS4.Concrete_RCC,
          borderColor: "#EF4444",
          backgroundColor: "rgba(239, 68, 68, 0.1)",
          tension: 0.35,
          borderWidth: 2.5,
          pointRadius: 3
        },
        {
          label: "Asbestos / Cement Sheet",
          data: DS4.Asbestos_Cement,
          borderColor: "#8B5CF6",
          backgroundColor: "rgba(139, 92, 246, 0.1)",
          tension: 0.35,
          borderWidth: 2,
          pointRadius: 3
        },
        {
          label: "Clay / Ceramic Tile (Cool Baseline)",
          data: DS4.Clay_Tile,
          borderColor: "#10B981",
          backgroundColor: "rgba(16, 185, 129, 0.1)",
          tension: 0.35,
          borderWidth: 2,
          pointRadius: 3
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          title: { display: true, text: "Surface Temperature (°C)", color: "#94A3B8", font: { size: 11, weight: "600" } },
          grid: { color: "rgba(148, 163, 184, 0.12)" },
          ticks: { color: "#94A3B8" }
        },
        x: {
          grid: { display: false },
          ticks: { color: "#94A3B8", font: { size: 10 } }
        }
      },
      plugins: {
        legend: { labels: { color: "#F8FAFC", font: { size: 9.5, family: "Inter" } } }
      }
    }
  });
}

/**
 * Render Dataset 5: Census 2011 LLP Validation
 */
function RenderDS5CensusChart(CensusAnalytics) {
  const Canvas = document.getElementById("ChartDS5Census");
  if (!Canvas || !CensusAnalytics) return;

  const WardMetrics = CensusAnalytics.WardValidationMetrics || {};
  const WardIds = Object.keys(WardMetrics);
  if (WardIds.length === 0) return;

  const FirstWard = WardMetrics[WardIds[0]];
  const KLScoreText = document.getElementById("TextKLScore");
  if (KLScoreText) {
    KLScoreText.textContent = (CensusAnalytics.MeanWardKLDivergence || 0.21).toFixed(4);
  }

  if (State.Charts.DS5Census) State.Charts.DS5Census.destroy();

  const Labels = ["Metal/Tin", "Asbestos", "Concrete", "Clay Tile", "Thatch"];
  const CensusVals = [
    FirstWard.TargetCensusDistribution["Metal / Tin"],
    FirstWard.TargetCensusDistribution["Asbestos / Cement"],
    FirstWard.TargetCensusDistribution["Concrete / RCC"],
    FirstWard.TargetCensusDistribution["Clay / Tile"],
    FirstWard.TargetCensusDistribution["Thatch / Tarpaulin"]
  ];
  const ModelVals = [
    FirstWard.ModelPredictedDistribution["Metal / Tin"],
    FirstWard.ModelPredictedDistribution["Asbestos / Cement"],
    FirstWard.ModelPredictedDistribution["Concrete / RCC"],
    FirstWard.ModelPredictedDistribution["Clay / Tile"],
    FirstWard.ModelPredictedDistribution["Thatch / Tarpaulin"]
  ];

  State.Charts.DS5Census = new Chart(Canvas, {
    type: "bar",
    data: {
      labels: Labels,
      datasets: [
        {
          label: "Census 2011 Ground Proportion",
          data: CensusVals,
          backgroundColor: "rgba(139, 92, 246, 0.75)",
          borderColor: "#8B5CF6",
          borderWidth: 1
        },
        {
          label: "Model Predicted Proportion (LLP AI)",
          data: ModelVals,
          backgroundColor: "rgba(6, 182, 212, 0.75)",
          borderColor: "#06B6D4",
          borderWidth: 1
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: { beginAtZero: true, max: 1.0, grid: { color: "rgba(148, 163, 184, 0.12)" }, ticks: { color: "#94A3B8" } },
        x: { grid: { display: false }, ticks: { color: "#94A3B8", font: { size: 10 } } }
      },
      plugins: {
        legend: { labels: { color: "#F8FAFC", font: { size: 10, family: "Inter" } } }
      }
    }
  });
}

/**
 * Render Dataset 6: WorldPop Pareto Frontier With Currency Scaling
 */
function RenderDS6WorldPopChart(ParetoData) {
  const Canvas = document.getElementById("ChartDS6WorldPop");
  if (!Canvas || !ParetoData) return;

  if (State.Charts.DS6WorldPop) State.Charts.DS6WorldPop.destroy();

  const Points = ParetoData.map(P => ({ x: P.BudgetINR, y: P.ProtectedResidents }));

  State.Charts.DS6WorldPop = new Chart(Canvas, {
    type: "line",
    data: {
      datasets: [{
        label: "Pareto Optimal Frontier",
        data: Points,
        borderColor: "#10B981",
        backgroundColor: "rgba(16, 185, 129, 0.15)",
        fill: true,
        tension: 0.3,
        borderWidth: 2.5,
        pointRadius: 4,
        pointBackgroundColor: "#10B981"
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: {
          title: { display: true, text: "Cumulative Municipal Budget (INR)", color: "#94A3B8", font: { size: 11, weight: "600" } },
          grid: { color: "rgba(148, 163, 184, 0.12)" },
          ticks: {
            color: "#94A3B8",
            callback: value => `₹${(value / 100000).toFixed(1)}L`
          }
        },
        y: {
          beginAtZero: true,
          title: { display: true, text: "Residents Shielded From Heat", color: "#94A3B8", font: { size: 11, weight: "600" } },
          grid: { color: "rgba(148, 163, 184, 0.12)" },
          ticks: { color: "#94A3B8" }
        }
      },
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: context => `Budget: ₹${context.raw.x.toLocaleString()} → Shielded: ${context.raw.y.toLocaleString()} Residents`
          }
        }
      }
    }
  });
}

/**
 * Recompute Prioritisation On Weight / Budget Changes
 */
async function RecomputeScores() {
  try {
    const Payload = {
      CityName: State.CurrentCity,
      CustomWeights: State.ActiveWeights,
      BudgetLimitINR: State.BudgetCapINR,
      PreferredCoatingType: State.PreferredCoating
    };

    const Response = await fetch("/Api/Score/Recompute", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(Payload)
    });

    if (!Response.ok) throw new Error("Recomputation API Failed");

    const Data = await Response.json();
    State.PipelineData = Data;
    State.GeojsonData = Data.GeoJSON;

    UpdateHeaderSummaryMetrics(Data);
    RenderGeoJSONLayer();
    UpdateWorkOrderTable();
    UpdateExecutiveBriefing(Data);
  } catch (Error) {
    console.error(`Recompute Error: ${Error.message}`);
  }
}

/**
 * Update Header Metric Pills
 */
function UpdateHeaderSummaryMetrics(Data) {
  const WorkAnalytics = Data.WorkOrderAnalytics || {};
  const RiskAnalytics = Data.RiskScoreAnalytics || {};
  const ClassifierAnalytics = Data.ClassifierAnalytics || {};

  document.getElementById("HeaderCriticalRoofs").textContent = (RiskAnalytics.CriticalPriorityCount || 0).toLocaleString();
  document.getElementById("HeaderProtectedPop").textContent = (WorkAnalytics.TotalPopulationProtected || 0).toLocaleString();
  document.getElementById("HeaderBudgetAllocated").textContent = `₹${Math.round(WorkAnalytics.TotalCumulativeBudgetINR || 0).toLocaleString()}`;
  document.getElementById("HeaderMeanKL").textContent = (ClassifierAnalytics.MeanWardKLDivergence || 0.21).toFixed(4);
}

/**
 * Populate Contractor Work-Order Table
 */
function UpdateWorkOrderTable() {
  const TBody = document.getElementById("WorkOrderTableBody");
  if (!TBody || !State.GeojsonData) return;

  TBody.innerHTML = "";
  const Features = State.GeojsonData.features || [];

  Features.slice(0, 300).forEach(Feature => {
    const Props = Feature.properties;
    const Row = document.createElement("tr");

    const IsFunded = Props.IncludedInCurrentBudget !== false;
    const StatusBadge = IsFunded
      ? `<span style="background: rgba(16, 185, 129, 0.2); color: #10B981; padding: 2px 8px; border-radius: 4px; font-weight: 700;">Funded</span>`
      : `<span style="background: rgba(100, 116, 139, 0.2); color: #94A3B8; padding: 2px 8px; border-radius: 4px;">Deferred</span>`;

    Row.innerHTML = `
      <td style="font-weight: 700; color: #06B6D4;">#${Props.Rank}</td>
      <td style="font-family: 'JetBrains Mono';">${Props.BuildingId}</td>
      <td>${Props.WardName || Props.WardId}</td>
      <td style="color: ${MATERIAL_COLORS[Props.PredictedMaterial] || '#FFFFFF'}; font-weight: 600;">${Props.PredictedMaterial}</td>
      <td>${Math.round(Props.MaterialConfidence * 100)}%</td>
      <td style="font-weight: 700; color: ${Props.HeatRiskAnalysis?.RiskColorHex || '#EF4444'};">${Props.RiskScore}</td>
      <td>${Props.RiskTier}</td>
      <td>${Props.RoofAreaSquareMeters} m²</td>
      <td style="max-width: 140px; overflow: hidden; text-overflow: ellipsis;">${Props.RecommendedCoatingType}</td>
      <td style="font-weight: 600;">₹${Props.EstimatedCostINR?.toLocaleString()}</td>
      <td style="color: var(--accent-emerald); font-weight: 600;">${Props.PopulationProtectedEst}</td>
      <td>₹${Props.CostPerPersonProtectedINR}</td>
      <td>${StatusBadge}</td>
    `;

    Row.addEventListener("click", () => {
      SelectBuildingFeature(Feature);
      State.Map.flyTo([Props.CentroidLat, Props.CentroidLon], 17, { duration: 0.8 });
    });

    TBody.appendChild(Row);
  });
}

/**
 * Generate Full Official Municipal Heat Action Briefing Report (Strict Title Case)
 */
function UpdateExecutiveBriefing(Data) {
  const Container = document.getElementById("ExecutiveBriefingContent");
  if (!Container) return;

  const CityName = State.CurrentCity;
  const Work = Data.WorkOrderAnalytics || {};
  const Risk = Data.RiskScoreAnalytics || {};
  const Features = State.GeojsonData?.features || [];
  const FundedCount = Features.filter(f => f.properties.IncludedInCurrentBudget !== false).length;
  const TotalAreaM2 = Features.reduce((acc, f) => acc + (f.properties.RoofAreaSquareMeters || 0), 0);

  Container.innerHTML = `
    <!-- Top HUD Summary Header -->
    <div style="border-bottom: 1px solid rgba(148, 163, 184, 0.15); padding-bottom: 14px; margin-bottom: 16px;">
      <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 10px;">
        <div>
          <h2 style="font-size: 1.22rem; font-weight: 800; color: #FFFFFF; letter-spacing: -0.02em;">
            Official Municipal Heat Action Briefing & Cool-Roof Deployment Roadmap
          </h2>
          <p style="font-size: 0.78rem; color: var(--text-secondary); margin-top: 2px;">
            Target Municipality: <b style="color: var(--accent-cyan);">${CityName}</b> • Urban Heatwave Action Plan (HAP) Statutory Compliance
          </p>
        </div>
        <div style="display: flex; align-items: center; gap: 8px;">
          <button id="BtnTriggerAIBriefing" class="btn-accent" style="padding: 5px 12px; font-size: 0.74rem; box-shadow: 0 0 12px rgba(139, 92, 246, 0.35);">
            <i data-lucide="sparkles" style="width: 13px; height: 13px;"></i>
            <span>Synthesize Live AI Briefing (LLM API)</span>
          </button>
          <span style="background: rgba(6, 182, 212, 0.15); border: 1px solid var(--accent-cyan-glow); color: var(--accent-cyan); padding: 4px 10px; border-radius: 6px; font-size: 0.72rem; font-weight: 700; font-family: 'JetBrains Mono';">
            Doc Ref: PARoo-HAP-${CityName.toUpperCase().replace(/ /g, "_")}-2026
          </span>
        </div>
      </div>
    </div>

    <!-- 4 High-Impact Stat KPI Cards -->
    <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 22px;">
      <div style="background: rgba(15, 23, 42, 0.7); padding: 14px; border-radius: 8px; border-left: 3px solid var(--accent-cyan);">
        <div style="font-size: 0.68rem; color: var(--text-muted); text-transform: capitalize; font-weight: 600;">Cumulative Budget Envelope</div>
        <div style="font-size: 1.15rem; font-weight: 800; color: #FFFFFF; font-family: 'JetBrains Mono'; margin-top: 4px;">
          ₹${Math.round(Work.TotalCumulativeBudgetINR || 0).toLocaleString()}
        </div>
        <div style="font-size: 0.68rem; color: var(--accent-cyan); margin-top: 2px;">${FundedCount} Buildings Fully Funded Under Cap</div>
      </div>

      <div style="background: rgba(15, 23, 42, 0.7); padding: 14px; border-radius: 8px; border-left: 3px solid var(--accent-emerald);">
        <div style="font-size: 0.68rem; color: var(--text-muted); text-transform: capitalize; font-weight: 600;">Vulnerable Lives Shielded</div>
        <div style="font-size: 1.15rem; font-weight: 800; color: var(--accent-emerald); font-family: 'JetBrains Mono'; margin-top: 4px;">
          ${(Work.TotalPopulationProtected || 0).toLocaleString()}
        </div>
        <div style="font-size: 0.68rem; color: var(--text-muted); margin-top: 2px;">WorldPop 100m Spatial Validation</div>
      </div>

      <div style="background: rgba(15, 23, 42, 0.7); padding: 14px; border-radius: 8px; border-left: 3px solid var(--accent-red);">
        <div style="font-size: 0.68rem; color: var(--text-muted); text-transform: capitalize; font-weight: 600;">Critical Hazard Rooftops</div>
        <div style="font-size: 1.15rem; font-weight: 800; color: var(--accent-red); font-family: 'JetBrains Mono'; margin-top: 4px;">
          ${Risk.CriticalPriorityCount || 0}
        </div>
        <div style="font-size: 0.68rem; color: var(--accent-red); margin-top: 2px;">Extreme Daytime Conductive Heat Traps</div>
      </div>

      <div style="background: rgba(15, 23, 42, 0.7); padding: 14px; border-radius: 8px; border-left: 3px solid var(--accent-purple);">
        <div style="font-size: 0.68rem; color: var(--text-muted); text-transform: capitalize; font-weight: 600;">Cost Per Life Shielded</div>
        <div style="font-size: 1.15rem; font-weight: 800; color: var(--accent-purple); font-family: 'JetBrains Mono'; margin-top: 4px;">
          ₹${Work.AverageCostPerPersonProtectedINR || 0}
        </div>
        <div style="font-size: 0.68rem; color: var(--text-muted); margin-top: 2px;">Pareto Knapsack Knapsack Frontier</div>
      </div>
    </div>

    <!-- Section 1: Executive Context & Scope of Intervention (Title Case) -->
    <div style="margin-bottom: 20px;">
      <h3 style="font-size: 0.92rem; color: var(--accent-cyan); font-weight: 700; margin-bottom: 6px;">
        1. Executive Context & Scope Of Intervention
      </h3>
      <p id="BriefingContext" style="color: var(--text-secondary); font-size: 0.78rem; line-height: 1.6;">
        This Operational Dossier Provides Actionable Municipal Prioritization For High-Albedo Solar-Reflective Rooftop Coatings Under The State Urban Heatwave Action Plan (HAP). Utilizing Multi-Sensor Earth Observation Data From <b>Google Open Buildings v3</b>, <b>Sentinel-2 L2A</b>, <b>Landsat 8/9 TIRS</b>, And <b>NASA JPL ECOSTRESS</b>, The Platform Has Surveyed <b>${Features.length}</b> Building Rooftops Covering A Cumulative Surface Area Of <b>${Math.round(TotalAreaM2).toLocaleString()} m²</b> Across High-Density Urban Wards In ${CityName}.
      </p>
    </div>

    <!-- Section 2: Meteorological & Thermal Risk Analysis (Title Case) -->
    <div style="margin-bottom: 20px;">
      <h3 style="font-size: 0.92rem; color: var(--accent-amber); font-weight: 700; margin-bottom: 6px;">
        2. Satellite Thermal Infrared & Night Heat Retention Diagnostics
      </h3>
      <p id="BriefingDiagnostics" style="color: var(--text-secondary); font-size: 0.78rem; line-height: 1.6;">
        Satellite Thermal Infrared Radiometry Reveals Severe Micro-Urban Heat Island Hotspots Where Uninsulated Sheet Metal And Corrugated Asbestos Envelopes Exceed Daytime Surface Temperatures Of <b>50°C</b>, Transferring Lethal Conductive Heat Flux Into Interior Living Quarters. Concurrently, Dense Multi-Storey Concrete Tenements Trap Absorbed Daytime Irradiance And Re-Radiate Nocturnal Heat Fluxes Above <b>34°C</b> Past Midnight, Inhibiting Physiological Thermal Recovery Among Vulnerable Populations.
      </p>
    </div>

    <!-- Section 3: Phase-By-Phase Contractor Procurement & Coating Schedule (Title Case) -->
    <div style="margin-bottom: 20px;">
      <h3 style="font-size: 0.92rem; color: var(--accent-emerald); font-weight: 700; margin-bottom: 6px;">
        3. Phase-By-Phase Contractor Procurement & Coating Schedule
      </h3>
      <div id="BriefingScheduleGrid" style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; margin-top: 8px;">
        <div style="background: rgba(15, 23, 42, 0.5); padding: 10px; border-radius: 6px; border: 1px solid rgba(148, 163, 184, 0.1);">
          <div style="font-size: 0.74rem; font-weight: 700; color: var(--accent-red);">Phase 1: Immediate Critical Hazard Mitigation</div>
          <div style="font-size: 0.70rem; color: var(--text-secondary); margin-top: 4px;">
            Target: Top Priority Critical Rooftops (${Risk.CriticalPriorityCount || 0} Buildings) With Peak Daytime LST > 48°C. Coating Spec: Fibre-Reinforced Dual-Coat High-Albedo Elastomeric Membrane (SRI ≥ 104, ₹150–₹220/m²).
          </div>
        </div>
        <div style="background: rgba(15, 23, 42, 0.5); padding: 10px; border-radius: 6px; border: 1px solid rgba(148, 163, 184, 0.1);">
          <div style="font-size: 0.74rem; font-weight: 700; color: var(--accent-orange);">Phase 2: High Nocturnal Retention Tenements</div>
          <div style="font-size: 0.70rem; color: var(--text-secondary); margin-top: 4px;">
            Target: Dense Slum Tenements And Low-Income Housing With Elevated Night Temperatures > 34°C. Coating Spec: Solar Reflective Cross-Linking Acrylic Primer Combined With High-Emissivity Topcoat.
          </div>
        </div>
        <div style="background: rgba(15, 23, 42, 0.5); padding: 10px; border-radius: 6px; border: 1px solid rgba(148, 163, 184, 0.1);">
          <div style="font-size: 0.74rem; font-weight: 700; color: var(--accent-emerald);">Phase 3: Broad Community Refresh & Maintenance</div>
          <div style="font-size: 0.70rem; color: var(--text-secondary); margin-top: 4px;">
            Target: Moderate Heat-Risk Wards And Public Civic Infrastructure Buildings. Coating Spec: Economic High-Reflectance Lime Wash (SRI ≥ 90, ₹80/m²) For Annual Pre-Monsoon Community Deployment.
          </div>
        </div>
      </div>
    </div>

    <!-- Section 4: SOP Application Protocol (Title Case) -->
    <div style="background: rgba(6, 182, 212, 0.06); border: 1px solid var(--accent-cyan-glow); padding: 14px; border-radius: 8px;">
      <h4 style="font-size: 0.82rem; color: var(--accent-cyan); font-weight: 700; margin-bottom: 4px;">
        Standard Operating Procedure (SOP) For Dual-Coat Application:
      </h4>
      <p id="BriefingSOP" style="font-size: 0.74rem; color: var(--text-secondary); line-height: 1.6;">
        1. <b>Surface Decontamination:</b> High-Pressure Water Jetting And Mechanical Wire-Brushing To Eliminate Dust, Moss, And Corroded Scaling.<br>
        2. <b>Base Primer Coat:</b> Application Of High-Bond Acrylic Penetrating Primer At 0.15 Liters/m².<br>
        3. <b>Dual Solar-Reflective Topcoat:</b> Application Of 2 Successive Elastomeric Solar Reflective Coats (Solar Reflectance Index SRI ≥ 104) With 4-Hour Cross-Curing Intervals.
      </p>
    </div>
  `;

  // Bind AI Synthesis Button
  document.getElementById("BtnTriggerAIBriefing")?.addEventListener("click", () => TriggerAIBriefingSynthesis());
  if (window.lucide) lucide.createIcons();
}

/**
 * Trigger Real-Time Live AI Model API Synthesis With Live Progress Tracking
 */
async function TriggerAIBriefingSynthesis() {
  const Btn = document.getElementById("BtnTriggerAIBriefing");
  if (Btn) {
    Btn.innerHTML = `<i data-lucide="loader-2" class="spin-animation" style="width: 13px; height: 13px;"></i><span>Synthesizing With AI Model API...</span>`;
    Btn.disabled = true;
  }

  ShowMapLoader(`AI Synthesis For ${State.CurrentCity}`, "Step 1: Authenticating Google Gemini 1.5 Flash API...", 20);

  try {
    await new Promise(r => setTimeout(r, 120));
    SetMapProgress(50, `AI Synthesis For ${State.CurrentCity}`, "Step 2: Processing Multi-Sensor Thermal Telemetry & Knapsack Frontier...");

    const Response = await fetch(`/Api/AI/GenerateBriefing/${encodeURIComponent(State.CurrentCity)}`);
    if (!Response.ok) throw new Error("AI Synthesis API Call Failed");
    
    SetMapProgress(80, `AI Synthesis For ${State.CurrentCity}`, "Step 3: Synthesizing Title Case Municipal Action Plan...");
    const Result = await Response.json();
    
    if (Result.Briefing) {
      const B = Result.Briefing;
      if (B.ExecutiveContext) document.getElementById("BriefingContext").textContent = B.ExecutiveContext;
      if (B.ThermalDiagnostics) document.getElementById("BriefingDiagnostics").textContent = B.ThermalDiagnostics;
      if (B.ApplicationProtocolSOP) {
        document.getElementById("BriefingSOP").innerHTML = B.ApplicationProtocolSOP.replace(/\n/g, "<br>");
      }
    }

    SetMapProgress(100, `AI Synthesis Complete`, `Generated Policy Brief via ${Result.Source}`);
  } catch (Err) {
    console.error(`AI Synthesis Error: ${Err.message}`);
    ShowMapLoader("AI Synthesis Fallback", "Domain Analytical Engine Injected", 100);
  } finally {
    setTimeout(() => HideMapLoader(), 800);
    if (Btn) {
      Btn.innerHTML = `<i data-lucide="sparkles" style="width: 13px; height: 13px;"></i><span>Synthesize Live AI Briefing (LLM API)</span>`;
      Btn.disabled = false;
      if (window.lucide) lucide.createIcons();
    }
  }
}

/**
 * Event Listeners & Interactive UI Binding
 */
function InitEventListeners() {
  // City Selector
  document.getElementById("CitySelector")?.addEventListener("change", (e) => {
    LoadCityData(e.target.value);
  });

  // Run Pipeline Button
  document.getElementById("BtnRunPipeline")?.addEventListener("click", () => {
    LoadCityData(State.CurrentCity, true);
  });

  // Export CSV Work Order
  document.getElementById("BtnExportCSV")?.addEventListener("click", () => DownloadCSVWorkOrder());
  document.getElementById("BtnDownloadWorkOrderCSV")?.addEventListener("click", () => DownloadCSVWorkOrder());

  // Interactive Rectangle Draw Tool
  document.getElementById("BtnDrawRectangle")?.addEventListener("click", () => {
    console.log("Activating Interactive Rectangle AOI Drawing Mode...");
    const RectangleDrawer = new L.Draw.Rectangle(State.Map, {
      shapeOptions: {
        color: "#06B6D4",
        weight: 2,
        fillOpacity: 0.2
      }
    });
    RectangleDrawer.enable();
  });

  // Toggle Satellite Base Layer
  document.getElementById("BtnToggleSatelliteBase")?.addEventListener("click", () => {
    if (State.IsSatelliteBaseActive) {
      State.Map.removeLayer(State.SatelliteBaseLayer);
      State.Map.addLayer(State.DarkBaseLayer);
      State.IsSatelliteBaseActive = false;
      document.getElementById("BtnToggleSatelliteBase").classList.remove("active");
    } else {
      State.Map.removeLayer(State.DarkBaseLayer);
      State.Map.addLayer(State.SatelliteBaseLayer);
      State.IsSatelliteBaseActive = true;
      document.getElementById("BtnToggleSatelliteBase").classList.add("active");
    }
  });

  // Reset Map View
  document.getElementById("BtnResetMapView")?.addEventListener("click", () => {
    State.DrawnAOILayer.clearLayers();
    LoadCityData("Jaipur");
  });

  // Open Dataset Guide Modal
  document.getElementById("BtnOpenDatasetGuide")?.addEventListener("click", () => {
    OpenDatasetGuideModal();
  });
  document.getElementById("BtnCloseDatasetGuideModal")?.addEventListener("click", () => {
    document.getElementById("ModalDatasetGuide").classList.remove("open");
  });

  // Quick AOI Preset Chips Click Handlers
  document.querySelectorAll(".aoi-chip-btn").forEach(Chip => {
    Chip.addEventListener("click", (e) => {
      const ChipName = e.target.textContent.trim();
      const City = e.target.getAttribute("data-city");
      const BBoxJSON = e.target.getAttribute("data-bbox");
      if (BBoxJSON) {
        const BBox = JSON.parse(BBoxJSON);
        console.log(`Loading Quick AOI Preset: ${ChipName} -> BBox: ${BBox}`);
        RunCustomAOIPipeline(BBox, ChipName);
      } else if (City) {
        LoadCityData(City);
      }
    });
  });

  // Direct Raw Dataset Download Buttons (Datasets 1 to 6)
  document.querySelectorAll(".BtnDownloadDataset").forEach(Btn => {
    Btn.addEventListener("click", (e) => {
      const TargetBtn = e.target.closest(".BtnDownloadDataset");
      const DSNum = TargetBtn.getAttribute("data-dataset");
      const DownloadUrl = `/Api/Datasets/Download/${DSNum}/${encodeURIComponent(State.CurrentCity)}`;
      console.log(`Initiating Direct Download For Dataset #${DSNum} From ${DownloadUrl}`);
      window.location.href = DownloadUrl;
    });
  });

  // Layer Selector Buttons
  document.querySelectorAll(".layer-btn").forEach(Btn => {
    Btn.addEventListener("click", (e) => {
      document.querySelectorAll(".layer-btn").forEach(B => B.classList.remove("active"));
      e.target.classList.add("active");
      State.ActiveLayer = e.target.getAttribute("data-layer");
      UpdateMapLegend();
      RenderGeoJSONLayer();
    });
  });

  // Scoring Weight Sliders
  const WeightSliders = [
    { Id: "WeightMaterial", Key: "MaterialWeight", LabelId: "ValWeightMaterial" },
    { Id: "WeightLST", Key: "LSTAnomalyWeight", LabelId: "ValWeightLST" },
    { Id: "WeightNight", Key: "NightRetentionWeight", LabelId: "ValWeightNight" },
    { Id: "WeightDensity", Key: "DensityHeightWeight", LabelId: "ValWeightDensity" },
    { Id: "WeightOccupancy", Key: "OccupancyWeight", LabelId: "ValWeightOccupancy" }
  ];

  WeightSliders.forEach(({ Id, Key, LabelId }) => {
    const Slider = document.getElementById(Id);
    if (Slider) {
      Slider.addEventListener("input", (e) => {
        const Val = parseFloat(e.target.value);
        document.getElementById(LabelId).textContent = Val.toFixed(2);
        State.ActiveWeights[Key] = Val;
        RecomputeScores();
      });
    }
  });

  // Budget Envelope Slider
  const BudgetSlider = document.getElementById("BudgetCapSlider");
  if (BudgetSlider) {
    BudgetSlider.addEventListener("input", (e) => {
      const Val = parseFloat(e.target.value);
      State.BudgetCapINR = Val;
      document.getElementById("ValBudgetCap").textContent = `₹${Val.toLocaleString()}`;
      RecomputeScores();
    });
  }

  // Coating Specification Selector
  document.getElementById("CoatingSpecSelector")?.addEventListener("change", (e) => {
    State.PreferredCoating = e.target.value;
    RecomputeScores();
  });

  // Bottom Drawer Navigation Tabs
  document.querySelectorAll(".dock-tab-btn").forEach(TabBtn => {
    TabBtn.addEventListener("click", (e) => {
      const TargetDrawerId = "Drawer" + TabBtn.getAttribute("data-drawer");
      const Drawer = document.getElementById(TargetDrawerId);
      const IsOpen = Drawer?.classList.contains("open");
      
      document.querySelectorAll(".drawer-overlay").forEach(D => D.classList.remove("open"));
      document.querySelectorAll(".dock-tab-btn").forEach(B => B.classList.remove("active"));

      if (!IsOpen && Drawer) {
        Drawer.classList.add("open");
        TabBtn.classList.add("active");
        if (window.lucide) lucide.createIcons();
      }
    });
  });

  // Drawer Minimize Button (Collapse Down / Restore)
  document.querySelectorAll(".BtnMinimizeDrawer").forEach(Btn => {
    Btn.addEventListener("click", (e) => {
      const Drawer = e.target.closest(".drawer-overlay");
      if (!Drawer) return;
      if (Drawer.offsetHeight <= 220) {
        Drawer.style.height = "440px";
      } else {
        Drawer.style.height = "200px";
      }
    });
  });

  // Drawer Maximize Button (Expand Full Height / Restore)
  document.querySelectorAll(".BtnMaximizeDrawer").forEach(Btn => {
    Btn.addEventListener("click", (e) => {
      const Drawer = e.target.closest(".drawer-overlay");
      if (!Drawer) return;
      const MaxHeight = window.innerHeight - 110;
      if (Drawer.offsetHeight >= MaxHeight - 40) {
        Drawer.style.height = "440px";
      } else {
        Drawer.style.height = `${MaxHeight}px`;
      }
    });
  });

  // Drawer Draggable Top Edge Resizer
  let ActiveResizeDrawer = null;
  let StartY = 0;
  let StartHeight = 0;

  document.querySelectorAll(".drawer-resize-handle").forEach(Handle => {
    Handle.addEventListener("mousedown", (e) => {
      e.preventDefault();
      ActiveResizeDrawer = Handle.closest(".drawer-overlay");
      if (!ActiveResizeDrawer) return;
      StartY = e.clientY;
      StartHeight = ActiveResizeDrawer.offsetHeight;
      document.body.style.cursor = "ns-resize";
      document.body.style.userSelect = "none";
    });
  });

  window.addEventListener("mousemove", (e) => {
    if (!ActiveResizeDrawer) return;
    const DeltaY = StartY - e.clientY;
    const MaxAllowedHeight = window.innerHeight - 110;
    const NewHeight = Math.min(Math.max(StartHeight + DeltaY, 180), MaxAllowedHeight);
    ActiveResizeDrawer.style.height = `${NewHeight}px`;
  });

  window.addEventListener("mouseup", () => {
    if (ActiveResizeDrawer) {
      ActiveResizeDrawer = null;
      document.body.style.cursor = "";
      document.body.style.userSelect = "";
    }
  });

  // Close Drawer Buttons
  document.querySelectorAll(".BtnCloseDrawer").forEach(Btn => {
    Btn.addEventListener("click", () => {
      document.querySelectorAll(".drawer-overlay").forEach(D => D.classList.remove("open"));
      document.querySelectorAll(".dock-tab-btn").forEach(B => B.classList.remove("active"));
    });
  });
}

/**
 * Open Dataset Guide Modal
 */
async function OpenDatasetGuideModal() {
  const Modal = document.getElementById("ModalDatasetGuide");
  const Container = document.getElementById("DatasetGuideCardsList");
  if (!Modal || !Container) return;

  Modal.classList.add("open");
  Container.innerHTML = `<div style="color: var(--text-secondary);">Loading Dataset Registry & API Guide...</div>`;

  try {
    const Response = await fetch("/Api/Datasets/Guide");
    const Guide = await Response.json();
    Container.innerHTML = "";

    Guide.Datasets.forEach(D => {
      const Card = document.createElement("div");
      Card.style.background = "rgba(30, 41, 59, 0.4)";
      Card.style.border = "1px solid rgba(148, 163, 184, 0.12)";
      Card.style.borderRadius = "8px";
      Card.style.padding = "14px";

      Card.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
          <div style="font-weight: 800; color: #FFFFFF; font-size: 0.92rem;">#${D.DatasetNumber}. ${D.DatasetName}</div>
          <span style="background: rgba(6, 182, 212, 0.2); color: #06B6D4; padding: 2px 8px; border-radius: 4px; font-size: 0.70rem; font-weight: 700;">${D.Resolution}</span>
        </div>
        <div style="font-size: 0.75rem; color: var(--accent-amber); margin-bottom: 4px;">Provider: <b>${D.Provider}</b></div>
        <div style="font-size: 0.74rem; color: var(--text-secondary); margin-bottom: 8px;">Role: ${D.RoleInPipeline}</div>
        <div style="background: rgba(15, 23, 42, 0.6); padding: 8px; border-radius: 4px; font-family: 'JetBrains Mono'; font-size: 0.70rem; color: var(--accent-cyan); overflow-x: auto;">
          ${JSON.stringify(D.APIAndAccessEndpoints, null, 2)}
        </div>
      `;
      Container.appendChild(Card);
    });
  } catch (Ex) {
    Container.innerHTML = `<div style="color: var(--accent-red);">Failed To Load Dataset Documentation Guide.</div>`;
  }
}

/**
 * Download CSV Work-Order Via API With Live Progress Indicator
 */
async function DownloadCSVWorkOrder() {
  ShowMapLoader(`Exporting Work Order For ${State.CurrentCity}`, "Generating Contractor Schedule & Cost Assessment CSV...", 40);
  try {
    const Payload = {
      CityName: State.CurrentCity,
      OnlyBudgetIncluded: false,
      CustomWeights: State.ActiveWeights,
      BudgetLimitINR: State.BudgetCapINR,
      PreferredCoatingType: State.PreferredCoating
    };

    SetMapProgress(75, `Exporting Work Order`, "Formatting INR Rates & Material Specifications...");
    const Response = await fetch("/Api/WorkOrder/Export/CSV", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(Payload)
    });

    if (!Response.ok) throw new Error("CSV Export Failed");

    const Blob = await Response.blob();
    const Url = window.URL.createObjectURL(Blob);
    const Link = document.createElement("a");
    Link.href = Url;
    Link.download = `PARoo_Contractor_WorkOrder_${State.CurrentCity.replace(/\s+/g, '_')}.csv`;
    document.body.appendChild(Link);
    Link.click();
    document.body.removeChild(Link);
    window.URL.revokeObjectURL(Url);

    SetMapProgress(100, `CSV Export Complete`, `Downloaded Work Order For ${State.CurrentCity}`);
  } catch (Err) {
    console.error(`Export Error: ${Err.message}`);
    ShowMapLoader("Export Failed", Err.message, 100);
  } finally {
    setTimeout(() => HideMapLoader(), 600);
  }
}

/**
 * Update Map Floating Legend Content
 */
function UpdateMapLegend() {
  const Title = document.getElementById("LegendTitle");
  const Container = document.getElementById("LegendItemsList");
  if (!Title || !Container) return;

  switch (State.ActiveLayer) {
    case "CompositeRisk":
      Title.textContent = "Composite Heat-Risk Tiers";
      Container.innerHTML = `
        <div class="legend-row"><span class="legend-dot" style="background: #EF4444;"></span><span>Critical Priority (≥ 0.75)</span></div>
        <div class="legend-row"><span class="legend-dot" style="background: #F97316;"></span><span>High Priority (0.55 - 0.74)</span></div>
        <div class="legend-row"><span class="legend-dot" style="background: #FBBF24;"></span><span>Moderate Priority (0.40 - 0.54)</span></div>
        <div class="legend-row"><span class="legend-dot" style="background: #10B981;"></span><span>Low / Stable (&lt; 0.40)</span></div>
      `;
      break;

    case "Material":
      Title.textContent = "Predicted Roof Material (LLP)";
      Container.innerHTML = `
        <div class="legend-row"><span class="legend-dot" style="background: #06B6D4;"></span><span>Metal / Tin / Sheet</span></div>
        <div class="legend-row"><span class="legend-dot" style="background: #8B5CF6;"></span><span>Asbestos / Fibre Cement</span></div>
        <div class="legend-row"><span class="legend-dot" style="background: #64748B;"></span><span>Concrete / RCC</span></div>
        <div class="legend-row"><span class="legend-dot" style="background: #EA580C;"></span><span>Clay / Ceramic Tile</span></div>
        <div class="legend-row"><span class="legend-dot" style="background: #F59E0B;"></span><span>Thatch / Tarpaulin</span></div>
      `;
      break;

    case "DayLST":
      Title.textContent = "Landsat/ECOSTRESS Day LST (°C)";
      Container.innerHTML = `
        <div class="legend-row"><span class="legend-dot" style="background: #EF4444;"></span><span>Extreme Heat (&gt; 49°C)</span></div>
        <div class="legend-row"><span class="legend-dot" style="background: #F97316;"></span><span>High Heat (45°C - 49°C)</span></div>
        <div class="legend-row"><span class="legend-dot" style="background: #EAB308;"></span><span>Moderate Heat (41°C - 44°C)</span></div>
        <div class="legend-row"><span class="legend-dot" style="background: #3B82F6;"></span><span>Mild (&lt; 41°C)</span></div>
      `;
      break;

    case "NightRetention":
      Title.textContent = "Night Heat Retention Anomaly";
      Container.innerHTML = `
        <div class="legend-row"><span class="legend-dot" style="background: #EF4444;"></span><span>Severe Retention (&gt; 35°C)</span></div>
        <div class="legend-row"><span class="legend-dot" style="background: #F97316;"></span><span>High Retention (32°C - 35°C)</span></div>
        <div class="legend-row"><span class="legend-dot" style="background: #3B82F6;"></span><span>Dissipated (&lt; 32°C)</span></div>
      `;
      break;

    case "Population":
      Title.textContent = "WorldPop Density Protected";
      Container.innerHTML = `
        <div class="legend-row"><span class="legend-dot" style="background: #EF4444;"></span><span>Dense Population (&gt; 80 People)</span></div>
        <div class="legend-row"><span class="legend-dot" style="background: #F59E0B;"></span><span>Medium Density (20 - 80 People)</span></div>
        <div class="legend-row"><span class="legend-dot" style="background: #10B981;"></span><span>Low Density (&lt; 20 People)</span></div>
      `;
      break;
  }
}
