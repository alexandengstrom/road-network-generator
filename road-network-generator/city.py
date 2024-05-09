from config import *
import random
from utils import create_circle_positions, get_closest_point_in_list

class BaseCity:
    def __init__(self, position, road_network, size):
        self.pos = position
        self.poi = {}
        self.rn = road_network
        self.type = None
        self.ring_points = list()
        self.street_density = 1

    def get_points_of_interest(self):
        return self.poi

    def generate(self, size):
        pass

    def generate_clusters(self, num_suburbs, cost, Type, spread, size):
        suburbs = []
        local_points = []

        x, y = self.pos

        for _ in range(num_suburbs):
            new_x = random.randint(max((0, x - self.rn.width // spread)), min((x + self.rn.width // spread, self.rn.width - 1)))
            new_y = random.randint(max((0, y - self.rn.height // spread)), min((y + self.rn.height // spread, self.rn.height - 1)))
            self.rn.connect_with_potential_stop((x, y), (new_x, new_y), local_points, cost, 20, 30)
            #self.rn.connect((x, y), (new_x, new_y), cost)
            suburbs.append(Type((new_x, new_y), self.rn, size))
            self.poi[new_x, new_y] = Type

        return suburbs
    
    def generate_streets(self, radius, num):
        point = self.pos

        for _ in range(num):
            new_x = random.randint(max((0, point[0] - radius)), min((point[0] + radius, self.rn.width - 1)))
            new_y = random.randint(max((0, point[1] - radius)), min((point[1] + radius, self.rn.height - 1)))
            n_point = (new_x, new_y)
            way_points = self.rn.connect(point, n_point, STREET_COST)
            for w_point in way_points:
                for _ in range(num // 2):
                    w_new_x = random.randint(max((0, w_point[0] - radius//2)), min((w_point[0] + radius//2, self.rn.width - 1)))
                    w_new_y = random.randint(max((0, w_point[1] - radius//2)), min((w_point[1] + radius//2, self.rn.height - 1)))
                    w_n_point = (w_new_x, w_new_y)
                    way_points2 = self.rn.connect(w_n_point, w_point, STREET_COST)

    def generate_streets_from_suburbs(self, street_pos, radius=20, num=2):
        for point in street_pos:
            for _ in range(num):
                if random.randint(0, 20) > self.street_density:
                    continue
                new_x = random.randint(max((0, point[0] - radius)), min((point[0] + radius, self.rn.width - 1)))
                new_y = random.randint(max((0, point[1] - radius)), min((point[1] + radius, self.rn.height - 1)))
                n_point = (new_x, new_y)
                way_points = self.rn.connect(point, n_point, STREET_COST)
                for w_point in way_points:
                    if random.randint(0, 10) > self.street_density:
                        continue
                    for _ in range(num // 2):
                        w_new_x = random.randint(max((0, w_point[0] - radius//2)), min((w_point[0] + radius//2, self.rn.width - 1)))
                        w_new_y = random.randint(max((0, w_point[1] - radius//2)), min((w_point[1] + radius//2, self.rn.height - 1)))
                        w_n_point = (w_new_x, w_new_y)
                        self.rn.connect(w_n_point, w_point, STREET_COST)


    def generate_circle_streets(self, way_points, num, radius):
        for w_point in way_points:
            for _ in range(num // 2):
                w_new_x = random.randint(max((0, w_point[0] - radius//2)), min((w_point[0] + radius//2, self.rn.width - 1)))
                w_new_y = random.randint(max((0, w_point[1] - radius//2)), min((w_point[1] + radius//2, self.rn.height - 1)))
                w_n_point = (w_new_x, w_new_y)
                way_points2 = self.rn.connect(w_n_point, w_point, STREET_COST)

    def generate_circle(self, radius, num_points, cost, way_point_density=5):
        width = self.rn.width
        height = self.rn.height
        points = create_circle_positions(self.pos, radius, width, height, num_points)
        self.rn.add_important_points(points)

        for i in range(len(points)):
            if i == len(points) - 1:
                self.rn.connect(points[i], points[0], cost)
            else:
                self.rn.connect(points[i], points[i + 1], cost)

            if random.randint(0, 1) > 0:
                way_points = self.rn.connect(self.pos, points[i], cost, way_point_density)
                self.generate_circle_streets(way_points, 5, 20)

    def generate_ring(self, points, cost):
        ring_points = list()
        diagonal_points = list()

        for i in range(len(points)):
            if i == len(points) - 1:
                ring_points += self.rn.connect(points[i], points[0], cost)
            else:
                ring_points += self.rn.connect(points[i], points[i + 1], cost)

            if random.randint(1, 6) > 5:
                diagonal_points += self.rn.connect(self.pos, points[i], cost)

        return ring_points, diagonal_points
    
    def generate_suburbs(self, size, radius, cost):
        suburb_ring_positions = create_circle_positions(self.pos, radius, self.rn.width, self.rn.height, 20)
        street_positions = list()
        for suburb_pos in suburb_ring_positions:
            if random.randint(0, 1) < 1:
                continue

            Suburb(suburb_pos, self.rn, size)
            street_positions += self.rn.connect(suburb_pos, self.pos, cost)

        self.generate_streets_from_suburbs(street_positions)



class Metropolis(BaseCity):
    def __init__(self, position, road_network, size):
        super().__init__(position, road_network, size)

    def generate(self, size):
        self.street_density = size
        ring_radius = random.randint(30, 50)
        ring_points = create_circle_positions(self.pos, ring_radius, self.rn.width, self.rn.height, 40)
        self.rn.add_important_points(ring_points)
        rp, dp = self.generate_ring(ring_points, MAIN_ROAD_COST)
        ring_points += rp

        town_offset = random.randint(10, 30)
        num_towns = random.randint(5, 10)
        town_ring_positions = create_circle_positions(self.pos, ring_radius + town_offset, self.rn.width, self.rn.height, num_towns)
        for town_pos in town_ring_positions:
            Town(town_pos, self.rn, size)
            closest_point = get_closest_point_in_list(town_pos, ring_points)
            self.rn.connect(town_pos, closest_point, MINOR_ROAD_COST)

        self.generate_suburbs(size, ring_radius, RURAL_ROAD_COST)


        return

        if size > 5:
            self.generate_circle(radius=circle_radius, num_points=circle_points, cost=MAIN_ROAD_COST)
        
        if size > 6 and circle_radius > 60:
            self.generate_circle(radius=circle_radius - 10, num_points=circle_points, cost=MAIN_ROAD_COST)
        if size > 8 and circle_radius > 50:
            self.generate_circle(radius=circle_radius - 20, num_points=circle_points, cost=MINOR_ROAD_COST)
        if size > 9 and size > 40:
            self.generate_circle(radius=circle_radius - 32, num_points=circle_points, cost=RURAL_ROAD_COST)



        self.generate_clusters(num_towns, MINOR_ROAD_COST, Town, town_spread, size)

        if size > 5:
            self.generate_clusters(num_suburbs, MINOR_ROAD_COST, Suburb, 15, size)
        
        if size > 7:
            self.generate_streets(radius=circle_radius, num=num_streets)

class UrbanCenter(BaseCity):
    def __init__(self, position, road_network, size):
        super().__init__(position, road_network, size)

    def generate(self, size):
        self.street_density = size
        ring_radius = random.randint(15, 30)
        ring_points = create_circle_positions(self.pos, ring_radius, self.rn.width, self.rn.height, 20)
        self.rn.add_important_points(ring_points)
        rp, dp = self.generate_ring(ring_points, MAIN_ROAD_COST)
        ring_points += rp

        town_offset = random.randint(20, 30)
        num_towns = random.randint(5, 10)
        town_ring_positions = create_circle_positions(self.pos, ring_radius + town_offset, self.rn.width, self.rn.height, num_towns)
        for town_pos in town_ring_positions:
            if random.randint(0, 2) < 2:
                continue

            Town(town_pos, self.rn, size)
            closest_point = get_closest_point_in_list(town_pos, ring_points)
            self.rn.connect(town_pos, closest_point, MINOR_ROAD_COST)

        suburb_radius = random.randint(15, 30)
        num_suburbs = random.randint(5, 10)
        street_positions = list()
        suburb_ring_positions = create_circle_positions(self.pos, suburb_radius, self.rn.width, self.rn.height, num_suburbs)

        self.generate_suburbs(size, ring_radius, RURAL_ROAD_COST)
        

class Town(BaseCity):
    def __init__(self, position, road_network, size):
        super().__init__(position, road_network, size)
        self.rn.add_points_of_interest({self.pos: Town})
        self.rn.towns.append(self)
        self.street_density = 3

        self.generate(size)

    def generate(self, size):
        
        suburb_radius = random.randint(15, 30)
        num_suburbs = random.randint(5, 10)
        suburb_ring_positions = create_circle_positions(self.pos, suburb_radius, self.rn.width, self.rn.height, num_suburbs)
        self.generate_suburbs(size, suburb_radius, SLOW_ROAD_COST)

class Village(BaseCity):
    def __init__(self, position, road_network, size):
        super().__init__(position, road_network, size)
        self.rn.add_points_of_interest({self.pos: Village})
        self.rn.villages.append(self)
        self.street_density = 2

        if size > 10:
            self.generate(size)

    def generate(self, size):
        self.generate_suburbs(size, 10, SLOW_ROAD_COST)
        return
        num_streets = 2

        if size > 11:
            num_streets = 4

        self.generate_circle(radius=8, num_points=7, cost=SLOW_ROAD_COST)
        #self.generate_streets(radius=20, num=num_streets)

class Hamlet(BaseCity):
    def __init__(self, position, road_network, size):
        super().__init__(position, road_network, size)
        self.rn.add_points_of_interest({self.pos: Hamlet})
        self.rn.hamlets.append(self)
        self.street_density = 1
        
        self.generate(size)

    def generate(self, size):
        self.generate_suburbs(size, 8, SLOW_ROAD_COST)

class Suburb(BaseCity):
    def __init__(self, position, road_network, size):
        super().__init__(position, road_network, size)
        if size > 7:
            self.generate(size)

    def generate(self, size):
        return
        num_streets = 0
        num_base_cities = 0
        street_radius = 20

        if size > 5:
            num_streets += 1
        if size > 8:
            num_streets += 1
            num_base_cities += 1
        if size > 10:
            num_streets += 1
            num_base_cities += 1
        if size > 15:
            num_streets += 1
            num_base_cities += 1

        self.generate_circle(radius=7, num_points=4, cost=SLOW_ROAD_COST, way_point_density=2)
        #self.generate_streets(radius=50, num=num_streets)
        #suburbs = self.generate_clusters(num_base_cities, RURAL_ROAD_COST, BaseCity, 50, size)