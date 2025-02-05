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


# Step 5: Extract & Display Zoning and Historic District Data
def extract_zoning_data(zone_response, zone_label_response, historic_response):
    zoning_data = {}

    if "features" in zone_response:
        for feature in zone_response["features"]:
            attributes = feature.get("attributes", {})
            zoning_data["Zone District"] = attributes.get("District", "Not Available")

    if "features" in zone_label_response:
        for feature in zone_label_response["features"]:
            attributes = feature.get("attributes", {})
            zoning_data["Specific Zoning Label"] = attributes.get("Zoning_Label", "Not Available")

    if "features" in historic_response:
        for feature in historic_response["features"]:
            attributes = feature.get("attributes", {})
            zoning_data["Historic District"] = attributes.get("HistDistrict_NAME", "No Historic District")

    return zoning_data


# Example Usage
if __name__ == "__main__":
    address = "1729 T St NW, Washington, DC"
    lat, lon = geocode_address(address)
    if lat and lon:
        print(f"Coordinates: {lat}, {lon}")
        zone_info = get_zone_district(lat, lon)
        zone_label_info = get_zone_label(lat, lon)
        historic_info = get_historic_district(lat, lon)

        if zone_info and zone_label_info and historic_info:
            zoning_data = extract_zoning_data(zone_info, zone_label_info, historic_info)
            print("Zoning Information:", json.dumps(zoning_data, indent=2))
        else:
            print("Zoning or Historic data not found.")
    else:
        print("Failed to geocode address.")