import networkx as nx
import matplotlib.pyplot as plt
from utils import distance, correct_cost, interpolate_points, point_inside_circle
from config import *
from city import Metropolis, UrbanCenter, Town, Village, Hamlet, BaseCity

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

NODE_COLORS = {
    METROPOLIS: 'black', 
    URBAN_AREA: '#164018', 
    TOWN: '#26752a', 
    VILLAGE: 'orange', 
    HAMLET: "#ffcccb",
    }

NODE_SIZES = {
    METROPOLIS: 200, 
    URBAN_AREA: 50, 
    TOWN: 20, 
    VILLAGE: 10, 
    HAMLET: 7,
    }

def plot(graph, show_gas_stations=False, show_cameras=False):
        num_nodes = graph.G.number_of_nodes()
        num_edges = graph.G.number_of_edges()
        colors = []
        widths = []
        node_sizes = []
        node_colors = []

        pos = {node: node for node in graph.G.nodes()}
        #pos = nx.spring_layout(graph.G)

        # Sort the edges in so we plot the slowest roads first. This is so we can clearly see the highways.
        edges = sorted(graph.G.edges(data=True), reverse=True, key=lambda x: x[2]["weight"] / distance(x[0], x[1]))

        for u, v, data in edges:
            distance_uv = distance(u, v)
            avg_cost = data["weight"] / distance_uv

            for cost, color in EDGE_COLORS.items():
                if avg_cost < cost + 0.2:
                    colors.append(color)
                    widths.append(EDGE_SIZES[cost])
                    break
            else:
                colors.append(EDGE_COLORS[SLOW_ROAD_COST])
                widths.append(EDGE_SIZES[SLOW_ROAD_COST])

        nx.draw_networkx_edges(graph.G, pos, edgelist=edges, edge_color=colors, width=widths)

        for node in graph.G.nodes():
            node_type = graph.poi.get(node)
            if node_type == Metropolis:
                node_sizes.append(NODE_SIZES[METROPOLIS])
                node_colors.append(NODE_COLORS[METROPOLIS])
            elif node_type == UrbanCenter:
                 node_sizes.append(NODE_SIZES[URBAN_AREA])
                 node_colors.append(NODE_COLORS[URBAN_AREA])
            elif node_type == Town:
                 node_sizes.append(NODE_SIZES[TOWN])
                 node_colors.append(NODE_COLORS[TOWN])
            elif node_type == Village:
                node_sizes.append(NODE_SIZES[VILLAGE])
                node_colors.append(EDGE_COLORS[VILLAGE])
            elif node_type == Hamlet:
                node_sizes.append(NODE_SIZES[HAMLET])
                node_colors.append(EDGE_COLORS[HAMLET])
            elif show_cameras and node in graph.cameras:
                 node_sizes.append(100)
                 node_colors.append("red")
            # elif show_gas_stations and node in self.gas_stations:
            #     node_sizes.append(50)
            #     node_colors.append("blue")
            else:
                node_sizes.append(0)
                node_colors.append(EDGE_COLORS[SLOW_ROAD_COST])


        nx.draw_networkx_nodes(graph.G, pos, node_size=node_sizes, node_color=node_colors)
        plt.title(f"Road Network with {num_nodes} nodes and {num_edges} edges")
        plt.show()