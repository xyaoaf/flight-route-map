# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the App

```bash
streamlit run app.py --server.port 8501
```

Open http://localhost:8501. There are no tests or lint commands.

## Architecture

Everything lives in `app.py` — a single-file Streamlit app. The flow is:

1. **`AIRPORTS` dict** — the only airport database. Each entry: `"IATA": (lon, lat, "Full Name", "Region")`. If a CSV references an unknown IATA code, add it here.
2. **Data loading** (`load_routes`) — reads `data/my_flight_log.csv` or a user-uploaded CSV. Cached with `@st.cache_data`. CSV must have `origin` and `destination` columns (IATA codes).
3. **`compute_stats`** — derives visit counts, total distance, regions, and missing airports from the route list.
4. **Three rendering modes** (selected via sidebar radio):
   - **Globe** (`🌐`) — `go.Scattergeo` with orthographic projection
   - **Flat Map** (`🗺️`) — `go.Scattergeo` with natural-earth projection
   - **Satellite** (`🛰️`) — `go.Scattermapbox` with Esri World Imagery raster tiles (free, no API key)
5. **Great-circle paths** (`great_circle_path`) — computed via `pyproj.Geod`. Antimeridian crossings are handled by inserting `None` breaks in the lon/lat lists.

## Key Design Decisions

- **Antimeridian gap fix for Satellite mode**: the initial view is centered near `lon=-175` (just east of the antimeridian) so that both Asian and American route segments are inside the same Mapbox viewport. `Scattergeo` handles antimeridian internally; `Scattermapbox` does not.
- **No API keys**: all tile sources must remain free/anonymous. The Esri World Imagery URL is defined as `_ESRI_SAT`.
- **Route deduplication**: routes are normalized with `tuple(sorted(pair))` and counted; width/opacity scale with frequency.
- **Do not modify** `flight_route_map_interactive.ipynb` — it is preserved as the original notebook.

## Adding Airports

Add missing airports to the `AIRPORTS` dict in `app.py`:
```python
"XYZ": (longitude, latitude, "Airport Full Name", "Region"),
```
Valid region values (used for stats grouping): `"East Asia"`, `"Southeast Asia"`, `"Central Asia"`, `"Oceania"`, `"Europe"`, `"North America"`.
