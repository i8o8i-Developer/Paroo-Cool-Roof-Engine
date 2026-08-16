"""
Stage 6: Ranking And Municipal Work-Order Generator Pipeline
Ranks Vulnerable Rooftops By Risk Score, Applies Budget/Coverage Constraints,
Calculates High-Albedo Coating Costs In INR, And Exports GeoJSON + CSV Work-Orders.
"""

import io
import csv
from typing import Dict, List, Any, Tuple, Optional
from ..Utils.TitleCaseLogger import LogInfo, LogWarning, LogError

# Coating Cost Rates In Indian Rupees (INR) Per Square Meter
COATING_COST_RATES_INR: Dict[str, float] = {
    "High-Albedo Elastomeric Cool Roof Coating (Dual Coat)": 150.0,
    "Traditional High-Reflectance Lime Wash (Economic)": 80.0,
    "Fibre-Reinforced Solar Reflective Membrane (Asbestos Encapsulation)": 220.0
}

class WorkOrderGenerator:
    """Stage 6 Work-Order And Prioritisation Generator."""

    def __init__(self):
        LogInfo("Initializing Stage 6: Municipal Work-Order Generator")

    def GenerateRankedWorkOrder(
        self,
        ScoredFootprints: List[Dict[str, Any]],
        BudgetLimitINR: Optional[float] = None,
        TargetPopulationLimit: Optional[int] = None,
        PreferredCoatingType: str = "High-Albedo Elastomeric Cool Roof Coating (Dual Coat)"
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """Rank All Buildings, Compute Cost And Population Metrics, And Produce Prioritized Work-Order."""
        LogInfo(f"Generating Ranked Work-Order For {len(ScoredFootprints)} Buildings")
        
        # Sort Buildings By Risk Score Descending
        SortedFeatures = sorted(
            ScoredFootprints,
            key=lambda f: f["properties"].get("RiskScore", 0.0),
            reverse=True
        )
        
        BaseRatePerM2 = COATING_COST_RATES_INR.get(PreferredCoatingType, 150.0)
        
        RankedFeatures = []
        CumulativeCost = 0.0
        CumulativePopulation = 0
        CumulativeArea = 0.0
        
        TotalRank = 1
        for Feature in SortedFeatures:
            Props = Feature["properties"]
            RoofArea = float(Props.get("RoofAreaSquareMeters", 50.0))
            Material = Props.get("PredictedMaterial", "Concrete / RCC")
            PopProtected = int(Props.get("PopulationProtectedEst", 5))
            RiskScore = float(Props.get("RiskScore", 0.5))
            
            # Select Optimal Coating Strategy
            if Material == "Asbestos / Cement":
                # Asbestos Requires Protective Encapsulation Membrane
                CoatingType = "Fibre-Reinforced Solar Reflective Membrane (Asbestos Encapsulation)"
                Rate = COATING_COST_RATES_INR[CoatingType]
                TempReduction = 14.5
            elif Material == "Metal / Tin":
                CoatingType = "High-Albedo Elastomeric Cool Roof Coating (Dual Coat)"
                Rate = COATING_COST_RATES_INR[CoatingType]
                TempReduction = 18.2
            elif Material == "Thatch / Tarpaulin":
                CoatingType = "Traditional High-Reflectance Lime Wash (Economic)"
                Rate = COATING_COST_RATES_INR[CoatingType]
                TempReduction = 11.0
            else:
                CoatingType = PreferredCoatingType
                Rate = BaseRatePerM2
                TempReduction = 12.5
                
            EstimatedCost = round(RoofArea * Rate, 2)
            
            # Check Budget Or Population Optimization Cutoff
            IsWithinBudget = True
            if BudgetLimitINR and (CumulativeCost + EstimatedCost) > BudgetLimitINR:
                IsWithinBudget = False
                
            if IsWithinBudget:
                CumulativeCost += EstimatedCost
                CumulativePopulation += PopProtected
                CumulativeArea += RoofArea
                Props["IncludedInCurrentBudget"] = True
            else:
                Props["IncludedInCurrentBudget"] = False
                
            Props["Rank"] = TotalRank
            Props["EstimatedCostINR"] = EstimatedCost
            Props["RecommendedCoatingType"] = CoatingType
            Props["EstimatedSurfaceTempReductionCelsius"] = TempReduction
            Props["CostPerPersonProtectedINR"] = round(EstimatedCost / max(1, PopProtected), 1)
            Props["CumulativeCostINR"] = round(CumulativeCost, 2)
            Props["CumulativePopulationProtected"] = CumulativePopulation
            
            RankedFeatures.append(Feature)
            TotalRank += 1
            
        BudgetIncludedCount = sum(1 for f in RankedFeatures if f["properties"]["IncludedInCurrentBudget"])
        CostPerPersonOverall = round(CumulativeCost / max(1, CumulativePopulation), 1)
        
        LogInfo(f"Work-Order Prioritisation Complete. Total Buildings: {len(RankedFeatures)}, Funded Under Cap: {BudgetIncludedCount}, Cumulative Protected Population: {CumulativePopulation:,}, Total Cost: INR {CumulativeCost:,.2f}")

        SummaryReport = {
            "TotalBuildingsRanked": len(RankedFeatures),
            "FundedBuildingsCount": BudgetIncludedCount,
            "TotalCumulativeBudgetINR": round(CumulativeCost, 2),
            "TotalPopulationProtected": CumulativePopulation,
            "TotalRoofAreaSquareMeters": round(CumulativeArea, 1),
            "AverageCostPerPersonProtectedINR": CostPerPersonOverall,
            "PreferredCoatingType": PreferredCoatingType
        }
        
        return RankedFeatures, SummaryReport

    def ExportWorkOrderToCSV(self, RankedFeatures: List[Dict[str, Any]], OnlyBudgetIncluded: bool = False) -> str:
        """Export Ranked Work-Order To Formatted Municipal Contractor CSV String."""
        Output = io.StringIO()
        Writer = csv.writer(Output)
        
        # CSV Header Formatted In Title Case
        Header = [
            "Contractor Priority Rank",
            "Building Identifier",
            "Municipality / City",
            "Ward Identifier",
            "Ward Name",
            "Latitude Centroid",
            "Longitude Centroid",
            "Predicted Roof Material",
            "Material Classification Confidence",
            "Composite Heat-Risk Score",
            "Vulnerability Tier",
            "Roof Surface Area (m²)",
            "Recommended Cool-Roof Coating",
            "Estimated Surface Temp Reduction (°C)",
            "Estimated Coating Cost (INR)",
            "Estimated Residents Protected",
            "Cost Per Resident Protected (INR)",
            "Funded In Current Budget Envelope"
        ]
        Writer.writerow(Header)
        
        for Feature in RankedFeatures:
            Props = Feature["properties"]
            if OnlyBudgetIncluded and not Props.get("IncludedInCurrentBudget", True):
                continue
                
            Row = [
                Props.get("Rank", ""),
                Props.get("BuildingId", ""),
                Props.get("City", ""),
                Props.get("WardId", ""),
                Props.get("WardName", ""),
                Props.get("CentroidLat", ""),
                Props.get("CentroidLon", ""),
                Props.get("PredictedMaterial", ""),
                Props.get("MaterialConfidence", ""),
                Props.get("RiskScore", ""),
                Props.get("RiskTier", ""),
                Props.get("RoofAreaSquareMeters", ""),
                Props.get("RecommendedCoatingType", ""),
                Props.get("EstimatedSurfaceTempReductionCelsius", ""),
                Props.get("EstimatedCostINR", ""),
                Props.get("PopulationProtectedEst", ""),
                Props.get("CostPerPersonProtectedINR", ""),
                "Yes" if Props.get("IncludedInCurrentBudget", True) else "No"
            ]
            Writer.writerow(Row)
            
        return Output.getvalue()
