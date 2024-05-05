import numpy as np

def distance(city1, city2):
    return np.sqrt((city1[0] - city2[0])**2 + (city1[1] - city2[1])**2)

def correct_cost(cur_x, tmp_x, cur_y, tmp_y, cost):
    new_cost = cost

    if not (cur_x - tmp_x == 0 or cur_y - tmp_y == 0):
       new_cost = np.sqrt(cost**2 + cost**2)

    return round(new_cost, 2)


def interpolate_points(point1, point2, num_points):
    step_x = (point2[0] - point1[0]) / (num_points + 1)
    step_y = (point2[1] - point1[1]) / (num_points + 1)
    
    intermediate_points = [(point1[0] + i * step_x, point1[1] + i * step_y) for i in range(1, num_points + 1)]
    
    return intermediate_points

def point_inside_circle(point, circle_origin, radius, target):
    distance_squared = (point[0] - circle_origin[0])**2 + (point[1] - circle_origin[1])**2
    if distance_squared > (target[0] - circle_origin[0])**2 + (target[1] - circle_origin[1])**2:
        return False
    return distance_squared <= radius**2
