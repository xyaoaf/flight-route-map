"""
Flight Route Map – Streamlit App
Run:  streamlit run app.py
"""

import io
from collections import Counter

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from pyproj import Geod

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Flight Route Map",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Airport database  (lon, lat, full name, region) ───────────────────────────
# 'region' kept for internal stats only – never shown on hover
AIRPORTS: dict[str, tuple] = {
    # Mainland China
    "HGH": (120.4333,  30.2295, "Hangzhou Xiaoshan",         "East Asia"),
    "PVG": (121.8052,  31.1443, "Shanghai Pudong",            "East Asia"),
    "SHA": (121.3361,  31.1981, "Shanghai Hongqiao",          "East Asia"),
    "PEK": (116.5975,  40.0801, "Beijing Capital",            "East Asia"),
    "CAN": (113.2988,  23.3924, "Guangzhou Baiyun",           "East Asia"),
    "SZX": (113.8107,  22.6393, "Shenzhen Bao'an",            "East Asia"),
    "TAO": (120.3744,  36.2661, "Qingdao Liuting",            "East Asia"),
    "WNZ": (120.8530,  27.9122, "Wenzhou Longwan",            "East Asia"),
    # HK / Macau / Taiwan
    "HKG": (113.9185,  22.3080, "Hong Kong Intl",             "East Asia"),
    "MFM": (113.5925,  22.1496, "Macau Intl",                 "East Asia"),
    "TPE": (121.2325,  25.0777, "Taipei Taoyuan",             "East Asia"),
    # Southeast Asia
    "SIN": (103.9894,   1.3644, "Singapore Changi",           "Southeast Asia"),
    "KUL": (101.7098,   2.7456, "Kuala Lumpur Intl",          "Southeast Asia"),
    "BKK": (100.7501,  13.6811, "Bangkok Suvarnabhumi",       "Southeast Asia"),
    "BWN": (114.9283,   4.9442, "Bandar Seri Begawan",        "Southeast Asia"),
    # Japan / Korea
    "NRT": (140.3929,  35.7668, "Tokyo Narita",               "East Asia"),
    "HND": (139.7814,  35.5494, "Tokyo Haneda",               "East Asia"),
    "KIX": (135.2380,  34.4272, "Osaka Kansai",               "East Asia"),
    "ICN": (126.4505,  37.4602, "Seoul Incheon",              "East Asia"),
    # Central Asia
    "ALA": ( 76.8844,  43.3521, "Almaty",                     "Central Asia"),
    "NQZ": ( 71.4669,  51.0222, "Nur-Sultan (Astana)",        "Central Asia"),
    # Australia
    "SYD": (151.1772, -33.9461, "Sydney Kingsford Smith",     "Oceania"),
    "BNE": (153.1094, -27.3842, "Brisbane",                   "Oceania"),
    # Europe
    "FRA": (  8.5706,  50.0333, "Frankfurt Main",             "Europe"),
    "TXL": ( 13.2877,  52.5597, "Berlin Tegel",               "Europe"),
    "LHR": ( -0.4543,  51.4700, "London Heathrow",            "Europe"),
    # North America – West
    "SFO": (-122.375,  37.6189, "San Francisco Intl",         "North America"),
    "OAK": (-122.221,  37.7126, "Oakland Intl",               "North America"),
    "SJC": (-121.929,  37.3627, "San Jose Mineta",            "North America"),
    "LAX": (-118.408,  33.9416, "Los Angeles Intl",           "North America"),
    "SAN": (-117.190,  32.7336, "San Diego Intl",             "North America"),
    "SEA": (-122.309,  47.4502, "Seattle-Tacoma",             "North America"),
    "PDX": (-122.598,  45.5898, "Portland Intl",              "North America"),
    "BOI": (-116.223,  43.5644, "Boise Airport",              "North America"),
    "LAS": (-115.152,  36.0833, "Las Vegas Harry Reid",       "North America"),
    # North America – South / Central
    "AUS": ( -97.670,  30.1945, "Austin-Bergstrom",           "North America"),
    "DFW": ( -97.040,  32.8998, "Dallas Fort Worth",          "North America"),
    "IAH": ( -95.341,  29.9844, "Houston George Bush",        "North America"),
    "JAN": ( -90.076,  32.3112, "Jackson-Medgar Wiley Evers", "North America"),
    "ABQ": (-106.609,  35.0496, "Albuquerque Sunport",        "North America"),
    "MIA": ( -80.291,  25.7959, "Miami Intl",                 "North America"),
    "ATL": ( -84.428,  33.6407, "Atlanta Hartsfield-Jackson", "North America"),
    "GSP": ( -82.221,  34.8954, "Greenville-Spartanburg",     "North America"),
    "CHS": ( -80.040,  32.8986, "Charleston Intl",            "North America"),
    "CLT": ( -80.943,  35.2140, "Charlotte Douglas",          "North America"),
    "BNA": ( -86.678,  36.1245, "Nashville Intl",             "North America"),
    # North America – East
    "BOS": ( -71.005,  42.3656, "Boston Logan",               "North America"),
    "JFK": ( -73.778,  40.6413, "New York JFK",               "North America"),
    "EWR": ( -74.175,  40.6895, "Newark Liberty",             "North America"),
    "RDU": ( -78.788,  35.8776, "Raleigh-Durham",             "North America"),
    "MSN": ( -89.338,  43.1399, "Madison Dane County",        "North America"),
    "MKE": ( -87.897,  42.9481, "Milwaukee Mitchell",         "North America"),
    "STL": ( -90.370,  38.7487, "St. Louis Lambert",          "North America"),
    "MSP": ( -93.222,  44.8848, "Minneapolis-Saint Paul",     "North America"),
    # Canada
    "YVR": (-123.183,  49.1951, "Vancouver Intl",             "North America"),
    "YYZ": ( -79.631,  43.6777, "Toronto Pearson",            "North America"),
}

