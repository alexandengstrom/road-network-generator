from graph_generator import RoadNetwork
import plotter
import argparse
from config import *
from file_saver import save_to_file, save_to_json
import logging

def main(args):
    if args.log:
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    else:
        logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')

    graph = RoadNetwork(args.width, args.height)
    graph.generate(size=args.size, seed=args.seed, camery_density=args.camera_density, make_complex=args.complex)

    if args.plot:
        plotter.plot(graph, show_cameras=args.plot_cameras, grayscale=args.grayscale)

    if args.file:
        if args.json:
            save_to_json(graph=graph, output_path=args.output)
        else:
            save_to_file(graph=graph, output_path=args.output)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a customizable graph for road networks.")
    
    parser.add_argument("-s", "--size", type=int, help="Decides the size of the graph", default=13)
    parser.add_argument("-S", "--seed", type=int, help="Generates the graph based on a seed. If not given, a random seed will be created", default=None)
    parser.add_argument("-W", "--width", type=int, help="The width of the graph, the max x coordinate", default=WIDTH)
    parser.add_argument("-H", "--height", type=int, help="The height of the graph, the max y coordinate", default=HEIGHT)
    parser.add_argument("-c", "--camera_density", type=int, help="Decides how much cameras the road network will have", default=10)
    parser.add_argument("-p", "--plot", action='store_true', help="If set, the graph will be plotted")
    parser.add_argument("-C", "--plot_cameras", action='store_true', help="If set, cameras will be shown when plotting")
    parser.add_argument("-g", "--grayscale", action='store_true', help="If set, the plot will be in grayscale")
    parser.add_argument("-f", "--file", action='store_true', help="If set, the graph will be saved to a file")
    parser.add_argument("-o", "--output", type=str, help="The name of the output file. This is used only if the -f flag is also used", default=None)
    parser.add_argument("-j", "--json", action='store_true', help="If set, the output file will be in JSON format. This is used only if -f flag is also used")
    parser.add_argument("-l", "--log", action='store_true', help="If set, logging messages will be displayed")
    parser.add_argument("-x", "--complex", action='store_true', help="If set, a more accurate network will be created, but it will be more expensive")

    args = parser.parse_args()

    if args.output and not args.file:
        parser.error("The -o/--output argument requires the -f/--file flag.")

    if args.json and not args.file:
        parser.error("The -j/--json argument requires the -f/--file flag.")

    if args.plot_cameras and not args.plot:
        parser.error("The -C/--plot_cameras argument requires the -p/--plot flag.")

    if args.grayscale and not args.plot:
        parser.error("The -g/--grayscale argument requires the -p/--plot flag.")
    
    main(args)