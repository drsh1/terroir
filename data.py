import requests
import pandas as pd
import json
from pathlib import Path

CITIES = [
    {"name": "Lisbon", "country": "Portugal", "lat": 38.7, "lon": -9.1},
    {"name": "Madeira", "country": "Portugal", "lat": 32.6, "lon": -16.9},
    {"name": "Porto", "country": "Portugal", "lat": 41.2, "lon": -8.6},
    {"name": "Seville", "country": "Spain", "lat": 37.4, "lon": -5.9},
    {"name": "Valencia", "country": "Spain", "lat": 39.5, "lon": -0.4},
    {"name": "Barcelona", "country": "Spain", "lat": 41.4, "lon": 2.2},
    {"name": "Madrid", "country": "Spain", "lat": 40.4, "lon": -3.7},
    {"name": "Malaga", "country": "Spain", "lat": 36.7, "lon": -4.4},
    {"name": "Alicante", "country": "Spain", "lat": 38.3, "lon": -0.5},
    {"name": "Las Palmas", "country": "Canary Islands", "lat": 28.1, "lon": -15.4},
    {"name": "Tenerife", "country": "Canary Islands", "lat": 28.3, "lon": -16.6},
    {"name": "Rome", "country": "Italy", "lat": 41.9, "lon": 12.5},
    {"name": "Milan", "country": "Italy", "lat": 45.5, "lon": 9.2},
    {"name": "Palermo", "country": "Italy", "lat": 38.1, "lon": 13.4},
    {"name": "Nice", "country": "France", "lat": 43.7, "lon": 7.3},
    {"name": "Marseille", "country": "France", "lat": 43.3, "lon": 5.4},
    {"name": "Paris", "country": "France", "lat": 48.9, "lon": 2.3},
    {"name": "Athens", "country": "Greece", "lat": 38.0, "lon": 23.7},
    {"name": "Crete", "country": "Greece", "lat": 35.3, "lon": 25.1},
    {"name": "Dubrovnik", "country": "Croatia", "lat": 42.6, "lon": 18.1},
    {"name": "Split", "country": "Croatia", "lat": 43.5, "lon": 16.4},
    {"name": "Valletta", "country": "Malta", "lat": 35.9, "lon": 14.5},
    {"name": "Nicosia", "country": "Cyprus", "lat": 35.2, "lon": 33.4},
    {"name": "Tel Aviv", "country": "Israel", "lat": 32.1, "lon": 34.8},
    {"name": "Dubai", "country": "UAE", "lat": 25.2, "lon": 55.3},
    {"name": "Bangkok", "country": "Thailand", "lat": 13.8, "lon": 100.5},
    {"name": "Chiang Mai", "country": "Thailand", "lat": 18.8, "lon": 98.9},
    {"name": "Bali", "country": "Indonesia", "lat": -8.4, "lon": 115.2},
    {"name": "Singapore", "country": "Singapore", "lat": 1.3, "lon": 103.8},
    {"name": "Tokyo", "country": "Japan", "lat": 35.7, "lon": 139.7},
    {"name": "Osaka", "country": "Japan", "lat": 34.7, "lon": 135.5},
    {"name": "Sydney", "country": "Australia", "lat": -33.9, "lon": 151.2},
    {"name": "Melbourne", "country": "Australia", "lat": -37.8, "lon": 145.0},
    {"name": "Perth", "country": "Australia", "lat": -31.9, "lon": 115.9},
    {"name": "Auckland", "country": "New Zealand", "lat": -36.9, "lon": 174.8},
    {"name": "Cape Town", "country": "South Africa", "lat": -33.9, "lon": 18.4},
    {"name": "Nairobi", "country": "Kenya", "lat": -1.3, "lon": 36.8},
    {"name": "Casablanca", "country": "Morocco", "lat": 33.6, "lon": -7.6},
    {"name": "Agadir", "country": "Morocco", "lat": 30.4, "lon": -9.6},
    {"name": "Cairo", "country": "Egypt", "lat": 30.1, "lon": 31.2},
    {"name": "Tunis", "country": "Tunisia", "lat": 36.8, "lon": 10.2},
    {"name": "Miami", "country": "USA", "lat": 25.8, "lon": -80.2},
    {"name": "Los Angeles", "country": "USA", "lat": 34.1, "lon": -118.2},
    {"name": "San Diego", "country": "USA", "lat": 32.7, "lon": -117.2},
    {"name": "San Francisco", "country": "USA", "lat": 37.8, "lon": -122.4},
    {"name": "Mexico City", "country": "Mexico", "lat": 19.4, "lon": -99.1},
    {"name": "Cancun", "country": "Mexico", "lat": 21.2, "lon": -86.8},
    {"name": "Buenos Aires", "country": "Argentina", "lat": -34.6, "lon": -58.4},
    {"name": "Santiago", "country": "Chile", "lat": -33.5, "lon": -70.6},
    {"name": "Medellin", "country": "Colombia", "lat": 6.2, "lon": -75.6},
    {"name": "Amsterdam", "country": "Netherlands", "lat": 52.4, "lon": 4.9},
    {"name": "Berlin", "country": "Germany", "lat": 52.5, "lon": 13.4},
    {"name": "Munich", "country": "Germany", "lat": 48.1, "lon": 11.6},
    {"name": "Vienna", "country": "Austria", "lat": 48.2, "lon": 16.4},
    {"name": "Prague", "country": "Czech Republic", "lat": 50.1, "lon": 14.4},
    {"name": "Warsaw", "country": "Poland", "lat": 52.2, "lon": 21.0},
    {"name": "Krakow", "country": "Poland", "lat": 50.1, "lon": 20.0},
    {"name": "Istanbul", "country": "Turkey", "lat": 41.0, "lon": 28.9},
    {"name": "Antalya", "country": "Turkey", "lat": 36.9, "lon": 30.7},
    {"name": "Tbilisi", "country": "Georgia", "lat": 41.7, "lon": 44.8},
    {"name": "Yerevan", "country": "Armenia", "lat": 40.2, "lon": 44.5},
    {"name": "Colombo", "country": "Sri Lanka", "lat": 6.9, "lon": 79.9},
    {"name": "Da Nang", "country": "Vietnam", "lat": 16.1, "lon": 108.2},
    {"name": "Ho Chi Minh", "country": "Vietnam", "lat": 10.8, "lon": 106.7},
    {"name": "Kuala Lumpur", "country": "Malaysia", "lat": 3.1, "lon": 101.7},
    {"name": "Montevideo", "country": "Uruguay", "lat": -34.9, "lon": -56.2},
    {"name": "Lisbon", "country": "Portugal", "lat": 38.7, "lon": -9.1},
    {"name": "Funchal", "country": "Portugal", "lat": 32.6, "lon": -16.9},
    {"name": "Valletta", "country": "Malta", "lat": 35.9, "lon": 14.5},
    {"name": "Limassol", "country": "Cyprus", "lat": 34.7, "lon": 33.0},
    {"name": "Bodrum", "country": "Turkey", "lat": 37.0, "lon": 27.4},
    {"name": "Kotor", "country": "Montenegro", "lat": 42.4, "lon": 18.8},
    {"name": "Plovdiv", "country": "Bulgaria", "lat": 42.1, "lon": 24.7},
    {"name": "Varna", "country": "Bulgaria", "lat": 43.2, "lon": 27.9},
]