# ── Visual themes ─────────────────────────────────────────────────────────────
GLOBE_STYLES = {
    "🌿 Natural":  dict(land="rgb(55,105,55)",    ocean="rgb(20,70,130)",
                        bg="rgb(10,30,60)",        coast="rgba(180,220,180,0.6)",
                        country="rgba(180,210,180,0.3)"),
    "🌑 Dark":     dict(land="rgb(35,35,35)",      ocean="rgb(12,22,45)",
                        bg="rgb(5,5,15)",           coast="rgba(120,120,120,0.6)",
                        country="rgba(80,80,80,0.4)"),
    "🏜️ Sandy":   dict(land="rgb(195,165,110)",   ocean="rgb(75,140,195)",
                        bg="rgb(55,110,165)",       coast="rgba(220,200,160,0.6)",
                        country="rgba(160,140,100,0.4)"),
    "🧊 Ice":      dict(land="rgb(215,228,240)",   ocean="rgb(145,195,230)",
                        bg="rgb(175,210,235)",      coast="rgba(80,130,170,0.6)",
                        country="rgba(100,130,160,0.3)"),
}

# Flat map uses same color dicts but with natural-earth projection
FLAT_STYLES = GLOBE_STYLES  # reuse themes

COLOR_THEMES = {
    "Crimson Red":  "#DC143C",
    "Royal Blue":   "#3A7BD5",
    "Amber Gold":   "#FFC107",
    "Emerald":      "#2ECC71",
    "Neon Orange":  "#FF6600",
    "Violet":       "#7B2FBE",
    "Ice Blue":     "#00BFFF",
    "Coral":        "#FF6B6B",
}

# Satellite tile (Esri World Imagery – free, no API key)
_ESRI_SAT = ("https://server.arcgisonline.com/ArcGIS/rest/services/"
             "World_Imagery/MapServer/tile/{z}/{y}/{x}")

