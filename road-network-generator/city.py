from config import *
import random

class BaseCity:
    def __init__(self, position, road_network, size):
        self.pos = position
        self.poi = {}
        self.rn = road_network
        self.type = None
        self.generate(size)

    def generate(self, size):
        pass

    def generate_clusters(self, num_suburbs, cost, Type, spread, size):
        suburbs = []

        x, y = self.pos

        for _ in range(num_suburbs):
            new_x = random.randint(max((0, x - self.rn.width // spread)), min((x + self.rn.width // spread, self.rn.width - 1)))
            new_y = random.randint(max((0, y - self.rn.height // spread)), min((y + self.rn.height // spread, self.rn.height - 1)))
            self.rn.connect((x, y), (new_x, new_y), cost)
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

class Metropolis(BaseCity):
    def __init__(self, position, road_network, size):
        super().__init__(position, road_network, size)

    def generate(self, size):
        num_suburbs = 10
        num_towns = 0
        num_streets = 0
        street_radius = 0

        if size > 3:
            num_suburbs += 1
        if size > 5:
            num_suburbs += 1
            num_streets += 2
            street_radius = 20
        if size > 7:
            num_streets += 3
            street_radius += 10
        if size > 9:
            num_streets += 1
            street_radius += 10
            num_towns += 1
        if size > 11:
            num_streets += 2
            street_radius += 10
        if size > 13:
            num_streets += 2
            num_towns += 2
        if size > 15:
            num_streets += 2

        self.generate_streets(radius=street_radius, num=num_streets)
        self.generate_clusters(num_suburbs, MINOR_ROAD_COST, Suburb, 15, size)
        self.generate_clusters(num_towns, MAIN_ROAD_COST, Town, 10, size)

class UrbanCenter(BaseCity):
    def __init__(self, position, road_network, size):
        super().__init__(position, road_network, size)

    def generate(self, size):
        num_suburbs = 5
        num_towns = 0
        num_streets = 0
        street_radius = 0

        if size > 3:
            num_suburbs += 1
        if size > 5:
            num_suburbs += 1
            num_streets += 2
            street_radius = 20
        if size > 7:
            num_towns += 1
            num_streets += 3
            street_radius += 10
            num_towns += 1
        if size > 9:
            num_streets += 1
            street_radius += 10
        if size > 11:
            num_streets += 2
            street_radius += 10

        self.generate_streets(radius=street_radius, num=num_streets)
        self.generate_clusters(num_suburbs, MINOR_ROAD_COST, Suburb, 15, size)
        self.generate_clusters(num_towns, MAIN_ROAD_COST, Town, 10, size)

class Town(BaseCity):
    def __init__(self, position, road_network, size):
        super().__init__(position, road_network, size)
        self.rn.add_points_of_interest({self.pos: Town})
        self.rn.towns.append(self)

    def generate(self, size):
        self.generate_streets(radius=10, num=5)
        self.generate_clusters(2, MINOR_ROAD_COST, Suburb, 20, size)

class Village(BaseCity):
    def __init__(self, position, road_network, size):
        super().__init__(position, road_network, size)
        self.rn.add_points_of_interest({self.pos: Village})
        self.rn.villages.append(self)

    def generate(self, size):
        self.generate_streets(radius=20, num=4)

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