"""
Standalone Command Line Interface For PARoo Pipeline
Executes Full End-To-End Heat Vulnerability Prioritisation And Outputs Work-Orders.
"""

import sys
import os
import argparse
import json

# Ensure Project Root Is In Python Path
CurrentDir = os.path.dirname(os.path.abspath(__file__))
if CurrentDir not in sys.path:
    sys.path.insert(0, CurrentDir)

from Backend.Utils.TitleCaseLogger import LogInfo, LogWarning, LogError, ToTitleCase
from Backend.Pipelines.MasterPipelineManager import MasterPipelineManager
from Backend.Data.CityRegistry import CITIES_REGISTRY

def Main():
    """Main Execution Routine For Command Line Interface."""
    Parser = argparse.ArgumentParser(
        description=ToTitleCase("PARoo Satellite Rooftop Heat Vulnerability Prioritisation Engine")
    )
    Parser.add_argument("--City", type=str, default="Jaipur", help=ToTitleCase("Target Indian Municipality Name"))
    Parser.add_argument("--Budget", type=float, default=1000000.0, help=ToTitleCase("Budget Cap In Indian Rupees (INR)"))
    Parser.add_argument("--Coating", type=str, default="High-Albedo Elastomeric Cool Roof Coating (Dual Coat)", help=ToTitleCase("Preferred Coating Type"))
    Parser.add_argument("--ExportCSV", type=str, default=None, help=ToTitleCase("Optional CSV File Path To Export Work Order"))
    Parser.add_argument("--ExportGeoJSON", type=str, default=None, help=ToTitleCase("Optional GeoJSON File Path To Export Footprints"))
    
    Args = Parser.parse_args()
    
    LogInfo(f"Starting PARoo Command Line Engine For City: {Args.City}")
    
    Manager = MasterPipelineManager()
    Result = Manager.RunFullPipeline(
        CityName=Args.City,
        BudgetLimitINR=Args.Budget,
        PreferredCoatingType=Args.Coating
    )
    
    Features = Result["GeoJSON"]["features"]
    WorkAnalytics = Result["WorkOrderAnalytics"]
    ClassifierAnalytics = Result["ClassifierAnalytics"]
    ThermalAnalytics = Result["ThermalAnalytics"]
    RiskAnalytics = Result["RiskScoreAnalytics"]
    
    print("\n" + "=" * 70)
    print(ToTitleCase("PAROO HEAT VULNERABILITY PRIORITISATION SUMMARY REPORT"))
    print("=" * 70)
    print(f"Target Municipality                : {Args.City}")
    print(f"Total Building Footprints Processed : {len(Features):,}")
    print(f"Mean Ward KL-Divergence (LLP Match): {ClassifierAnalytics.get('MeanWardKLDivergence', 0.0):.4f}")
    print(f"Thermal QA Physical Pass Rate       : {ThermalAnalytics.get('ThermalQAPassRatePercentage', 0.0)}%")
    print(f"Critical Priority Hazard Roofs     : {RiskAnalytics.get('CriticalPriorityCount', 0):,}")
    print(f"High Priority Hazard Roofs         : {RiskAnalytics.get('HighPriorityCount', 0):,}")
    print("-" * 70)
    print(ToTitleCase("MUNICIPAL CONTRACTOR BUDGET ALLOCATION"))
    print("-" * 70)
    print(f"Selected Coating Specification      : {Args.Coating}")
    print(f"Total Budget Envelope Allocated    : INR {WorkAnalytics.get('TotalCumulativeBudgetINR', 0.0):,.2f}")
    print(f"Number Of Roofs Funded Under Cap   : {WorkAnalytics.get('FundedBuildingsCount', 0):,} / {len(Features):,}")
    print(f"Total Population Directly Protected: {WorkAnalytics.get('TotalPopulationProtected', 0):,} Residents")
    print(f"Total Reflective Roof Area Coated  : {WorkAnalytics.get('TotalRoofAreaSquareMeters', 0.0):,.1f} m²")
    print(f"Average Cost Per Resident Protected: INR {WorkAnalytics.get('AverageCostPerPersonProtectedINR', 0.0):.2f}")
    print("=" * 70 + "\n")
    
    if Args.ExportCSV:
        CSVData = Manager.Stage6WorkOrder.ExportWorkOrderToCSV(Features, OnlyBudgetIncluded=False)
        with open(Args.ExportCSV, "w", encoding="utf-8") as F:
            F.write(CSVData)
        LogInfo(f"Successfully Exported Contractor Work Order CSV To: {Args.ExportCSV}")
        
    if Args.ExportGeoJSON:
        with open(Args.ExportGeoJSON, "w", encoding="utf-8") as F:
            json.dump(Result["GeoJSON"], F, indent=2)
        LogInfo(f"Successfully Exported Ranked GeoJSON To: {Args.ExportGeoJSON}")

if __name__ == "__main__":
    Main()
