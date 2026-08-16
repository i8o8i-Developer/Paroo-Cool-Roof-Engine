"""
Stage 4: Thermal Cross-Validation And Diurnal Heat Dynamics Engine
Fuses Day/Night Landsat And ECOSTRESS LST Observations At Building Centroids,
Computes Diurnal Amplitude And Night Heat Retention Anomalies,
And Performs Physical Thermal Consistency Verification.
"""

from typing import Dict, List, Any, Tuple
import numpy as np
from ..Utils.TitleCaseLogger import LogInfo, LogWarning, LogError

class ThermalCrossValidation:
    """Stage 4 Thermal Cross-Validation And Heat Retention Engine."""

    def __init__(self):
        LogInfo("Initializing Stage 4: Thermal Cross-Validation Engine")

    def ProcessThermalObservations(self, Footprints: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """Compute Diurnal Thermal Dynamics, Ward Heat Anomalies, And QA Physical Consistency Checks."""
        LogInfo(f"Executing Thermal Cross-Validation On {len(Footprints)} Buildings")
        
        # Step 1: Collect Ward-Level Thermal Baselines
        WardDayLSTs: Dict[str, List[float]] = {}
        WardNightLSTs: Dict[str, List[float]] = {}
        
        for Feature in Footprints:
            Props = Feature["properties"]
            WardId = Props.get("WardId", "GeneralWard")
            Thermals = Props.get("ThermalObservations", {})
            DayLST = float(Thermals.get("DayLSTCelsius", 45.0))
            NightLST = float(Thermals.get("NightLSTCelsius", 30.0))
            
            if WardId not in WardDayLSTs:
                WardDayLSTs[WardId] = []
                WardNightLSTs[WardId] = []
                
            WardDayLSTs[WardId].append(DayLST)
            WardNightLSTs[WardId].append(NightLST)
            
        WardStats: Dict[str, Dict[str, float]] = {}
        for WardId in WardDayLSTs:
            DayArr = np.array(WardDayLSTs[WardId])
            NightArr = np.array(WardNightLSTs[WardId])
            WardStats[WardId] = {
                "MeanDayLST": float(np.mean(DayArr)),
                "StdDayLST": float(np.std(DayArr)) + 1e-4,
                "MeanNightLST": float(np.mean(NightArr)),
                "StdNightLST": float(np.std(NightArr)) + 1e-4
            }
            
        # Step 2: Calculate Standardized LST Anomalies And Physical QA Checks
        ThermalConsistentCount = 0
        HighNightRetentionCount = 0
        EnrichedFootprints = []
        
        for Feature in Footprints:
            Props = Feature["properties"]
            WardId = Props.get("WardId", "GeneralWard")
            Stats = WardStats.get(WardId, {
                "MeanDayLST": 45.0, "StdDayLST": 2.0, "MeanNightLST": 30.0, "StdNightLST": 1.5
            })
            
            Thermals = Props.get("ThermalObservations", {})
            DayLST = float(Thermals.get("DayLSTCelsius", 45.0))
            NightLST = float(Thermals.get("NightLSTCelsius", 30.0))
            DiurnalAmplitude = float(Thermals.get("DiurnalAmplitudeCelsius", DayLST - NightLST))
            
            # Standardized LST Anomaly Z-Score: (Building LST - Ward Mean LST) / Ward Std
            DayLSTAnomalyZ = (DayLST - Stats["MeanDayLST"]) / Stats["StdDayLST"]
            NightLSTAnomalyZ = (NightLST - Stats["MeanNightLST"]) / Stats["StdNightLST"]
            
            # Normalized 0-1 Anomaly Indices
            DayLSTAnomalyNorm = float(np.clip(1.0 / (1.0 + np.exp(-DayLSTAnomalyZ)), 0.0, 1.0))
            NightRetentionNorm = float(np.clip(1.0 / (1.0 + np.exp(-NightLSTAnomalyZ)), 0.0, 1.0))
            
            # Thermal QA Sanity Check (Physical Consistency Check)
            PredictedMaterial = Props.get("PredictedMaterial", "Concrete / RCC")
            QAMismatchFlag = False
            QADiagnostic = "Thermal Signature Consistent With Material Physics"
            
            # Metal / Tin Expected To Have High Diurnal Amplitude And High Day Temperature
            if PredictedMaterial == "Metal / Tin" and DiurnalAmplitude < 7.0:
                QAMismatchFlag = True
                QADiagnostic = "Low Diurnal Swing For Metal Roof (Check For Tree Canopy Or Super-Insulation)"
            # Concrete Expected To Have High Night Retention
            elif PredictedMaterial == "Concrete / RCC" and NightLSTAnomalyZ < -1.8:
                QAMismatchFlag = True
                QADiagnostic = "Unusually Low Night Heat For Concrete Mass"
            elif NightLSTAnomalyZ > 1.2:
                HighNightRetentionCount += 1
                QADiagnostic = "Severe Nocturnal Heat Trapping Zone"
                
            if not QAMismatchFlag:
                ThermalConsistentCount += 1
                
            ThermalAnalysis = {
                "DayLSTCelsius": DayLST,
                "NightLSTCelsius": NightLST,
                "DiurnalAmplitudeCelsius": DiurnalAmplitude,
                "DayLSTAnomalyScore": round(DayLSTAnomalyNorm, 3),
                "NightRetentionScore": round(NightRetentionNorm, 3),
                "WardMeanDayLST": round(Stats["MeanDayLST"], 1),
                "WardMeanNightLST": round(Stats["MeanNightLST"], 1),
                "ThermalQAPass": not QAMismatchFlag,
                "ThermalQADiagnostic": QADiagnostic
            }
            
            Props["ThermalAnalysis"] = ThermalAnalysis
            EnrichedFootprints.append(Feature)
            
        QAPassRate = round((ThermalConsistentCount / max(1, len(Footprints))) * 100.0, 1)
        LogInfo(f"Thermal Cross-Validation Complete. QA Physical Consistency Rate: {QAPassRate}%")
        
        SummaryReport = {
            "TotalBuildingsProcessed": len(Footprints),
            "ThermalQAPassRatePercentage": QAPassRate,
            "HighNightRetentionRoofsCount": HighNightRetentionCount,
            "WardThermalBaselines": WardStats
        }
        
        return EnrichedFootprints, SummaryReport
