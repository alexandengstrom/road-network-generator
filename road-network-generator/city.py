from config import *
import random
from utils import create_circle_positions, get_closest_point_in_list

class BaseCity:
    def __init__(self, position, road_network, size):
        self.pos = position
        self.poi = {}
        self.rn = road_network
        self.street_density = 1

    def get_points_of_interest(self):
        return self.poi

    def generate(self, size):
        raise NotImplemented

    def generate_streets_from_suburbs(self, street_pos, radius=20, num=2):
        for point in street_pos:
            for _ in range(num):
                if random.randint(0, 20) > self.street_density:
                    continue
                
                n_point = self.random_position_within_radius(point, radius)
                way_points = self.rn.connect(point, n_point, STREET_COST)
                self.add_street_waypoints(way_points, radius)

    def add_street_waypoints(self, way_points, radius):
        for w_point in way_points:
            if random.randint(0, 10) > self.street_density:
                continue
            for _ in range(len(way_points) // 2):
                w_n_point = self.random_position_within_radius(w_point, radius//2)
                self.rn.connect(w_n_point, w_point, STREET_COST)

    def generate_circle(self, radius, num_points, cost, way_point_density=5):
        points = create_circle_positions(self.pos, radius, self.rn.width, self.rn.height, num_points)
        self.rn.add_important_points(points)
        self.connect_points_in_circle(points, cost, way_point_density)

    def generate_ring(self, points, cost):
        ring_points, diagonal_points = self.connect_and_diagonalize(points, cost)
        return ring_points, diagonal_points
    
    def generate_suburbs(self, size, radius, cost):
        positions = create_circle_positions(self.pos, radius, self.rn.width, self.rn.height, 20)
        street_positions = self.connect_and_filter(positions, cost)
        self.generate_streets_from_suburbs(street_positions)

    def random_position_within_spread(self, spread):
        x, y = self.pos
        new_x = random.randint(max(0, x - self.rn.width // spread), min(x + self.rn.width // spread, self.rn.width - 1))
        new_y = random.randint(max(0, y - self.rn.height // spread), min(y + self.rn.height // spread, self.rn.height - 1))
        return new_x, new_y

    def random_position_within_radius(self, point, radius):
        x, y = point
        new_x = random.randint(max(0, x - radius), min(x + radius, self.rn.width - 1))
        new_y = random.randint(max(0, y - radius), min(y + radius, self.rn.height - 1))
        return (new_x, new_y)

    def connect_and_diagonalize(self, points, cost):
        ring_points = []
        diagonal_points = []
        for i, point in enumerate(points):
            next_point = points[0] if i == len(points) - 1 else points[i + 1]
            ring_points.extend(self.rn.connect(point, next_point, cost))
            if random.randint(1, 6) > 5:
                diagonal_points.extend(self.rn.connect(self.pos, point, cost))
        return ring_points, diagonal_points

    def connect_points_in_circle(self, points, cost, way_point_density):
        for i, point in enumerate(points):
            next_point = points[0] if i == len(points) - 1 else points[i + 1]
            self.rn.connect(point, next_point, cost)
            if random.randint(0, 1) > 0:
                way_points = self.rn.connect(self.pos, point, cost, way_point_density)
                self.add_street_waypoints(way_points, 20)

    def connect_and_filter(self, positions, cost):
        street_positions = []
        for pos in positions:
            if random.randint(0, 1) < 1:
                continue
            Suburb(pos, self.rn, self.street_density)
            street_positions.extend(self.rn.connect(pos, self.pos, cost))
        return street_positions

class Metropolis(BaseCity):
    def __init__(self, position, road_network, size):
        super().__init__(position, road_network, size)
        self.street_density = size

    def generate(self, size):
        ring_radius = random.randint(30, 50)
        ring_points = list()
        
        if size > 5:
            ring_points = create_circle_positions(self.pos, ring_radius, self.rn.width, self.rn.height, 40)
            self.rn.add_important_points(ring_points)
            rp, dp = self.generate_ring(ring_points, MAIN_ROAD_COST)
            ring_points += rp

        if size > 7:
            town_offset = random.randint(10, 30)
            num_towns = random.randint(5, 10)
            town_ring_positions = create_circle_positions(self.pos, ring_radius + town_offset, self.rn.width, self.rn.height, num_towns)
            for town_pos in town_ring_positions:
                Town(town_pos, self.rn, size)
                closest_point = get_closest_point_in_list(town_pos, ring_points)
                self.rn.connect(town_pos, closest_point, MINOR_ROAD_COST)

        if size > 9:
            self.generate_suburbs(size, ring_radius, RURAL_ROAD_COST)


class UrbanCenter(BaseCity):
    def __init__(self, position, road_network, size):
        super().__init__(position, road_network, size)
        self.street_density = size

    def generate(self, size):
        ring_radius = random.randint(15, 30)
        ring_points = list()

        if size > 6:
            ring_points = create_circle_positions(self.pos, ring_radius, self.rn.width, self.rn.height, 20)
            self.rn.add_important_points(ring_points)
            rp, dp = self.generate_ring(ring_points, MAIN_ROAD_COST)
            ring_points += rp

        if size > 8:
            town_offset = random.randint(20, 30)
            num_towns = random.randint(5, 10)
            town_ring_positions = create_circle_positions(self.pos, ring_radius + town_offset, self.rn.width, self.rn.height, num_towns)
            for town_pos in town_ring_positions:
                if random.randint(0, 2) < 2:
                    continue

                Town(town_pos, self.rn, size)
                closest_point = get_closest_point_in_list(town_pos, ring_points)
                self.rn.connect(town_pos, closest_point, MINOR_ROAD_COST)

        if size > 10:
            self.generate_suburbs(size, ring_radius, RURAL_ROAD_COST)
        

class Town(BaseCity):
    def __init__(self, position, road_network, size):
        super().__init__(position, road_network, size)
        self.rn.add_points_of_interest({self.pos: Town})
        self.rn.towns.append(self)
        self.street_density = 3

        self.generate(size)

    def generate(self, size):
        if size > 12:
            max_radius = min((50, max((30, size * 2))))
            suburb_radius = random.randint(15, max_radius)
            self.generate_suburbs(size, suburb_radius, SLOW_ROAD_COST)

class Village(BaseCity):
    def __init__(self, position, road_network, size):
        super().__init__(position, road_network, size)
        self.rn.add_points_of_interest({self.pos: Village})
        self.rn.villages.append(self)
        self.street_density = 2

        self.generate(size)

    def generate(self, size):
        if size > 13:
            self.generate_suburbs(size, 10, SLOW_ROAD_COST)

class Hamlet(BaseCity):
    def __init__(self, position, road_network, size):
        super().__init__(position, road_network, size)
        self.rn.add_points_of_interest({self.pos: Hamlet})
        self.rn.hamlets.append(self)
        self.street_density = 1
        
        self.generate(size)

    def generate(self, size):
        if size > 15:
            self.generate_suburbs(size, 8, SLOW_ROAD_COST)

class Suburb(BaseCity):
    def __init__(self, position, road_network, size):
        super().__init__(position, road_network, size)
        if size > 7:
            self.generate(size)

    def generate(self, size):
        pass