# ✈️ Flight Route Map

Interactive visualization of personal flight history — great-circle arcs on a map, with statistics and multiple base-map styles.

---

## Quick Start (Streamlit App)

```bash
pip install -r requirements.txt
streamlit run app.py
```

Open http://localhost:8501 in your browser.

## Features

| Feature | Details |
|---|---|
| **Base maps** | Satellite (Esri), Street Map, Dark, Light, Topo — no API key needed |
| **Route colors** | 8 color themes, routes scale in width/opacity by frequency |
| **Airport markers** | Bubble size = visit count; hover for details |
| **Focus region** | Asia-Pacific (default), North America, Europe, World |
| **Statistics** | Flights, airports, distance, countries, CO₂ estimate, Earth laps |
| **Top airports** | Horizontal bar chart of most-visited airports |
| **Route log** | Expandable table of every flight with distance |
| **Custom data** | Upload your own CSV (columns: `origin`, `destination`) |

## Data Format

```csv
origin,destination
HKG,SFO
SFO,AUS
AUS,OAK
```

IATA 3-letter codes only. Dates are optional (not yet used).

## Project Structure

```
flight-route-map/
├── app.py                            # Streamlit web app  ← START HERE
├── flight_route_map_interactive.ipynb # Original Jupyter notebook (preserved)
├── data/
│   └── my_flight_log.csv             # Flight log (edit to add your own flights)
├── requirements.txt
└── .streamlit/
    └── config.toml                   # Dark-theme defaults
```

## Adding Airports

If you see a warning about unknown IATA codes, add them to the `AIRPORTS` dict in `app.py`:

```python
"XYZ": (longitude, latitude, "Airport Full Name", "Country"),
```

## Dependencies

- [Streamlit](https://streamlit.io) — web app framework
- [Plotly](https://plotly.com/python/) — interactive maps and charts
- [pyproj](https://pyproj4.github.io/pyproj/) — great-circle geodesics
- [pandas](https://pandas.pydata.org/) — CSV parsing

For the original Jupyter notebook, install via conda:
```bash
conda install -c conda-forge basemap basemap-data-hires matplotlib ipywidgets
```
