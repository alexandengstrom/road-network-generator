import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import random
from utils import distance
from config import *

connected_cities = set()

class RoadNetwork:
    def __init__(self):
        self.G = nx.Graph()
        self.highway_points = list()

    def generate(self, size=STANDARD_SIZE, seed=0):
        if seed:
            random.seed(seed)
        
        self.layer1 = [(random.randint(0, WIDTH - 1), random.randint(0, HEIGHT - 1)) for _ in range(size)]
        self.layer2 = [(random.randint(0, WIDTH - 1), random.randint(0, HEIGHT - 1)) for _ in range(size*8)]
        self.layer3 = [(random.randint(0, WIDTH - 1), random.randint(0, HEIGHT - 1)) for _ in range(size*16)]
        self.layer4 = [(random.randint(0, WIDTH - 1), random.randint(0, HEIGHT - 1)) for _ in range(size*64)]
        self.layer5 = [(random.randint(0, WIDTH - 1), random.randint(0, HEIGHT - 1)) for _ in range(size*256)]

        self.create_highway_system()
        self.create_city_suburbs()

        self.connect_point_to_nearest_larger_point(self.layer1 + self.highway_points, self.layer2, MAIN_ROAD_COST)
        self.connect_with_closest_points(self.layer2, MAIN_ROAD_COST)
        self.create_clusters(self.layer2, 2, MINOR_ROAD_COST, 2)

        self.connect_point_to_nearest_larger_point(self.layer1 + self.layer2 + self.highway_points, self.layer3, MINOR_ROAD_COST)
        self.create_clusters(self.layer3, 3, RURAL_ROAD_COST, 1)

        self.connect_point_to_nearest_larger_point(self.layer1 + self.layer2 + self.layer3 + self.highway_points, self.layer4, RURAL_ROAD_COST)
        self.create_clusters(self.layer3, 3, SLOW_ROAD_COST, 1)

        self.connect_point_to_nearest_larger_point(self.layer3 + self.layer4, self.layer5, SLOW_ROAD_COST)

        self.add_random_connections(self.layer2, MAIN_ROAD_COST, 5)
        self.add_random_connections(self.layer3 + self.layer4, MINOR_ROAD_COST, 40)

        self.remove_redundant_nodes()

    def create_highway_system(self):
        for x, y in self.layer1:
            neighbours = sorted(self.layer1, key=lambda city: distance(city, (x, y)))
            neighbours = [neigh for neigh in neighbours if neigh != (x, y) and ((x, y), neigh) not in connected_cities]

            to_x, to_y = neighbours[0]
            self.highway_points += self.connect((x, y), (to_x, to_y), HIGHWAY_COST)
            connected_cities.add(((x, y), (to_x, to_y)))
            connected_cities.add(((to_x, to_y), (x, y)))

        self.make_connected()

    def create_city_suburbs(self):
        suburbs = self.create_clusters(self.layer1, 6, MAIN_ROAD_COST, 3)
        villages = self.create_clusters(suburbs, 5, RURAL_ROAD_COST, 1)
        self.create_clusters(suburbs, 10, SLOW_ROAD_COST, 1)

    def create_clusters(self, cities, num_suburbs, cost, spread):
        suburbs = []

        for x, y in cities:
            local_points = list()

            for i in range(num_suburbs):
                new_x = random.randint(max((0, x - WIDTH // (15 - spread))), min((x + WIDTH // (15 - spread), WIDTH - 1)))
                new_y = random.randint(max((0, y - HEIGHT // (15 - spread))), min((y + HEIGHT // (15 - spread), HEIGHT - 1)))
                self.connect((x, y), (new_x, new_y), cost)
                suburbs.append((new_x, new_y))
                local_points.append((new_x, new_y))

            self.add_random_connections(local_points, cost, 2)

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

            if not self.G.has_edge((cur_x, cur_y), (tmp_x, tmp_y)):
                if (cur_x - tmp_x == 0 or cur_y - tmp_y == 0):
                    self.G.add_edge((cur_x, cur_y), (tmp_x, tmp_y), weight=cost)
                else:
                    new_cost = np.sqrt(cost**2 + cost**2)
                    self.G.add_edge((cur_x, cur_y), (tmp_x, tmp_y), weight=new_cost)
            
            cur_x = tmp_x
            cur_y = tmp_y

        return points_on_way
    
    def connect_with_closest_points(self, cities, cost):
        for small_city in cities:
            closest_big_cities = sorted(cities, key=lambda city: distance(city, small_city))[1:2]

            for closest_big_city in closest_big_cities:
                self.connect(small_city, closest_big_city, cost)
                self.G.add_node(small_city)
    
    def make_connected(self):
        while not nx.is_connected(self.G):
            city1 = random.choice(self.layer1)
            city2 = random.choice(self.layer1)

            while city1 == city2:
                city2 = random.choice(self.layer1)

            self.connect(city1, city2, HIGHWAY_COST)

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
        
        for node in self.G.nodes():
            neighbors = list(self.G.neighbors(node))
            if len(neighbors) == 2:
                u, v = neighbors
                weight_u_node = self.G.edges[(u, node)]['weight']
                weight_node_v = self.G.edges[(node, v)]['weight']
                weight_uv = weight_u_node + weight_node_v
                self.G.add_edge(u, v, weight=weight_uv)
                nodes_to_remove.append(node)

        for node in nodes_to_remove:
            self.G.remove_node(node)
    
    def plot(self):
        print(f"Edges: {self.G.number_of_edges()}")
        print(f"Nodes: {self.G.number_of_nodes()}")

        colors = []
        widths = []
        node_sizes = []
        node_colors = []

        for u, v, data in self.G.edges(data=True):
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
            else:
                node_sizes.append(0)
                node_colors.append(EDGE_COLORS[SLOW_ROAD_COST])

        pos = {node: node for node in self.G.nodes()}
        nx.draw(self.G, pos, node_size=node_sizes, node_color=node_colors, edge_color=colors, width=widths, with_labels=False)
        plt.show()
    



graph = RoadNetwork()
graph.generate(size=20, seed=1)
graph.plot()