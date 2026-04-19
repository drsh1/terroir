---
trigger: always_on
---

# Terroir — project rules

## What is Terroir
Terroir is a Streamlit web app that helps users find their ideal place to live on Earth. It matches cities worldwide against personal climate preferences using real climate data and AI-powered natural language search.

The name comes from the wine concept of "terroir" — the unique character of a place defined by its climate, soil, and geography.

## Current stack
- Python 3.11
- Streamlit — UI framework
- pydeck (deck.gl) — interactive world map
- pandas — data filtering and manipulation
- google-genai — Gemini 2.5 Flash for AI natural language search
- python-dotenv — environment variables
- Open-Meteo API — historical climate data source

## Project structure
terroir/
├── app.py          # main Streamlit app — UI, layout, filtering, scoring
├── ai.py           # Gemini API integration — natural language to filter params
├── data.py         # data fetching from Open-Meteo, builds cities.csv
├── cities.csv      # climate database (~23 complete cities currently)
├── .env            # API keys (never commit)
├── .gitignore
└── README.md

## Data model
Each city in cities.csv has:
- name, country, lat, lon
- avg_temp — average annual temperature (°C)
- sunny_days — days per year with >6h of sunshine
- annual_rain — average annual rainfall (mm)
- avg_humidity — average relative humidity (%)
- temp_amplitude — difference between max and min daily temp

## Architecture principles
- No backend — everything runs in the browser via Streamlit
- @st.cache_data for data loading — never reload CSV on every interaction
- st.session_state for AI results — persist across Streamlit reruns
- AI search sets filter values, manual sliders allow fine-tuning
- Scoring is 0-100, equal weights across 4 parameters currently

## UX flow
1. User lands on app — sees only AI search field, map is empty
2. User describes ideal climate in natural language
3. Gemini interprets description → sets filter parameters
4. Sliders appear with AI-chosen values, user can fine-tune
5. Map shows matching cities colored by score (green/yellow/red)
6. Right panel shows top 10 matches with scores

## Roadmap (planned features)
- Weighted scoring — define what matters most to you
- Expand to 150+ cities with full climate data
- UI / UX
- Add geography filters: proximity to mountains, sea, city size
- Cost of living layer
- Lifestyle filters: air quality, safety, healthcare, food?
- Estethics filters: cultural monuments? architecture style? color of sea / rocks?

## Coding conventions
- English only in code, comments, and commit messages
- Streamlit components in app.py, AI logic in ai.py, data logic in data.py
- Keep functions small and focused
- Always use python-dotenv for API keys, never hardcode
- Commit messages: conventional commits format (feat:, fix:, docs:, refactor:)

## Environment
- Windows 11, VSCode, PowerShell
- Virtual environment: .venv (activate with .venv\Scripts\Activate.ps1)
- Map style: CartoDB dark-matter (no Mapbox token needed)