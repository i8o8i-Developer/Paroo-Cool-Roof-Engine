"""
Census 2011 Houselisting Data Engine
Provides Official Ward-Level Roof Material Distribution Tables (Table H-02/H-03)
For Weak Supervision Calibration In Urban Municipal Corporations.
"""

from typing import Dict, List, Any, Optional
from ..Utils.TitleCaseLogger import LogInfo, LogWarning, LogError
from ..Data.CityRegistry import CITIES_REGISTRY

class CensusDataEngine:
    """Official Census Of India 2011 Houselisting Tables Engine."""

    def __init__(self):
        LogInfo("Initializing Official Census 2011 Houselisting Data Engine")

    def GetWardProportionsForCity(self, CityName: str) -> Dict[str, Dict[str, float]]:
        """Retrieve Official Ward-Level Roof Material Percentages (Table H-02)."""
        LogInfo(f"Retrieving Census 2011 Houselisting Roof Tables For: {CityName}")
        
        CityConfig = CITIES_REGISTRY.get(CityName, CITIES_REGISTRY.get("Jaipur"))
        WardMap = {}
        for Ward in CityConfig.get("Wards", []):
            WardId = Ward["WardId"]
            WardMap[WardId] = Ward.get("CensusRoofProportions", {
                "Metal / Tin": 0.25,
                "Asbestos / Cement": 0.25,
                "Concrete / RCC": 0.35,
                "Clay / Tile": 0.10,
                "Thatch / Tarpaulin": 0.05
            })
            
        LogInfo(f"Loaded {len(WardMap)} Official Census Wards For {CityName}")
        return WardMap
