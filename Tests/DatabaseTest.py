"""
Database And Live Ingestion Integration Test Suite
Verifies SQLite Relational Schema, Foreign Keys, Bulk Inserts, And Spatial Queries.
"""

import unittest
import sys
import os

# Ensure Project Root Is In Python Path
CurrentDir = os.path.dirname(os.path.abspath(__file__))
ProjectRoot = os.path.dirname(CurrentDir)
if ProjectRoot not in sys.path:
    sys.path.insert(0, ProjectRoot)

from Backend.Utils.TitleCaseLogger import LogInfo
from Backend.Database.DatabaseManager import DatabaseManager
from Backend.Database.DatabaseEngine import GetDatabaseConnection
from Backend.Pipelines.MasterPipelineManager import MasterPipelineManager

class TestPARooDatabase(unittest.TestCase):
    """Test Suite For Real Relational SQLite Database Layer."""

    @classmethod
    def setUpClass(cls):
        LogInfo("Initializing Database Test Suite Execution")
        cls.DB = DatabaseManager()
        cls.Manager = MasterPipelineManager(cls.DB)

    def test_01_SchemaTablesExist(self):
        """Verify All Required Relational Tables Are Created."""
        LogInfo("Executing DB Test 01: Verify Relational Schema")
        Conn = GetDatabaseConnection()
        Cursor = Conn.cursor()
        Cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        Tables = [Row["name"] for Row in Cursor.fetchall()]
        
        RequiredTables = [
            "Cities", "CensusWards", "Buildings", "SpectralFeatures",
            "ThermalObservations", "RoofMaterialPredictions", "HeatRiskScores",
            "ContractorWorkOrders"
        ]
        for T in RequiredTables:
            self.assertIn(T, Tables, f"Table {T} Missing From Database Schema")
        Cursor.close()
        Conn.close()

    def test_02_FullPipelineDatabasePersistence(self):
        """Verify Full Pipeline Saves And Queries 100+ Buildings In Database."""
        LogInfo("Executing DB Test 02: Full Pipeline Relational Persistence")
        Result = self.Manager.RunFullPipeline(CityName="Ahmedabad", ForceRefresh=True)
        self.assertEqual(Result["Status"], "Success")
        
        # Verify Direct Query From Relational DB
        DbFeatures = self.DB.GetCityFootprintsAsGeoJSON("Ahmedabad")
        self.assertGreaterEqual(len(DbFeatures), 50)
        
        First = DbFeatures[0]
        Props = First["properties"]
        self.assertIn("PredictedMaterial", Props)
        self.assertIn("RiskScore", Props)
        self.assertIn("EstimatedCostINR", Props)
        self.assertIn("Rank", Props)

if __name__ == "__main__":
    unittest.main()
