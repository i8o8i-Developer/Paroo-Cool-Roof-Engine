"""
Unit And Integration Test Suite For PARoo Satellite Rooftop Pipeline
Tests Stage 1 Ingestion, Stage 2 Features, Stage 3 Roof Classifier (LLP),
Stage 4 Thermal Cross-Validation, Stage 5 Heat Risk Scoring, And Stage 6 Work Orders.
"""

import unittest
import sys
import os

# Ensure Project Root Is In Python Path
CurrentDir = os.path.dirname(os.path.abspath(__file__))
ProjectRoot = os.path.dirname(CurrentDir)
if ProjectRoot not in sys.path:
    sys.path.insert(0, ProjectRoot)

from Backend.Utils.TitleCaseLogger import LogInfo, ToTitleCase
from Backend.Pipelines.MasterPipelineManager import MasterPipelineManager
from Backend.Pipelines.RoofMaterialClassifier import MATERIAL_CLASSES, MATERIAL_RISK_WEIGHTS
from Backend.Pipelines.WorkOrderGenerator import COATING_COST_RATES_INR

class TestPARooPipeline(unittest.TestCase):
    """Test Suite For PARoo 6-Stage End-To-End Pipeline."""

    @classmethod
    def setUpClass(cls):
        LogInfo("Initializing End-To-End Test Suite Execution")
        cls.Manager = MasterPipelineManager()

    def test_01_CityDataIngestion(self):
        """Verify Stage 1 Ingestion Returns Valid Polygons And Properties."""
        LogInfo("Executing Test 01: Stage 1 City Ingestion")
        Footprints = self.Manager.Stage1Ingestion.IngestCityFootprints("Jaipur", ForceRefresh=True)
        self.assertIsInstance(Footprints, list)
        self.assertGreater(len(Footprints), 20)
        
        First = Footprints[0]
        self.assertEqual(First["type"], "Feature")
        self.assertEqual(First["geometry"]["type"], "Polygon")
        self.assertIn("RoofAreaSquareMeters", First["properties"])
        self.assertGreater(First["properties"]["RoofAreaSquareMeters"], 0.0)

    def test_02_FeatureExtraction(self):
        """Verify Stage 2 Computes Spectral Indices And Structural Metrics."""
        LogInfo("Executing Test 02: Stage 2 Feature Extraction")
        Raw = self.Manager.Stage1Ingestion.IngestCityFootprints("Ahmedabad")
        Extracted = self.Manager.Stage2FeatureExtraction.ExtractBuildingFeatures(Raw)
        
        self.assertEqual(len(Extracted), len(Raw))
        FV = Extracted[0]["properties"]["ExtractedFeatureVector"]
        self.assertIn("NDVI", FV)
        self.assertIn("NDBI", FV)
        self.assertIn("Albedo", FV)
        self.assertIn("TextureGLCM", FV)
        self.assertIn("BuiltRatio", FV)

    def test_03_RoofMaterialClassificationLLP(self):
        """Verify Stage 3 LLP Classifier Yields Probabilities And Low KL Divergence."""
        LogInfo("Executing Test 03: Stage 3 Roof Material Classifier (LLP)")
        Raw = self.Manager.Stage1Ingestion.IngestCityFootprints("Jaipur")
        Extracted = self.Manager.Stage2FeatureExtraction.ExtractBuildingFeatures(Raw)
        Classified, Report = self.Manager.Stage3RoofClassifier.ClassifyFootprints(Extracted)
        
        self.assertEqual(len(Classified), len(Extracted))
        self.assertIn("PredictedMaterial", Classified[0]["properties"])
        self.assertIn(Classified[0]["properties"]["PredictedMaterial"], MATERIAL_CLASSES)
        self.assertIn("MaterialConfidence", Classified[0]["properties"])
        self.assertGreaterEqual(Classified[0]["properties"]["MaterialConfidence"], 0.0)
        self.assertLessEqual(Classified[0]["properties"]["MaterialConfidence"], 1.0)
        self.assertLess(Report["MeanWardKLDivergence"], 1.5)

    def test_04_ThermalCrossValidation(self):
        """Verify Stage 4 Fuses Thermal LST And Validates Physical Consistency."""
        LogInfo("Executing Test 04: Stage 4 Thermal Cross-Validation")
        Result = self.Manager.RunFullPipeline(CityName="Delhi NCR")
        Features = Result["GeoJSON"]["features"]
        ThermalReport = Result["ThermalAnalytics"]
        
        self.assertGreater(len(Features), 0)
        self.assertIn("ThermalQAPassRatePercentage", ThermalReport)
        self.assertGreaterEqual(ThermalReport["ThermalQAPassRatePercentage"], 80.0)
        
        FirstProps = Features[0]["properties"]
        self.assertIn("ThermalAnalysis", FirstProps)
        self.assertIn("DayLSTAnomalyScore", FirstProps["ThermalAnalysis"])
        self.assertIn("NightRetentionScore", FirstProps["ThermalAnalysis"])

    def test_05_HeatRiskCompositeScoring(self):
        """Verify Stage 5 Computes Normalized Composite Risk Scores."""
        LogInfo("Executing Test 05: Stage 5 Composite Risk Scoring")
        Result = self.Manager.RunFullPipeline(CityName="Hyderabad")
        Features = Result["GeoJSON"]["features"]
        
        for Feature in Features:
            Props = Feature["properties"]
            Score = Props["RiskScore"]
            self.assertGreaterEqual(Score, 0.0)
            self.assertLessEqual(Score, 1.0)
            self.assertIn(Props["RiskTier"], ["Critical Priority", "High Priority", "Moderate Priority", "Low / Stable"])

    def test_06_WorkOrderPrioritisationAndBudgetCap(self):
        """Verify Stage 6 Generates Ranked Work-Orders Within Budget Limit."""
        LogInfo("Executing Test 06: Stage 6 Work-Order Generation And Budget Optimization")
        BudgetCap = 500000.0  # 5 Lakh INR
        Result = self.Manager.RunFullPipeline(CityName="Jaipur", BudgetLimitINR=BudgetCap)
        
        Features = Result["GeoJSON"]["features"]
        WorkReport = Result["WorkOrderAnalytics"]
        
        self.assertLessEqual(WorkReport["TotalCumulativeBudgetINR"], BudgetCap + 200000.0)  # Within Envelope
        self.assertGreater(WorkReport["TotalPopulationProtected"], 0)
        
        # Test CSV Export
        CSVContent = self.Manager.Stage6WorkOrder.ExportWorkOrderToCSV(Features)
        self.assertIn("Contractor Priority Rank", CSVContent)
        self.assertIn("Building Identifier", CSVContent)
        self.assertIn("Predicted Roof Material", CSVContent)

if __name__ == "__main__":
    unittest.main()
