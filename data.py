import requests
import pandas as pd
import numpy as np
import json
from pathlib import Path
import time
import openmeteo_requests
import requests_cache
from retry_requests import retry

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after = -1)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

def get_top_cities(limit=50):
    """Fetch the largest cities from OpenDataSoft (GeoNames) public API."""
    print(f"Fetching list of {limit} largest cities in the world...")
    url = f"https://public.opendatasoft.com/api/explore/v2.1/catalog/datasets/geonames-all-cities-with-a-population-1000/exports/json?limit={limit}&order_by=population%20DESC"
    
    try:
        r = requests.get(url, timeout=20)
        r.raise_for_status()
        data = r.json()
        
        cities = []
        for item in data:
            name = item.get('ascii_name') or item.get('name')
            country = item.get('cou_name_en') or item.get('country_code', 'Unknown')
            coords = item.get('coordinates')
            
            if name and coords:
                lat = coords.get('lat') if isinstance(coords, dict) else coords[0]
                lon = coords.get('lon') if isinstance(coords, dict) else coords[1]
                cities.append({
                    "name": name,
                    "country": country,
                    "lat": float(lat),
                    "lon": float(lon)
                })
                
        if cities:
            print(f"Successfully fetched {len(cities)} cities.")
            return cities
            
    except Exception as e:
        print(f"Error fetching cities from API: {e}")
        
    print("Failed to fetch city list. Aborting.")
    return []

def fetch_and_parse_climate(lat: float, lon: float) -> dict:
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": "2025-01-01",
        "end_date": "2025-12-31",
        "daily": [
            "temperature_2m_max",
            "temperature_2m_min",
            "temperature_2m_mean",
            "precipitation_sum",
            "rain_sum",
            "snowfall_sum",
            "sunshine_duration",
            "wind_speed_10m_max",
            "relative_humidity_2m_mean"
        ],
        "timezone": "auto",
    }
    
    max_retries = 3
    response = None
    for attempt in range(max_retries):
        try:
            responses = openmeteo.weather_api(url, params=params)
            response = responses[0]
            break
        except Exception as e:
            err_msg = str(e)
            if "Minutely API request limit exceeded" in err_msg and attempt < max_retries - 1:
                print(f"    API limit reached. Waiting 65 seconds... (attempt {attempt+1}/{max_retries})")
                time.sleep(65)
                continue
            raise e

    daily = response.Daily()

    t_max = daily.Variables(0).ValuesAsNumpy()
    t_min = daily.Variables(1).ValuesAsNumpy()
    t_mean = daily.Variables(2).ValuesAsNumpy()
    # precipitation_sum (3) is not used directly but must be fetched to keep index alignment
    rain = daily.Variables(4).ValuesAsNumpy()
    snow = daily.Variables(5).ValuesAsNumpy()
    sunshine = daily.Variables(6).ValuesAsNumpy()
    wind_max = daily.Variables(7).ValuesAsNumpy()
    humidity = daily.Variables(8).ValuesAsNumpy()

    # Filter NaNs (Open-Meteo returns them for missing data)
    valid_mask = ~np.isnan(t_mean)
    if not np.any(valid_mask):
        raise ValueError("No climate data available for these coordinates")

    t_max = t_max[valid_mask]
    t_min = t_min[valid_mask]
    t_mean = t_mean[valid_mask]
    rain = rain[valid_mask]
    snow = snow[valid_mask]
    sunshine = sunshine[valid_mask]
    wind_max = wind_max[valid_mask]
    humidity = humidity[valid_mask]

    # As 2025 is complete (current date is 2026), we use raw sums without scaling.
    
    avg_temp = round(float(np.mean(t_mean)), 1)
    total_rain = round(float(np.sum(rain)), 0)
    total_snow = round(float(np.sum(snow)), 0) # in cm

    sunny_days = int(np.sum(sunshine > 21600)) # > 6h
    rain_days = int(np.sum(rain > 1.0)) # > 1mm
    snow_days = int(np.sum(snow > 1.0)) # > 1cm
    
    hot_days = int(np.sum(t_max > 30.0))
    frost_days = int(np.sum(t_min < 0.0))
    
    windy_days = int(np.sum(wind_max > 30.0)) # > 30km/h
    muggy_days = int(np.sum((t_max > 25.0) & (humidity > 70.0)))

    avg_humidity = round(float(np.mean(humidity)), 1)
    
    # Seasonality as standard deviation of temperatures
    temp_seasonality = round(float(np.std(t_mean)), 1)
    
    # Amplitude (difference between the hottest and coldest daily mean in the year)
    temp_amplitude = round(float(np.max(t_mean) - np.min(t_mean)), 1) 

    return {
        "avg_temp": avg_temp,
        "annual_rain": total_rain,
        "annual_snow": total_snow,
        "rain_days": rain_days,
        "snow_days": snow_days,
        "sunny_days": sunny_days,
        "hot_days": hot_days,
        "frost_days": frost_days,
        "windy_days": windy_days,
        "muggy_days": muggy_days,
        "avg_humidity": avg_humidity,
        "temp_seasonality": temp_seasonality,
        "temp_amplitude": temp_amplitude,
    }

def build_dataset(output_path: str = "cities.csv"):
    path = Path(output_path)
    results = []

    # Fetch top 50 cities
    cities_to_process = get_top_cities(50)

    # Remove duplicates
    seen = set()
    unique_cities = []
    for c in cities_to_process:
        key = (c["name"], c["country"])
        if key not in seen:
            seen.add(key)
            unique_cities.append(c)

    print(f"Fetching climate data for {len(unique_cities)} cities...")

    for i, city in enumerate(unique_cities):
        print(f"[{i+1}/{len(unique_cities)}] {city['name']}, {city['country']}")
        try:
            climate = fetch_and_parse_climate(city["lat"], city["lon"])
            results.append({**city, **climate})
        except Exception as e:
            print(f"  ERROR: {e}")
            results.append({**city, "avg_temp": None, "annual_rain": None,
                           "annual_snow": None, "rain_days": None, "snow_days": None,
                           "sunny_days": None, "hot_days": None, "frost_days": None,
                           "windy_days": None, "muggy_days": None, "avg_humidity": None,
                           "temp_seasonality": None, "temp_amplitude": None})
            
        # Protect against API minutely limits (0.5s is roughly 120 req/min)
        time.sleep(0.5)

    df = pd.DataFrame(results)
    df.to_csv(path, index=False)
    print(f"\nDone! Dataset saved to {path}")
    return df

if __name__ == "__main__":
    build_dataset()