"""
Comprehensive Satellite And Geospatial Dataset Documentation Guide For PARoo
Details All 6 Datasets, 3 Satellite Sensors, API Endpoints, And Access Mechanisms.
"""

from typing import Dict, List, Any

DATASET_DOCUMENTATION_REGISTRY: List[Dict[str, Any]] = [
    {
        "DatasetNumber": 1,
        "DatasetName": "Google Open Buildings v3 (+ 2.5D Temporal)",
        "Provider": "Google Research / Google Earth Engine",
        "RoleInPipeline": "Building Footprint Polygons, Geometric Areas (m²), Structural Heights, And Confidence Scores (> 0.70)",
        "Resolution": "0.5m Spatial Footprint Precision (Country-Scale S2 Geometry)",
        "APIAndAccessEndpoints": {
            "GoogleEarthEngineAsset": "ee.FeatureCollection('GOOGLE/Research/open-buildings/v3/polygons')",
            "PublicGCSBucket": "gs://open-buildings-data/v3/polygons_s2_level_4_gzip/",
            "WebPortal": "https://sites.research.google/open-buildings/",
            "AuthMethod": "Google Cloud Service Account / Earth Engine API Key"
        },
        "KeyAttributesExtracted": ["geometry", "area_in_meters", "confidence", "building_height_meters"]
    },
    {
        "DatasetNumber": 2,
        "DatasetName": "Sentinel-2 L2A Multispectral Satellite (RGB + NIR + SWIR)",
        "Provider": "European Space Agency (ESA) Copernicus Programme",
        "RoleInPipeline": "Optical Multispectral Reflectance Used To Classify Rooftop Materials (Metal, Asbestos, Concrete, Tile, Thatch)",
        "Resolution": "10m (B02, B03, B04, B08) & 20m (B11 SWIR)",
        "APIAndAccessEndpoints": {
            "CopernicusDataSpaceAPI": "https://shapps.dataspace.copernicus.eu/api/v1/",
            "PlanetaryComputerSTAC": "https://planetarycomputer.microsoft.com/api/stac/v1/collections/sentinel-2-l2a",
            "PublicAWSS3": "s3://sentinel-cogs/",
            "AuthMethod": "Copernicus CDSE OAuth2 / Microsoft Planetary Token / Free Public STAC"
        },
        "KeyAttributesExtracted": ["B02_Blue", "B03_Green", "B04_Red", "B08_NIR", "B11_SWIR", "NDVI", "NDBI", "Albedo", "GLCM_Texture"]
    },
    {
        "DatasetNumber": 3,
        "DatasetName": "Landsat 8/9 TIRS (Thermal Infrared Sensor)",
        "Provider": "USGS / NASA Earth Observation System",
        "RoleInPipeline": "Primary Thermal Land Surface Temperature (LST) Day & Night Infrared Measurements",
        "Resolution": "100m Native Thermal Resampled To 30m Level-2 Product",
        "APIAndAccessEndpoints": {
            "USGSEarthExplorer": "https://m2m.cr.usgs.gov/api/api/json/stable/",
            "PlanetaryComputerLandsat": "https://planetarycomputer.microsoft.com/api/stac/v1/collections/landsat-c2-l2",
            "OpenMeteoSurfaceTempAPI": "https://api.open-meteo.com/v1/forecast?hourly=surface_temperature",
            "AuthMethod": "USGS EROS M2M Token / Planetary Computer Token / Open-Meteo REST"
        },
        "KeyAttributesExtracted": ["ST_B10_Kelvin", "DayLSTCelsius", "LST_Anomaly_ZScore", "Emissivity_Band10"]
    },
    {
        "DatasetNumber": 4,
        "DatasetName": "NASA JPL ECOSTRESS (ISS Space Station Thermal Radiometer)",
        "Provider": "NASA Jet Propulsion Laboratory (JPL) / LP DAAC",
        "RoleInPipeline": "High-Frequency Diurnal Thermal Dynamics & Nocturnal Heat Retention (Captures Heat Trapped Overnight)",
        "Resolution": "70m High-Resolution Thermal Radiometry (Non-Sun-Synchronous Diurnal Orbit)",
        "APIAndAccessEndpoints": {
            "NASAAppEEARSAPI": "https://appeears.earthdatacloud.nasa.gov/api/",
            "NASAEarthdataCMR": "https://cmr.earthdata.nasa.gov/search/granules.json?collection_concept_id=C2075727977-LPCLOUD",
            "AuthMethod": "NASA Earthdata Bearer Token (Free Public Registration via urs.earthdata.nasa.gov)"
        },
        "KeyAttributesExtracted": ["ECOSTRESS_LST", "DiurnalAmplitudeCelsius", "NightHeatRetentionScore"]
    },
    {
        "DatasetNumber": 5,
        "DatasetName": "Census of India 2011 Houselisting & Housing Tables (Table H-02/H-03)",
        "Provider": "Office of the Registrar General & Census Commissioner, India",
        "RoleInPipeline": "Ward-Level Aggregate % of Roof Materials (Weak Supervision Signal For Learning From Label Proportions)",
        "Resolution": "Ward-Level Administrative Aggregations (100% Complete Indian Urban Coverage)",
        "APIAndAccessEndpoints": {
            "OfficialCensusDataPortal": "https://censusindia.gov.in/census.website/data/census-tables",
            "LocalDatabaseEngine": "Internal Database Table: CensusWards",
            "AuthMethod": "Open Government Data (OGD India) / Public Domain Census Tables"
        },
        "KeyAttributesExtracted": ["MetalProportion", "AsbestosProportion", "ConcreteProportion", "TileProportion", "ThatchProportion"]
    },
    {
        "DatasetNumber": 6,
        "DatasetName": "WorldPop Gridded Population Density (100m)",
        "Provider": "WorldPop Research Group / University of Southampton",
        "RoleInPipeline": "Gridded Demographic Density Used To Calculate Population Protected Per Rooftop Coating",
        "Resolution": "100m (1 Hectare Grid Cells)",
        "APIAndAccessEndpoints": {
            "WorldPopRESTAPI": "https://api.worldpop.org/v1/services/stats",
            "DirectFTPGeotiff": "https://data.worldpop.org/GIS/Population/Global_2000_2020_1km_UNadj/",
            "AuthMethod": "Free Public Open Access (Creative Commons CC-BY 4.0)"
        },
        "KeyAttributesExtracted": ["PopulationDensityPerHectare", "PopulationProtectedEst", "CostPerPersonProtectedINR"]
    }
]

def GetDatasetDocumentationGuide() -> Dict[str, Any]:
    """Retrieve Complete Standardized Documentation Guide For All 6 Datasets."""
    return {
        "SystemTitle": "PARoo Satellite & Geospatial Data Ingestion Architecture",
        "TotalDatasets": len(DATASET_DOCUMENTATION_REGISTRY),
        "TotalSatelliteSensors": 3,
        "Datasets": DATASET_DOCUMENTATION_REGISTRY
    }
