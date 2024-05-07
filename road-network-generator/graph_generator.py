import networkx as nx
import matplotlib.pyplot as plt
import random
from utils import distance, correct_cost, interpolate_points, point_inside_circle
from config import *
import os
from datetime import datetime
import time
from city import Metropolis, UrbanCenter, Town, Village, Hamlet, BaseCity

city_connections = dict()

METROPOLIS = 1
URBAN_CENTER = 2
TOWN = 3
VILLAGE = 4
HAMLET = 5
SUBURB = 6

class RoadNetwork:
    def __init__(self, width=WIDTH, height=HEIGHT):
        self.G = nx.Graph()
        self.highway_points = list()
        self.cameras = list()
        self.gas_stations = list()
        self.important_points = list()
        self.width = width
        self.height = height
        self.poi = {}

    def add_important_points(self, points):
        self.important_points += points

    def add_points_of_interest(self, points):
        for key, value in points.items():
            if key not in self.poi:
                self.poi[key] = value

    def generate_cities(self, size):
        self.towns = []
        self.metropolitans = self.create_city_objects(Metropolis, size, size)
        self.urban_centers = self.create_city_objects(UrbanCenter, size*2, size)
        #self.towns += self.create_city_objects(Town, size*4, size)

        #self.layer1 = [(random.randint(0, self.width - 1), random.randint(0, self.height - 1)) for _ in range(size)]

    def create_city_objects(self, Type, size, map_size):
        points = list()

        for _ in range(size):
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            pos = (x, y)
            point = Type(pos, self, map_size)
            points.append(point)
            self.poi[point.pos] = Type
            self.add_points_of_interest(point.get_points_of_interest())

            city_connections[pos] = dict()
            city_connections[pos][pos] = True

        return points
    
    def get_coordinates(self, points):
        return list(map(lambda city: city.pos, points))
    
    def decide_number_of_cities(self, size):
        metropolitans = 0
        urban_areas = 0

        if size > 10:
            metropolitans = size
            urban_areas = size * 2
        elif size > 5:
            metropolitans = 5
            urban_areas = 3
        elif size > 2:
            metropolitans = 4
            urban_areas = 8
        elif size > 1:
            metropolitans = 3
            urban_areas = 7
        else:
            metropolitans = 5

        return metropolitans, urban_areas
            
    def generate(self, size=STANDARD_SIZE, seed=0, camery_density=5, gas_station_density=5, suburbs_size=5):
        start_time = time.time()

        if seed:
            random.seed(seed)

        self.camera_density = camery_density
        self.gas_station_density = gas_station_density
        
        num_metropolitans, num_urban_areas = self.decide_number_of_cities(size)

        self.towns = list()
        self.villages = list()
        self.hamlets = list()
        
        self.metropolitans = self.create_city_objects(Metropolis, num_metropolitans, size)
        self.urban_centers = self.create_city_objects(UrbanCenter, num_urban_areas, size)
        self.create_highway_system(size)

        main_connections = self.get_coordinates(self.metropolitans + self.urban_centers)
        main_connections += self.highway_points

        all_poi = main_connections

        if size > 15:
            self.add_random_connections(self.get_coordinates(self.towns), MINOR_ROAD_COST, size, 40)
        
        if size > 5:
            self.towns += self.create_city_objects(Town, size*4, size)
            self.connect_point_to_nearest_larger_point(main_connections, self.get_coordinates(self.towns), MINOR_ROAD_COST, 20, 10)
            town_cors = self.get_coordinates(self.towns)
            all_poi += town_cors
            self.add_random_connections(town_cors, MINOR_ROAD_COST, size, 40)
        if size > 8:
            self.villages = self.create_city_objects(Village, size*8, size)
            village_cors = self.get_coordinates(self.villages)
            all_poi += village_cors
            self.connect_point_to_nearest_larger_point(main_connections + self.get_coordinates(self.towns), village_cors, RURAL_ROAD_COST, 20, 10)
            self.add_random_connections(self.get_coordinates(self.villages), RURAL_ROAD_COST, size, 40)

        if size > 12:
            self.hamlets = self.create_city_objects(Hamlet, size*16, size)
            hamlet_cors = self.get_coordinates(self.hamlets)

            connections = main_connections + self.get_coordinates(self.towns) + self.get_coordinates(self.villages)
            self.connect_point_to_nearest_larger_point(all_poi, hamlet_cors, RURAL_ROAD_COST, 20, 10)
            all_poi += hamlet_cors
            self.add_random_connections(all_poi, MINOR_ROAD_COST, size * 50, size)
            self.add_random_connections(all_poi, RURAL_ROAD_COST, size * 100, size)

        

        #self.create_highway_system(size)
        # print("Generated layer 1")
        
        # print("Generated suburbs")

        # if size > 5:
        #     self.connect_point_to_nearest_larger_point(self.layer1 + self.highway_points, self.layer2, MAIN_ROAD_COST, 20, 10)
        #     self.connect_with_closest_points(self.layer2, MAIN_ROAD_COST)
        #     self.generate_streets(self.layer2, 30, 10)
        #     self.create_clusters(self.layer2, 3, MINOR_ROAD_COST, 1)
        #     print("Generated layer 2")

        # if not size > 10:
        #     self.layer3 = self.layer3[:len(self.layer3) // (size // 2)]

        # self.connect_point_to_nearest_larger_point(self.layer1 + self.layer2 + self.highway_points, self.layer3, MINOR_ROAD_COST, 10, 5)
        # self.create_clusters(self.layer3, 6, RURAL_ROAD_COST, 1)
        # self.generate_streets(self.layer3, 20, 8)
        # print("Generated layer 3")
        
        # if not size > 15:
        #     self.layer4 = self.layer4[:len(self.layer4) // (size // 2)]

        # self.connect_point_to_nearest_larger_point(self.layer1 + self.layer2 + self.layer3 + self.highway_points, self.layer4, RURAL_ROAD_COST)
        # self.create_clusters(self.layer4, 3, SLOW_ROAD_COST, 1)
        # self.generate_streets(self.layer4, 20, 5)
        # print("Generated layer 4")

        # tmp = self.layer5
        # if not size > 20:
        #     self.layer5 = self.layer5[:len(self.layer5) // (size // 2)]

        # self.connect_point_to_nearest_larger_point(self.layer3 + self.layer4, self.layer5, SLOW_ROAD_COST)
        # print("Generated layer 5")

        # self.create_city_suburbs(suburbs_size, size)

        
        
        

        # if size > 15:
        #     self.add_random_connections(self.layer3 + self.layer4, MINOR_ROAD_COST, 20)
        # if size > 10:
        #     self.add_random_connections(self.layer2 + self.layer3, MINOR_ROAD_COST, 10)
        # if size > 5:
        #     self.add_random_connections(self.layer1 + self.layer2, MINOR_ROAD_COST, 7)
        # else:
        #     self.add_random_connections(self.layer1 + self.layer2, MINOR_ROAD_COST, 3)

        # print("Generated random connections")


        self.make_connected(all_poi, SLOW_ROAD_COST, strict=False)
        # #self.make_connected(self.layer1 + self.layer2 + self.layer3 + self.layer4 + self.layer5, RURAL_ROAD_COST)
        
        before = self.G.number_of_edges()
        self.remove_redundant_nodes()
        after = self.G.number_of_edges()
        print(f"Removed {before - after} redundant nodes")

        end_time = time.time()
        self.display_graph_creation_info(end_time - start_time)
        

    def display_graph_creation_info(self, time_elapsed):
        print(f"Created graph with {self.G.number_of_nodes()} vertices and {self.G.number_of_edges()} edges in {round(time_elapsed, 2)} seconds")


    def create_layers(self, size):
        self.layer1 = [(random.randint(0, self.width - 1), random.randint(0, self.height - 1)) for _ in range(size)]
        self.layer2 = [(random.randint(0, self.width - 1), random.randint(0, self.height - 1)) for _ in range(size*8)]
        self.layer3 = [(random.randint(0, self.width - 1), random.randint(0, self.height - 1)) for _ in range(size*16)]
        self.layer4 = [(random.randint(0, self.width - 1), random.randint(0, self.height - 1)) for _ in range(size*50)]
        self.layer5 = [(random.randint(0, self.width - 1), random.randint(0, self.height - 1)) for _ in range(size*50)]

        top_levels = self.layer1 + self.layer2 + self.layer3 + self.layer4

        for x, y in top_levels:
            city_connections[(x, y)] = {(dx, dy): True if (x, y) == (dx, dy) else False for dx, dy in top_levels}

    def create_highway_system(self, size):
        cities_to_connect = self.metropolitans + self.urban_centers
        cities_to_connect = list(map(lambda city: city.pos, cities_to_connect))

        for point in cities_to_connect:
            x, y = point
            neighbours = sorted(cities_to_connect, key=lambda city: distance(city, (x, y)))
            neighbours = list(filter(lambda city: city not in city_connections[point], neighbours))

            if not neighbours:
                return
            
            to_x, to_y = neighbours[0]
            self.highway_points += self.connect_with_potential_stop((x, y), (to_x, to_y), cities_to_connect, HIGHWAY_COST, 10, 50)
            #self.highway_points += self.connect((x, y), (to_x, to_y), HIGHWAY_COST)
        
        #self.connect_with_others(self.layer1, HIGHWAY_COST, num=2)
        
        self.make_connected(cities_to_connect, HIGHWAY_COST)

    def generate_streets(self, points, radius, num):
        for point in points:
            local_points = []
            for _ in range(num):
                new_x = random.randint(max((0, point[0] - radius)), min((point[0] + radius, self.width - 1)))
                new_y = random.randint(max((0, point[1] - radius)), min((point[1] + radius, self.height - 1)))
                n_point = (new_x, new_y)
                way_points = self.connect(point, n_point, STREET_COST)
                for w_point in way_points:
                    for _ in range(num // 2):
                        w_new_x = random.randint(max((0, w_point[0] - radius//2)), min((w_point[0] + radius//2, self.width - 1)))
                        w_new_y = random.randint(max((0, w_point[1] - radius//2)), min((w_point[1] + radius//2, self.height - 1)))
                        w_n_point = (w_new_x, w_new_y)
                        way_points2 = self.connect(w_point, w_n_point, STREET_COST)


    def create_city_suburbs(self, size, graph_size):
        city_size = random.randint(1, 3)
        self.generate_streets(self.layer1, 50, 20)
        suburbs = self.create_clusters(self.layer1, size, MAIN_ROAD_COST, size // (city_size * 2))
        self.generate_streets(suburbs, 20, 7)
        villages = self.create_clusters(suburbs, size, RURAL_ROAD_COST, size//2)
        #self.create_clusters(villages, 5, STREET_COST, size//2)
        self.generate_streets(villages, 15, 7)

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

            #self.add_random_connections(local_points, cost, 2)
            #self.add_random_connections(local_points, STREET_COST, 3)

        return suburbs
    
    def connect(self, city1, city2, cost, curvature=0.2):
        if city1 in city_connections and city2 in city_connections:
            if city_connections[city1].get(city2):
                return []
            
            city_connections[city1][city2] = True
            city_connections[city2][city1] = True

        middle1 = self.calculate_midpoint(city1, city2, curvature)
        middle2 = self.calculate_midpoint(city1, middle1, curvature)
        middle3 = self.calculate_midpoint(middle1, city2, curvature)

        way_points = self.connect_helper(city1, middle2, cost)
        way_points += self.connect_helper(middle2, middle1, cost)
        way_points += self.connect_helper(middle1, middle3, cost)
        way_points += self.connect_helper(middle3, city2, cost)
        return way_points

    def calculate_midpoint(self, city1, city2, curvature):
        mid_x = (city1[0] + city2[0]) / 2
        mid_y = (city1[1] + city2[1]) / 2
        
        offset_x = random.uniform(-curvature, curvature)
        offset_y = random.uniform(-curvature, curvature)

        if random.randint(0, 10) < 1:
            offset_x += random.randint(-10, 10)

        if random.randint(0, 10) < 1:
            offset_y += random.randint(-10, 10)
        
        mid_x += offset_x
        mid_y += offset_y

        mid_x = max(0, min(self.width - 1, mid_x))
        mid_y = max(0, min(self.height - 1, mid_y))
        
        mid_x = int(mid_x)
        mid_y = int(mid_y)

        return mid_x, mid_y

    
    def connect_helper(self, city1, city2, cost):
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

                if random.randint(0, 10000) < self.camera_density and cost <= RURAL_ROAD_COST:
                    self.cameras.append((tmp_x, tmp_y))

            new_cost = correct_cost(cur_x, tmp_x, cur_y, tmp_y, cost)

            if self.G.has_edge((cur_x, cur_y), (tmp_x, tmp_y)):
                edge_data = self.G.get_edge_data((cur_x, cur_y), (tmp_x, tmp_y))
                if edge_data:
                    old_cost = edge_data['weight']
                    
                    if new_cost < old_cost:
                        self.G.add_edge((cur_x, cur_y), (tmp_x, tmp_y), weight=new_cost)
            else:
                self.G.add_edge((cur_x, cur_y), (tmp_x, tmp_y), weight=new_cost)

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
    
    def make_connected(self, layers, cost, strict=True):
        while not nx.is_connected(self.G):
            components = list(nx.connected_components(self.G))
            print(len(components))

            if not strict:
                index = random.randint(0, len(components) - 1)
                nodes_to_connect = [list(component)[index] for component in components]

                city1 = random.randint(0, len(nodes_to_connect) - 1)
                city2 = random.randint(0, len(nodes_to_connect) - 1)

                while city1 == city2:
                    city2 = random.randint(0, len(nodes_to_connect) - 1)

                self.connect(nodes_to_connect[city1], nodes_to_connect[city2], cost=cost)
                continue
            
            nodes_to_connect = [list(filter(lambda city: city in layers, component)) for component in components]

            flag = False
            for i in range(len(nodes_to_connect[0])):
                flag = False
                for j in range(len(nodes_to_connect[1])):
                    way_points = self.connect_with_potential_stop(nodes_to_connect[0][i], nodes_to_connect[1][j], layers, cost, 20, 50)

                    if len(way_points) > 0:
                        self.highway_points += way_points
                        flag = True
                        break
                if flag:
                    break

                if not flag:
                # If we couldnt find a good way to connect
                    self.highway_points = self.connect(nodes_to_connect[0][0], nodes_to_connect[1][0], cost=cost)

            

            

    def connect_with_potential_stop(self, start, target, potential_conns, cost, curvature, precision):
        way_points = []

        flag = False
        if precision:
            points_between = interpolate_points(start, target, precision)
            for origin in points_between:
                for potential_conn in potential_conns:
                    if point_inside_circle(potential_conn, origin, 50, target) and potential_conn != start:
                        if city_connections.get(potential_conn) and city_connections[potential_conn].get(start):
                            return way_points
                        
                        way_points += self.connect(start, potential_conn, cost, curvature)
                        self.G.add_node(start)
                        flag = True
                        break
                if flag:
                    break
            
        if not flag:
            way_points += self.connect(start, target, cost, curvature)
            self.G.add_node(start)

        return way_points

    def connect_point_to_nearest_larger_point(self, points, small_points, cost, curvature=5, precision=None):
        way_points = list()

        for small_point in small_points:
            closest_big_city = min(points, key=lambda city: distance(city, small_point))
            way_points += self.connect_with_potential_stop(small_point, closest_big_city, small_points, cost, curvature, precision)

        return way_points

    def find_middle_points(self):
        pass

    def add_random_connections(self, points, cost, connections, precision=None):
        for _ in range(connections):
            city1 = random.choice(points)
            city2 = random.choice(points)

            while city1 == city2:
                city2 = random.choice(points)

            self.connect_with_potential_stop(city1, city2, points, cost, 10, precision)

    def remove_redundant_nodes(self):
        removed = True
        
        while removed:
            removed = False
            nodes_to_remove = []

            for node in self.G.nodes():
                neighbors = list(self.G.neighbors(node))
                if len(neighbors) == 2 and node not in city_connections and node not in self.important_points:
                    u, v = neighbors
                    weight_u_node = self.G.edges[(u, node)]['weight']
                    weight_node_v = self.G.edges[(node, v)]['weight']
                    weight_uv = weight_u_node + weight_node_v
                    self.G.add_edge(u, v, weight=weight_uv)
                    nodes_to_remove.append(node)
                    removed = True

            for node in nodes_to_remove:
                self.G.remove_node(node)

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
            node_type = self.poi.get(node, BaseCity)
            if node_type == Metropolis:
                node_sizes.append(200)
                node_colors.append(EDGE_COLORS[HIGHWAY_COST])
            elif node_type == UrbanCenter:
                 node_sizes.append(50)
                 node_colors.append(EDGE_COLORS[MAIN_ROAD_COST])
            elif node_type == Town:
                 node_sizes.append(20)
                 node_colors.append(EDGE_COLORS[MINOR_ROAD_COST])
            elif node_type == Village:
                node_sizes.append(10)
                node_colors.append(EDGE_COLORS[RURAL_ROAD_COST])
            elif node_type == Hamlet:
                node_sizes.append(7)
                node_colors.append(EDGE_COLORS[SLOW_ROAD_COST])
            elif show_cameras and node in self.cameras:
                node_sizes.append(100)
                node_colors.append("red")
            # elif show_gas_stations and node in self.gas_stations:
            #     node_sizes.append(50)
            #     node_colors.append("blue")
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
                    





