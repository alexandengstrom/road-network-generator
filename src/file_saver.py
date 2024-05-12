import time
import json
import logging

def save_to_file(graph, output_path):
    if not output_path:
        output_path = f"road_network_graph-{time.time()}.rn"

    try:
        with open(output_path, "w") as output:
            buffer = str()
            buffer += f"{graph.width} {graph.height}\n"
            buffer += f"{graph.number_of_nodes()} {graph.number_of_edges()}\n"

            for node in graph.nodes():
                buffer += f"{node[0]} {node[1]} {graph.get_node_type(node)}\n"

            for u, v, data in graph.edges():
                buffer += f"{u[0]} {u[1]} {v[0]} {v[1]} {round(data['weight'], 2)}\n"

            output.write(buffer)
    except IOError as e:
        logging.error(f"Failed to write to file {output_path}: {e}")
    except Exception as e:
        logging.critical(f"An unexpected error occurred while saving the graph to file: {str(e)}")


def save_to_json(graph, output_path):
    if not output_path:
        output_path = f"road_network_graph-{time.time()}.json"

    graph_data = {
        "width": graph.width,
        "height": graph.height,
        "nodes": [],
        "edges": []
    }

    for node in graph.nodes():
        node_data = {
            "x": node[0],
            "y": node[1],
            "type": graph.get_node_type(node)
        }
        graph_data["nodes"].append(node_data)

    for u, v, data in graph.edges():
        edge_data = {
            "u": {"x": u[0], "y": u[1]},
            "v": {"x": v[0], "y": v[1]},
            "weight": round(data['weight'], 2)
        }
        graph_data["edges"].append(edge_data)

    try:
        with open(output_path, "w") as output_file:
            json.dump(graph_data, output_file, indent=4)
    except IOError as e:
        logging.error(f"Failed to write to file {output_path}: {e}")
    except json.JSONDecodeError as e:
        logging.error(f"JSON encoding error when trying to write to file: {e}")
    except Exception as e:
        logging.critical(f"An unexpected error occurred while saving the graph to file: {str(e)}")

