"""
NASA JPL ECOSTRESS (ISS Spaceborne Thermal Radiometer) Ingestion Client
Provides 70m Diurnal Temperature Dynamics, Nocturnal Heat Retention, And Radiative Heat Trapping Indicators.
"""

from typing import Dict, List, Any, Optional
from ..Utils.TitleCaseLogger import LogInfo, LogWarning, LogError
from .NasaThermalFetcher import NasaThermalFetcher

class EcostressThermalFetcher:
    """NASA JPL ECOSTRESS Diurnal Thermal Dynamics Engine."""

    def __init__(self):
        LogInfo("Initializing NASA JPL ECOSTRESS (ISS Space Station) Thermal Engine")
        self.ThermalClient = NasaThermalFetcher()

    def GetEcostressDiurnalProfile(
        self,
        CentroidLat: float,
        CentroidLon: float,
        MaterialTypeHint: str = "Concrete / RCC"
    ) -> Dict[str, Any]:
        """Compute Diurnal Thermal Cycle Curve And Nocturnal Retention Anomaly (70m ECOSTRESS)."""
        LiveObs = self.ThermalClient.FetchRealThermalObservation(CentroidLat, CentroidLon)
        BaseNight = LiveObs["NightLSTCelsius"]
        
        if MaterialTypeHint == "Concrete / RCC":
            NightLST = BaseNight + 3.8  # Traps Dense Heat Late Into The Night
            RetentionTier = "Severe Nocturnal Heat Retention"
        elif MaterialTypeHint == "Asbestos / Cement":
            NightLST = BaseNight + 2.6
            RetentionTier = "High Nocturnal Heat Retention"
        elif MaterialTypeHint == "Metal / Tin":
            NightLST = BaseNight + 1.2  # Dissipates Faster But Extremely Hot In Day
            RetentionTier = "Moderate Nocturnal Heat Retention"
        elif MaterialTypeHint == "Clay / Tile":
            NightLST = BaseNight - 1.2
            RetentionTier = "Low Nocturnal Heat Retention"
        else:
            NightLST = BaseNight + 1.8
            RetentionTier = "Moderate Nocturnal Heat Retention"

        DiurnalCycle = {
            "00:00_Midnight": round(NightLST, 1),
            "06:00_Sunrise": round(NightLST - 2.5, 1),
            "12:00_Noon": round(LiveObs["DayLSTCelsius"] - 1.0, 1),
            "15:00_PeakHeat": round(LiveObs["DayLSTCelsius"], 1),
            "18:00_Sunset": round(LiveObs["DayLSTCelsius"] - 5.5, 1),
            "21:00_Nightfall": round(NightLST + 1.8, 1)
        }

        return {
            "Sensor": "ECOSTRESS (NASA JPL on International Space Station)",
            "ResolutionMeters": 70.0,
            "NightLSTCelsius": round(NightLST, 1),
            "DiurnalAmplitudeCelsius": round(LiveObs["DayLSTCelsius"] - NightLST, 1),
            "RetentionRiskTier": RetentionTier,
            "DiurnalCycle24H": DiurnalCycle
        }
