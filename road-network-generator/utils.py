import numpy as np

def distance(city1, city2):
    return np.sqrt((city1[0] - city2[0])**2 + (city1[1] - city2[1])**2)

def correct_cost(cur_x, tmp_x, cur_y, tmp_y, cost):
    new_cost = cost

    if not (cur_x - tmp_x == 0 or cur_y - tmp_y == 0):
       new_cost = np.sqrt(cost**2 + cost**2)

    return round(new_cost, 2)