# ── Great-circle helpers ──────────────────────────────────────────────────────
_geod = Geod(ellps="WGS84")


def great_circle_path(lon1, lat1, lon2, lat2, npts=100):
    """
    Great-circle arc with None breaks at the antimeridian.

    For go.Scattergeo this is the correct approach: Plotly's geo-projection
    engine places both segments in the right screen position, so the break
    (if any) is invisible at the ±180° meridian.

    For go.Scattermapbox (satellite mode) we center the initial view near
    the antimeridian so that both segments are inside the visible viewport.
    """
    if (lon1, lat1) == (lon2, lat2):
        return [lon1], [lat1]
    pts  = _geod.npts(lon1, lat1, lon2, lat2, npts)
    lons = [lon1] + [p[0] for p in pts] + [lon2]
    lats = [lat1] + [p[1] for p in pts] + [lat2]
    out_lons, out_lats = [lons[0]], [lats[0]]
    for i in range(1, len(lons)):
        if abs(lons[i] - lons[i - 1]) > 180:
            out_lons.append(None)
            out_lats.append(None)
        out_lons.append(lons[i])
        out_lats.append(lats[i])
    return out_lons, out_lats


def dist_km(lon1, lat1, lon2, lat2) -> float:
    _, _, d = _geod.inv(lon1, lat1, lon2, lat2)
    return d / 1000


def marker_size(count: int) -> int:
    """Bucketed sizes to reduce visual inflation from transit counts."""
    if count <= 5:   return 8
    if count <= 10:  return 12
    if count <= 15:  return 16
    return 20


# ── Data loading / stats ──────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_routes(csv_bytes: bytes | None = None) -> list[tuple[str, str]]:
    try:
        src = io.BytesIO(csv_bytes) if csv_bytes else "data/my_flight_log.csv"
        df  = pd.read_csv(src)
        routes = []
        for _, row in df.iterrows():
            o = str(row.get("origin",      "")).strip().upper()
            d = str(row.get("destination", "")).strip().upper()
            if len(o) == 3 and len(d) == 3 and "NAN" not in (o, d):
                routes.append((o, d))
        return routes
    except Exception as e:
        st.error(f"Failed to load flight data: {e}")
        return []


def compute_stats(routes: list[tuple[str, str]]) -> dict:
    all_ap   = [a for pair in routes for a in pair]
    visits   = Counter(all_ap)
    total_km = sum(
        dist_km(*AIRPORTS[o][:2], *AIRPORTS[d][:2])
        for o, d in routes if o in AIRPORTS and d in AIRPORTS
    )
    regions  = sorted({AIRPORTS[a][3] for a in all_ap if a in AIRPORTS})
    missing  = sorted({a for o, d in routes for a in (o, d) if a not in AIRPORTS})
    return dict(n_flights=len(routes), n_airports=len(visits),
                total_km=total_km, n_regions=len(regions),
                regions=regions, visits=visits, missing=missing)


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("✈️ Controls")

    uploaded = st.file_uploader(
        "Upload your flight log (CSV)", type="csv",
        help="Two columns: `origin` and `destination` (IATA codes).",
    )

    st.divider()
    st.subheader("🗺 Map")

    mode = st.radio(
        "Mode",
        ["🌐 Globe", "🗺️ Flat Map", "🛰️ Satellite"],
        index=0, horizontal=True,
    )

    if mode == "🌐 Globe":
        style_key = st.selectbox("Globe style", list(GLOBE_STYLES.keys()), index=0)
    elif mode == "🗺️ Flat Map":
        style_key = st.selectbox("Map style",   list(FLAT_STYLES.keys()),  index=0)
    else:
        style_key = None
        st.caption(
            "Satellite imagery © Esri (free, no API key).  \n"
            "Initial view is Pacific-centered so routes across the ocean "
            "render without gaps. Pan/zoom to explore."
        )

    color_key = st.selectbox("Route color", list(COLOR_THEMES.keys()), index=0)

    st.divider()
    st.subheader("🔍 Display")
    show_airports = st.checkbox("Airport markers",           value=True)
    show_labels   = st.checkbox("Airport IATA labels",       value=False)
    scale_width   = st.checkbox("Scale routes by frequency", value=True)

    st.divider()
    st.subheader("📍 Initial View")
    # Globe & Flat use projection rotation; Satellite uses lat/lon center + zoom
    region = st.radio("Focus on",
                      ["Asia-Pacific", "North America", "Europe", "World"],
                      index=0)

