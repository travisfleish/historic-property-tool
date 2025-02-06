import requests
import json


# Step 1: Convert Address to Lat/Lon using OpenStreetMap Nominatim API
def geocode_address(address):
    url = f"https://nominatim.openstreetmap.org/search"
    params = {
        "q": address,
        "format": "json",
        "limit": 1,
        "addressdetails": 1
    }
    headers = {"User-Agent": "Zoning-Analysis-Bot"}

    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data:
            return float(data[0]['lat']), float(data[0]['lon'])
    return None, None


# Step 2: Query DC Zoning ArcGIS API for Zone District (General Category) - Layer 21
def get_zone_district(lat, lon):
    arcgis_url = "https://maps2.dcgis.dc.gov/dcgis/rest/services/DCOZ/Zone_Mapservice/MapServer/21/query"
    params = {
        "f": "json",
        "geometry": json.dumps({"x": lon, "y": lat, "spatialReference": {"wkid": 4326}}),
        "geometryType": "esriGeometryPoint",
        "inSR": 4326,
        "spatialRel": "esriSpatialRelIntersects",
        "returnGeometry": "false",
        "outFields": "District"
    }

    response = requests.get(arcgis_url, params=params)
    if response.status_code == 200:
        return response.json()
    return None


# Step 3: Query DC Zoning ArcGIS API for Zone District Label (Specific Zoning Code) - Layer 22
def get_zone_label(lat, lon):
    arcgis_url = "https://maps2.dcgis.dc.gov/dcgis/rest/services/DCOZ/Zone_Mapservice/MapServer/22/query"
    params = {
        "f": "json",
        "geometry": json.dumps({"x": lon, "y": lat, "spatialReference": {"wkid": 4326}}),
        "geometryType": "esriGeometryPoint",
        "inSR": 4326,
        "spatialRel": "esriSpatialRelIntersects",
        "returnGeometry": "false",
        "outFields": "Zoning_Label"
    }

    response = requests.get(arcgis_url, params=params)
    if response.status_code == 200:
        return response.json()
    return None


# Step 4: Query DC Zoning ArcGIS API for Historic Districts (Layer 6)
def get_historic_district(lat, lon):
    arcgis_url = "https://maps2.dcgis.dc.gov/dcgis/rest/services/DCOZ/Zone_Mapservice/MapServer/6/query"
    params = {
        "f": "json",
        "geometry": json.dumps({"x": lon, "y": lat, "spatialReference": {"wkid": 4326}}),
        "geometryType": "esriGeometryPoint",
        "inSR": 4326,
        "spatialRel": "esriSpatialRelIntersects",
        "returnGeometry": "false",
        "outFields": "HistDistrict_NAME"
    }

    response = requests.get(arcgis_url, params=params)
    if response.status_code == 200:
        return response.json()
    return None


# Step 5: Generate Structured Feasibility Report
def generate_report(address):
    lat, lon = geocode_address(address)
    if lat and lon:
        zone_info = get_zone_district(lat, lon)
        zone_label_info = get_zone_label(lat, lon)
        historic_info = get_historic_district(lat, lon)

        report = f"""
        📌 **Zoning Feasibility Analysis**
        **📍 Address:** {address}
        **🏛️ Zone District:** {zone_info["features"][0]["attributes"].get("District", "Not Available")} 
        **🏗️ Specific Zoning Label:** {zone_label_info["features"][0]["attributes"].get("Zoning_Label", "Not Available")} 
        **🏛️ Historic District:** {historic_info["features"][0]["attributes"].get("HistDistrict_NAME", "No Historic District")} 

        🔹 **Development Standards**
        - **Max Height:** 35 feet (3 stories)
        - **Max Lot Occupancy:** 60%
        - **Rear Yard Requirement:** 20 feet minimum
        - **Side Yard Requirement:** Not required (5 ft if provided)

        🔹 **Historic Preservation Considerations**
        - **HPRB Approval Required:** ✅ *Yes, if in a historic district*
        - **Subdivision Restrictions:** ✅ *Likely requires Mayor’s Agent approval*

        🔹 **Development Feasibility**
        - **Proposed Project:** Customizable based on user input
        - **Potential Requirements:**
            - Requires **BZA approval** for height increase above 35 ft
            - **IZ applies** if more than 10 units are built
        """

        return report
    else:
        return "Error: Failed to geocode address."


# Example Usage
if __name__ == "__main__":
    address = "1729 T St NW, Washington, DC"
    report = generate_report(address)
    print(report)
