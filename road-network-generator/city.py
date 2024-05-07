from config import *
import random
from utils import create_circle_positions

class BaseCity:
    def __init__(self, position, road_network, size):
        self.pos = position
        self.poi = {}
        self.rn = road_network
        self.type = None
        self.generate(size)

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
            self.rn.connect_with_potential_stop((x, y), (new_x, new_y), local_points, cost, 20, 20)
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

    def generate_circle(self, radius, num_points, cost):
        width = self.rn.width
        height = self.rn.height
        points = create_circle_positions(self.pos, radius, width, height, num_points)
        self.rn.add_important_points(points)

        for i in range(len(points)):
            if i == len(points) - 1:
                self.rn.connect(points[i], points[0], cost)
            else:
                self.rn.connect(points[i], points[i + 1], cost)

            if random.randint(0, 10) < 2:
                self.rn.connect(self.pos, points[i], cost)

class Metropolis(BaseCity):
    def __init__(self, position, road_network, size):
        super().__init__(position, road_network, size)

    def generate(self, size):
        num_suburbs = 0
        num_towns = 0
        town_spread = 10
        num_streets = 0
        street_radius = 0
        circle_points = 0
        circle_radius = 30
        circle_radius_offset = random.randint(-10, 10)

        if size > 15:
            num_streets = 12
            street_radius = 40
            num_towns = 5
            num_suburbs = 11
            circle_points = 25
        if size > 12:
            num_streets = 10
            street_radius = 40
            num_towns = 5
            num_suburbs = 10
            circle_radius = 40
        elif size > 9:
            num_streets = 6
            street_radius = 35
            num_towns = 4
            num_suburbs = 7
        elif size > 8:
            num_streets = 4
            street_radius = 35
            num_towns = 3
            circle_points = 16
            num_suburbs = 3
        elif size > 7:
            num_streets = 6
            street_radius = 35
            num_towns = 4
            num_suburbs = 7
        elif size > 6:
            num_streets = 3
            street_radius = 30
            num_towns = 2
            num_suburbs = 4
        elif size > 4:
            num_suburbs = 4
            num_towns = 5
            town_spread = 5
            circle_points = 5
        elif size > 3:
            num_towns = 5
            town_spread = 5
        elif size > 2:
            num_towns = 11
            town_spread = 5

        self.generate_circle(radius=circle_radius + circle_radius_offset, num_points=circle_points, cost=MAIN_ROAD_COST)

        if size > 7:
            self.generate_circle(radius=circle_radius + circle_radius_offset // 2, num_points=circle_points, cost=MINOR_ROAD_COST)



        self.generate_clusters(num_towns, MAIN_ROAD_COST, Town, town_spread, size)
        self.generate_clusters(num_suburbs, MINOR_ROAD_COST, Suburb, 15, size)
        self.generate_streets(radius=street_radius, num=num_streets)

class UrbanCenter(BaseCity):
    def __init__(self, position, road_network, size):
        super().__init__(position, road_network, size)

    def generate(self, size):
        num_suburbs = 0
        num_towns = 0
        num_streets = 0
        street_radius = 0

        if size > 13:
            street_radius = 40
            num_streets = 8
            num_towns = 3
            num_suburbs = 6
        elif size > 8:
            street_radius = 30
            num_streets = 6
            num_towns = 2
            num_suburbs = 4
        elif size > 6:
            street_radius = 30
            num_streets = 5
            num_towns = 2
            num_suburbs = 3
        elif size > 4:
            num_towns = 3
            num_suburbs = 3
        elif size > 3:
            num_towns = 3

        self.generate_circle(radius=30, num_points=10, cost=MINOR_ROAD_COST)
        self.generate_clusters(num_towns, MAIN_ROAD_COST, Town, 10, size)
        self.generate_clusters(num_suburbs, MINOR_ROAD_COST, Suburb, 15, size)
        self.generate_streets(radius=street_radius, num=num_streets)
        
        
        

class Town(BaseCity):
    def __init__(self, position, road_network, size):
        super().__init__(position, road_network, size)
        self.rn.add_points_of_interest({self.pos: Town})
        self.rn.towns.append(self)

    def generate(self, size):
        num_suburbs = 0
        num_streets = 0
        suburb_radius = 20

        if size > 10:
            num_suburbs = 2
            num_streets = 5
        elif size > 6:
            num_suburbs = 6
            num_streets = 5
            suburb_radius = 15
        elif size > 4:
            num_suburbs = 5
        elif size > 3:
            num_suburbs = 3
        

        self.generate_streets(radius=20, num=num_streets)
        self.generate_clusters(num_suburbs, MINOR_ROAD_COST, Suburb, suburb_radius, size)

class Village(BaseCity):
    def __init__(self, position, road_network, size):
        super().__init__(position, road_network, size)
        self.rn.add_points_of_interest({self.pos: Village})
        self.rn.villages.append(self)

    def generate(self, size):
        num_streets = 2

        if size > 11:
            num_streets = 4

        self.generate_streets(radius=20, num=num_streets)

class Hamlet(BaseCity):
    def __init__(self, position, road_network, size):
        super().__init__(position, road_network, size)
        self.rn.add_points_of_interest({self.pos: Hamlet})
        self.rn.hamlets.append(self)

    def generate(self, size):
        self.generate_streets(radius=20, num=2)

class Suburb(BaseCity):
    def __init__(self, position, road_network, size):
        super().__init__(position, road_network, size)

    def generate(self, size):
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

        self.generate_streets(radius=50, num=num_streets)
        suburbs = self.generate_clusters(num_base_cities, RURAL_ROAD_COST, BaseCity, 50, size)