import streamlit as st
import pandas as pd
import pydeck as pdk
from ai import parse_climate_preferences

st.set_page_config(
    page_title="Terroir",
    page_icon="🌍",
    layout="wide"
)

@st.cache_data
def load_data():
    df = pd.read_csv("cities.csv")
    df = df.dropna(subset=["avg_temp", "sunny_days", "annual_rain", "avg_humidity"])
    df["sunny_days"] = df["sunny_days"].astype(int)
    df["annual_rain"] = df["annual_rain"].astype(int)
    return df

df = load_data()

# --- SIDEBAR ---
st.sidebar.title("🌍 Terroir")
st.sidebar.caption("Find the best place to live for you on Earth.")
st.sidebar.divider()

# --- AI SEARCH ---
st.sidebar.subheader("✨ AI search")

ai_input = st.sidebar.text_area(
    "Describe your ideal place to live",
    placeholder="e.g. I love warm sunny summers, mild winters, not too humid, don't mind some rain...",
    height=120
)

if st.sidebar.button("Find my place", type="primary"):
    if ai_input.strip():
        with st.spinner("Analysing your preferences..."):
            try:
                df_stats = {
                    "temp_min": int(df.avg_temp.min()),
                    "temp_max": int(df.avg_temp.max()),
                    "sun_min": int(df.sunny_days.min()),
                    "sun_max": int(df.sunny_days.max()),
                    "rain_min": int(df.annual_rain.min()),
                    "rain_max": int(df.annual_rain.max()),
                    "hum_min": int(df.avg_humidity.min()),
                    "hum_max": int(df.avg_humidity.max()),
                }
                result = parse_climate_preferences(ai_input, df_stats)
                st.session_state["ai_result"] = result
                
                # Reset weight sliders in session state to AI-suggested values
                # PATTERN: Explicit State Reset for Interactive Components
                if "weights" in result:
                    st.session_state["w_temp"] = result["weights"].get("temp", 25)
                    st.session_state["w_sun"] = result["weights"].get("sun", 25)
                    st.session_state["w_rain"] = result["weights"].get("rain", 25)
                    st.session_state["w_hum"] = result["weights"].get("hum", 25)
            except Exception as e:
                st.sidebar.error(f"Error: {e}")
    else:
        st.sidebar.warning("Please describe your ideal climate first.")

ai = st.session_state.get("ai_result", {})

if ai:
    st.sidebar.success(ai["explanation"])
    st.sidebar.divider()
    st.sidebar.subheader("Fine-tune results")
    
    ai_weights = ai.get("weights", {"temp": 25, "sun": 25, "rain": 25, "hum": 25})

    # --- TEMPERATURE ---
    st.sidebar.markdown("##### 🌡 Temperature")
    c1, c2 = st.sidebar.columns([2, 1])
    with c1:
        temp_min, temp_max = st.slider(
            "Range (°C)", -10, 40,
            (ai.get("temp_min", int(df.avg_temp.min())), ai.get("temp_max", int(df.avg_temp.max()))),
            key="temp_range"
        )
    with c2:
        w_temp = st.slider("Weight (0-100)", 0, 100, ai_weights.get("temp", 25), key="w_temp")

    # --- SUNSHINE ---
    st.sidebar.markdown("##### ☀️ Sunshine")
    c1, c2 = st.sidebar.columns([2, 1])
    with c1:
        sun_min, sun_max = st.slider(
            "Days per year", 0, 365,
            (ai.get("sun_min", int(df.sunny_days.min())), ai.get("sun_max", int(df.sunny_days.max()))),
            key="sun_range"
        )
    with c2:
        w_sun = st.slider("Weight (0-100)", 0, 100, ai_weights.get("sun", 25), key="w_sun")

    # --- RAINFALL ---
    st.sidebar.markdown("##### 🌧 Rainfall")
    c1, c2 = st.sidebar.columns([2, 1])
    with c1:
        rain_min, rain_max = st.slider(
            "Annual (mm)", 0, 3000,
            (ai.get("rain_min", int(df.annual_rain.min())), ai.get("rain_max", int(df.annual_rain.max()))),
            key="rain_range"
        )
    with c2:
        w_rain = st.slider("Weight (0-100)", 0, 100, ai_weights.get("rain", 25), key="w_rain")

    # --- HUMIDITY ---
    st.sidebar.markdown("##### 💧 Humidity")
    c1, c2 = st.sidebar.columns([2, 1])
    with c1:
        hum_min, hum_max = st.slider(
            "Avg (%)", 0, 100,
            (ai.get("hum_min", int(df.avg_humidity.min())), ai.get("hum_max", int(df.avg_humidity.max()))),
            key="hum_range"
        )
    with c2:
        w_hum = st.slider("Weight (0-100)", 0, 100, ai_weights.get("hum", 25), key="w_hum")

    st.sidebar.divider()
    total_w = max(w_temp + w_sun + w_rain + w_hum, 1)

    filtered = df[
        df.avg_temp.between(temp_min, temp_max) &
        df.sunny_days.between(sun_min, sun_max) &
        df.annual_rain.between(rain_min, rain_max) &
        df.avg_humidity.between(hum_min, hum_max)
    ].copy()

    def score(row):
        # We normalize each parameter's contribution by its range and then multiply by its weight.
        # This ensures that even if ranges differ wildly, the importance (weight) is respected.
        # PATTERN: Normalized Weighted Scoring
        
        s_temp = (row.avg_temp - temp_min) / max(temp_max - temp_min, 1)
        s_sun = (row.sunny_days - sun_min) / max(sun_max - sun_min, 1)
        s_rain = 1 - (row.annual_rain - rain_min) / max(rain_max - rain_min, 1)
        s_hum = 1 - (row.avg_humidity - hum_min) / max(hum_max - hum_min, 1)
        
        # Multiply by weights and normalize to 0-100 scale
        weighted_score = (
            s_temp * w_temp + 
            s_sun * w_sun + 
            s_rain * w_rain + 
            s_hum * w_hum
        ) / total_w * 100
        
        return round(weighted_score)

    if not filtered.empty:
        filtered["score"] = filtered.apply(score, axis=1)
        filtered = filtered.sort_values("score", ascending=False)

