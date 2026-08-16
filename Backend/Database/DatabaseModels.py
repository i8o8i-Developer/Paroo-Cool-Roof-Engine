"""
Database Models And Schema Definitions For PARoo Production Engine
Defines Relational SQL DDL For Spatial Buildings, Sensor Readings, And Work Orders.
"""

from ..Utils.TitleCaseLogger import LogInfo, LogError
from .DatabaseEngine import GetDatabaseCursor

CREATE_SCHEMA_SQL = """
-- Cities Registry Table
CREATE TABLE IF NOT EXISTS Cities (
    CityName TEXT PRIMARY KEY,
    StateName TEXT NOT NULL,
    CenterLat REAL NOT NULL,
    CenterLon REAL NOT NULL,
    DefaultZoom INTEGER NOT NULL,
    BoundingBoxJSON TEXT NOT NULL,
    BaselineMaxSummerLST REAL NOT NULL,
    NightRetentionBaseline REAL NOT NULL,
    TotalPopulation INTEGER NOT NULL,
    ClimateZone TEXT NOT NULL,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Census Wards Table (Weak Supervision Baselines)
CREATE TABLE IF NOT EXISTS CensusWards (
    WardId TEXT PRIMARY KEY,
    CityName TEXT NOT NULL,
    WardName TEXT NOT NULL,
    MetalProportion REAL NOT NULL,
    AsbestosProportion REAL NOT NULL,
    ConcreteProportion REAL NOT NULL,
    TileProportion REAL NOT NULL,
    ThatchProportion REAL NOT NULL,
    PopulationDensityPerHectare REAL NOT NULL,
    FOREIGN KEY(CityName) REFERENCES Cities(CityName) ON DELETE CASCADE
);

-- Buildings Geospatial Footprints Table
CREATE TABLE IF NOT EXISTS Buildings (
    BuildingId TEXT PRIMARY KEY,
    CityName TEXT NOT NULL,
    WardId TEXT NOT NULL,
    CentroidLat REAL NOT NULL,
    CentroidLon REAL NOT NULL,
    PolygonCoordinatesJSON TEXT NOT NULL,
    RoofAreaSquareMeters REAL NOT NULL,
    BuildingHeightMeters REAL NOT NULL,
    EstimatedStoreys INTEGER NOT NULL,
    CompactnessRatio REAL NOT NULL,
    PerimeterMeters REAL NOT NULL,
    OpenBuildingsConfidence REAL NOT NULL,
    SourceDataSource TEXT DEFAULT 'OpenStreetMap / OpenBuildings',
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(CityName) REFERENCES Cities(CityName) ON DELETE CASCADE,
    FOREIGN KEY(WardId) REFERENCES CensusWards(WardId) ON DELETE CASCADE
);

-- Spectral Features Table (Sentinel-2 L2A)
CREATE TABLE IF NOT EXISTS SpectralFeatures (
    BuildingId TEXT PRIMARY KEY,
    NDVI REAL NOT NULL,
    NDBI REAL NOT NULL,
    Albedo REAL NOT NULL,
    Brightness REAL NOT NULL,
    TextureGLCM REAL NOT NULL,
    BuiltRatio REAL NOT NULL,
    CorrugationIndex REAL NOT NULL,
    ThermalMassIndex REAL NOT NULL,
    FOREIGN KEY(BuildingId) REFERENCES Buildings(BuildingId) ON DELETE CASCADE
);

-- Thermal Observations Table (Landsat 8/9 & ECOSTRESS LST)
CREATE TABLE IF NOT EXISTS ThermalObservations (
    BuildingId TEXT PRIMARY KEY,
    DayLSTCelsius REAL NOT NULL,
    NightLSTCelsius REAL NOT NULL,
    DiurnalAmplitudeCelsius REAL NOT NULL,
    DayLSTAnomalyScore REAL NOT NULL,
    NightRetentionScore REAL NOT NULL,
    ThermalQAPass INTEGER NOT NULL,
    ThermalQADiagnostic TEXT NOT NULL,
    FOREIGN KEY(BuildingId) REFERENCES Buildings(BuildingId) ON DELETE CASCADE
);

-- Roof Material Predictions Table (LLP Weak Supervision Output)
CREATE TABLE IF NOT EXISTS RoofMaterialPredictions (
    BuildingId TEXT PRIMARY KEY,
    PredictedMaterial TEXT NOT NULL,
    MaterialConfidence REAL NOT NULL,
    MaterialRiskWeight REAL NOT NULL,
    SoftProbabilitiesJSON TEXT NOT NULL,
    FOREIGN KEY(BuildingId) REFERENCES Buildings(BuildingId) ON DELETE CASCADE
);

-- Multi-Factor Heat Risk Scores Table
CREATE TABLE IF NOT EXISTS HeatRiskScores (
    BuildingId TEXT PRIMARY KEY,
    CompositeRiskScore REAL NOT NULL,
    RiskTier TEXT NOT NULL,
    RiskColorHex TEXT NOT NULL,
    SubScoresJSON TEXT NOT NULL,
    ActiveWeightsJSON TEXT NOT NULL,
    FOREIGN KEY(BuildingId) REFERENCES Buildings(BuildingId) ON DELETE CASCADE
);

-- Municipal Contractor Work Orders Table
CREATE TABLE IF NOT EXISTS ContractorWorkOrders (
    BuildingId TEXT PRIMARY KEY,
    PriorityRank INTEGER NOT NULL,
    EstimatedCostINR REAL NOT NULL,
    RecommendedCoatingType TEXT NOT NULL,
    EstimatedSurfaceTempReductionCelsius REAL NOT NULL,
    PopulationProtectedEst INTEGER NOT NULL,
    CostPerPersonProtectedINR REAL NOT NULL,
    IncludedInCurrentBudget INTEGER NOT NULL,
    FOREIGN KEY(BuildingId) REFERENCES Buildings(BuildingId) ON DELETE CASCADE
);

-- High-Performance Indices For Spatial Bounding Boxes And Rapid Prioritization Queries
CREATE INDEX IF NOT EXISTS Idx_Buildings_Spatial ON Buildings(CityName, CentroidLat, CentroidLon);
CREATE INDEX IF NOT EXISTS Idx_Buildings_Ward ON Buildings(WardId);
CREATE INDEX IF NOT EXISTS Idx_RiskScores_Score ON HeatRiskScores(CompositeRiskScore DESC);
CREATE INDEX IF NOT EXISTS Idx_WorkOrders_Rank ON ContractorWorkOrders(PriorityRank ASC);
CREATE INDEX IF NOT EXISTS Idx_Material_Pred ON RoofMaterialPredictions(PredictedMaterial);
"""

def InitializeDatabaseSchema() -> None:
    """Execute DDL To Initialize All Production Database Tables And Indices."""
    LogInfo("Initializing Relational Database Schema And Spatial Indices")
    try:
        with GetDatabaseCursor() as Cursor:
            Cursor.executescript(CREATE_SCHEMA_SQL)
        LogInfo("Production Database Schema Initialized Successfully")
    except Exception as Ex:
        LogError(f"Failed To Initialize Database Schema: {str(Ex)}")
        raise Ex
