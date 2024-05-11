import networkx as nx
import random
from utils import distance, correct_cost, interpolate_points, point_inside_circle, calculate_midpoint, divide_into_squares, find_closest_pair, randomize_cost, find_closest
from config import *
import time
from city import Metropolis, UrbanCenter, Town, Village, Hamlet

city_connections = dict()

METROPOLIS = 1
URBAN_CENTER = 2
TOWN = 3
VILLAGE = 4
HAMLET = 5
SUBURB = 6
CAMERA = 7

class RoadNetwork:
    def __init__(self, width=WIDTH, height=HEIGHT):
        self.G = nx.Graph()
        self.highway_points = list()
        self.cameras = list()
        self.important_points = list()
        self.towns = list()
        self.width = width
        self.height = height
        self.poi = {}

    def get_node_type(self, node):
        node_type = self.poi.get(node)
        if node_type == Metropolis:
            return METROPOLIS
        elif node_type == UrbanCenter:
                return URBAN_CENTER
        elif node_type == Town:
                return TOWN
        elif node_type == Village:
            return VILLAGE
        elif node_type == Hamlet:
            return HAMLET
        elif node in self.cameras:
            return CAMERA
        else:
            return 0

    def number_of_nodes(self):
        return self.G.number_of_nodes()
    
    def number_of_edges(self):
        return self.G.number_of_edges()
    
    def nodes(self):
        return self.G.nodes()
    
    def edges(self):
        return self.G.edges(data=True)

    def add_important_points(self, points):
        self.important_points += points

    def add_points_of_interest(self, points):
        for key, value in points.items():
            if key not in self.poi:
                self.poi[key] = value

    def get_main_connections(self):
        return self.get_coordinates(self.metropolitans + self.urban_centers) + self.highway_points

    def create_city_objects(self, Type, size, map_size):
        points = list()
        positions = list()

        for _ in range(size):
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            pos = (x, y)
            point = Type(pos, self, map_size)

            too_close = False
            for prev_pos in positions:
                if distance(pos, prev_pos) < 50:
                    too_close = True
                    break
            if too_close:
                continue

            points.append(point)
            positions.append(pos)
            self.poi[point.pos] = Type
            self.add_points_of_interest(point.get_points_of_interest())

            city_connections[pos] = dict()
            city_connections[pos][pos] = True

        return points
    
    def get_coordinates(self, points):
        return list(map(lambda city: city.pos, points))
    
    def generate_back_bone(self):
        num_big_cities = 10 if self.size < 10 else self.size
        
        self.metropolitans = self.create_city_objects(Metropolis, num_big_cities, self.size)
        self.urban_centers = self.create_city_objects(UrbanCenter, num_big_cities, self.size)
        self.create_highway_system()
        self.log("Generated highway system")

        for city in self.metropolitans + self.urban_centers:
            city.generate(self.size)


        self.log("Generated big cities")
    
    def generate_towns(self):
        self.create_city_objects(Town, self.size * 8, self.size)
        town_cors = self.get_towns()
        main_cors = self.get_main_connections()

        self.connect_point_to_nearest_larger_point(main_cors, town_cors, MINOR_ROAD_COST, 20, 10)

        if self.size > 13:
            self.add_random_connections_between(main_cors, town_cors, 5, MAIN_ROAD_COST)

        self.log("Generated towns")

    def get_towns(self):
        return self.get_coordinates(self.towns)

    def generate_villages(self):
        self.villages = list()
        self.villages = self.create_city_objects(Village, self.size * 16, self.size)
        village_cors = self.get_villages()
        main_cors = self.get_main_connections()

        self.connect_point_to_nearest_larger_point(main_cors, village_cors, MINOR_ROAD_COST, 20, 10)
        self.add_random_connections(village_cors, RURAL_ROAD_COST, self.size, 40)
        self.log("Generated villages")

    def get_villages(self):
        return self.get_coordinates(self.villages)

    def generate_hamlets(self):
        self.hamlets = list()
        self.hamlets = self.create_city_objects(Hamlet, self.size * 64, self.size)
        hamlet_cors = self.get_hamlets()
        main_cors = self.get_main_connections()
        minor_cors = self.get_towns() + self.get_villages()

        self.connect_point_to_nearest_larger_point(main_cors, hamlet_cors, MINOR_ROAD_COST, 20, 10)
        self.connect_point_to_nearest_larger_point(minor_cors, hamlet_cors, RURAL_ROAD_COST, 20, 10)
        self.log("Generated hamlets")

    def get_hamlets(self):
        return self.get_coordinates(self.hamlets)
            
    def generate(self, size=STANDARD_SIZE, seed=None, camery_density=5,  make_complex=False, logging=False):
        self.logging = logging
        self.size = size
        self.make_complex = make_complex
        start_time = time.time()

        if not seed:
            self.seed = random.randint(0, 10000000)
        else:
            self.seed = seed

        random.seed(seed)

        self.camera_density = camery_density

        self.generate_back_bone()
        
        if size > 1:
            self.generate_towns()
        if size > 3:
            self.generate_villages()
        if size > 4:
            self.generate_hamlets()

        if size > 15:
            cors = self.get_main_connections() + self.get_towns()
            self.add_random_connections(cors, MAIN_ROAD_COST, size, 20)
            self.add_random_connections(cors, MINOR_ROAD_COST, size, 40)

        self.connect_squares()

        self.remove_redundant_nodes()
        self.make_connected(SLOW_ROAD_COST)
        self.remove_redundant_nodes()

        end_time = time.time()
        self.display_graph_creation_info(end_time - start_time)
        self.log(f"Use seed {self.seed} to recreate this graph")
        

    def display_graph_creation_info(self, time_elapsed):
        self.log(f"Created graph with {self.G.number_of_nodes()} vertices and {self.G.number_of_edges()} edges in {round(time_elapsed, 2)} seconds")

    def create_highway_system(self):
        cities_to_connect = self.metropolitans + self.urban_centers
        cities_to_connect = list(map(lambda city: city.pos, cities_to_connect))

        for point in cities_to_connect:
            x, y = point
            neighbours = sorted(cities_to_connect, key=lambda city: distance(city, (x, y)))
            neighbours = list(filter(lambda city: city not in city_connections[point], neighbours))

            if not neighbours:
                return

            for i, (to_x, to_y) in enumerate(neighbours):
                self.highway_points += self.connect_with_potential_stop((x, y), (to_x, to_y), cities_to_connect, HIGHWAY_COST, 10, 50)
                break
        
        self.make_highways_connected(cities_to_connect, HIGHWAY_COST)
    
    def connect(self, city1, city2, cost, curvature=0.2, way_point_density=2):
        if city1 in city_connections and city2 in city_connections:
            if city_connections[city1].get(city2):
                return []
            
            city_connections[city1][city2] = True
            city_connections[city2][city1] = True

        middle1 = calculate_midpoint(city1, city2, curvature, self.width, self.height)
        middle2 = calculate_midpoint(city1, middle1, curvature, self.width, self.height)
        middle3 = calculate_midpoint(middle1, city2, curvature, self.width, self.height)

        way_points = self.connect_helper(city1, middle2, cost, way_point_density)
        way_points += self.connect_helper(middle2, middle1, cost, way_point_density)
        way_points += self.connect_helper(middle1, middle3, cost, way_point_density)
        way_points += self.connect_helper(middle3, city2, cost, way_point_density)
        return way_points

    def connect_helper(self, city1, city2, cost, way_point_density=2):
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
                if random.randint(1, 10) > (10 - way_point_density):
                    points_on_way.append((tmp_x, tmp_y))

                if random.randint(0, 10000) < self.camera_density and cost < STREET_COST:
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
            
            cur_x = tmp_x
            cur_y = tmp_y

        return points_on_way
    
    def connect_squares(self):
        points = self.get_main_connections() + self.get_towns() + self.get_villages() + self.get_hamlets()
        squares = divide_into_squares(points, self.width, self.height, SQUARE_DIAMETER)

        for i in range(len(squares)):
            for j in range(len(squares[i])):
                if j < SQUARE_DIAMETER - 1:
                    if self.make_complex:
                        city1, city2 = find_closest_pair(squares[i][j], squares[i][j + 1])
                        if city1 and city2:
                            self.connect(city1, city2, randomize_cost())
                    elif len(squares[i][j]) > 0 and len(squares[i][j + 1]):
                        city1 = random.choice(squares[i][j])
                        city2 = find_closest(city1, squares[i][j + 1])
                        self.connect(city1, city2, SLOW_ROAD_COST)

                if i < SQUARE_DIAMETER - 1:
                    if self.make_complex:
                        city1, city2 = find_closest_pair(squares[i][j], squares[i + 1][j])
                        if city1 and city2:
                            self.connect(city1, city2, randomize_cost())
                    elif len(squares[i][j]) > 0 and len(squares[i + 1][j]):
                        city1 = random.choice(squares[i][j])
                        city2 = find_closest(city1, squares[i + 1][j])
                        self.connect(city1, city2, SLOW_ROAD_COST)


    
    def connect_with_closest_points(self, cities, cost):
        for small_city in cities:
            closest_big_cities = sorted(cities, key=lambda city: distance(city, small_city))[1:1]

            for closest_big_city in closest_big_cities:
                self.connect(small_city, closest_big_city, cost)
                self.G.add_node(small_city)

    def make_connected(self, cost):
        if nx.is_connected(self.G):
            return
        
        components = list(nx.connected_components(self.G))
        main_comp = list(max(components, key=lambda com: len(com)))

        number_of_components = len(components)
        connected_components = 0

        print(f"Components to connect: {len(components)}")
        for component in components:
            component = list(component)
            if component is main_comp:
                continue
            
            # Its to expensive to calculate correct connections if there are many components
            # We can afford to do it for the last 20 components
            if number_of_components - connected_components > 20 or not self.make_complex:
                city1 = random.randint(0, len(main_comp) - 1)
                city2 = random.randint(0, len(component) - 1)
                self.connect(component[city2], main_comp[city1], cost=cost)
            else:
                city1, city2 = find_closest_pair(component, main_comp)
                self.connect(city1, city2, cost=cost)

            connected_components += 1
            print(f"Connected components: {connected_components}/{number_of_components}")

        self.log(f"Created {connected_components} new edges to make the graph connected")

    def make_highways_connected(self, layers, cost, strict=True):
        # The time complexity of this function looks really bad but we will never have many nodes to work with here.
        # This will create a main road network that makes sense.

        while not nx.is_connected(self.G):
            components = list(nx.connected_components(self.G))
            
            nodes_to_connect = [list(filter(lambda city: city in layers, component)) for component in components]
            main_component = max(nodes_to_connect, key=lambda node: len(node))

            for nodes in nodes_to_connect:
                if nodes is main_component:
                    continue

                from_point = None
                to_point = None
                min_distance = float("inf")
                
                for node in nodes:
                    for conn_point in main_component:
                        cur_distance = distance(conn_point, node)
                        if cur_distance < min_distance:
                            from_point = node
                            to_point = conn_point
                            min_distance = cur_distance
                
                if from_point and to_point:
                    self.highway_points += self.connect(from_point, to_point, cost, 20)
                    break      

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

    def add_random_connections_between(self, first_points, second_points, connections, cost):
        for _ in range(connections):
            city1 = random.choice(first_points)
            city2 = random.choice(second_points)

            self.connect_with_potential_stop(city1, city2, first_points, cost, 30, 30)

    def add_random_connections(self, points, cost, connections, precision=None):
        for _ in range(connections):
            city1 = random.choice(points)
            city2 = random.choice(points)

            while city1 == city2:
                city2 = random.choice(points)

            self.connect_with_potential_stop(city1, city2, points, cost, 10, precision)

    def remove_redundant_nodes(self):
        before = self.G.number_of_edges()
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

        after = self.G.number_of_edges()
        self.log(f"Removed {before - after} redundant nodes in the first round")

    def log(self, message):
        if self.logging:
            print(message)

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
        return new_network
                    





