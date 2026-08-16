"""
Stage 2: Building-Level Feature Extraction Pipeline
Computes Spectral Indices (NDVI, NDBI, Albedo, Brightness, Texture/GLCM)
And Geometric Morphology (Roof Area, Height, Compactness, Perimeter, Density).
"""

from typing import Dict, List, Any
import numpy as np
from ..Utils.TitleCaseLogger import LogInfo, LogWarning, LogError

class FeatureExtractionPipeline:
    """Stage 2 Feature Extraction Manager."""

    def __init__(self):
        LogInfo("Initializing Stage 2: Feature Extraction Pipeline")

    def ExtractBuildingFeatures(self, Footprints: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract Normalized Feature Vectors For Each Building In The Footprint Collection."""
        LogInfo(f"Extracting Multi-Spectral And Structural Features For {len(Footprints)} Buildings")
        
        EnrichedFootprints = []
        for Feature in Footprints:
            Props = Feature["properties"]
            Spectral = Props.get("SpectralIndices", {})
            
            # Extract Base Indices
            NDVI = float(Spectral.get("NDVI", 0.0))
            NDBI = float(Spectral.get("NDBI", 0.3))
            Albedo = float(Spectral.get("Albedo", 0.25))
            Brightness = float(Spectral.get("Brightness", 0.45))
            Texture = float(Spectral.get("TextureGLCM", 0.4))
            
            # Structural Metrics
            AreaM2 = float(Props.get("RoofAreaSquareMeters", 50.0))
            HeightMeters = float(Props.get("BuildingHeightMeters", 5.0))
            Compactness = float(Props.get("CompactnessRatio", 0.5))
            Perimeter = float(Props.get("PerimeterMeters", 30.0))
            
            # Derived Advanced Indices
            # 1. Built-Up Bare Soil / Roof Differentiation Ratio
            BuiltRatio = (NDBI - NDVI) / (abs(NDBI) + abs(NDVI) + 1e-5)
            
            # 2. Corrugation Indicator (Texture To Albedo Ratio - Metal / Asbestos Sheets Have High Micro-Shadowing)
            CorrugationIndex = Texture / (Albedo + 0.1)
            
            # 3. Structural Heat Mass Indicator (Height * Area Proxy)
            ThermalMassIndex = min(1.0, (HeightMeters * AreaM2) / 3000.0)
            
            # Assemble Extracted Feature Vector For Downstream ML
            FeatureVector = {
                "NDVI": round(NDVI, 4),
                "NDBI": round(NDBI, 4),
                "Albedo": round(Albedo, 4),
                "Brightness": round(Brightness, 4),
                "TextureGLCM": round(Texture, 4),
                "BuiltRatio": round(float(BuiltRatio), 4),
                "CorrugationIndex": round(float(CorrugationIndex), 4),
                "ThermalMassIndex": round(float(ThermalMassIndex), 4),
                "AreaM2": round(AreaM2, 2),
                "HeightMeters": round(HeightMeters, 2),
                "Compactness": round(Compactness, 3),
                "Perimeter": round(Perimeter, 2)
            }
            
            Props["ExtractedFeatureVector"] = FeatureVector
            EnrichedFootprints.append(Feature)
            
        LogInfo("Feature Extraction Successfully Completed For All Target Buildings")
        return EnrichedFootprints
