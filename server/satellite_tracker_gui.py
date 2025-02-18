from flask import Flask, render_template, jsonify
import threading
import folium

class SatelliteTrackerGUI:
    app = Flask(__name__)
    data = {}
    icons_set = {
        "satellites": {
            "iconUrl": "static/satellite.png",
            "iconSize": [32, 32]
        },
        "ground_stations": {
            "iconUrl": "static/ground_station.png",
            "iconSize": [32, 32]
        },
        "users": {
            "iconUrl": "static/user.png",
            "iconSize": [24, 24]
        },
        "servers": {
            "iconUrl": "static/server.png",
            "iconSize": [30, 30]
        }
    }

    @app.route('/icons.json')
    def get_icons():
        return jsonify(SatelliteTrackerGUI.icons_set)

    def set_data(data):
        SatelliteTrackerGUI.data = data

    @staticmethod
    def generate_map():
        """Generate the base map without markers."""
        m = folium.Map(location=[0, 0], zoom_start=2, tiles="CartoDB dark_matter")
        return m._repr_html_()

    @app.route("/")
    def index():
        return render_template("index.html", map_html=SatelliteTrackerGUI.generate_map())

    @app.route("/update_markers")
    def update_markers():
        """Simulate updated positions and return as JSON."""
        return jsonify(SatelliteTrackerGUI.data)
    
    def run():
        SatelliteTrackerGUI.app.run(debug=True, host="0.0.0.0", port=5000, use_reloader=False)

    def run_deamon():
        SatelliteTrackerGUI.stop_event = threading.Event()
        SatelliteTrackerGUI.server_thread = threading.Thread(target=SatelliteTrackerGUI.run)
        SatelliteTrackerGUI.server_thread.start()
    
    def stop_deamon():
        if SatelliteTrackerGUI.stop_deamon:
            SatelliteTrackerGUI.stop_event.set()

if __name__ == "__main__":
    SatelliteTrackerGUI.run()
