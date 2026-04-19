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

# --- CONFIGURATION (PATTERN: Config-Driven UI) ---
# We define all metrics in a single source of truth.
# Adding a new metric (e.g. Cost of Living) only requires adding a key here.
METRICS = {
    "avg_temp": {
        "label": "Temperature",
        "icon": "🌡",
        "unit": "°C",
        "range": (-10, 40),
        "ai_key": "temp",
        "higher_is_better": True
    },
    "sunny_days": {
        "label": "Sunshine",
        "icon": "☀️",
        "unit": "days per year",
        "range": (0, 365),
        "ai_key": "sun",
        "higher_is_better": True
    },
    "annual_rain": {
        "label": "Rainfall",
        "icon": "🌧",
        "unit": "annual mm",
        "range": (0, 3000),
        "ai_key": "rain",
        "higher_is_better": False
    },
    "avg_humidity": {
        "label": "Humidity",
        "icon": "💧",
        "unit": "%",
        "range": (0, 100),
        "ai_key": "hum",
        "higher_is_better": False
    }
}

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
                
                # Reset sliders in session state to AI-suggested values
                # PATTERN: Explicit State Reset for Interactive Components
                for key, cfg in METRICS.items():
                    ai_key = cfg["ai_key"]
                    if "weights" in result:
                        st.session_state[f"w_{ai_key}"] = result["weights"].get(ai_key, 25)
                    
                    # Also reset range sliders
                    st.session_state[f"range_{key}"] = (
                        result.get(f"{ai_key}_min", cfg["range"][0]),
                        result.get(f"{ai_key}_max", cfg["range"][1])
                    )
            except Exception as e:
                st.sidebar.error(f"Error: {e}")
    else:
        st.sidebar.warning("Please describe your ideal climate first.")

ai = st.session_state.get("ai_result", {})

if ai:
    st.sidebar.success(ai["explanation"])
    st.sidebar.divider()
    st.sidebar.subheader("Fine-tune results")
    
    ai_weights = ai.get("weights", {})
    user_settings = {}

    for key, cfg in METRICS.items():
        ai_key = cfg["ai_key"]
        st.sidebar.markdown(f"##### {cfg['icon']} {cfg['label']}")
        
        c1, c2 = st.sidebar.columns([2, 1])
        with c1:
            val_range = st.slider(
                cfg["unit"],
                cfg["range"][0], cfg["range"][1],
                value=st.session_state.get(f"range_{key}", (ai.get(f"{ai_key}_min", cfg["range"][0]), ai.get(f"{ai_key}_max", cfg["range"][1]))),
                key=f"range_{key}"
            )
        with c2:
            weight = st.slider(
                "Weight (0-100)", 0, 100,
                value=st.session_state.get(f"w_{ai_key}", ai_weights.get(ai_key, 25)),
                key=f"w_{ai_key}"
            )
        
        user_settings[key] = {
            "min": val_range[0],
            "max": val_range[1],
            "weight": weight
        }

    st.sidebar.divider()
    
    total_w = max(sum(s["weight"] for s in user_settings.values()), 1)

    # --- FILTERING ---
    filtered = df.copy()
    for key, settings in user_settings.items():
        filtered = filtered[filtered[key].between(settings["min"], settings["max"])]

    def score(row):
        # PATTERN: Normalized Weighted Scoring (Dynamic)
        total_score = 0
        
        for key, cfg in METRICS.items():
            settings = user_settings[key]
            
            # Normalize value to 0-1 within the user-defined range
            val_min, val_max = settings["min"], settings["max"]
            val = row[key]
            
            # Calculate normalized score for this metric
            s = (val - val_min) / max(val_max - val_min, 1)
            
            # If "higher is better" is False (e.g. rain), we flip the score
            if not cfg["higher_is_better"]:
                s = 1 - s
                
            total_score += s * settings["weight"]
            
        return round((total_score / total_w) * 100)

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

        # Build tooltip HTML dynamically from METRICS
        # PATTERN: Dynamic UI Generation
        metrics_html = ""
        for key, cfg in METRICS.items():
            metrics_html += f"{cfg['icon']} {{{key}}}{cfg['unit']} &nbsp; "

        tooltip = {
            "html": f"""
                <b>{{name}}</b>, {{country}}<br/>
                {metrics_html}<br/>
                <b>Score: {{score}}/100</b>
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
                    
                    # Dynamic caption from METRICS
                    caption_parts = []
                    for key, cfg in METRICS.items():
                        val = row[key]
                        # Format as int if it's a whole number
                        val_str = f"{int(val)}" if val == int(val) else f"{val:.1f}"
                        caption_parts.append(f"{cfg['icon']} {val_str}{cfg['unit']}")
                    
                    st.caption(" · ".join(caption_parts))
                with c2:
                    st.metric("Score", f"{row.score}")
    elif ai:
        st.info("Adjust filters to see results.")