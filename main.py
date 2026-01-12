from flask import Flask, render_template, request
import requests
from datetime import datetime

app = Flask(__name__)

NWS_HEADERS = {
    "User-Agent": "myweatherapp.com, contact@myweatherapp.com"
}

WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    56: "Light freezing drizzle",
    57: "Dense freezing drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Light freezing rain",
    67: "Heavy freezing rain",
    71: "Slight snow fall",
    73: "Moderate snow fall",
    75: "Heavy snow fall",
    77: "Snow grains",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm (slight or moderate)",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail"
}

def normalize_longitude(lon):
    return ((lon + 180) % 360 + 360) % 360 - 180

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
        return float(data[0]["lat"]), float(data[0]["lon"])
    except Exception:
        return None, None


def reverse_geocode(lat, lon):
    try:
        url = "https://nominatim.openstreetmap.org/reverse"
        params = {
            "lat": lat,
            "lon": lon,
            "format": "json",
            "zoom": 10,
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
            city = address.get("city") or address.get("town") or address.get(
                "village") or address.get("hamlet")
            state = address.get("state")
            country = address.get("country")
            location = ", ".join(filter(None, [city, state, country]))
            return location
        return "Unknown location"
    except Exception:
        return "Unknown location"


def get_forecast_open_meteo(lat, lon):
    try:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "daily": "temperature_2m_max,temperature_2m_min,weathercode,wind_speed_10m_max,wind_direction_10m_dominant,surface_pressure_mean",
            "timezone": "auto"
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()["daily"]
    except Exception as e:
        print(f"Open-Meteo error: {e}")
        return None


def format_date_label(date_str):
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return dt.strftime("%a, %b %d")
    except Exception:
        return date_str


@app.route("/", methods=["GET", "POST"])
def index():
    forecast = None
    error = None
    location_name = None
    lat = lon = ""
    source = None

    if request.method == "POST":
        city = request.form.get("city")
        lat = request.form.get("lat")
        lon = request.form.get("lon")

        if city:
            lat, lon = geocode_city(city)
            if not lat or not lon:
                error = f"Could not find coordinates for city: {city}"
        elif lat and lon:
            try:
                lat = float(lat)
                lon = float(lon)
                lon = normalize_longitude(lon)
            except ValueError:
                error = "Invalid coordinates provided."
        else:
            error = "Please provide a city or both latitude and longitude."

        if not error:
            try:
                location_name = reverse_geocode(lat, lon)

                try:
                    # Try NWS (only US)
                    point_url = f"https://api.weather.gov/points/{lat},{lon}"
                    point_resp = requests.get(point_url, headers=NWS_HEADERS)
                    point_resp.raise_for_status()

                    forecast_url = point_resp.json()["properties"]["forecast"]
                    forecast_resp = requests.get(forecast_url,
                                                 headers=NWS_HEADERS)
                    forecast_resp.raise_for_status()
                    source = {
                        "name": "National Weather Service (USA)",
                        "url": "https://www.weather.gov/"
                    }
                    forecast = forecast_resp.json()["properties"]["periods"]

                except Exception as nws_error:
                    print(f"NWS failed, switching to Open-Meteo: {nws_error}")
                    # Fallback: Open-Meteo
                    daily_data = get_forecast_open_meteo(lat, lon)
                    if daily_data:
                        source = {
                            "name": "Open-Meteo",
                            "url": "https://open-meteo.com/"
                        }
                        forecast = []
                        for i in range(len(daily_data["time"])):
                            pressure_mmHg = round(
                                daily_data["surface_pressure_mean"][
                                    i] * 0.75006)
                            forecast.append({
                                "name": format_date_label(
                                    daily_data["time"][i]),
                                "temperature": f"{daily_data['temperature_2m_max'][i]}° / {daily_data['temperature_2m_min'][i]}°",
                                "temperatureUnit": "C",
                                "detailedForecast": WEATHER_CODES.get(
                                    daily_data['weathercode'][i],
                                    f"Code {daily_data['weathercode'][i]}"
                                ),
                                "windSpeed": f"{daily_data['wind_speed_10m_max'][i]} km/h",
                                "windDirection": f"{daily_data['wind_direction_10m_dominant'][i]}°",
                                "pressure": f"{pressure_mmHg} mmHg"
                            })
                    else:
                        error = "Could not get forecast from any source."

            except Exception as e:
                error = f"Unexpected error: {str(e)}"

    return render_template("index.html", forecast=forecast, error=error,
                           lat=lat, lon=lon, location_name=location_name, source=source)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
