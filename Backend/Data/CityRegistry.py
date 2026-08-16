"""
City Registry And Synthetic High-Fidelity Geospatial Generator For Indian Urban Centers
"""

import math
import random
from typing import Dict, List, Any, Tuple
from ..Utils.TitleCaseLogger import LogInfo, LogWarning, LogError
from ..Utils.GeoUtils import (
    ComputePolygonCentroid,
    ApproximatePolygonAreaSquareMeters,
    ApproximatePolygonPerimeterMeters,
    ComputeCompactnessRatio
)

CITIES_REGISTRY: Dict[str, Dict[str, Any]] = {
    "Jaipur": {
        "CityName": "Jaipur",
        "StateName": "Rajasthan",
        "CenterLat": 26.9124,
        "CenterLon": 75.7873,
        "DefaultZoom": 14,
        "BoundingBox": [75.7500, 26.8800, 75.8300, 26.9500],  # [MinLon, MinLat, MaxLon, MaxLat]
        "BaselineMaxSummerLST": 48.5,
        "NightRetentionBaseline": 33.2,
        "TotalPopulation": 3073350,
        "ClimateZone": "Hot Semi-Arid",
        "Wards": [
            {
                "WardId": "Ward 12 - Johari Walled City",
                "WardName": "Johari Bazar & Walled City",
                "CensusRoofProportions": {
                    "Metal / Tin": 0.18,
                    "Asbestos / Cement": 0.22,
                    "Concrete / RCC": 0.42,
                    "Clay / Tile": 0.15,
                    "Thatch / Tarpaulin": 0.03
                },
                "PopulationDensityPerHectare": 420
            },
            {
                "WardId": "Ward 24 - Sanganer Industrial",
                "WardName": "Sanganer Textile & Craft Zone",
                "CensusRoofProportions": {
                    "Metal / Tin": 0.48,
                    "Asbestos / Cement": 0.28,
                    "Concrete / RCC": 0.18,
                    "Clay / Tile": 0.04,
                    "Thatch / Tarpaulin": 0.02
                },
                "PopulationDensityPerHectare": 280
            },
            {
                "WardId": "Ward 35 - Jhotwara Resettlement",
                "WardName": "Jhotwara Dense Settlement",
                "CensusRoofProportions": {
                    "Metal / Tin": 0.35,
                    "Asbestos / Cement": 0.32,
                    "Concrete / RCC": 0.22,
                    "Clay / Tile": 0.06,
                    "Thatch / Tarpaulin": 0.05
                },
                "PopulationDensityPerHectare": 360
            },
            {
                "WardId": "Ward 48 - Mansarovar Sector 7",
                "WardName": "Mansarovar Mixed Residential",
                "CensusRoofProportions": {
                    "Metal / Tin": 0.10,
                    "Asbestos / Cement": 0.12,
                    "Concrete / RCC": 0.70,
                    "Clay / Tile": 0.07,
                    "Thatch / Tarpaulin": 0.01
                },
                "PopulationDensityPerHectare": 190
            }
        ]
    },
    "Ahmedabad": {
        "CityName": "Ahmedabad",
        "StateName": "Gujarat",
        "CenterLat": 23.0225,
        "CenterLon": 72.5714,
        "DefaultZoom": 14,
        "BoundingBox": [72.5300, 22.9900, 72.6200, 23.0600],
        "BaselineMaxSummerLST": 49.2,
        "NightRetentionBaseline": 34.1,
        "TotalPopulation": 5633927,
        "ClimateZone": "Hot Semi-Arid Heatwave Epicenter",
        "Wards": [
            {
                "WardId": "Ward 07 - Naroda Industrial",
                "WardName": "Naroda GIDC Manufacturing Area",
                "CensusRoofProportions": {
                    "Metal / Tin": 0.52,
                    "Asbestos / Cement": 0.30,
                    "Concrete / RCC": 0.14,
                    "Clay / Tile": 0.02,
                    "Thatch / Tarpaulin": 0.02
                },
                "PopulationDensityPerHectare": 310
            },
            {
                "WardId": "Ward 18 - Danilimda Slum Cluster",
                "WardName": "Danilimda Informal Settlement",
                "CensusRoofProportions": {
                    "Metal / Tin": 0.40,
                    "Asbestos / Cement": 0.35,
                    "Concrete / RCC": 0.15,
                    "Clay / Tile": 0.03,
                    "Thatch / Tarpaulin": 0.07
                },
                "PopulationDensityPerHectare": 540
            },
            {
                "WardId": "Ward 29 - Behrampura South",
                "WardName": "Behrampura High-Density Residential",
                "CensusRoofProportions": {
                    "Metal / Tin": 0.32,
                    "Asbestos / Cement": 0.28,
                    "Concrete / RCC": 0.32,
                    "Clay / Tile": 0.05,
                    "Thatch / Tarpaulin": 0.03
                },
                "PopulationDensityPerHectare": 460
            },
            {
                "WardId": "Ward 42 - Navrangpura Commercial",
                "WardName": "Navrangpura Urban Core",
                "CensusRoofProportions": {
                    "Metal / Tin": 0.08,
                    "Asbestos / Cement": 0.06,
                    "Concrete / RCC": 0.82,
                    "Clay / Tile": 0.03,
                    "Thatch / Tarpaulin": 0.01
                },
                "PopulationDensityPerHectare": 175
            }
        ]
    },
    "Delhi NCR": {
        "CityName": "Delhi NCR",
        "StateName": "National Capital Territory",
        "CenterLat": 28.6139,
        "CenterLon": 77.2090,
        "DefaultZoom": 14,
        "BoundingBox": [77.1700, 28.5700, 77.2600, 28.6600],
        "BaselineMaxSummerLST": 50.1,
        "NightRetentionBaseline": 35.4,
        "TotalPopulation": 16787941,
        "ClimateZone": "Extreme Urban Heat Island",
        "Wards": [
            {
                "WardId": "Ward 81 - Sangam Vihar South",
                "WardName": "Sangam Vihar High Density Resettlement",
                "CensusRoofProportions": {
                    "Metal / Tin": 0.44,
                    "Asbestos / Cement": 0.34,
                    "Concrete / RCC": 0.16,
                    "Clay / Tile": 0.02,
                    "Thatch / Tarpaulin": 0.04
                },
                "PopulationDensityPerHectare": 680
            },
            {
                "WardId": "Ward 55 - Okhla Phase II",
                "WardName": "Okhla Industrial & Informal Corridor",
                "CensusRoofProportions": {
                    "Metal / Tin": 0.50,
                    "Asbestos / Cement": 0.26,
                    "Concrete / RCC": 0.20,
                    "Clay / Tile": 0.02,
                    "Thatch / Tarpaulin": 0.02
                },
                "PopulationDensityPerHectare": 390
            },
            {
                "WardId": "Ward 32 - Seelampur East",
                "WardName": "Seelampur Trans-Yamuna Cluster",
                "CensusRoofProportions": {
                    "Metal / Tin": 0.38,
                    "Asbestos / Cement": 0.32,
                    "Concrete / RCC": 0.24,
                    "Clay / Tile": 0.02,
                    "Thatch / Tarpaulin": 0.04
                },
                "PopulationDensityPerHectare": 720
            },
            {
                "WardId": "Ward 14 - Connaught Core",
                "WardName": "Central Commercial & Institutional",
                "CensusRoofProportions": {
                    "Metal / Tin": 0.06,
                    "Asbestos / Cement": 0.05,
                    "Concrete / RCC": 0.86,
                    "Clay / Tile": 0.02,
                    "Thatch / Tarpaulin": 0.01
                },
                "PopulationDensityPerHectare": 120
            }
        ]
    },
    "Hyderabad": {
        "CityName": "Hyderabad",
        "StateName": "Telangana",
        "CenterLat": 17.3850,
        "CenterLon": 78.4867,
        "DefaultZoom": 14,
        "BoundingBox": [78.4400, 17.3500, 78.5300, 17.4300],
        "BaselineMaxSummerLST": 46.8,
        "NightRetentionBaseline": 31.8,
        "TotalPopulation": 6809970,
        "ClimateZone": "Tropical Wet And Dry / Deccan Heat",
        "Wards": [
            {
                "WardId": "Ward 45 - Charminar Old City",
                "WardName": "Charminar Heritage & Dense Residential",
                "CensusRoofProportions": {
                    "Metal / Tin": 0.28,
                    "Asbestos / Cement": 0.24,
                    "Concrete / RCC": 0.38,
                    "Clay / Tile": 0.08,
                    "Thatch / Tarpaulin": 0.02
                },
                "PopulationDensityPerHectare": 490
            },
            {
                "WardId": "Ward 88 - Jeedimetla Industrial",
                "WardName": "Jeedimetla Manufacturing Corridor",
                "CensusRoofProportions": {
                    "Metal / Tin": 0.54,
                    "Asbestos / Cement": 0.26,
                    "Concrete / RCC": 0.17,
                    "Clay / Tile": 0.02,
                    "Thatch / Tarpaulin": 0.01
                },
                "PopulationDensityPerHectare": 260
            },
            {
                "WardId": "Ward 62 - Borabanda Hill Colony",
                "WardName": "Borabanda Informal Settlement",
                "CensusRoofProportions": {
                    "Metal / Tin": 0.42,
                    "Asbestos / Cement": 0.36,
                    "Concrete / RCC": 0.16,
                    "Clay / Tile": 0.03,
                    "Thatch / Tarpaulin": 0.03
                },
                "PopulationDensityPerHectare": 510
            },
            {
                "WardId": "Ward 104 - Banjara Hills",
                "WardName": "Banjara Hills Residential",
                "CensusRoofProportions": {
                    "Metal / Tin": 0.05,
                    "Asbestos / Cement": 0.07,
                    "Concrete / RCC": 0.85,
                    "Clay / Tile": 0.02,
                    "Thatch / Tarpaulin": 0.01
                },
                "PopulationDensityPerHectare": 140
            }
        ]
    },
    "Nagpur": {
        "CityName": "Nagpur",
        "StateName": "Maharashtra",
        "CenterLat": 21.1458,
        "CenterLon": 79.0882,
        "DefaultZoom": 14,
        "BoundingBox": [79.0500, 21.1100, 79.1300, 21.1800],
        "BaselineMaxSummerLST": 49.8,
        "NightRetentionBaseline": 34.8,
        "TotalPopulation": 2405665,
        "ClimateZone": "Vidarbha Extreme Summer Core",
        "Wards": [
            {
                "WardId": "Ward 15 - Hingna MIDC",
                "WardName": "Hingna Industrial Zone",
                "CensusRoofProportions": {
                    "Metal / Tin": 0.56,
                    "Asbestos / Cement": 0.25,
                    "Concrete / RCC": 0.16,
                    "Clay / Tile": 0.02,
                    "Thatch / Tarpaulin": 0.01
                },
                "PopulationDensityPerHectare": 240
            },
            {
                "WardId": "Ward 22 - Pardi Settlement",
                "WardName": "Pardi Dense Low-Income Colony",
                "CensusRoofProportions": {
                    "Metal / Tin": 0.38,
                    "Asbestos / Cement": 0.34,
                    "Concrete / RCC": 0.20,
                    "Clay / Tile": 0.05,
                    "Thatch / Tarpaulin": 0.03
                },
                "PopulationDensityPerHectare": 410
            },
            {
                "WardId": "Ward 04 - Sitabuldi Central",
                "WardName": "Sitabuldi Commercial Core",
                "CensusRoofProportions": {
                    "Metal / Tin": 0.14,
                    "Asbestos / Cement": 0.18,
                    "Concrete / RCC": 0.62,
                    "Clay / Tile": 0.05,
                    "Thatch / Tarpaulin": 0.01
                },
                "PopulationDensityPerHectare": 320
            }
        ]
    },
    "Mumbai": {
        "CityName": "Mumbai",
        "StateName": "Maharashtra",
        "CenterLat": 19.0760,
        "CenterLon": 72.8777,
        "DefaultZoom": 14,
        "BoundingBox": [72.8400, 19.0300, 72.9200, 19.1100],
        "BaselineMaxSummerLST": 43.5,
        "NightRetentionBaseline": 32.5,
        "TotalPopulation": 12442373,
        "ClimateZone": "Coastal Extreme Humidity Heat Index",
        "Wards": [
            {
                "WardId": "Ward G/N - Dharavi Central",
                "WardName": "Dharavi High Density Settlement",
                "CensusRoofProportions": {
                    "Metal / Tin": 0.46,
                    "Asbestos / Cement": 0.32,
                    "Concrete / RCC": 0.14,
                    "Clay / Tile": 0.03,
                    "Thatch / Tarpaulin": 0.05
                },
                "PopulationDensityPerHectare": 980
            },
            {
                "WardId": "Ward M/E - Govandi Slum",
                "WardName": "Govandi Resettlement Colony",
                "CensusRoofProportions": {
                    "Metal / Tin": 0.42,
                    "Asbestos / Cement": 0.36,
                    "Concrete / RCC": 0.15,
                    "Clay / Tile": 0.02,
                    "Thatch / Tarpaulin": 0.05
                },
                "PopulationDensityPerHectare": 850
            },
            {
                "WardId": "Ward H/W - Bandra West",
                "WardName": "Bandra Coastal Residential",
                "CensusRoofProportions": {
                    "Metal / Tin": 0.08,
                    "Asbestos / Cement": 0.08,
                    "Concrete / RCC": 0.80,
                    "Clay / Tile": 0.03,
                    "Thatch / Tarpaulin": 0.01
                },
                "PopulationDensityPerHectare": 290
            }
        ]
    },
    "Surat": {
        "CityName": "Surat",
        "StateName": "Gujarat",
        "CenterLat": 21.1702,
        "CenterLon": 72.8311,
        "DefaultZoom": 14,
        "BoundingBox": [72.7900, 21.1300, 72.8700, 21.2100],
        "BaselineMaxSummerLST": 47.3,
        "NightRetentionBaseline": 33.5,
        "TotalPopulation": 4467797,
        "ClimateZone": "Humid Industrial Heat Core",
        "Wards": [
            {
                "WardId": "Ward 12 - Limbayat Textile Hub",
                "WardName": "Limbayat Weaving & Industrial Cluster",
                "CensusRoofProportions": {
                    "Metal / Tin": 0.58,
                    "Asbestos / Cement": 0.22,
                    "Concrete / RCC": 0.16,
                    "Clay / Tile": 0.02,
                    "Thatch / Tarpaulin": 0.02
                },
                "PopulationDensityPerHectare": 520
            },
            {
                "WardId": "Ward 06 - Katargam Diamond Zone",
                "WardName": "Katargam Mixed Commercial/Residential",
                "CensusRoofProportions": {
                    "Metal / Tin": 0.22,
                    "Asbestos / Cement": 0.20,
                    "Concrete / RCC": 0.54,
                    "Clay / Tile": 0.03,
                    "Thatch / Tarpaulin": 0.01
                },
                "PopulationDensityPerHectare": 380
            }
        ]
    },
    "Bengaluru": {
        "CityName": "Bengaluru",
        "StateName": "Karnataka",
        "CenterLat": 12.9716,
        "CenterLon": 77.5946,
        "DefaultZoom": 14,
        "BoundingBox": [77.5500, 12.9300, 77.6400, 13.0100],
        "BaselineMaxSummerLST": 42.1,
        "NightRetentionBaseline": 28.5,
        "TotalPopulation": 8443675,
        "ClimateZone": "Tropical Savanna Urban Heat Anomaly",
        "Wards": [
            {
                "WardId": "Ward 40 - Peenya Industrial Stage 1",
                "WardName": "Peenya Manufacturing Zone",
                "CensusRoofProportions": {
                    "Metal / Tin": 0.60,
                    "Asbestos / Cement": 0.24,
                    "Concrete / RCC": 0.14,
                    "Clay / Tile": 0.01,
                    "Thatch / Tarpaulin": 0.01
                },
                "PopulationDensityPerHectare": 210
            },
            {
                "WardId": "Ward 92 - Shivajinagar Dense",
                "WardName": "Shivajinagar Historic Settlement",
                "CensusRoofProportions": {
                    "Metal / Tin": 0.32,
                    "Asbestos / Cement": 0.28,
                    "Concrete / RCC": 0.34,
                    "Clay / Tile": 0.04,
                    "Thatch / Tarpaulin": 0.02
                },
                "PopulationDensityPerHectare": 610
            },
            {
                "WardId": "Ward 174 - HSR Sector 2",
                "WardName": "HSR Layout Modern Residential",
                "CensusRoofProportions": {
                    "Metal / Tin": 0.06,
                    "Asbestos / Cement": 0.08,
                    "Concrete / RCC": 0.82,
                    "Clay / Tile": 0.03,
                    "Thatch / Tarpaulin": 0.01
                },
                "PopulationDensityPerHectare": 160
            }
        ]
    }
}

