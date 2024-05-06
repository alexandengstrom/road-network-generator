WIDTH = 1000
HEIGHT = 1000

HIGHWAY_COST = 1
MAIN_ROAD_COST = 1.33
MINOR_ROAD_COST = 1.71
RURAL_ROAD_COST = 2.4
SLOW_ROAD_COST = 3.2
STREET_COST = 4

METROPOLIS = 1
URBAN_AREA = 1.33
TOWN = 1.71
VILLAGE = 2.4
HAMLET = 3.2


EDGE_COLORS = {
    HIGHWAY_COST: 'black', 
    MAIN_ROAD_COST: '#164018', 
    MINOR_ROAD_COST: '#26752a', 
    RURAL_ROAD_COST: 'orange', 
    SLOW_ROAD_COST: "#ffcccb",
    STREET_COST: "lightgrey"
    }

EDGE_SIZES = {HIGHWAY_COST: 5, 
              MAIN_ROAD_COST: 2, 
              MINOR_ROAD_COST: 1, 
              RURAL_ROAD_COST: 0.9, 
              SLOW_ROAD_COST: 0.8,
              STREET_COST: 0.7}


STANDARD_SIZE = 10
ROAD_CURVATURE = 3