def coordinates_history(sat, step):
    coordinates = sat["mobility_model_parameters"]["next_coordinates"]
    sat["coordinates"] = coordinates[step%len(coordinates)]