# ── Presets ───────────────────────────────────────────────────────────────────
# Globe / Flat: rotation center for Scattergeo projection
GEO_ROTATION = {
    "Asia-Pacific":  dict(lon=160, lat=15),
    "North America": dict(lon=-95, lat=40),
    "Europe":        dict(lon=15,  lat=50),
    "World":         dict(lon=160, lat=15),   # Pacific-centric world view
}
# Satellite: Mapbox center + zoom
# Asia-Pacific center is set near the antimeridian (lon=-175) so that
# BOTH the Asian side (positive lons) and the American side (negative lons)
# are inside the same viewport – eliminating the Pacific gap for Scattermapbox.
SAT_VIEW = {
    "Asia-Pacific":  dict(lat=25,  lon=-175, zoom=1.6),
    "North America": dict(lat=40,  lon=-100, zoom=2.8),
    "Europe":        dict(lat=50,  lon=10,   zoom=3.0),
    "World":         dict(lat=15,  lon=-175, zoom=1.2),
}

# ── Load data ─────────────────────────────────────────────────────────────────
csv_bytes = uploaded.read() if uploaded else None
routes    = load_routes(csv_bytes)
stats     = compute_stats(routes) if routes else {}

# ── Header metrics ────────────────────────────────────────────────────────────
st.title("✈️ My Flight Route Map")
st.caption("Interactive personal flight history — great-circle routes, Asia-Pacific focused.")

if stats:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Flights",    stats["n_flights"])
    c2.metric("Airports Visited", stats["n_airports"])
    c3.metric("Distance Flown",   f"{stats['total_km']:,.0f} km")
    c4.metric("Regions",          stats["n_regions"])

# ── Build figure ──────────────────────────────────────────────────────────────
route_color = COLOR_THEMES[color_key]
fig         = go.Figure()
normalized  = Counter(tuple(sorted(pair)) for pair in routes)


def add_routes_geo(fig, normalized, route_color, scale_width):
    """Add Scattergeo route traces (Globe or Flat mode)."""
    for (o, d), cnt in normalized.items():
        if o not in AIRPORTS or d not in AIRPORTS:
            continue
        lons, lats = great_circle_path(*AIRPORTS[o][:2], *AIRPORTS[d][:2])
        width   = (1.5 + 0.7 * (cnt - 1)) if scale_width else 2.0
        opacity = min(0.45 + 0.12 * cnt, 0.95) if scale_width else 0.65
        fig.add_trace(go.Scattergeo(
            lon=lons, lat=lats, mode="lines",
            line=dict(width=width, color=route_color),
            opacity=opacity,
            hoverinfo="text",
            text=f"✈ {o} → {d}" + (f"  ×{cnt}" if cnt > 1 else ""),
            showlegend=False,
        ))


def add_airports_geo(fig, stats, route_color, show_labels):
    """Add Scattergeo airport markers."""
    for airport, cnt in stats["visits"].items():
        if airport not in AIRPORTS:
            continue
        lon, lat, name, _ = AIRPORTS[airport]
        fig.add_trace(go.Scattergeo(
            lon=[lon], lat=[lat],
            mode="markers+text" if show_labels else "markers",
            marker=dict(size=marker_size(cnt), color=route_color, opacity=0.85),
            text=airport if show_labels else "",
            textposition="top right",
            textfont=dict(color="white", size=9),
            hovertext=f"<b>{airport}</b> – {name}<br>Visited {cnt}×",
            hoverinfo="text",
            showlegend=False,
        ))