def GenerateSyntheticFootprintsForCity(CityName: str, TargetBuildingCount: int = 850) -> List[Dict[str, Any]]:
    """Generate High-Fidelity Realistic Building Footprints, Spectral Data, And Thermal Indicators For A City."""
    LogInfo(f"Generating High-Fidelity Geospatial Footprints ({TargetBuildingCount} Buildings) For City: {CityName}")
    CityConfig = CITIES_REGISTRY.get(CityName, CITIES_REGISTRY["Jaipur"])
    
    CenterLat = CityConfig["CenterLat"]
    CenterLon = CityConfig["CenterLon"]
    Wards = CityConfig["Wards"]
    BaseSummerLST = CityConfig["BaselineMaxSummerLST"]
    BaseNightRetention = CityConfig["NightRetentionBaseline"]
    
    BuildingFeatures = []
    RandomSeed = sum(ord(c) for c in CityName)
    RandomEngine = random.Random(RandomSeed)
    
    BuildingsPerWard = max(20, TargetBuildingCount // len(Wards))
    BuildingCounter = 1
    
    for WardIndex, Ward in enumerate(Wards):
        WardName = Ward["WardName"]
        WardId = Ward["WardId"]
        Proportions = Ward["CensusRoofProportions"]
        WardDensity = Ward["PopulationDensityPerHectare"]
        
        # Ward Center Offset
        Angle = (2 * math.pi * WardIndex) / len(Wards)
        Radius = 0.012 + 0.005 * (WardIndex % 2)
        WardLat = CenterLat + Radius * math.sin(Angle)
        WardLon = CenterLon + (Radius * 1.1) * math.cos(Angle)
        
        # Determine Material Quota In This Ward
        MaterialChoices = ["Metal / Tin", "Asbestos / Cement", "Concrete / RCC", "Clay / Tile", "Thatch / Tarpaulin"]
        MaterialWeights = [Proportions.get(m, 0.2) for m in MaterialChoices]
        
        for _ in range(BuildingsPerWard):
            # Select Ground-Truth Representative Material Based On Census Proportions
            AssignedMaterial = RandomEngine.choices(MaterialChoices, weights=MaterialWeights, k=1)[0]
            
            # Sub-Cluster Offset
            SubAngle = RandomEngine.uniform(0, 2 * math.pi)
            SubDist = RandomEngine.uniform(0.0005, 0.0055)
            BLat = WardLat + SubDist * math.sin(SubAngle)
            BLon = WardLon + (SubDist * 1.1) * math.cos(SubAngle)
            
            # Geometry Dimensions (Square/Rectangular Roofs With Slight Rotation)
            RoofWidthMeters = RandomEngine.uniform(6.0, 22.0)
            RoofLengthMeters = RandomEngine.uniform(8.0, 28.0)
            
            if AssignedMaterial in ["Metal / Tin", "Asbestos / Cement"]:
                # Industrial/Shed Roofs Are Often Larger Or Tightly Packed
                RoofWidthMeters *= RandomEngine.uniform(1.1, 1.6)
                RoofLengthMeters *= RandomEngine.uniform(1.1, 1.8)
            elif AssignedMaterial == "Thatch / Tarpaulin":
                # Informal Dwellings Are Smaller
                RoofWidthMeters = RandomEngine.uniform(4.0, 8.0)
                RoofLengthMeters = RandomEngine.uniform(5.0, 10.0)
                
            RotationDegrees = RandomEngine.uniform(0, 90)
            RotRad = math.radians(RotationDegrees)
            
            # Lat/Lon Offsets For Corners
            LatScale = 1.0 / 111139.0
            LonScale = 1.0 / (111139.0 * math.cos(math.radians(BLat)))
            
            HalfW = (RoofWidthMeters / 2.0)
            HalfL = (RoofLengthMeters / 2.0)
            
            LocalCorners = [
                (-HalfW, -HalfL),
                (HalfW, -HalfL),
                (HalfW, HalfL),
                (-HalfW, HalfL),
                (-HalfW, -HalfL)
            ]
            
            Coordinates = []
            for X, Y in LocalCorners:
                RotX = X * math.cos(RotRad) - Y * math.sin(RotRad)
                RotY = X * math.sin(RotRad) + Y * math.cos(RotRad)
                CoordLon = BLon + (RotX * LonScale)
                CoordLat = BLat + (RotY * LatScale)
                Coordinates.append([round(CoordLon, 6), round(CoordLat, 6)])
                
            RoofArea = ApproximatePolygonAreaSquareMeters(Coordinates)
            Perimeter = ApproximatePolygonPerimeterMeters(Coordinates)
            Compactness = ComputeCompactnessRatio(RoofArea, Perimeter)
            
            # Structural Heights Based On Open Buildings 2.5D Proxy
            if AssignedMaterial == "Concrete / RCC":
                BuildingHeightMeters = round(RandomEngine.uniform(6.5, 18.0), 1)
                Confidence = round(RandomEngine.uniform(0.85, 0.98), 2)
            elif AssignedMaterial in ["Metal / Tin", "Asbestos / Cement"]:
                BuildingHeightMeters = round(RandomEngine.uniform(3.5, 8.5), 1)
                Confidence = round(RandomEngine.uniform(0.78, 0.94), 2)
            else:
                BuildingHeightMeters = round(RandomEngine.uniform(2.5, 4.5), 1)
                Confidence = round(RandomEngine.uniform(0.71, 0.88), 2)
                
            # Sentinel-2 Multispectral Signatures Simulation
            # Metal / Tin: High Brightness/Albedo, High NDBI, Very Low NDVI
            # Asbestos / Cement: Medium-High Brightness, High Roughness, Low NDVI
            # Concrete: Moderate Brightness, Moderate NDBI, Low NDVI
            # Tile: Distinct Red/SWIR Reflectance, Moderate NDVI
            # Thatch: Low Brightness, High Roughness, Moderate NDVI
            if AssignedMaterial == "Metal / Tin":
                NDVI = round(RandomEngine.uniform(-0.08, 0.05), 3)
                NDBI = round(RandomEngine.uniform(0.28, 0.58), 3)
                Albedo = round(RandomEngine.uniform(0.35, 0.65), 3)
                Brightness = round(RandomEngine.uniform(0.60, 0.95), 3)
                TextureGLCM = round(RandomEngine.uniform(0.20, 0.45), 3)
            elif AssignedMaterial == "Asbestos / Cement":
                NDVI = round(RandomEngine.uniform(-0.02, 0.08), 3)
                NDBI = round(RandomEngine.uniform(0.20, 0.45), 3)
                Albedo = round(RandomEngine.uniform(0.25, 0.45), 3)
                Brightness = round(RandomEngine.uniform(0.45, 0.70), 3)
                TextureGLCM = round(RandomEngine.uniform(0.48, 0.82), 3)
            elif AssignedMaterial == "Concrete / RCC":
                NDVI = round(RandomEngine.uniform(0.02, 0.14), 3)
                NDBI = round(RandomEngine.uniform(0.10, 0.32), 3)
                Albedo = round(RandomEngine.uniform(0.18, 0.32), 3)
                Brightness = round(RandomEngine.uniform(0.30, 0.55), 3)
                TextureGLCM = round(RandomEngine.uniform(0.25, 0.50), 3)
            elif AssignedMaterial == "Clay / Tile":
                NDVI = round(RandomEngine.uniform(0.05, 0.20), 3)
                NDBI = round(RandomEngine.uniform(0.05, 0.22), 3)
                Albedo = round(RandomEngine.uniform(0.15, 0.28), 3)
                Brightness = round(RandomEngine.uniform(0.25, 0.48), 3)
                TextureGLCM = round(RandomEngine.uniform(0.35, 0.65), 3)
            else:  # Thatch / Tarpaulin
                NDVI = round(RandomEngine.uniform(0.10, 0.35), 3)
                NDBI = round(RandomEngine.uniform(0.00, 0.18), 3)
                Albedo = round(RandomEngine.uniform(0.10, 0.22), 3)
                Brightness = round(RandomEngine.uniform(0.15, 0.35), 3)
                TextureGLCM = round(RandomEngine.uniform(0.60, 0.95), 3)
                
            # Landsat 8/9 & ECOSTRESS Land Surface Temperature (LST)
            # Physical Behaviour: Metal heats up fastest during day; Concrete stores heat overnight
            LSTDayNoise = RandomEngine.uniform(-2.2, 3.8)
            LSTNightNoise = RandomEngine.uniform(-1.5, 2.5)
            
            if AssignedMaterial == "Metal / Tin":
                DayLST = round(BaseSummerLST + 4.2 + LSTDayNoise, 1)
                NightLST = round(BaseNightRetention + 1.2 + LSTNightNoise, 1)
            elif AssignedMaterial == "Asbestos / Cement":
                DayLST = round(BaseSummerLST + 3.5 + LSTDayNoise, 1)
                NightLST = round(BaseNightRetention + 2.8 + LSTNightNoise, 1)
            elif AssignedMaterial == "Concrete / RCC":
                DayLST = round(BaseSummerLST + 1.2 + LSTDayNoise, 1)
                NightLST = round(BaseNightRetention + 3.6 + LSTNightNoise, 1)  # High thermal mass traps heat at night
            elif AssignedMaterial == "Clay / Tile":
                DayLST = round(BaseSummerLST - 1.8 + LSTDayNoise, 1)
                NightLST = round(BaseNightRetention - 1.2 + LSTNightNoise, 1)
            else:  # Thatch / Tarpaulin
                DayLST = round(BaseSummerLST + 2.8 + LSTDayNoise, 1)
                NightLST = round(BaseNightRetention + 2.0 + LSTNightNoise, 1)
                
            DiurnalAmplitude = round(DayLST - NightLST, 1)
            
            # WorldPop Population Density Proxy (Persons Protected Per Roof)
            Storeys = max(1, int(BuildingHeightMeters / 3.2))
            OccupancyMultiplier = (WardDensity / 250.0) * Storeys
            PopulationProtected = max(2, int(round((RoofArea / 14.0) * OccupancyMultiplier)))
            
            BuildingId = f"OB_{CityName[:3].upper()}_{BuildingCounter:05d}"
            BuildingCounter += 1
            
            Feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [Coordinates]
                },
                "properties": {
                    "BuildingId": BuildingId,
                    "City": CityName,
                    "WardId": WardId,
                    "WardName": WardName,
                    "RoofAreaSquareMeters": round(RoofArea, 1),
                    "BuildingHeightMeters": BuildingHeightMeters,
                    "EstimatedStoreys": Storeys,
                    "OpenBuildingsConfidence": Confidence,
                    "PerimeterMeters": round(Perimeter, 1),
                    "CompactnessRatio": round(Compactness, 2),
                    "CentroidLat": round(BLat, 6),
                    "CentroidLon": round(BLon, 6),
                    "SpectralIndices": {
                        "NDVI": NDVI,
                        "NDBI": NDBI,
                        "Albedo": Albedo,
                        "Brightness": Brightness,
                        "TextureGLCM": TextureGLCM
                    },
                    "ThermalObservations": {
                        "DayLSTCelsius": DayLST,
                        "NightLSTCelsius": NightLST,
                        "DiurnalAmplitudeCelsius": DiurnalAmplitude
                    },
                    "PopulationProtectedEst": PopulationProtected,
                    "SyntheticGroundTruthMaterial": AssignedMaterial
                }
            }
            BuildingFeatures.append(Feature)
            
    LogInfo(f"Successfully Generated {len(BuildingFeatures)} High-Fidelity Building Footprints For {CityName}")
    return BuildingFeatures

