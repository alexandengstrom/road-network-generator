import networkx as nx
import matplotlib.pyplot as plt
import random
from utils import distance, correct_cost
from config import *
import os
from datetime import datetime
import time

connected_cities = set()

class RoadNetwork:
    def __init__(self, width=WIDTH, height=HEIGHT):
        self.G = nx.Graph()
        self.highway_points = list()
        self.cameras = list()
        self.gas_stations = list()
        self.width = width
        self.height = height

    def generate(self, size=STANDARD_SIZE, seed=0, camery_density=5, gas_station_density=5, suburbs_size=5):
        CPU_CPUNT = os.cpu_count()

        start_time = time.time()

        if seed:
            random.seed(seed)

        self.camera_density = camery_density
        self.gas_station_density = gas_station_density
        
        self.create_layers(size)

        self.create_highway_system(size)
        self.create_city_suburbs(suburbs_size)

        if size > 5:
            self.connect_point_to_nearest_larger_point(self.layer1 + self.highway_points, self.layer2, MAIN_ROAD_COST)
            self.connect_with_closest_points(self.layer2, MAIN_ROAD_COST)
            self.create_clusters(self.layer2, 3, MINOR_ROAD_COST, 1)

        if size > 10:
            self.connect_point_to_nearest_larger_point(self.layer1 + self.layer2 + self.highway_points, self.layer3, MINOR_ROAD_COST)
            self.create_clusters(self.layer3, 3, RURAL_ROAD_COST, 1)

        if size > 15:
            self.connect_point_to_nearest_larger_point(self.layer1 + self.layer2 + self.layer3 + self.highway_points, self.layer4, RURAL_ROAD_COST)
            self.create_clusters(self.layer3, 3, SLOW_ROAD_COST, 1)

        if size > 20:
            self.connect_point_to_nearest_larger_point(self.layer3 + self.layer4, self.layer5, SLOW_ROAD_COST)

        self.add_random_connections(self.layer2, MAIN_ROAD_COST, min((size, 5)))

        if size > 15:
            self.add_random_connections(self.layer3 + self.layer4, MINOR_ROAD_COST, 20)
        if size > 10:
            self.add_random_connections(self.layer2 + self.layer3, MINOR_ROAD_COST, 10)
        if size > 5:
            self.add_random_connections(self.layer1 + self.layer2, MINOR_ROAD_COST, 7)
        else:
            self.add_random_connections(self.layer1 + self.layer2, MINOR_ROAD_COST, 3)

        self.make_connected(self.layer1 + self.layer2 + self.layer3 + self.layer4 + self.layer5, RURAL_ROAD_COST)

        while self.remove_redundant_nodes():
            pass

        end_time = time.time()
        self.display_graph_creation_info(end_time - start_time)
        

    def display_graph_creation_info(self, time_elapsed):
        print(f"Created graph with {self.G.number_of_nodes()} vertices and {self.G.number_of_edges()} edges in {round(time_elapsed, 2)} seconds")


    def create_layers(self, size):
        self.layer1 = [(random.randint(0, self.width - 1), random.randint(0, self.height - 1)) for _ in range(size)]
        self.layer2 = [(random.randint(0, self.width - 1), random.randint(0, self.height - 1)) for _ in range(size*8)]
        self.layer3 = [(random.randint(0, self.width - 1), random.randint(0, self.height - 1)) for _ in range(size*16)]
        self.layer4 = [(random.randint(0, self.width - 1), random.randint(0, self.height - 1)) for _ in range(size*64)]
        self.layer5 = [(random.randint(0, self.width - 1), random.randint(0, self.height - 1)) for _ in range(size*256)]

    def create_highway_system(self, size):
        for x, y in self.layer1:
            neighbours = sorted(self.layer1, key=lambda city: distance(city, (x, y)))
            neighbours = [neigh for neigh in neighbours if neigh != (x, y) and ((x, y), neigh) not in connected_cities or (neigh, (x, y) not in connected_cities)]

            if not neighbours:
                return
            
            to_x, to_y = neighbours[0]
            self.highway_points += self.connect((x, y), (to_x, to_y), HIGHWAY_COST)
            connected_cities.add(((x, y), (to_x, to_y)))
            connected_cities.add(((to_x, to_y), (x, y)))
        
        self.connect_with_others(self.layer1, HIGHWAY_COST, num=2)
        
        self.make_connected(self.layer1, HIGHWAY_COST)

    def create_city_suburbs(self, size):
        city_size = random.randint(1, 3)
        suburbs = self.create_clusters(self.layer1, size, MAIN_ROAD_COST, size // city_size)
        villages = self.create_clusters(suburbs, size, RURAL_ROAD_COST, size//2)
        self.create_clusters(villages, size//2, STREET_COST, size//2)

    def create_clusters(self, cities, num_suburbs, cost, spread):
        suburbs = []

        for x, y in cities:
            local_points = list()

            for _ in range(num_suburbs):
                new_x = random.randint(max((0, x - self.width // (15 - spread))), min((x + self.width // (15 - spread), self.width - 1)))
                new_y = random.randint(max((0, y - self.height // (15 - spread))), min((y + self.height // (15 - spread), self.height - 1)))
                self.connect((x, y), (new_x, new_y), cost)
                suburbs.append((new_x, new_y))
                local_points.append((new_x, new_y))

            self.add_random_connections(local_points, cost, 2)
            self.add_random_connections(local_points, STREET_COST, 3)

        return suburbs
    
    def connect(self, city1, city2, cost):
        cur_x, cur_y = city1
        to_x, to_y = city2

        points_on_way = []

        while cur_x != to_x or cur_y != to_y:
            tmp_x = cur_x
            tmp_y = cur_y

            if cur_x > to_x:
                tmp_x -= 1
            elif cur_x < to_x:
                tmp_x += 1

            if cur_y > to_y:
                tmp_y -= 1
            elif cur_y < to_y:
                tmp_y += 1

            if not self.G.has_node((tmp_x, tmp_y)):
                self.G.add_node((tmp_x, tmp_y))
                if random.randint(1, 10) > 9:
                    points_on_way.append((tmp_x, tmp_y))

                if random.randint(0, 10000) < self.camera_density:
                    self.cameras.append((tmp_x, tmp_y))

            if not self.G.has_edge((cur_x, cur_y), (tmp_x, tmp_y)):
                cor_cost = correct_cost(cur_x, tmp_x, cur_y, tmp_y, cost)
                self.G.add_edge((cur_x, cur_y), (tmp_x, tmp_y), weight=cor_cost)

            if (cost == HIGHWAY_COST or cost == MAIN_ROAD_COST) and random.randint(1, 100) < self.gas_station_density:
                self.gas_stations.append(((tmp_x, tmp_y)))
            
            cur_x = tmp_x
            cur_y = tmp_y

        return points_on_way
    
    def connect_with_closest_points(self, cities, cost):
        for small_city in cities:
            closest_big_cities = sorted(cities, key=lambda city: distance(city, small_city))[1:1]

            for closest_big_city in closest_big_cities:
                self.connect(small_city, closest_big_city, cost)
                self.G.add_node(small_city)

    def connect_with_others(self, cities, cost, num=2):
        if random.randint(0, 1 < 1):
            return
        
        for small_city in cities:
            closest_big_cities = sorted(cities, key=lambda city: distance(city, small_city))[2:num+1]

            for closest_big_city in closest_big_cities:
                self.connect(small_city, closest_big_city, cost)
                self.G.add_node(small_city)
    
    def make_connected(self, layers, cost):
        if len(layers) == 1:
            return

        while not nx.is_connected(self.G):
            city1 = random.choice(layers)
            city2 = random.choice(layers)

            while city1 == city2:
                city2 = random.choice(layers)

            self.connect(city1, city2, cost)

    def connect_point_to_nearest_larger_point(self, points, small_points, cost):
        for small_point in small_points:
            closest_big_city = min(points, key=lambda city: distance(city, small_point))
            self.connect(small_point, closest_big_city, cost)
            self.G.add_node(small_point)

    def add_random_connections(self, points, cost, connections):
        for _ in range(connections):
            city1 = random.choice(points)
            city2 = random.choice(points)

            while city1 == city2:
                city2 = random.choice(points)

            self.connect(city1, city2, cost)

    def remove_redundant_nodes(self):
        nodes_to_remove = []
        removed = False
        
        for node in self.G.nodes():
            neighbors = list(self.G.neighbors(node))
            if len(neighbors) == 2:
                u, v = neighbors
                weight_u_node = self.G.edges[(u, node)]['weight']
                weight_node_v = self.G.edges[(node, v)]['weight']
                weight_uv = weight_u_node + weight_node_v
                self.G.add_edge(u, v, weight=weight_uv)
                nodes_to_remove.append(node)
                removed = True

        for node in nodes_to_remove:
            self.G.remove_node(node)

        return removed
    
    def plot_old(self, show_gas_stations=False, show_cameras=False):
        colors = []
        self.widths = []
        node_sizes = []
        node_colors = []

        for u, v, data in self.G.edges(data=True):
            distance_uv = distance(u, v)
            avg_cost = data["weight"] / distance_uv

            for cost, color in EDGE_COLORS.items():
                if avg_cost < cost + 0.2:
                    colors.append(color)
                    self.widths.append(EDGE_SIZES[cost])
                    break
            else:
                colors.append(EDGE_COLORS[SLOW_ROAD_COST])
                self.widths.append(EDGE_SIZES[SLOW_ROAD_COST])

        for node in self.G.nodes():
            if node in self.layer1:
                node_sizes.append(200)
                node_colors.append(EDGE_COLORS[HIGHWAY_COST])
            elif node in self.layer2:
                node_sizes.append(50)
                node_colors.append(EDGE_COLORS[MAIN_ROAD_COST])
            elif node in self.layer3:
                node_sizes.append(20)
                node_colors.append(EDGE_COLORS[MINOR_ROAD_COST])
            elif show_cameras and node in self.cameras:
                node_sizes.append(200)
                node_colors.append("red")
            elif show_gas_stations and node in self.gas_stations:
                node_sizes.append(50)
                node_colors.append("blue")
            else:
                node_sizes.append(0)
                node_colors.append(EDGE_COLORS[SLOW_ROAD_COST])

        pos = {node: node for node in self.G.nodes()}
        nx.draw(self.G, pos, node_size=node_sizes, node_color=node_colors, edge_color=colors, width=self.widths, with_labels=False)
        plt.show()

    def plot(self, show_gas_stations=False, show_cameras=False):
        colors = []
        widths = []
        node_sizes = []
        node_colors = []

        pos = {node: node for node in self.G.nodes()}

        # Sort the edges in so we plot the slowest roads first. This is so we can clearly see the highways.
        edges = sorted(self.G.edges(data=True), reverse=True, key=lambda x: x[2]["weight"] / distance(x[0], x[1]))

        for u, v, data in edges:
            distance_uv = distance(u, v)
            avg_cost = data["weight"] / distance_uv

            for cost, color in EDGE_COLORS.items():
                if avg_cost < cost + 0.2:
                    colors.append(color)
                    widths.append(EDGE_SIZES[cost])
                    break
            else:
                colors.append(EDGE_COLORS[SLOW_ROAD_COST])
                widths.append(EDGE_SIZES[SLOW_ROAD_COST])

        nx.draw_networkx_edges(self.G, pos, edgelist=edges, edge_color=colors, width=widths)

        for node in self.G.nodes():
            if node in self.layer1:
                node_sizes.append(200)
                node_colors.append(EDGE_COLORS[HIGHWAY_COST])
            elif node in self.layer2:
                node_sizes.append(50)
                node_colors.append(EDGE_COLORS[MAIN_ROAD_COST])
            elif node in self.layer3:
                node_sizes.append(20)
                node_colors.append(EDGE_COLORS[MINOR_ROAD_COST])
            elif show_cameras and node in self.cameras:
                node_sizes.append(200)
                node_colors.append("red")
            elif show_gas_stations and node in self.gas_stations:
                node_sizes.append(50)
                node_colors.append("blue")
            else:
                node_sizes.append(0)
                node_colors.append(EDGE_COLORS[SLOW_ROAD_COST])

        nx.draw_networkx_nodes(self.G, pos, node_size=node_sizes, node_color=node_colors)
        plt.show()

    def output_to_file(self, filename=None): 
        if not filename:
            current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = os.path.join("graph_files", f"road_network_{current_time}.txt")
        
        os.makedirs(os.path.dirname(filename), exist_ok=True)
            
        with open(filename, 'w') as f:
            f.write(f"Number of nodes: {self.G.number_of_nodes()}\n")
            f.write(f"Number of edges: {self.G.number_of_edges()}\n\n")
                
            for node in self.G.nodes():
                x, y = node
                if node in self.layer1:
                    importance_factor = 1
                elif node in self.layer2:
                    importance_factor = 2
                elif node in self.layer3:
                    importance_factor = 3
                elif node in self.layer4:
                    importance_factor = 4
                elif node in self.layer5:
                    importance_factor = 5
                elif node in self.cameras:
                    importance_factor = 0
                if node in self.gas_stations:
                    importance_factor = 7
                else: importance_factor = -1
                    
                f.write(f"{x} {y} {importance_factor}\n")
                
            f.write("\n")
                
            for edge in self.G.edges():
                from_x, from_y = edge[0]
                to_x, to_y = edge[1]
                cost = round(self.G.edges[edge]['weight'], 2)
                f.write(f"{from_x} {from_y} {to_x} {to_y} {cost}\n")


    def __len__(self):
        return len(self.G.nodes())
    
    def __str__(self):
        return f"RoadNetwork with {self.G.number_of_nodes()} nodes and {self.G.number_of_edges()} edges"

    def __iter__(self):
        return iter(self.G.nodes())

    def __getitem__(self, node):
        if node not in self.G:
            raise KeyError(f"Node {node} not found in the road network")
        
        return self.G[node]

    def __contains__(self, node):
        return node in self.G
    

    def __eq__(self, other):
        if not isinstance(other, RoadNetwork):
            return False
        
        if (self.G.nodes() != other.G.nodes()) or \
        (self.G.edges() != other.G.edges()) or \
        (len(self.highway_points) != len(other.highway_points)) or \
        (len(self.cameras) != len(other.cameras)):
            return False
        
        return True


    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.G.number_of_nodes(), self.G.number_of_edges()))

    def __getitem__(self, node):
        if node not in self.G:
            raise KeyError(f"Node {node} not found in the road network")
        return self.G[node]

    def __add__(self, other):
        if not isinstance(other, RoadNetwork):
            raise TypeError("Can only add RoadNetwork instances")
        new_network = RoadNetwork()
        new_network.G = nx.compose(self.G, other.G)
        new_network.highway_points = self.highway_points + other.highway_points
        new_network.layer1 = self.layer1 + other.layer1
        new_network.layer2 = self.layer2 + other.layer2
        new_network.layer3 = self.layer3 + other.layer3
        new_network.layer4 = self.layer4 + other.layer4
        new_network.layer5 = self.layer5 + other.layer5
        new_network.cameras = self.cameras + other.cameras
        new_network.gas_stations = self.gas_stations + other.gas_stations
        return new_network
                    
    


graph1 = RoadNetwork()
graph1.generate(seed=52, size=25, camery_density=5, gas_station_density=5)


graph1.plot(show_cameras=False, show_gas_stations=False)