"""
Geospatial Utilities Module For PARoo Rooftop Vulnerability Engine
"""

import math
from typing import Dict, List, Any, Tuple
from shapely.geometry import Polygon, MultiPolygon, Point, mapping, shape
from .TitleCaseLogger import LogInfo, LogWarning, LogError

def ComputePolygonCentroid(Coordinates: List[List[float]]) -> Tuple[float, float]:
    """Compute The Centroid Latitude And Longitude Of A Polygon Coordinate Ring."""
    try:
        Poly = Polygon(Coordinates)
        Centroid = Poly.centroid
        return (Centroid.y, Centroid.x)  # (Lat, Lon)
    except Exception as Ex:
        LogError(f"Failed To Compute Centroid: {str(Ex)}")
        # Fallback Arithmetic Average
        Lats = [Coord[1] for Coord in Coordinates]
        Lons = [Coord[0] for Coord in Coordinates]
        return (sum(Lats) / len(Lats), sum(Lons) / len(Lons))

def ApproximatePolygonAreaSquareMeters(Coordinates: List[List[float]]) -> float:
    """Approximate Area Of Polygon In Square Meters Given WGS84 Longitude / Latitude Ring."""
    try:
        Poly = Polygon(Coordinates)
        CentroidLat = Poly.centroid.y
        # 1 Degree Latitude ~ 111,139 Meters
        # 1 Degree Longitude ~ 111,139 * Cos(Latitude Radians) Meters
        LatScale = 111139.0
        LonScale = 111139.0 * math.cos(math.radians(CentroidLat))
        
        # Scale Coordinates To Metric Plane
        MetricCoords = [(Point[0] * LonScale, Point[1] * LatScale) for Point in Coordinates]
        MetricPoly = Polygon(MetricCoords)
        return abs(float(MetricPoly.area))
    except Exception as Ex:
        LogWarning(f"Error Computing Area Square Meters: {str(Ex)}")
        return 50.0

def ApproximatePolygonPerimeterMeters(Coordinates: List[List[float]]) -> float:
    """Approximate Perimeter Length In Meters Given WGS84 Ring."""
    try:
        Poly = Polygon(Coordinates)
        CentroidLat = Poly.centroid.y
        LatScale = 111139.0
        LonScale = 111139.0 * math.cos(math.radians(CentroidLat))
        
        MetricCoords = [(Point[0] * LonScale, Point[1] * LatScale) for Point in Coordinates]
        MetricPoly = Polygon(MetricCoords)
        return abs(float(MetricPoly.length))
    except Exception as Ex:
        LogWarning(f"Error Computing Perimeter Meters: {str(Ex)}")
        return 30.0

def ComputeCompactnessRatio(AreaSquareMeters: float, PerimeterMeters: float) -> float:
    """Compute Isoperimetric Compactness Ratio (4 * Pi * Area / Perimeter^2)."""
    if PerimeterMeters <= 0.001:
        return 0.5
    Compactness = (4.0 * math.pi * AreaSquareMeters) / (PerimeterMeters ** 2)
    return min(1.0, max(0.05, float(Compactness)))

def CreateBoundingBoxPolygon(MinLon: float, MinLat: float, MaxLon: float, MaxLat: float) -> Polygon:
    """Create A Bounding Box Polygon From Coordinates."""
    return Polygon([
        (MinLon, MinLat),
        (MaxLon, MinLat),
        (MaxLon, MaxLat),
        (MinLon, MaxLat),
        (MinLon, MinLat)
    ])

def ConvertFeatureCollectionToGeoJSON(Features: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Wrap List Of GeoJSON Features Into A Standard GeoJSON FeatureCollection."""
    return {
        "type": "FeatureCollection",
        "features": Features
    }
