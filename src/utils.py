import numpy as np
import random
import math
from config import *

def distance(city1, city2):
    return np.sqrt((city1[0] - city2[0])**2 + (city1[1] - city2[1])**2)

def correct_cost(cur_x, tmp_x, cur_y, tmp_y, cost):
    new_cost = cost

    if not (cur_x - tmp_x == 0 or cur_y - tmp_y == 0):
       new_cost = np.sqrt(cost**2 + cost**2)

    return round(new_cost, 2)


def interpolate_points(point1, point2, num_points):
    step_x = round((point2[0] - point1[0]) / (num_points + 1))
    step_y = round((point2[1] - point1[1]) / (num_points + 1))
    
    intermediate_points = [(point1[0] + i * step_x, point1[1] + i * step_y) for i in range(1, num_points + 1)]
    
    return intermediate_points

def point_inside_circle(point, circle_origin, radius, target):
    distance_squared = (point[0] - circle_origin[0])**2 + (point[1] - circle_origin[1])**2
    if distance_squared > (target[0] - circle_origin[0])**2 + (target[1] - circle_origin[1])**2:
        return False
    return distance_squared <= radius**2

def create_circle_positions(center, radius, width, height, num_points):
    cx, cy = center
    
    points = []
    
    for i in range(num_points):
        angle = 2 * math.pi * i / num_points
        
        x = int(cx + radius * math.cos(angle))
        y = int(cy + radius * math.sin(angle))

        x += random.randint(-radius // 11, radius // 11)
        y += random.randint(-radius // 11, radius // 11)
        
        x = max(5, min(width-1, x))
        y = max(5, min(height-1, y))
        
        points.append((x, y))
    
    points.sort(key=lambda point: math.atan2(point[1] - cy, point[0] - cx))
    
    return points

def get_closest_point_in_list(point, points):
    return min(points, key=lambda city: distance(city, point))

def calculate_midpoint(city1, city2, curvature, width, height):
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

    mid_x = max(0, min(width - 1, mid_x))
    mid_y = max(0, min(height - 1, mid_y))
        
    mid_x = int(mid_x)
    mid_y = int(mid_y)

    return mid_x, mid_y

def divide_into_squares(points, width, height, diameter):
    square_width = width / diameter
    square_height = height / diameter
    
    squares = [[[] for _ in range(diameter)] for _ in range(diameter)]
    
    for x, y in points:
        col = int(x // square_width)
        row = int(y // square_height)
        
        squares[min(row, diameter - 1)][min(col, diameter)].append((x, y))
    
    return squares


def find_closest_pair(first, second):
    from_point = None
    to_point = None
    min_distance = float("inf")

    for node in first:
        for conn_point in second:
            cur_distance = distance(conn_point, node)
            if cur_distance < min_distance:
                from_point = node
                to_point = conn_point
                min_distance = cur_distance

    return from_point, to_point

def randomize_cost():
    return random.choice([MAIN_ROAD_COST, MINOR_ROAD_COST, RURAL_ROAD_COST, SLOW_ROAD_COST])

def find_closest(origo, points):
    closest_point = None
    min_distance = float("inf")

    for node in points:
        cur_distance = distance(origo, node)
        if cur_distance < min_distance:
            closest_point = node
            min_distance = cur_distance

    return closest_point