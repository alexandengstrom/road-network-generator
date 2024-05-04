WIDTH = 1000
HEIGHT = 1000

HIGHWAY_COST = 1
MAIN_ROAD_COST = 1.33
MINOR_ROAD_COST = 1.71
RURAL_ROAD_COST = 2.4
SLOW_ROAD_COST = 3.2
STREET_COST = 4


EDGE_COLORS = {
    HIGHWAY_COST: 'black', 
    MAIN_ROAD_COST: 'green', 
    MINOR_ROAD_COST: 'yellow', 
    RURAL_ROAD_COST: 'orange', 
    SLOW_ROAD_COST: "#ffcccb",
    STREET_COST: "lightgrey"
    }

EDGE_SIZES = {HIGHWAY_COST: 8, 
              MAIN_ROAD_COST: 3, 
              MINOR_ROAD_COST: 2, 
              RURAL_ROAD_COST: 1, 
              SLOW_ROAD_COST: 1,
              STREET_COST: 1}


STANDARD_SIZE = 10