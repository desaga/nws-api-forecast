# nws-api-forecast
# 🌤️ Weather Forecast App (USA, NWS API)
### https://open-meteo.com/en/docs

A simple Flask-based web application that provides a 7-day weather forecast using the [National Weather Service API](https://www.weather.gov/documentation/services-web-api).  
Users can get forecasts by:

- Entering a city name
- Selecting coordinates on an interactive map
- Using their current location (via browser geolocation)

---

## 🚀 Features

- 📍 Interactive Leaflet map to pick any U.S. location
- 🏙️ City geocoding via OpenStreetMap (Nominatim)
- 📡 Real-time 7-day forecast from [weather.gov](https://api.weather.gov)
- 🔁 Reverse geocoding to show nearest known city or place
- 🖥️ Responsive and mobile-friendly UI with Bootstrap
- 📌 “Use My Location” button with automatic forecast submission
- 🌐 “View on Map” (opens Google Maps)

---

## 🛠️ Tech Stack

- **Python 3**
- **Flask**
- **HTML / Bootstrap 5**
- **Leaflet.js**
- **OpenStreetMap / Nominatim API**
- **weather.gov API**

---

## 📦 Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/nws-api-forecast.git
cd nws-api-forecast
```
### 2. (Optional) Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
### 3. Install dependencies
pip install -r requirements.txt
### 4. Run the app
python main.py

### 🌍 APIs Used
Weather data: National Weather Service API
Geocoding & Reverse geocoding: Nominatim (OpenStreetMap)

### License

This project is open-source and available under the MIT License.