else:
    filtered = pd.DataFrame()

# --- MAIN LAYOUT ---
col_map, col_list = st.columns([2, 1])

with col_map:
    if ai:
        st.subheader(f"Map — {len(filtered)} cities match")
    else:
        st.subheader("Map")

    if not ai:
        st.info("Describe your ideal place to live in the sidebar to get started.")
    elif filtered.empty:
        st.warning("No cities match your filters. Try widening the ranges.")
    else:
        filtered["color"] = filtered["score"].apply(
            lambda s: [104, 211, 145, 200] if s >= 75
            else [246, 173, 85, 200] if s >= 50
            else [252, 129, 129, 200]
        )
        filtered["radius"] = filtered["score"].apply(
            lambda s: 80000 if s >= 75 else 60000
        )

        layer = pdk.Layer(
            "ScatterplotLayer",
            data=filtered,
            get_position=["lon", "lat"],
            get_fill_color="color",
            get_radius="radius",
            pickable=True,
        )

        view = pdk.ViewState(
            latitude=20,
            longitude=10,
            zoom=1.2,
            pitch=0,
        )

        tooltip = {
            "html": """
                <b>{name}</b>, {country}<br/>
                🌡 {avg_temp}°C &nbsp;
                ☀️ {sunny_days} days &nbsp;
                🌧 {annual_rain}mm<br/>
                💧 {avg_humidity}% humidity<br/>
                <b>Score: {score}/100</b>
            """,
            "style": {
                "backgroundColor": "#1a2438",
                "color": "white",
                "padding": "10px",
                "borderRadius": "8px",
            }
        }

        st.pydeck_chart(pdk.Deck(
            layers=[layer],
            initial_view_state=view,
            tooltip=tooltip,
            map_style="https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json",
        ))

with col_list:
    if ai:
        st.subheader("Top matches")

    if ai and not filtered.empty:
        for _, row in filtered.head(10).iterrows():
            with st.container(border=True):
                c1, c2 = st.columns([3, 1])
                with c1:
                    st.markdown(f"**{row['name']}**, {row['country']}")
                    st.caption(
                        f"🌡 {row.avg_temp}°C · "
                        f"☀️ {int(row.sunny_days)}d · "
                        f"🌧 {int(row.annual_rain)}mm · "
                        f"💧 {int(row.avg_humidity)}%"
                    )
                with c2:
                    st.metric("Score", f"{row.score}")
    elif ai:
        st.info("Adjust filters to see results.")