# 🌍 Terroir

> Find the best place to live for you on Earth.

Terroir helps you discover your ideal place to live by matching cities 
worldwide against your personal priorities — climate, geography, lifestyle 
and cost of living.

Most "best places to live" rankings give you someone else's answer. 
Terroir lets you define what matters to you.

## Current features

- Interactive world map with city climate data
- Climate filters: temperature, sunny days, rainfall, humidity
- Scoring system — cities ranked by match quality
- AI-powered search: describe your ideal climate in plain text

## Roadmap

- [ ] Expand to 150+ cities with full climate data
- [ ] Add geography filters: proximity to mountains, sea, city size
- [ ] Cost of living layer
- [ ] Lifestyle filters: air quality, safety, healthcare
- [ ] Weighted scoring — define what matters most to you
- [ ] Snowflake integration

## Tech stack

- Python + Streamlit
- pydeck (deck.gl) for map rendering
- Open-Meteo API for climate data
- Anthropic Claude API for AI features

## Run locally

```bash
python -m venv .venv
.venv\Scripts\activate
pip install streamlit pydeck pandas requests anthropic
streamlit run app.py
```