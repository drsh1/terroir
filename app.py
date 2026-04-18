import streamlit as st
import pandas as pd
import pydeck as pdk

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
st.sidebar.caption("Find your perfect place on Earth")
st.sidebar.divider()

st.sidebar.subheader("Climate filters")

temp_min, temp_max = st.sidebar.slider(
    "Average annual temperature (°C)",
    min_value=-10, max_value=40,
    value=(int(df.avg_temp.min()), int(df.avg_temp.max()))
)

sun_min, sun_max = st.sidebar.slider(
    "Sunny days per year",
    min_value=0, max_value=365,
    value=(int(df.sunny_days.min()), int(df.sunny_days.max()))
)

rain_min, rain_max = st.sidebar.slider(
    "Annual rainfall (mm)",
    min_value=0, max_value=3000,
    value=(int(df.annual_rain.min()), int(df.annual_rain.max()))
)

hum_min, hum_max = st.sidebar.slider(
    "Average humidity (%)",
    min_value=0, max_value=100,
    value=(int(df.avg_humidity.min()), int(df.avg_humidity.max()))
)

# --- FILTERING ---
filtered = df[
    df.avg_temp.between(temp_min, temp_max) &
    df.sunny_days.between(sun_min, sun_max) &
    df.annual_rain.between(rain_min, rain_max) &
    df.avg_humidity.between(hum_min, hum_max)
].copy()

# --- SCORING ---
def score(row):
    total = 0
    total += (row.avg_temp - temp_min) / max(temp_max - temp_min, 1) * 25
    total += (row.sunny_days - sun_min) / max(sun_max - sun_min, 1) * 25
    total += (1 - (row.annual_rain - rain_min) / max(rain_max - rain_min, 1)) * 25
    total += (1 - (row.avg_humidity - hum_min) / max(hum_max - hum_min, 1)) * 25
    return round(total)

if not filtered.empty:
    filtered["score"] = filtered.apply(score, axis=1)
    filtered = filtered.sort_values("score", ascending=False)

# --- MAIN LAYOUT ---
col_map, col_list = st.columns([2, 1])

with col_map:
    st.subheader(f"Map — {len(filtered)} cities match")

    if filtered.empty:
        st.warning("No cities match your filters. Try widening the ranges.")
    else:
        # kolor zależny od score
        filtered["color"] = filtered["score"].apply(
            lambda s: [104, 211, 145, 200] if s >= 75
            else [246, 173, 85, 200] if s >= 50
            else [252, 129, 129, 200]
        )
        filtered["radius"] = filtered["score"].apply(lambda s: 80000 if s >= 75 else 60000)

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
    st.subheader("Top matches")

    if filtered.empty:
        st.info("Adjust filters to see results.")
    else:
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