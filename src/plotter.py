import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from utils import distance
from config import *
from city import Metropolis, UrbanCenter, Town, Village, Hamlet
from error_handler import log

EDGE_COLORS = {
    HIGHWAY_COST: 'black', 
    MAIN_ROAD_COST: '#164018', 
    MINOR_ROAD_COST: '#26752a', 
    RURAL_ROAD_COST: 'orange', 
    SLOW_ROAD_COST: "#ffcccb",
    STREET_COST: "lightgrey"
    }

EDGE_COLORS_GRAYSCALE = {
    HIGHWAY_COST: '#000000', 
    MAIN_ROAD_COST: '#2A2A2A', 
    MINOR_ROAD_COST: '#555555', 
    RURAL_ROAD_COST: '#808080', 
    SLOW_ROAD_COST: "#ABABAB",
    STREET_COST: "#D6D6D6"
    }

EDGE_SIZES = {HIGHWAY_COST: 5, 
              MAIN_ROAD_COST: 2, 
              MINOR_ROAD_COST: 1, 
              RURAL_ROAD_COST: 0.9, 
              SLOW_ROAD_COST: 0.8,
              STREET_COST: 0.7}

NODE_COLORS = {
    METROPOLIS: 'black', 
    URBAN_AREA: '#164018', 
    TOWN: '#26752a', 
    VILLAGE: 'orange', 
    HAMLET: "#ffcccb",
    }

NODE_COLORS_GRAYSCALE = {
    METROPOLIS: '#000000', 
    URBAN_AREA: '#2A2A2A', 
    TOWN: '#555555', 
    VILLAGE: '#808080', 
    HAMLET: "#ABABAB",
    }

NODE_SIZES = {
    METROPOLIS: 200, 
    URBAN_AREA: 50, 
    TOWN: 20, 
    VILLAGE: 10, 
    HAMLET: 7,
    }

@log
def plot(graph, show_cameras=False, grayscale=False):
        edge_colors_map = EDGE_COLORS if not grayscale else EDGE_COLORS_GRAYSCALE
        node_colors_map = NODE_COLORS if not grayscale else NODE_COLORS_GRAYSCALE

    num_nodes = graph.G.number_of_nodes()
    num_edges = graph.G.number_of_edges()
    colors = []
    widths = []
    node_sizes = []
    node_colors = []

    pos = {node: node for node in graph.G.nodes()}

    edges = sorted(graph.G.edges(data=True), reverse=True, key=lambda x: x[2]["weight"] / distance(x[0], x[1]))

    for u, v, data in edges:
        distance_uv = distance(u, v)
        avg_cost = data["weight"] / distance_uv

            for cost, color in edge_colors_map.items():
                if avg_cost < cost + 0.2:
                    colors.append(color)
                    widths.append(EDGE_SIZES[cost])
                    break
            else:
                colors.append(edge_colors_map[SLOW_ROAD_COST])
                widths.append(EDGE_SIZES[SLOW_ROAD_COST])

    nx.draw_networkx_edges(graph.G, pos, edgelist=edges, edge_color=colors, width=widths)

        for node in graph.G.nodes():
            node_type = graph.poi.get(node)
            if node_type == Metropolis:
                node_sizes.append(NODE_SIZES[METROPOLIS])
                node_colors.append(node_colors_map[METROPOLIS])
            elif node_type == UrbanCenter:
                 node_sizes.append(NODE_SIZES[URBAN_AREA])
                 node_colors.append(node_colors_map[URBAN_AREA])
            elif node_type == Town:
                 node_sizes.append(NODE_SIZES[TOWN])
                 node_colors.append(node_colors_map[TOWN])
            elif node_type == Village:
                node_sizes.append(NODE_SIZES[VILLAGE])
                node_colors.append(node_colors_map[VILLAGE])
            elif node_type == Hamlet:
                node_sizes.append(NODE_SIZES[HAMLET])
                node_colors.append(node_colors_map[HAMLET])
            elif show_cameras and node in graph.cameras:
                 node_sizes.append(100)
                 node_colors.append("#34b4eb")
            else:
                node_sizes.append(0)
                node_colors.append(edge_colors_map[SLOW_ROAD_COST])


    nx.draw_networkx_nodes(graph.G, pos, node_size=node_sizes, node_color=node_colors)
    plt.title(f"Road Network with {num_nodes} nodes and {num_edges} edges")

        edge_labels = {color: mpatches.Patch(color=color, label=f"{round(120//cost)} km/h") for cost, color in edge_colors_map.items()}
        plt.legend(handles=edge_labels.values(), title="Speed limits", loc='upper right')
        plt.show()