def add_routes_mapbox(fig, normalized, route_color, scale_width):
    """Add Scattermapbox route traces (Satellite mode)."""
    for (o, d), cnt in normalized.items():
        if o not in AIRPORTS or d not in AIRPORTS:
            continue
        lons, lats = great_circle_path(*AIRPORTS[o][:2], *AIRPORTS[d][:2])
        width   = (1.5 + 0.7 * (cnt - 1)) if scale_width else 2.0
        opacity = min(0.45 + 0.12 * cnt, 0.95) if scale_width else 0.65
        fig.add_trace(go.Scattermapbox(
            lon=lons, lat=lats, mode="lines",
            line=dict(width=width, color=route_color),
            opacity=opacity,
            hoverinfo="text",
            text=f"✈ {o} → {d}" + (f"  ×{cnt}" if cnt > 1 else ""),
            showlegend=False,
        ))


def add_airports_mapbox(fig, stats, route_color, show_labels):
    """Add Scattermapbox airport markers."""
    for airport, cnt in stats["visits"].items():
        if airport not in AIRPORTS:
            continue
        lon, lat, name, _ = AIRPORTS[airport]
        fig.add_trace(go.Scattermapbox(
            lon=[lon], lat=[lat],
            mode="markers+text" if show_labels else "markers",
            marker=dict(size=marker_size(cnt), color=route_color, opacity=0.85),
            text=airport if show_labels else "",
            textposition="top right",
            textfont=dict(color="white", size=9),
            hovertext=f"<b>{airport}</b> – {name}<br>Visited {cnt}×",
            hoverinfo="text",
            showlegend=False,
        ))


# ── Globe mode ────────────────────────────────────────────────────────────────
if mode == "🌐 Globe":
    gs  = GLOBE_STYLES[style_key]
    rot = GEO_ROTATION[region]
    add_routes_geo(fig, normalized, route_color, scale_width)
    if show_airports and stats:
        add_airports_geo(fig, stats, route_color, show_labels)
    fig.update_layout(
        geo=dict(
            projection_type="orthographic",
            projection_rotation=dict(lon=rot["lon"], lat=rot["lat"]),
            showland=True,       landcolor=gs["land"],
            showocean=True,      oceancolor=gs["ocean"],
            showcountries=True,  countrycolor=gs["country"],
            showcoastlines=True, coastlinecolor=gs["coast"],
            showlakes=True,      lakecolor=gs["ocean"],
            showframe=False,
            bgcolor=gs["bg"],
        ),
        paper_bgcolor=gs["bg"],
        margin=dict(r=0, t=0, l=0, b=0),
        height=680, showlegend=False,
    )

# ── Flat Map mode ─────────────────────────────────────────────────────────────
# Uses go.Scattergeo with natural-earth projection.
# Rotating the projection to lon=160 makes it Pacific-centric.
# Scattergeo handles the antimeridian internally → no Pacific gap.
elif mode == "🗺️ Flat Map":
    gs  = FLAT_STYLES[style_key]
    rot = GEO_ROTATION[region]
    add_routes_geo(fig, normalized, route_color, scale_width)
    if show_airports and stats:
        add_airports_geo(fig, stats, route_color, show_labels)
    fig.update_layout(
        geo=dict(
            projection_type="natural earth",
            projection_rotation=dict(lon=rot["lon"]),
            showland=True,       landcolor=gs["land"],
            showocean=True,      oceancolor=gs["ocean"],
            showcountries=True,  countrycolor=gs["country"],
            showcoastlines=True, coastlinecolor=gs["coast"],
            showlakes=True,      lakecolor=gs["ocean"],
            showframe=False,
            bgcolor=gs["bg"],
            lonaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.08)", dtick=30),
            lataxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.08)", dtick=30),
        ),
        paper_bgcolor=gs["bg"],
        margin=dict(r=0, t=0, l=0, b=0),
        height=620, showlegend=False,
    )

