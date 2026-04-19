import streamlit as st
import pandas as pd
import pydeck as pdk
from ai import parse_climate_preferences

st.set_page_config(
    page_title="Terroir — Find Your Perfect Climate",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── SVG icons (Lucide thin-stroke) ────────────────────────────────────────────
def svg_icon(key, color="#9CA3AF", size=13):
    icons = {
        "avg_temp":    f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 14.76V3.5a2.5 2.5 0 0 0-5 0v11.26a4.5 4.5 0 1 0 5 0z"/></svg>',
        "sunny_days":  f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41"/></svg>',
        "annual_rain": f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="16" y1="13" x2="16" y2="21"/><line x1="8" y1="13" x2="8" y2="21"/><line x1="12" y1="15" x2="12" y2="23"/><path d="M20 16.58A5 5 0 0 0 18 7h-1.26A8 8 0 1 0 4 15.25"/></svg>',
        "avg_humidity":f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2.69l5.66 5.66a8 8 0 1 1-11.31 0z"/></svg>',
    }
    return icons.get(key, "")

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* Main background */
.stApp { background: #F4F6FB; color: #111827; }

/* Sidebar */
[data-testid="stSidebar"] {
    background: #FFFFFF !important;
    border-right: 1px solid #E4E9F2 !important;
}
[data-testid="stSidebar"] * { color: #111827 !important; }
[data-testid="stSidebar"] .stTextArea textarea {
    background: #F9FAFB !important;
    border: 1px solid #E4E9F2 !important;
    border-radius: 8px !important;
    font-size: 13px !important;
    color: #111827 !important;
}
[data-testid="stSidebar"] .stTextArea textarea:focus {
    border-color: #4F6EF7 !important;
    box-shadow: 0 0 0 3px rgba(79,110,247,0.12) !important;
}

/* Primary button */
.stButton > button[kind="primary"] {
    background: #4F6EF7 !important;
    border: none !important;
    color: #fff !important;
    font-weight: 600 !important;
    border-radius: 8px !important;
    width: 100% !important;
    padding: 0.55rem 1rem !important;
    letter-spacing: 0.01em !important;
    transition: opacity .2s, transform .1s !important;
    font-size: 13px !important;
}
.stButton > button[kind="primary"]:hover { opacity: .88 !important; transform: translateY(-1px) !important; }

/* Sliders */
[data-testid="stSlider"] [class*="thumb"] { background: #4F6EF7 !important; border: 2px solid #fff !important; box-shadow: 0 1px 4px rgba(79,110,247,.3) !important; }
[data-testid="stSlider"] [class*="track-fill"] { background: #4F6EF7 !important; }

/* Number input */
[data-testid="stNumberInput"] input {
    text-align: center !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    border-radius: 6px !important;
    border: 1px solid #E4E9F2 !important;
    background: #F9FAFB !important;
    color: #4F6EF7 !important;
}

/* Section labels */
.sec-label {
    font-size: 10px;
    font-weight: 700;
    letter-spacing: .1em;
    text-transform: uppercase;
    color: #9CA3AF;
    margin: 4px 0 10px 0;
}

/* Metric label row */
.metric-label {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 13px;
    font-weight: 600;
    color: #374151;
    padding-top: 6px;
}
.metric-range-val {
    font-size: 11px;
    color: #4F6EF7;
    font-weight: 500;
    text-align: center;
    margin-top: -8px;
    margin-bottom: 4px;
}

/* AI explanation */
.ai-card {
    border-left: 3px solid #10B981;
    background: #F0FDF4;
    border-radius: 0 8px 8px 0;
    padding: 10px 12px;
    font-size: 12px;
    color: #065F46;
    line-height: 1.5;
    margin: 8px 0;
}

/* City cards */
.city-card {
    background: #FFFFFF;
    border: 1px solid #E4E9F2;
    border-radius: 12px;
    padding: 14px 16px;
    margin-bottom: 9px;
    box-shadow: 0 1px 4px rgba(0,0,0,.05);
    transition: box-shadow .2s, border-color .2s;
}
.city-card:hover { box-shadow: 0 4px 14px rgba(79,110,247,.12); border-color: #4F6EF7; }
.city-rank { font-size: 10px; font-weight: 700; color: #9CA3AF; letter-spacing: .06em; text-transform: uppercase; margin-bottom: 4px; }
.city-name { font-size: 15px; font-weight: 700; color: #111827; }
.city-country { font-size: 12px; color: #6B7280; margin-bottom: 10px; }
.stat-pills { display: flex; flex-wrap: wrap; gap: 5px; margin-bottom: 10px; }
.stat-pill {
    display: inline-flex; align-items: center; gap: 4px;
    background: #F9FAFB; border: 1px solid #E4E9F2;
    border-radius: 6px; padding: 3px 8px;
    font-size: 11px; color: #374151; white-space: nowrap;
}
.stat-pill span { color: #6B7280; font-size: 10px; }
.score-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px; }
.score-label { font-size: 10px; font-weight: 600; letter-spacing: .06em; text-transform: uppercase; color: #9CA3AF; }
.score-val { font-size: 14px; font-weight: 700; }
.score-bar-bg { background: #F3F4F6; border-radius: 4px; height: 5px; overflow: hidden; }
.score-bar { height: 100%; border-radius: 4px; }

/* Map card */
.map-card-header {
    font-size: 18px; font-weight: 700; color: #111827;
    margin-bottom: 4px;
}
.map-card-sub { font-size: 12px; color: #6B7280; margin-bottom: 12px; }

/* Empty state */
.empty-state {
    display: flex; flex-direction: column; align-items: center;
    justify-content: center; height: 100%; min-height: 380px;
    color: #9CA3AF; text-align: center; gap: 10px;
}
.empty-icon { font-size: 44px; opacity: .45; }
.empty-title { font-size: 16px; font-weight: 600; color: #374151; }
.empty-sub { font-size: 12px; max-width: 220px; line-height: 1.6; }

/* Results column scroll */
.results-wrap { max-height: 76vh; overflow-y: auto; padding-right: 2px; }

/* Brand */
.brand { font-size: 20px; font-weight: 700; color: #111827; letter-spacing: -.02em; }
.brand-sub { font-size: 11px; color: #9CA3AF; margin-top: -2px; margin-bottom: 0; }

/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }

/* Divider */
hr { border-color: #E4E9F2 !important; margin: 12px 0 !important; }
</style>
""", unsafe_allow_html=True)

# ── Data ───────────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("cities.csv")
    df = df.dropna(subset=["avg_temp", "sunny_days", "annual_rain", "avg_humidity"])
    df["sunny_days"] = df["sunny_days"].astype(int)
    df["annual_rain"] = df["annual_rain"].astype(int)
    return df

METRICS = {
    "avg_temp":     {"label": "Temperature", "unit": "°C",      "range": (-10, 40),   "ai_key": "temp", "higher_is_better": True,  "fmt": lambda v: f"{v:.0f}°C"},
    "sunny_days":   {"label": "Sunshine",    "unit": "days/yr", "range": (0, 365),    "ai_key": "sun",  "higher_is_better": True,  "fmt": lambda v: f"{int(v)} d/yr"},
    "annual_rain":  {"label": "Rainfall",    "unit": "mm/yr",   "range": (0, 3000),   "ai_key": "rain", "higher_is_better": False, "fmt": lambda v: f"{int(v)} mm"},
    "avg_humidity": {"label": "Humidity",    "unit": "%",       "range": (0, 100),    "ai_key": "hum",  "higher_is_better": False, "fmt": lambda v: f"{v:.0f}%"},
}

df = load_data()

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="brand">Terroir</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-sub">Find your perfect place on Earth</div>', unsafe_allow_html=True)
    st.divider()

    st.markdown('<div class="sec-label">Describe your perfect place to live</div>', unsafe_allow_html=True)

    ai_input = st.text_area(
        "describe", placeholder="e.g. Warm sunny summers, mild winters, not too humid…",
        height=100, label_visibility="collapsed"
    )

    if st.button("Find my perfect climate", type="primary"):
        if ai_input.strip():
            with st.spinner("Analysing…"):
                try:
                    stats = {
                        "temp_min": int(df.avg_temp.min()), "temp_max": int(df.avg_temp.max()),
                        "sun_min":  int(df.sunny_days.min()), "sun_max": int(df.sunny_days.max()),
                        "rain_min": int(df.annual_rain.min()), "rain_max": int(df.annual_rain.max()),
                        "hum_min":  int(df.avg_humidity.min()), "hum_max": int(df.avg_humidity.max()),
                    }
                    result = parse_climate_preferences(ai_input, stats)
                    st.session_state["ai_result"] = result
                    for key, cfg in METRICS.items():
                        ak = cfg["ai_key"]
                        st.session_state[f"w_{ak}"]      = result.get("weights", {}).get(ak, 25)
                        st.session_state[f"range_{key}"] = (
                            result.get(f"{ak}_min", cfg["range"][0]),
                            result.get(f"{ak}_max", cfg["range"][1])
                        )
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.warning("Please describe your ideal climate first.")

    ai = st.session_state.get("ai_result", {})

    if ai:
        st.markdown(f'<div class="ai-card">✓ {ai["explanation"]}</div>', unsafe_allow_html=True)
        st.divider()
        st.markdown('<div class="sec-label">Climate Filters</div>', unsafe_allow_html=True)

        user_settings = {}
        for key, cfg in METRICS.items():
            ak = cfg["ai_key"]
            default_range  = (ai.get(f"{ak}_min", cfg["range"][0]), ai.get(f"{ak}_max", cfg["range"][1]))
            default_weight = ai.get("weights", {}).get(ak, 25)

            # Metric name + weight input on same row
            c_name, c_weight = st.columns([3, 1])
            with c_name:
                st.markdown(
                    f'<div class="metric-label">{svg_icon(key)} {cfg["label"]}</div>',
                    unsafe_allow_html=True
                )
            with c_weight:
                weight = st.number_input(
                    "w", min_value=0, max_value=100, step=5,
                    value=int(st.session_state.get(f"w_{ak}", default_weight)),
                    key=f"w_{ak}", label_visibility="collapsed"
                )

            # Range slider
            val_range = st.slider(
                cfg["label"], cfg["range"][0], cfg["range"][1],
                value=st.session_state.get(f"range_{key}", default_range),
                key=f"range_{key}", label_visibility="collapsed"
            )
            st.markdown(
                f'<div class="metric-range-val">{val_range[0]} — {val_range[1]} {cfg["unit"]}</div>',
                unsafe_allow_html=True
            )

            user_settings[key] = {"min": val_range[0], "max": val_range[1], "weight": weight}

    else:
        user_settings = {}

# ── Scoring ────────────────────────────────────────────────────────────────────
def score_city(row, settings):
    total_w = max(sum(s["weight"] for s in settings.values()), 1)
    total_s = 0
    for key, cfg in METRICS.items():
        s = settings[key]
        v = max(0.0, min(1.0, (row[key] - s["min"]) / max(s["max"] - s["min"], 1)))
        if not cfg["higher_is_better"]:
            v = 1 - v
        total_s += v * s["weight"]
    return round((total_s / total_w) * 100)

if user_settings:
    filtered = df.copy()
    for key, s in user_settings.items():
        filtered = filtered[filtered[key].between(s["min"], s["max"])]
    if not filtered.empty:
        filtered["score"] = filtered.apply(lambda r: score_city(r, user_settings), axis=1)
        filtered = filtered.sort_values("score", ascending=False)
else:
    filtered = pd.DataFrame()

def score_color(s):
    return "#10B981" if s >= 75 else "#F59E0B" if s >= 50 else "#EF4444"

def score_map_color(s):
    return [16, 185, 129, 220] if s >= 75 else [245, 158, 11, 220] if s >= 50 else [239, 68, 68, 200]

# ── Layout ─────────────────────────────────────────────────────────────────────
col_map, col_list = st.columns([5, 2], gap="medium")

with col_map:
    if ai and not filtered.empty:
        st.markdown(f'<div class="map-card-header">{len(filtered)} cities match</div>', unsafe_allow_html=True)
        st.markdown('<div class="map-card-sub">Sorted by match score · hover a dot for details</div>', unsafe_allow_html=True)
    elif ai:
        st.markdown('<div class="map-card-header">No cities match</div>', unsafe_allow_html=True)
        st.markdown('<div class="map-card-sub">Try widening the filter ranges</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="map-card-header">World Climate Map</div>', unsafe_allow_html=True)
        st.markdown('<div class="map-card-sub">Describe your ideal climate to get started</div>', unsafe_allow_html=True)

    if not ai:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-icon">🌍</div>
            <div class="empty-title">Where do you want to live?</div>
            <div class="empty-sub">Describe your ideal climate in the sidebar and let AI find your perfect city.</div>
        </div>""", unsafe_allow_html=True)

    elif filtered.empty:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-icon">🔍</div>
            <div class="empty-title">No cities match</div>
            <div class="empty-sub">Try widening the range sliders in the sidebar.</div>
        </div>""", unsafe_allow_html=True)

    else:
        filtered["color"]  = filtered["score"].apply(score_map_color)
        filtered["radius"] = filtered["score"].apply(lambda s: 85000 if s >= 75 else 60000 if s >= 50 else 40000)

        metrics_html = "".join(
            f"<span style='margin-right:8px'>{cfg['label']}: {{{key}}}{cfg['unit']}</span>"
            for key, cfg in METRICS.items()
        )
        tooltip = {
            "html": f"""<div style='font-family:Inter,sans-serif;font-size:12px;padding:4px 2px'>
              <div style='font-weight:700;font-size:13px;margin-bottom:5px'>{{name}}, {{country}}</div>
              <div style='color:#9CA3AF;margin-bottom:5px'>{metrics_html}</div>
              <div style='font-weight:700;color:#4F6EF7'>Score: {{score}} / 100</div>
            </div>""",
            "style": {"backgroundColor":"#fff","color":"#111827","padding":"10px 14px","borderRadius":"10px","border":"1px solid #E4E9F2","boxShadow":"0 4px 16px rgba(0,0,0,.1)"}
        }

        layer = pdk.Layer("ScatterplotLayer", data=filtered,
            get_position=["lon","lat"], get_fill_color="color",
            get_radius="radius", pickable=True, auto_highlight=True)

        st.pydeck_chart(pdk.Deck(
            layers=[layer],
            initial_view_state=pdk.ViewState(latitude=20, longitude=10, zoom=1.2, pitch=0),
            tooltip=tooltip,
            map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json",
        ))

with col_list:
    if ai:
        st.markdown('<div class="sec-label" style="margin-top:4px">Top Matches</div>', unsafe_allow_html=True)

    if ai and not filtered.empty:
        st.markdown('<div class="results-wrap">', unsafe_allow_html=True)
        for rank, (_, row) in enumerate(filtered.head(10).iterrows(), start=1):
            sc    = int(row["score"])
            color = score_color(sc)
            medal = {1: "🥇 #1", 2: "🥈 #2", 3: "🥉 #3"}.get(rank, f"#{rank}")

            pills = "".join(
                f'<div class="stat-pill">{svg_icon(key, "#6B7280", 11)}<span>{cfg["label"]}</span> {cfg["fmt"](row[key])}</div>'
                for key, cfg in METRICS.items()
            )

            st.markdown(f"""
            <div class="city-card">
                <div class="city-rank">{medal}</div>
                <div class="city-name">{row['name']}</div>
                <div class="city-country">{row['country']}</div>
                <div class="stat-pills">{pills}</div>
                <div class="score-row">
                    <span class="score-label">Match score</span>
                    <span class="score-val" style="color:{color}">{sc}</span>
                </div>
                <div class="score-bar-bg">
                    <div class="score-bar" style="width:{sc}%;background:{color}"></div>
                </div>
            </div>""", unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    elif ai:
        st.markdown("""
        <div class="empty-state" style="min-height:200px">
            <div class="empty-sub">Adjust filters to see results.</div>
        </div>""", unsafe_allow_html=True)