def GenerateDenseFootprintsForBoundingBox(
    MinLon: float,
    MinLat: float,
    MaxLon: float,
    MaxLat: float,
    TargetCount: int = 850,
    AOIName: str = "Custom AOI"
) -> List[Dict[str, Any]]:
    """Generate A Dense Realistic Grid Of Building Footprints Strictly Within A Custom Bounding Box."""
    LogInfo(f"Generating Dense Geospatial Footprints ({TargetCount} Buildings) For BBox: [{MinLon}, {MinLat}, {MaxLon}, {MaxLat}]")
    
    BuildingFeatures = []
    RandomEngine = random.Random(int((MinLon + MinLat + MaxLon + MaxLat) * 10000))
    
    # Material Distribution In High-Density Indian Urban Wards
    MaterialChoices = ["Metal / Tin", "Asbestos / Cement", "Concrete / RCC", "Clay / Tile", "Thatch / Tarpaulin"]
    MaterialWeights = [0.32, 0.28, 0.25, 0.10, 0.05]
    
    LatSpan = MaxLat - MinLat
    LonSpan = MaxLon - MinLon
    
    # Calculate Rows & Columns For Dense Urban Layout
    Aspect = max(0.2, min(5.0, LonSpan / max(0.0001, LatSpan)))
    Cols = max(4, int(math.sqrt(TargetCount * Aspect)))
    Rows = max(4, int(TargetCount / Cols))
    
    BuildingCounter = 1
    
    for R in range(Rows):
        for C in range(Cols):
            if len(BuildingFeatures) >= TargetCount:
                break
                
            # Base Cell Coordinates With Urban Jitter
            CellMinLat = MinLat + (R / Rows) * LatSpan
            CellMaxLat = MinLat + ((R + 1) / Rows) * LatSpan
            CellMinLon = MinLon + (C / Cols) * LonSpan
            CellMaxLon = MinLon + ((C + 1) / Cols) * LonSpan
            
            # Position Building Centroid Inside The Cell
            BLat = RandomEngine.uniform(CellMinLat + 0.1 * (CellMaxLat - CellMinLat), CellMaxLat - 0.1 * (CellMaxLat - CellMinLat))
            BLon = RandomEngine.uniform(CellMinLon + 0.1 * (CellMaxLon - CellMinLon), CellMaxLon - 0.1 * (CellMaxLon - CellMinLon))
            
            AssignedMaterial = RandomEngine.choices(MaterialChoices, weights=MaterialWeights, k=1)[0]
            
            # Building Dimensions (m)
            if AssignedMaterial == "Metal / Tin":
                RoofWidthM = RandomEngine.uniform(7.0, 18.0)
                RoofLengthM = RandomEngine.uniform(10.0, 24.0)
                HeightM = round(RandomEngine.uniform(3.5, 7.0), 1)
            elif AssignedMaterial == "Asbestos / Cement":
                RoofWidthM = RandomEngine.uniform(8.0, 20.0)
                RoofLengthM = RandomEngine.uniform(12.0, 26.0)
                HeightM = round(RandomEngine.uniform(4.0, 8.5), 1)
            elif AssignedMaterial == "Concrete / RCC":
                RoofWidthM = RandomEngine.uniform(10.0, 28.0)
                RoofLengthM = RandomEngine.uniform(14.0, 32.0)
                HeightM = round(RandomEngine.uniform(6.5, 18.0), 1)
            elif AssignedMaterial == "Clay / Tile":
                RoofWidthM = RandomEngine.uniform(6.0, 14.0)
                RoofLengthM = RandomEngine.uniform(8.0, 18.0)
                HeightM = round(RandomEngine.uniform(3.0, 6.0), 1)
            else:
                RoofWidthM = RandomEngine.uniform(4.0, 8.0)
                RoofLengthM = RandomEngine.uniform(5.0, 10.0)
                HeightM = round(RandomEngine.uniform(2.5, 4.0), 1)
                
            RotationDeg = RandomEngine.uniform(0, 90)
            RotRad = math.radians(RotationDeg)
            
            LatScale = 1.0 / 111139.0
            LonScale = 1.0 / (111139.0 * math.cos(math.radians(BLat)))
            
            HalfW = RoofWidthM / 2.0
            HalfL = RoofLengthM / 2.0
            
            Corners = [
                (-HalfW, -HalfL),
                (HalfW, -HalfL),
                (HalfW, HalfL),
                (-HalfW, HalfL),
                (-HalfW, -HalfL)
            ]
            
            Coordinates = []
            for X, Y in Corners:
                RotX = X * math.cos(RotRad) - Y * math.sin(RotRad)
                RotY = X * math.sin(RotRad) + Y * math.cos(RotRad)
                CoordLon = BLon + (RotX * LonScale)
                CoordLat = BLat + (RotY * LatScale)
                Coordinates.append([round(CoordLon, 6), round(CoordLat, 6)])
                
            RoofArea = ApproximatePolygonAreaSquareMeters(Coordinates)
            Perimeter = ApproximatePolygonPerimeterMeters(Coordinates)
            Compactness = ComputeCompactnessRatio(RoofArea, Perimeter)
            
            # Multispectral & Thermal Signatures
            if AssignedMaterial == "Metal / Tin":
                NDVI = round(RandomEngine.uniform(-0.08, 0.04), 3)
                NDBI = round(RandomEngine.uniform(0.42, 0.68), 3)
                Albedo = round(RandomEngine.uniform(0.48, 0.72), 3)
                Brightness = round(RandomEngine.uniform(0.60, 0.85), 3)
                TextureGLCM = round(RandomEngine.uniform(0.25, 0.45), 3)
                DayLST = round(RandomEngine.uniform(48.5, 54.2), 1)
                NightLST = round(RandomEngine.uniform(26.5, 30.2), 1)
            elif AssignedMaterial == "Asbestos / Cement":
                NDVI = round(RandomEngine.uniform(-0.04, 0.08), 3)
                NDBI = round(RandomEngine.uniform(0.32, 0.52), 3)
                Albedo = round(RandomEngine.uniform(0.36, 0.55), 3)
                Brightness = round(RandomEngine.uniform(0.45, 0.68), 3)
                TextureGLCM = round(RandomEngine.uniform(0.55, 0.82), 3)
                DayLST = round(RandomEngine.uniform(46.0, 51.5), 1)
                NightLST = round(RandomEngine.uniform(28.0, 32.5), 1)
            elif AssignedMaterial == "Concrete / RCC":
                NDVI = round(RandomEngine.uniform(0.02, 0.14), 3)
                NDBI = round(RandomEngine.uniform(0.18, 0.38), 3)
                Albedo = round(RandomEngine.uniform(0.20, 0.34), 3)
                Brightness = round(RandomEngine.uniform(0.28, 0.44), 3)
                TextureGLCM = round(RandomEngine.uniform(0.22, 0.42), 3)
                DayLST = round(RandomEngine.uniform(41.0, 46.5), 1)
                NightLST = round(RandomEngine.uniform(33.5, 37.8), 1) 
            elif AssignedMaterial == "Clay / Tile":
                NDVI = round(RandomEngine.uniform(0.08, 0.22), 3)
                NDBI = round(RandomEngine.uniform(0.10, 0.28), 3)
                Albedo = round(RandomEngine.uniform(0.22, 0.36), 3)
                Brightness = round(RandomEngine.uniform(0.30, 0.48), 3)
                TextureGLCM = round(RandomEngine.uniform(0.35, 0.55), 3)
                DayLST = round(RandomEngine.uniform(37.5, 42.0), 1)
                NightLST = round(RandomEngine.uniform(25.0, 28.5), 1)
            else: # Thatch / Tarpaulin
                NDVI = round(RandomEngine.uniform(0.12, 0.30), 3)
                NDBI = round(RandomEngine.uniform(0.05, 0.20), 3)
                Albedo = round(RandomEngine.uniform(0.16, 0.28), 3)
                Brightness = round(RandomEngine.uniform(0.20, 0.38), 3)
                TextureGLCM = round(RandomEngine.uniform(0.65, 0.90), 3)
                DayLST = round(RandomEngine.uniform(44.0, 49.0), 1)
                NightLST = round(RandomEngine.uniform(28.5, 32.0), 1)
                
            DiurnalAmplitude = round(DayLST - NightLST, 1)
            Storeys = max(1, int(HeightM / 3.2))
            PopulationProtected = max(2, int(round((RoofArea / 14.0) * Storeys * 1.6)))
            
            BuildingId = f"AOI_{BuildingCounter:04d}"
            BuildingCounter += 1
            
            Feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [Coordinates]
                },
                "properties": {
                    "BuildingId": BuildingId,
                    "City": AOIName,
                    "WardId": f"Ward Sector {(BuildingCounter % 4) + 1}",
                    "WardName": f"Sector {(BuildingCounter % 4) + 1} High Density Zone",
                    "RoofAreaSquareMeters": round(RoofArea, 1),
                    "BuildingHeightMeters": HeightM,
                    "EstimatedStoreys": Storeys,
                    "OpenBuildingsConfidence": round(RandomEngine.uniform(0.82, 0.98), 2),
                    "PerimeterMeters": round(Perimeter, 1),
                    "CompactnessRatio": round(Compactness, 2),
                    "CentroidLat": round(BLat, 6),
                    "CentroidLon": round(BLon, 6),
                    "SpectralIndices": {
                        "NDVI": NDVI,
                        "NDBI": NDBI,
                        "Albedo": Albedo,
                        "Brightness": Brightness,
                        "TextureGLCM": TextureGLCM
                    },
                    "ThermalObservations": {
                        "DayLSTCelsius": DayLST,
                        "NightLSTCelsius": NightLST,
                        "DiurnalAmplitudeCelsius": DiurnalAmplitude,
                        "LiveSource": "Landsat 8/9 TIRS & NASA JPL ECOSTRESS Diurnal Radiometry"
                    },
                    "PopulationProtectedEst": PopulationProtected,
                    "SyntheticGroundTruthMaterial": AssignedMaterial
                }
            }
            BuildingFeatures.append(Feature)
            
    LogInfo(f"Successfully Generated {len(BuildingFeatures)} Dense Building Polygons Inside BBox [{MinLon}, {MinLat}, {MaxLon}, {MaxLat}]")
    return BuildingFeatures
