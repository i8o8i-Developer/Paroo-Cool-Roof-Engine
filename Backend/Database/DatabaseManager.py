"""
Database Manager DAO For PARoo Geospatial Production Pipeline
Handles Persistence, Spatial Queries, Bulk Ingestion, And Joins For All Stages.
"""

import json
from typing import Dict, List, Any, Optional, Tuple
from ..Utils.TitleCaseLogger import LogInfo, LogWarning, LogError
from .DatabaseEngine import GetDatabaseCursor, GetDatabaseConnection
from .DatabaseModels import InitializeDatabaseSchema

class DatabaseManager:
    """Production Data Access Object For Spatial Rooftop Heat Vulnerability Engine."""

    def __init__(self):
        LogInfo("Initializing Database Manager DAO")
        InitializeDatabaseSchema()

    def SeedCityAndWards(self, CityConfig: Dict[str, Any]) -> None:
        """Upsert City Metadata And Associated Census Wards Into The Database."""
        CityName = CityConfig["CityName"]
        try:
            with GetDatabaseCursor() as Cursor:
                Cursor.execute("""
                    INSERT INTO Cities (
                        CityName, StateName, CenterLat, CenterLon, DefaultZoom,
                        BoundingBoxJSON, BaselineMaxSummerLST, NightRetentionBaseline,
                        TotalPopulation, ClimateZone
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(CityName) DO UPDATE SET
                        StateName=excluded.StateName,
                        CenterLat=excluded.CenterLat,
                        CenterLon=excluded.CenterLon,
                        DefaultZoom=excluded.DefaultZoom,
                        BoundingBoxJSON=excluded.BoundingBoxJSON,
                        BaselineMaxSummerLST=excluded.BaselineMaxSummerLST,
                        NightRetentionBaseline=excluded.NightRetentionBaseline,
                        TotalPopulation=excluded.TotalPopulation,
                        ClimateZone=excluded.ClimateZone;
                """, (
                    CityName,
                    CityConfig["StateName"],
                    CityConfig["CenterLat"],
                    CityConfig["CenterLon"],
                    CityConfig["DefaultZoom"],
                    json.dumps(CityConfig["BoundingBox"]),
                    CityConfig["BaselineMaxSummerLST"],
                    CityConfig["NightRetentionBaseline"],
                    CityConfig["TotalPopulation"],
                    CityConfig["ClimateZone"]
                ))
                
                # Upsert Wards
                for Ward in CityConfig.get("Wards", []):
                    Proportions = Ward.get("CensusRoofProportions", {})
                    Cursor.execute("""
                        INSERT INTO CensusWards (
                            WardId, CityName, WardName, MetalProportion, AsbestosProportion,
                            ConcreteProportion, TileProportion, ThatchProportion,
                            PopulationDensityPerHectare
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ON CONFLICT(WardId) DO UPDATE SET
                            WardName=excluded.WardName,
                            MetalProportion=excluded.MetalProportion,
                            AsbestosProportion=excluded.AsbestosProportion,
                            ConcreteProportion=excluded.ConcreteProportion,
                            TileProportion=excluded.TileProportion,
                            ThatchProportion=excluded.ThatchProportion,
                            PopulationDensityPerHectare=excluded.PopulationDensityPerHectare;
                    """, (
                        Ward["WardId"],
                        CityName,
                        Ward["WardName"],
                        Proportions.get("Metal / Tin", 0.2),
                        Proportions.get("Asbestos / Cement", 0.2),
                        Proportions.get("Concrete / RCC", 0.4),
                        Proportions.get("Clay / Tile", 0.1),
                        Proportions.get("Thatch / Tarpaulin", 0.05),
                        Ward.get("PopulationDensityPerHectare", 300.0)
                    ))
            LogInfo(f"Seeded City And Wards For {CityName}")
        except Exception as Ex:
            LogError(f"Failed To Seed City {CityName}: {str(Ex)}")
            raise Ex

    def BulkSaveProcessedFootprints(self, Footprints: List[Dict[str, Any]]) -> None:
        """Persist Complete Enriched Footprints, Spectral Vectors, Thermal Data, Predictions, And Scores."""
        if not Footprints:
            return
            
        LogInfo(f"Persisting {len(Footprints)} Processed Buildings To Database")
        try:
            with GetDatabaseCursor() as Cursor:
                # Ensure All Referenced Cities And Wards Exist
                ReferencedCities = set()
                ReferencedWards = set()
                for Feature in Footprints:
                    City = Feature["properties"].get("City", "Custom AOI")
                    Ward = Feature["properties"].get("WardId", "DefaultWard")
                    WardName = Feature["properties"].get("WardName", "Default Ward")
                    
                    if City not in ReferencedCities:
                        Cursor.execute("""
                            INSERT INTO Cities (
                                CityName, StateName, CenterLat, CenterLon, DefaultZoom,
                                BoundingBoxJSON, BaselineMaxSummerLST, NightRetentionBaseline,
                                TotalPopulation, ClimateZone
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            ON CONFLICT(CityName) DO NOTHING;
                        """, (City, "India", Feature["properties"].get("CentroidLat", 26.9), Feature["properties"].get("CentroidLon", 75.8), 14, "[]", 45.0, 30.0, 1000000, "Semi-Arid"))
                        ReferencedCities.add(City)
                        
                    if Ward not in ReferencedWards:
                        Cursor.execute("""
                            INSERT INTO CensusWards (
                                WardId, CityName, WardName, MetalProportion, AsbestosProportion,
                                ConcreteProportion, TileProportion, ThatchProportion, PopulationDensityPerHectare
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                            ON CONFLICT(WardId) DO NOTHING;
                        """, (Ward, City, WardName, 0.3, 0.25, 0.3, 0.1, 0.05, 300.0))
                        ReferencedWards.add(Ward)
                for Feature in Footprints:
                    Props = Feature["properties"]
                    BuildingId = Props["BuildingId"]
                    CityName = Props.get("City", "Jaipur")
                    WardId = Props.get("WardId", "DefaultWard")
                    
                    # 1. Buildings Table
                    Cursor.execute("""
                        INSERT INTO Buildings (
                            BuildingId, CityName, WardId, CentroidLat, CentroidLon,
                            PolygonCoordinatesJSON, RoofAreaSquareMeters, BuildingHeightMeters,
                            EstimatedStoreys, CompactnessRatio, PerimeterMeters, OpenBuildingsConfidence
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ON CONFLICT(BuildingId) DO UPDATE SET
                            CentroidLat=excluded.CentroidLat,
                            CentroidLon=excluded.CentroidLon,
                            PolygonCoordinatesJSON=excluded.PolygonCoordinatesJSON,
                            RoofAreaSquareMeters=excluded.RoofAreaSquareMeters,
                            BuildingHeightMeters=excluded.BuildingHeightMeters,
                            EstimatedStoreys=excluded.EstimatedStoreys,
                            CompactnessRatio=excluded.CompactnessRatio,
                            PerimeterMeters=excluded.PerimeterMeters,
                            OpenBuildingsConfidence=excluded.OpenBuildingsConfidence;
                    """, (
                        BuildingId,
                        CityName,
                        WardId,
                        Props["CentroidLat"],
                        Props["CentroidLon"],
                        json.dumps(Feature["geometry"]["coordinates"]),
                        Props["RoofAreaSquareMeters"],
                        Props.get("BuildingHeightMeters", 5.0),
                        Props.get("EstimatedStoreys", 1),
                        Props.get("CompactnessRatio", 0.5),
                        Props.get("PerimeterMeters", 30.0),
                        Props.get("OpenBuildingsConfidence", 0.85)
                    ))
                    
                    # 2. Spectral Features Table
                    FV = Props.get("ExtractedFeatureVector", {})
                    Cursor.execute("""
                        INSERT INTO SpectralFeatures (
                            BuildingId, NDVI, NDBI, Albedo, Brightness, TextureGLCM,
                            BuiltRatio, CorrugationIndex, ThermalMassIndex
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ON CONFLICT(BuildingId) DO UPDATE SET
                            NDVI=excluded.NDVI,
                            NDBI=excluded.NDBI,
                            Albedo=excluded.Albedo,
                            Brightness=excluded.Brightness,
                            TextureGLCM=excluded.TextureGLCM,
                            BuiltRatio=excluded.BuiltRatio,
                            CorrugationIndex=excluded.CorrugationIndex,
                            ThermalMassIndex=excluded.ThermalMassIndex;
                    """, (
                        BuildingId,
                        FV.get("NDVI", 0.0),
                        FV.get("NDBI", 0.0),
                        FV.get("Albedo", 0.25),
                        FV.get("Brightness", 0.45),
                        FV.get("TextureGLCM", 0.4),
                        FV.get("BuiltRatio", 0.0),
                        FV.get("CorrugationIndex", 1.0),
                        FV.get("ThermalMassIndex", 0.5)
                    ))
                    
                    # 3. Thermal Observations Table
                    Thermals = Props.get("ThermalAnalysis", {})
                    Obs = Props.get("ThermalObservations", {})
                    Cursor.execute("""
                        INSERT INTO ThermalObservations (
                            BuildingId, DayLSTCelsius, NightLSTCelsius, DiurnalAmplitudeCelsius,
                            DayLSTAnomalyScore, NightRetentionScore, ThermalQAPass, ThermalQADiagnostic
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        ON CONFLICT(BuildingId) DO UPDATE SET
                            DayLSTCelsius=excluded.DayLSTCelsius,
                            NightLSTCelsius=excluded.NightLSTCelsius,
                            DiurnalAmplitudeCelsius=excluded.DiurnalAmplitudeCelsius,
                            DayLSTAnomalyScore=excluded.DayLSTAnomalyScore,
                            NightRetentionScore=excluded.NightRetentionScore,
                            ThermalQAPass=excluded.ThermalQAPass,
                            ThermalQADiagnostic=excluded.ThermalQADiagnostic;
                    """, (
                        BuildingId,
                        Obs.get("DayLSTCelsius", 45.0),
                        Obs.get("NightLSTCelsius", 30.0),
                        Obs.get("DiurnalAmplitudeCelsius", 15.0),
                        Thermals.get("DayLSTAnomalyScore", 0.5),
                        Thermals.get("NightRetentionScore", 0.5),
                        1 if Thermals.get("ThermalQAPass", True) else 0,
                        Thermals.get("ThermalQADiagnostic", "Consistent")
                    ))
                    
                    # 4. Roof Material Predictions Table
                    Cursor.execute("""
                        INSERT INTO RoofMaterialPredictions (
                            BuildingId, PredictedMaterial, MaterialConfidence, MaterialRiskWeight,
                            SoftProbabilitiesJSON
                        ) VALUES (?, ?, ?, ?, ?)
                        ON CONFLICT(BuildingId) DO UPDATE SET
                            PredictedMaterial=excluded.PredictedMaterial,
                            MaterialConfidence=excluded.MaterialConfidence,
                            MaterialRiskWeight=excluded.MaterialRiskWeight,
                            SoftProbabilitiesJSON=excluded.SoftProbabilitiesJSON;
                    """, (
                        BuildingId,
                        Props.get("PredictedMaterial", "Concrete / RCC"),
                        Props.get("MaterialConfidence", 0.75),
                        Props.get("MaterialRiskWeight", 0.5),
                        json.dumps(Props.get("MaterialSoftProbabilities", {}))
                    ))
                    
                    # 5. Heat Risk Scores Table
                    RiskAnalysis = Props.get("HeatRiskAnalysis", {})
                    Cursor.execute("""
                        INSERT INTO HeatRiskScores (
                            BuildingId, CompositeRiskScore, RiskTier, RiskColorHex,
                            SubScoresJSON, ActiveWeightsJSON
                        ) VALUES (?, ?, ?, ?, ?, ?)
                        ON CONFLICT(BuildingId) DO UPDATE SET
                            CompositeRiskScore=excluded.CompositeRiskScore,
                            RiskTier=excluded.RiskTier,
                            RiskColorHex=excluded.RiskColorHex,
                            SubScoresJSON=excluded.SubScoresJSON,
                            ActiveWeightsJSON=excluded.ActiveWeightsJSON;
                    """, (
                        BuildingId,
                        Props.get("RiskScore", 0.5),
                        Props.get("RiskTier", "Moderate Priority"),
                        RiskAnalysis.get("RiskColorHex", "#FBBF24"),
                        json.dumps(RiskAnalysis.get("SubScores", {})),
                        json.dumps(RiskAnalysis.get("ActiveWeights", {}))
                    ))
                    
                    # 6. Contractor Work Orders Table
                    Cursor.execute("""
                        INSERT INTO ContractorWorkOrders (
                            BuildingId, PriorityRank, EstimatedCostINR, RecommendedCoatingType,
                            EstimatedSurfaceTempReductionCelsius, PopulationProtectedEst,
                            CostPerPersonProtectedINR, IncludedInCurrentBudget
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        ON CONFLICT(BuildingId) DO UPDATE SET
                            PriorityRank=excluded.PriorityRank,
                            EstimatedCostINR=excluded.EstimatedCostINR,
                            RecommendedCoatingType=excluded.RecommendedCoatingType,
                            EstimatedSurfaceTempReductionCelsius=excluded.EstimatedSurfaceTempReductionCelsius,
                            PopulationProtectedEst=excluded.PopulationProtectedEst,
                            CostPerPersonProtectedINR=excluded.CostPerPersonProtectedINR,
                            IncludedInCurrentBudget=excluded.IncludedInCurrentBudget;
                    """, (
                        BuildingId,
                        Props.get("Rank", 1),
                        Props.get("EstimatedCostINR", 5000.0),
                        Props.get("RecommendedCoatingType", "High-Albedo Elastomeric"),
                        Props.get("EstimatedSurfaceTempReductionCelsius", 15.0),
                        Props.get("PopulationProtectedEst", 5),
                        Props.get("CostPerPersonProtectedINR", 1000.0),
                        1 if Props.get("IncludedInCurrentBudget", True) else 0
                    ))
            LogInfo(f"Successfully Persisted {len(Footprints)} Buildings To Relational Database")
        except Exception as Ex:
            LogError(f"Database Bulk Save Failed: {str(Ex)}")
            raise Ex

    def GetCityFootprintsAsGeoJSON(self, CityName: str) -> List[Dict[str, Any]]:
        """Query Relational Database And Reconstruct Complete GeoJSON Feature List."""
        LogInfo(f"Querying Database For City: {CityName}")
        QuerySQL = """
            SELECT 
                b.BuildingId, b.CityName, b.WardId, b.CentroidLat, b.CentroidLon,
                b.PolygonCoordinatesJSON, b.RoofAreaSquareMeters, b.BuildingHeightMeters,
                b.EstimatedStoreys, b.CompactnessRatio, b.PerimeterMeters, b.OpenBuildingsConfidence,
                w.WardName,
                s.NDVI, s.NDBI, s.Albedo, s.Brightness, s.TextureGLCM, s.BuiltRatio, s.CorrugationIndex, s.ThermalMassIndex,
                t.DayLSTCelsius, t.NightLSTCelsius, t.DiurnalAmplitudeCelsius, t.DayLSTAnomalyScore, t.NightRetentionScore, t.ThermalQAPass, t.ThermalQADiagnostic,
                m.PredictedMaterial, m.MaterialConfidence, m.MaterialRiskWeight, m.SoftProbabilitiesJSON,
                r.CompositeRiskScore, r.RiskTier, r.RiskColorHex, r.SubScoresJSON, r.ActiveWeightsJSON,
                c.PriorityRank, c.EstimatedCostINR, c.RecommendedCoatingType, c.EstimatedSurfaceTempReductionCelsius, c.PopulationProtectedEst, c.CostPerPersonProtectedINR, c.IncludedInCurrentBudget
            FROM Buildings b
            LEFT JOIN CensusWards w ON b.WardId = w.WardId
            LEFT JOIN SpectralFeatures s ON b.BuildingId = s.BuildingId
            LEFT JOIN ThermalObservations t ON b.BuildingId = t.BuildingId
            LEFT JOIN RoofMaterialPredictions m ON b.BuildingId = m.BuildingId
            LEFT JOIN HeatRiskScores r ON b.BuildingId = r.BuildingId
            LEFT JOIN ContractorWorkOrders c ON b.BuildingId = c.BuildingId
            WHERE b.CityName = ?
            ORDER BY c.PriorityRank ASC;
        """
        
        Conn = GetDatabaseConnection()
        Cursor = Conn.cursor()
        Cursor.execute(QuerySQL, (CityName,))
        Rows = Cursor.fetchall()
        
        Features = []
        for Row in Rows:
            Coords = json.loads(Row["PolygonCoordinatesJSON"])
            SoftProbs = json.loads(Row["SoftProbabilitiesJSON"]) if Row["SoftProbabilitiesJSON"] else {}
            SubScores = json.loads(Row["SubScoresJSON"]) if Row["SubScoresJSON"] else {}
            ActiveWeights = json.loads(Row["ActiveWeightsJSON"]) if Row["ActiveWeightsJSON"] else {}
            
            Feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": Coords
                },
                "properties": {
                    "BuildingId": Row["BuildingId"],
                    "City": Row["CityName"],
                    "WardId": Row["WardId"],
                    "WardName": Row["WardName"] or Row["WardId"],
                    "CentroidLat": Row["CentroidLat"],
                    "CentroidLon": Row["CentroidLon"],
                    "RoofAreaSquareMeters": Row["RoofAreaSquareMeters"],
                    "BuildingHeightMeters": Row["BuildingHeightMeters"],
                    "EstimatedStoreys": Row["EstimatedStoreys"],
                    "CompactnessRatio": Row["CompactnessRatio"],
                    "PerimeterMeters": Row["PerimeterMeters"],
                    "OpenBuildingsConfidence": Row["OpenBuildingsConfidence"],
                    "SpectralIndices": {
                        "NDVI": Row["NDVI"],
                        "NDBI": Row["NDBI"],
                        "Albedo": Row["Albedo"],
                        "Brightness": Row["Brightness"],
                        "TextureGLCM": Row["TextureGLCM"]
                    },
                    "ExtractedFeatureVector": {
                        "NDVI": Row["NDVI"],
                        "NDBI": Row["NDBI"],
                        "Albedo": Row["Albedo"],
                        "Brightness": Row["Brightness"],
                        "TextureGLCM": Row["TextureGLCM"],
                        "BuiltRatio": Row["BuiltRatio"],
                        "CorrugationIndex": Row["CorrugationIndex"],
                        "ThermalMassIndex": Row["ThermalMassIndex"],
                        "AreaM2": Row["RoofAreaSquareMeters"],
                        "HeightMeters": Row["BuildingHeightMeters"],
                        "Compactness": Row["CompactnessRatio"],
                        "Perimeter": Row["PerimeterMeters"]
                    },
                    "ThermalObservations": {
                        "DayLSTCelsius": Row["DayLSTCelsius"],
                        "NightLSTCelsius": Row["NightLSTCelsius"],
                        "DiurnalAmplitudeCelsius": Row["DiurnalAmplitudeCelsius"]
                    },
                    "ThermalAnalysis": {
                        "DayLSTCelsius": Row["DayLSTCelsius"],
                        "NightLSTCelsius": Row["NightLSTCelsius"],
                        "DiurnalAmplitudeCelsius": Row["DiurnalAmplitudeCelsius"],
                        "DayLSTAnomalyScore": Row["DayLSTAnomalyScore"],
                        "NightRetentionScore": Row["NightRetentionScore"],
                        "ThermalQAPass": bool(Row["ThermalQAPass"]),
                        "ThermalQADiagnostic": Row["ThermalQADiagnostic"]
                    },
                    "PredictedMaterial": Row["PredictedMaterial"],
                    "MaterialConfidence": Row["MaterialConfidence"],
                    "MaterialRiskWeight": Row["MaterialRiskWeight"],
                    "MaterialSoftProbabilities": SoftProbs,
                    "RiskScore": Row["CompositeRiskScore"],
                    "RiskTier": Row["RiskTier"],
                    "HeatRiskAnalysis": {
                        "CompositeRiskScore": Row["CompositeRiskScore"],
                        "RiskTier": Row["RiskTier"],
                        "RiskColorHex": Row["RiskColorHex"],
                        "SubScores": SubScores,
                        "ActiveWeights": ActiveWeights
                    },
                    "Rank": Row["PriorityRank"],
                    "EstimatedCostINR": Row["EstimatedCostINR"],
                    "RecommendedCoatingType": Row["RecommendedCoatingType"],
                    "EstimatedSurfaceTempReductionCelsius": Row["EstimatedSurfaceTempReductionCelsius"],
                    "PopulationProtectedEst": Row["PopulationProtectedEst"],
                    "CostPerPersonProtectedINR": Row["CostPerPersonProtectedINR"],
                    "IncludedInCurrentBudget": bool(Row["IncludedInCurrentBudget"])
                }
            }
            Features.append(Feature)
            
        Cursor.close()
        Conn.close()
        LogInfo(f"Loaded {len(Features)} Buildings From Database For {CityName}")
        return Features
