from flask import Flask, render_template, request
import requests

app = Flask(__name__)

NWS_HEADERS = {
    "User-Agent": "myweatherapp.com, contact@myweatherapp.com"
}

def geocode_city(city_name):
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q": city_name,
            "format": "json",
            "limit": 1
        }
        headers = {
            "User-Agent": "myweatherapp.com"
        }
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        if not data:
            return None, None
        return data[0]["lat"], data[0]["lon"]
    except Exception:
        return None, None

def reverse_geocode(lat, lon):
    """Convert lat/lon to nearest city/place name"""
    try:
        url = "https://nominatim.openstreetmap.org/reverse"
        params = {
            "lat": lat,
            "lon": lon,
            "format": "json",
            "zoom": 10,  # city/town level
            "addressdetails": 1
        }
        headers = {
            "User-Agent": "myweatherapp.com"
        }
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        if "address" in data:
            address = data["address"]
            city = address.get("city") or address.get("town") or address.get("village") or address.get("hamlet")
            state = address.get("state")
            country = address.get("country")
            location = ", ".join(filter(None, [city, state, country]))
            return location
        return "Unknown location"
    except Exception:
        return "Unknown location"

@app.route("/", methods=["GET", "POST"])
def index():
    forecast = None
    error = None
    location_name = None
    lat = lon = ""

    if request.method == "POST":
        city = request.form.get("city")
        lat = request.form.get("lat")
        lon = request.form.get("lon")

        if city:
            lat, lon = geocode_city(city)
            if not lat or not lon:
                error = f"Could not find coordinates for city: {city}"

        elif not (lat and lon):
            error = "Please provide a city or both latitude and longitude."

        if not error:
            try:
                # Get location name from coordinates
                location_name = reverse_geocode(lat, lon)

                # Get forecast from NWS
                point_url = f"https://api.weather.gov/points/{lat},{lon}"
                point_resp = requests.get(point_url, headers=NWS_HEADERS)
                point_resp.raise_for_status()
                forecast_url = point_resp.json()["properties"]["forecast"]

                forecast_resp = requests.get(forecast_url, headers=NWS_HEADERS)
                forecast_resp.raise_for_status()
                forecast = forecast_resp.json()["properties"]["periods"]
            except Exception as e:
                error = f"Error fetching forecast: {str(e)}"

    return render_template("index.html", forecast=forecast, error=error,
                           lat=lat, lon=lon, location_name=location_name)

if __name__ == "__main__":
    app.run(debug=True)
