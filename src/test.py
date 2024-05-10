from utils import *
import unittest
import numpy as np

class TestUtilityFunctions(unittest.TestCase):
    def test_distance_calculation(self):
        test_cases = [
            ((0, 0), (3, 4), 5),
            ((0, 0), (-3, -4), 5),
            ((1, 1), (4, 5), 5),
            ((-1, -1), (-4, -5), 5)
        ]
        for (p1, p2, expected) in test_cases:
            with self.subTest(p1=p1, p2=p2):
                self.assertEqual(distance(p1, p2), expected)

    def test_correct_cost(self):
        test_cases = [
            (0, 1, 0, 1, 10, np.sqrt(200)),
            (0, 0, 0, 1, 10, 10),
            (0, 0, 1, 0, 10, 10)
        ]
        for (x1, x2, y1, y2, cost, expected) in test_cases:
            with self.subTest(x1=x1, x2=x2, y1=y1, y2=y2, cost=cost):
                self.assertAlmostEqual(correct_cost(x1, x2, y1, y2, cost), expected, places=2)

    def test_interpolate_points(self):
        start = (0, 0)
        end = (10, 10)
        num_points = 5
        expected_points = [(2.0, 2.0), (4.0, 4.0), (6.0, 6.0), (8.0, 8.0), (10.0, 10.0)]
        result = interpolate_points(start, end, num_points)
        self.assertEqual(result, expected_points)

    def test_point_inside_circle(self):
        center = (0, 0)
        radius = 5
        point_inside = (3, 4)
        point_outside = (6, 0)
        self.assertTrue(point_inside_circle(point_inside, center, radius, point_inside))
        self.assertFalse(point_inside_circle(point_outside, center, radius, point_outside))

    def test_get_closest_point_in_list(self):
        point = (0, 0)
        points = [(10, 10), (20, 20), (0, 1)]
        closest_point = get_closest_point_in_list(point, points)
        self.assertEqual(closest_point, (0, 1))

    def test_calculate_midpoint(self):
        point1 = (0, 0)
        point2 = (10, 10)
        curvature = 0.5
        width = 20
        height = 20
        midpoint = calculate_midpoint(point1, point2, curvature, width, height)
        self.assertTrue(0 <= midpoint[0] <= 20 and 0 <= midpoint[1] <= 20)

if __name__ == '__main__':
    unittest.main()
