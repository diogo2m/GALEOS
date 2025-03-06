def coordinates_history(sat, step):
    sat.coordinates = sat.coordinates_trace[(sat.model.scheduler.steps + 1) % len(sat.coordinates_trace)]