"""
Stage 5: Multi-Factor Heat-Risk Composite Scoring Engine
Computes Legible, Defensible Multi-Factor Risk Scores With Tunable Weights:
RiskScore = w1*Material_Risk + w2*LST_Anomaly + w3*Night_Retention + w4*Density_Height + w5*Occupancy_Vulnerability
"""

from typing import Dict, List, Any, Tuple, Optional
import numpy as np
from ..Utils.TitleCaseLogger import LogInfo, LogWarning, LogError

DEFAULT_WEIGHTS = {
    "MaterialWeight": 0.30,
    "LSTAnomalyWeight": 0.25,
    "NightRetentionWeight": 0.20,
    "DensityHeightWeight": 0.15,
    "OccupancyWeight": 0.10
}

class HeatRiskScoringEngine:
    """Stage 5 Multi-Factor Heat Risk Scoring Engine."""

    def __init__(self):
        LogInfo("Initializing Stage 5: Heat-Risk Composite Scoring Engine")

    def CalculateRiskScores(
        self,
        Footprints: List[Dict[str, Any]],
        CustomWeights: Optional[Dict[str, float]] = None
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """Compute Composite Multi-Factor Heat Risk Scores And Risk Tiers For All Buildings."""
        Weights = dict(DEFAULT_WEIGHTS)
        if CustomWeights:
            for Key, Val in CustomWeights.items():
                if Key in Weights:
                    Weights[Key] = float(Val)
                    
        # Normalize Weights To Sum To 1.0
        TotalWeight = sum(Weights.values())
        if TotalWeight > 0.001:
            Weights = {K: V / TotalWeight for K, V in Weights.items()}
            
        LogInfo(f"Scoring Risk With Weights: Material={Weights['MaterialWeight']:.2f}, LST={Weights['LSTAnomalyWeight']:.2f}, NightRetention={Weights['NightRetentionWeight']:.2f}, DensityHeight={Weights['DensityHeightWeight']:.2f}, Occupancy={Weights['OccupancyWeight']:.2f}")

        # Compute Population And Height Normalization Maxima
        PopDensities = [float(f["properties"].get("PopulationProtectedEst", 5)) for f in Footprints]
        MaxPop = max(10.0, float(np.percentile(PopDensities, 95)))
        
        Heights = [float(f["properties"].get("BuildingHeightMeters", 5.0)) for f in Footprints]
        MaxHeight = max(15.0, float(np.percentile(Heights, 95)))
        
        ScoredFootprints = []
        RiskScores = []
        
        for Feature in Footprints:
            Props = Feature["properties"]
            Thermals = Props.get("ThermalAnalysis", {})
            
            # Component 1: Material Risk Factor (0 to 1)
            MaterialRisk = float(Props.get("MaterialRiskWeight", 0.50))
            
            # Component 2: LST Anomaly Factor (0 to 1)
            LSTAnomaly = float(Thermals.get("DayLSTAnomalyScore", 0.50))
            
            # Component 3: Night Heat Retention Factor (0 to 1)
            NightRetention = float(Thermals.get("NightRetentionScore", 0.50))
            
            # Component 4: Density & Height Trap Factor (Low Dense Buildings Trap More Ground Heat)
            BuildingHeight = float(Props.get("BuildingHeightMeters", 5.0))
            Compactness = float(Props.get("CompactnessRatio", 0.5))
            # Lower Storeys + Higher Ground Footprint = Higher Density Heat Trap
            HeightFactor = max(0.1, 1.0 - min(1.0, BuildingHeight / MaxHeight))
            DensityHeightFactor = float(np.clip(HeightFactor * 0.7 + (1.0 - Compactness) * 0.3, 0.0, 1.0))
            
            # Component 5: Occupancy Vulnerability Factor (0 to 1)
            PopEst = float(Props.get("PopulationProtectedEst", 5.0))
            OccupancyFactor = float(np.clip(PopEst / MaxPop, 0.0, 1.0))
            
            # Composite Weighted Sum
            CompositeRisk = (
                Weights["MaterialWeight"] * MaterialRisk +
                Weights["LSTAnomalyWeight"] * LSTAnomaly +
                Weights["NightRetentionWeight"] * NightRetention +
                Weights["DensityHeightWeight"] * DensityHeightFactor +
                Weights["OccupancyWeight"] * OccupancyFactor
            )
            
            CompositeRisk = float(np.clip(CompositeRisk, 0.0, 1.0))
            RiskScores.append(CompositeRisk)
            
            # Determine Risk Tier Classification
            if CompositeRisk >= 0.75:
                RiskTier = "Critical Priority"
                RiskColorHex = "#EF4444"  # Neon Red
            elif CompositeRisk >= 0.55:
                RiskTier = "High Priority"
                RiskColorHex = "#F97316"  # Orange
            elif CompositeRisk >= 0.40:
                RiskTier = "Moderate Priority"
                RiskColorHex = "#FBBF24"  # Amber Yellow
            else:
                RiskTier = "Low / Stable"
                RiskColorHex = "#10B981"  # Emerald Green
                
            ScoreBreakdown = {
                "CompositeRiskScore": round(CompositeRisk, 3),
                "RiskTier": RiskTier,
                "RiskColorHex": RiskColorHex,
                "SubScores": {
                    "MaterialRiskComponent": round(MaterialRisk, 3),
                    "LSTAnomalyComponent": round(LSTAnomaly, 3),
                    "NightRetentionComponent": round(NightRetention, 3),
                    "DensityHeightComponent": round(DensityHeightFactor, 3),
                    "OccupancyComponent": round(OccupancyFactor, 3)
                },
                "ActiveWeights": {K: round(V, 3) for K, V in Weights.items()}
            }
            
            Props["HeatRiskAnalysis"] = ScoreBreakdown
            Props["RiskScore"] = round(CompositeRisk, 3)
            Props["RiskTier"] = RiskTier
            ScoredFootprints.append(Feature)
            
        MeanScore = float(np.mean(RiskScores)) if RiskScores else 0.0
        LogInfo(f"Stage 5 Risk Scoring Complete. Mean Risk Score: {round(MeanScore, 3)}")
        
        SummaryReport = {
            "TotalBuildingsScored": len(ScoredFootprints),
            "MeanRiskScore": round(MeanScore, 3),
            "CriticalPriorityCount": sum(1 for f in ScoredFootprints if f["properties"]["RiskTier"] == "Critical Priority"),
            "HighPriorityCount": sum(1 for f in ScoredFootprints if f["properties"]["RiskTier"] == "High Priority"),
            "ModeratePriorityCount": sum(1 for f in ScoredFootprints if f["properties"]["RiskTier"] == "Moderate Priority"),
            "LowPriorityCount": sum(1 for f in ScoredFootprints if f["properties"]["RiskTier"] == "Low / Stable")
        }
        
        return ScoredFootprints, SummaryReport
