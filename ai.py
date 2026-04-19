import os
import json
from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

def parse_climate_preferences(user_input: str, df_stats: dict) -> dict:
    prompt = f"""
You are a climate data assistant for an app called Terroir.
A user described their ideal place to live. Your job is to translate 
their description into filter parameters and importance weights for a climate database.

User said: "{user_input}"

The database has these ranges:
- avg_temp: {df_stats['temp_min']}°C to {df_stats['temp_max']}°C (annual average)
- sunny_days: {df_stats['sun_min']} to {df_stats['sun_max']} days per year
- annual_rain: {df_stats['rain_min']} to {df_stats['rain_max']} mm per year
- avg_humidity: {df_stats['hum_min']}% to {df_stats['hum_max']}%

Return ONLY a valid JSON object with these exact keys:
{{
  "temp_min": <number>,
  "temp_max": <number>,
  "sun_min": <number>,
  "sun_max": <number>,
  "rain_min": <number>,
  "rain_max": <number>,
  "hum_min": <number>,
  "hum_max": <number>,
  "weights": {{
    "temp": <0-100>,
    "sun": <0-100>,
    "rain": <0-100>,
    "hum": <0-100>
  }},
  "explanation": "<one sentence explaining your interpretation>"
}}

RULES for weights:
- Sum of weights MUST be 100.
- If user emphasizes a parameter (e.g., "very sunny", "must be warm"), give it a higher weight.
- If user doesn't mention a preference for a parameter, give it an equal share (25).
- If no preferences are mentioned at all, all weights should be 25.

Be generous with ranges — don't make them too narrow.
Return ONLY the JSON, no markdown, no backticks, no extra text.
"""
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    text = response.text.strip()

    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]

    return json.loads(text.strip())