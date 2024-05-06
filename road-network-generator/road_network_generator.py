from graph_generator import RoadNetwork
import plotter

graph1 = RoadNetwork()
graph1.generate(seed=2999911, size=15, camery_density=40, gas_station_density=5, suburbs_size=5)
plotter.plot(graph1, show_cameras=True)

#graph1.plot(show_cameras=False, show_gas_stations=False)