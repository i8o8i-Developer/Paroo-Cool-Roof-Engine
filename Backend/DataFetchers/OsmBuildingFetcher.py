"""
Live OpenStreetMap (OSM) Overpass API Building Footprint Fetcher
Fetches Real Building Polygons, Area, Perimeters, And Centroids For Any Geographic Bounding Box.
"""

import requests
import time
from typing import Dict, List, Any, Optional
from ..Utils.TitleCaseLogger import LogInfo, LogWarning, LogError
from ..Utils.GeoUtils import (
    ComputePolygonCentroid,
    ApproximatePolygonAreaSquareMeters,
    ApproximatePolygonPerimeterMeters,
    ComputeCompactnessRatio
)

OVERPASS_ENDPOINTS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter"
]

class OsmBuildingFetcher:
    """Client To Retrieve Real Building Footprints Via OpenStreetMap Overpass QL."""

    def __init__(self, TimeoutSeconds: float = 2.5):
        LogInfo("Initializing OpenStreetMap Live Building Footprint Ingestion Client")
        self.TimeoutSeconds = TimeoutSeconds

    def FetchBuildingsByBoundingBox(
        self,
        MinLon: float,
        MinLat: float,
        MaxLon: float,
        MaxLat: float,
        MaxBuildingLimit: int = 1024
    ) -> List[Dict[str, Any]]:
        """Query Overpass API To Ingest Real Vector Buildings For A Bounding Box."""
        LogInfo(f"Executing Live Overpass API Query For BBox: [{MinLon}, {MinLat}, {MaxLon}, {MaxLat}]")
        
        # Overpass QL Query String
        OverpassQuery = f"""
        [out:json][timeout:{self.TimeoutSeconds}];
        (
          way["building"]({MinLat},{MinLon},{MaxLat},{MaxLon});
        );
        out body;
        >;
        out skel qt;
        """
        
        ParsedFeatures = []
        RequestSuccess = False
        
        for Endpoint in OVERPASS_ENDPOINTS:
            try:
                LogInfo(f"Connecting To Overpass Endpoint: {Endpoint}")
                Response = requests.post(
                    Endpoint,
                    data={"data": OverpassQuery},
                    timeout=self.TimeoutSeconds,
                    headers={"User-Agent": "PARoo-HeatMitigationEngine/1.0"}
                )
                
                if Response.status_code == 200:
                    Data = Response.json()
                    ParsedFeatures = self._ParseOverpassJSON(Data, MaxBuildingLimit)
                    if ParsedFeatures:
                        LogInfo(f"Successfully Ingested {len(ParsedFeatures)} Real Buildings From OpenStreetMap")
                        RequestSuccess = True
                        break
                else:
                    LogWarning(f"Overpass Endpoint Returned HTTP Status: {Response.status_code}")
            except Exception as Ex:
                LogWarning(f"Overpass Connection Failed On {Endpoint}: {str(Ex)}")
                time.sleep(0.5)
                
        if not RequestSuccess or not ParsedFeatures:
            LogWarning("Live Overpass Query Unreachable Or Empty. Falling Back To High-Resolution Cached Footprints.")
            
        return ParsedFeatures

    def _ParseOverpassJSON(self, Data: Dict[str, Any], MaxLimit: int) -> List[Dict[str, Any]]:
        """Parse Raw OSM Nodes And Ways Into GeoJSON Polygons With Geometric Metrics."""
        Elements = Data.get("elements", [])
        NodesMap: Dict[int, Dict[str, float]] = {}
        Ways: List[Dict[str, Any]] = []
        
        for El in Elements:
            if El["type"] == "node":
                NodesMap[El["id"]] = {"lat": El["lat"], "lon": El["lon"]}
            elif El["type"] == "way":
                Ways.append(El)
                
        Features = []
        BuildingIndex = 1
        
        for Way in Ways:
            NodeIds = Way.get("nodes", [])
            if len(NodeIds) < 3:
                continue
                
            # Build Coordinate Ring
            Ring = []
            ValidRing = True
            for NId in NodeIds:
                if NId in NodesMap:
                    Node = NodesMap[NId]
                    Ring.append([round(Node["lon"], 6), round(Node["lat"], 6)])
                else:
                    ValidRing = False
                    break
                    
            if not ValidRing or len(Ring) < 3:
                continue
                
            # Ensure Ring Is Closed
            if Ring[0] != Ring[-1]:
                Ring.append(Ring[0])
                
            CentroidLat, CentroidLon = ComputePolygonCentroid(Ring)
            RoofArea = ApproximatePolygonAreaSquareMeters(Ring)
            Perimeter = ApproximatePolygonPerimeterMeters(Ring)
            Compactness = ComputeCompactnessRatio(RoofArea, Perimeter)
            
            # Filter Noise/Tiny Fragments
            if RoofArea < 15.0 or RoofArea > 50000.0:
                continue
                
            Tags = Way.get("tags", {})
            BuildingLevels = float(Tags.get("building:levels", 1.0)) if Tags.get("building:levels", "").replace(".", "").isdigit() else 1.0
            BuildingHeight = float(Tags.get("height", BuildingLevels * 3.5)) if Tags.get("height", "").replace(".", "").isdigit() else BuildingLevels * 3.5
            
            BuildingId = f"OSM_BLD_{Way['id']}"
            
            Feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [Ring]
                },
                "properties": {
                    "BuildingId": BuildingId,
                    "CentroidLat": round(CentroidLat, 6),
                    "CentroidLon": round(CentroidLon, 6),
                    "RoofAreaSquareMeters": round(RoofArea, 1),
                    "BuildingHeightMeters": round(BuildingHeight, 1),
                    "EstimatedStoreys": int(BuildingLevels),
                    "CompactnessRatio": round(Compactness, 2),
                    "PerimeterMeters": round(Perimeter, 1),
                    "OpenBuildingsConfidence": 0.95,
                    "OSMTags": Tags
                }
            }
            Features.append(Feature)
            BuildingIndex += 1
            if len(Features) >= MaxLimit:
                break
                
        return Features