# ── Satellite mode ────────────────────────────────────────────────────────────
# Uses go.Scattermapbox with Esri World Imagery tiles (free, no API key).
# Center is placed near lon=-175 (just east of the antimeridian) so that
# positive-longitude (Asia) and negative-longitude (Americas) route segments
# both fall inside the visible tile viewport, eliminating the Pacific gap.
else:
    sv = SAT_VIEW[region]
    add_routes_mapbox(fig, normalized, route_color, scale_width)
    if show_airports and stats:
        add_airports_mapbox(fig, stats, route_color, show_labels)
    fig.update_layout(
        mapbox=dict(
            style="white-bg",
            zoom=sv["zoom"],
            center=dict(lat=sv["lat"], lon=sv["lon"]),
            layers=[{"below": "traces", "sourcetype": "raster",
                     "source": [_ESRI_SAT]}],
        ),
        margin=dict(r=0, t=0, l=0, b=0),
        height=680, showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
    )

st.plotly_chart(fig, use_container_width=True, config={"scrollZoom": True})

# ── Fun statistics ────────────────────────────────────────────────────────────
if stats:
    st.divider()
    st.subheader("📊 By the Numbers")

    km = stats["total_km"]
    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown("#### 🌍 Distance Milestones")
        st.metric("Earth circumferences", f"{km / 40_075:.2f} ×")
        st.metric("Way to the Moon",      f"{km / 384_400 * 100:.1f} %")
        st.metric("Hours in the air",     f"{km / 870:,.0f} h")
        st.metric("Estimated CO₂",        f"{km * 0.19 / 1000:.1f} t")

    with col_r:
        st.markdown("#### 🏆 Top Airports")
        top    = stats["visits"].most_common(10)
        labels = [f"{c}  {AIRPORTS[c][2]}" if c in AIRPORTS else c for c, _ in top]
        values = [v for _, v in top]
        bar = go.Figure(go.Bar(
            y=labels, x=values, orientation="h",
            marker_color=route_color, opacity=0.85,
        ))
        bar.update_layout(
            margin=dict(l=0, r=10, t=10, b=0), height=310,
            yaxis=dict(autorange="reversed"),
            xaxis_title="Visits",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(bar, use_container_width=True)

    st.markdown(
        f"**🌏 Regions visited ({stats['n_regions']}):** "
        + " · ".join(stats["regions"])
    )

# ── Full route log ────────────────────────────────────────────────────────────
with st.expander("📋 Full Route Log"):
    rows = []
    for o, d in routes:
        km_val = (dist_km(*AIRPORTS[o][:2], *AIRPORTS[d][:2])
                  if o in AIRPORTS and d in AIRPORTS else None)
        rows.append({
            "Origin":        o,
            "Origin Name":   AIRPORTS[o][2] if o in AIRPORTS else "—",
            "Dest":          d,
            "Dest Name":     AIRPORTS[d][2] if d in AIRPORTS else "—",
            "Distance (km)": f"{km_val:,.0f}" if km_val else "—",
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

if stats.get("missing"):
    with st.expander(f"⚠️ {len(stats['missing'])} airport(s) not in database"):
        st.write("Add them to the AIRPORTS dict in app.py:")
        st.code(", ".join(stats["missing"]))

# ── Footer ────────────────────────────────────────────────────────────────────
st.divider()
st.caption(
    "Built with [Streamlit](https://streamlit.io) & [Plotly](https://plotly.com/python/) · "
    "Satellite imagery © Esri World Imagery (free) · "
    "Great-circle distances via pyproj"
)
