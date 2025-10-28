flight-route-map

This directory contains a small, self-contained project to visualize your past flights as great-circle routes on a world map.

Layout

- `flight_route_map.py` - A script that draws flight routes and saves `img/example_map.png`. It will read `data/my_flight_log.csv` if present.
 - `flight_route_map_interactive.ipynb` - An interactive Plotly notebook that renders routes inline and accepts pasted/uploaded route lists.
- `data/my_flight_log.csv` - Optional CSV with flight log (columns: origin,destination,date). Example provided.
- `img/example_map.png` - Output image (placeholder). The script writes here by default.
- `requirements.txt` - Minimal Python dependencies for this project.

Quick start (recommended using conda on Windows)

1. Create or activate a conda env:

   conda create -n flightmap python=3.10 -y; conda activate flightmap

2. Install dependencies:

   conda install -c conda-forge basemap basemap-data-hires matplotlib -y

   Also install ipywidgets if you plan to use the notebook UI: `conda install -c conda-forge ipywidgets -y`

3. Populate your flight log (optional):

   Edit `data/my_flight_log.csv` or leave it as-is. The CSV format should be: `origin,destination,date` (date optional).

4. Run the script:

   python flight_route_map.py

   The script will write `img/example_map.png` and print any missing airport codes.

Notes

- Basemap is deprecated; if you'd like I can convert the script and notebook to use Cartopy instead.
- If you want the notebook UI version, you already have `myFlights/flight_route_map_notebook.ipynb` in the repository; I can copy/convert it into this folder if you prefer.