def fetch_climate(lat: float, lon: float) -> dict:
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": "2020-01-01",
        "end_date": "2023-12-31",
        "daily": [
            "temperature_2m_mean",
            "precipitation_sum",
            "sunshine_duration",
            "relative_humidity_2m_mean",
        ],
        "timezone": "auto",
    }
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    return r.json()

def parse_climate(data: dict) -> dict:
    daily = data["daily"]
    temps = [t for t in daily["temperature_2m_mean"] if t is not None]
    precip = [p for p in daily["precipitation_sum"] if p is not None]
    sunshine = [s for s in daily["sunshine_duration"] if s is not None]
    humidity = [h for h in daily["relative_humidity_2m_mean"] if h is not None]

    avg_temp = round(sum(temps) / len(temps), 1) if temps else None
    total_rain = round(sum(precip) / 4, 0) if precip else None  # średnia roczna
    sunny_days = round(sum(1 for s in sunshine if s > 21600) / 4, 0)  # >6h słońca
    avg_humidity = round(sum(humidity) / len(humidity), 1) if humidity else None

    # amplituda: średnia najcieplejszego miesiąca minus najzimniejszego
    monthly_avgs = []
    for month in range(1, 13):
        month_temps = [
            t for i, t in enumerate(temps)
            if t is not None
        ]
    # uproszczona amplituda
    amplitude = round(max(temps) - min(temps), 1) if temps else None

    return {
        "avg_temp": avg_temp,
        "annual_rain": total_rain,
        "sunny_days": sunny_days,
        "avg_humidity": avg_humidity,
        "temp_amplitude": amplitude,
    }

def build_dataset(output_path: str = "cities.csv"):
    path = Path(output_path)
    results = []

    # usuń duplikaty
    seen = set()
    unique_cities = []
    for c in CITIES:
        key = (c["name"], c["country"])
        if key not in seen:
            seen.add(key)
            unique_cities.append(c)

    print(f"Pobieranie danych dla {len(unique_cities)} miast...")

    for i, city in enumerate(unique_cities):
        print(f"[{i+1}/{len(unique_cities)}] {city['name']}, {city['country']}")
        try:
            raw = fetch_climate(city["lat"], city["lon"])
            climate = parse_climate(raw)
            results.append({**city, **climate})
        except Exception as e:
            print(f"  BŁĄD: {e}")
            results.append({**city, "avg_temp": None, "annual_rain": None,
                           "sunny_days": None, "avg_humidity": None, "temp_amplitude": None})

    df = pd.DataFrame(results)
    df.to_csv(path, index=False)
    print(f"\nGotowe! Zapisano do {path}")
    return df

if __name__ == "__main__":
    build_dataset()