# Road Network Generator
Road Network Generator is a command line tool designed to generate undirected weighted graph representations that resemble road networks. This tool is configurable through various flags allowing users to specify the size of the graph, utilize seeds for reproducible results, save graphs in different formats, and plot the graph visually. It guarantees the generation of a connected graph. The tool is great for things like simulations, academic studies, and testing pathfinding algorithms.
## Background
I created the Road Network Generator to quickly produce different road network graphs for my experiments with pathfinding algorithms. This tool helps in testing these algorithms by generating varied and complex road networks easily. Traffic cameras are included in these networks as key points because i am experimenting with finding the shortest paths between all traffic camera pairs in an efficient way.
## Setup
1. Clone the repository
```bash
git clone git@github.com:alexandengstrom/road-network-generator.git
```
2. Navigate to the project root directory
```bash
cd road-network-generator
```
3. Run the setup script
```bash
bash setup.sh
```
The setup.sh script automates the setup of the Road Network Generator by creating a Python virtual environment, installing necessary dependencies, and making the main script executable. It also adds the project directory to your system's PATH, ensuring you can run the tool from anywhere in the terminal. 
## Usage
After installing the Road Network Generator, you can run it from anywhere in your system using the rd-gen command followed by various flags to customize your graph generation. Here’s a breakdown of all the flags you can use to customize the road network graph:
- **-s, --size [int]**: Specifies the size of the graph. It should probably be between 1 and 50. By default 13.
- **-S, --seed [int]**: Uses a specified seed for graph generation for reproducible results. If omitted, a random seed is used.
- **-W, --width [int]**: Sets the width of the graph, defining the maximum X coordinate. By default 1200.
- **-H, --height [int]**: Sets the height of the graph, defining the maximum Y coordinate. By default 800.
- **-c, --camera_density [int]**: Determines the density of traffic cameras in the road network. By default 10.
- **-p, --plot**: Plots the graph after generation. By default, the graph is not plotted.
- **-C, --plot_cameras**: If plotting is enabled, this flag will also display cameras on the plot.
- **-f, --file**: Saves the generated graph to a file. Uses an own file format by default.
- **-o, --output [file path]**: Specifies the output file name for saving the graph. Requires -f. If not provided a auto generated filename with timestamp will be used.
- **-j, --json**: Saves the output file in JSON format. Requires -f.
- **-l, --log**: Enables logging of messages during graph generation.
- **-x, --complex**: Generates a more complex and correct network at the expense of increased computational cost.
### Example:
Creates a graph with the dimensions 2000x1000 and saves it in JSON-format to my_graph.json. It will also plot the graph visually.
```
rd-gen -W 2000 -H 1000 -s 15 -f -o my_graph.json -j -p
```

## Algorithm
The generator begins by creating a graph structure where different city types are instantiated with predefined properties based on their size and importance. Cities are placed randomly within a defined area while ensuring they maintain a minimum distance from each other to avoid overlap. The backbone of the network is formed by connecting major cities (metropolises and urban centers) with highways. These connections are designed to simulate main traffic routes and are the first to be laid out. The generator ensures these connections make geographical sense and avoid unnecessary detours. Once the primary connections are established, the generator begins to incorporate towns, villages, and hamlets. These smaller cities are connected to the nearest larger cities or directly to the highway system, using minor roads. At last last we delete all unnecessary nodes in the graph, this means all nodes which have just two neighbours and doesnt have a special meaning. After that we make sure the graph is connected and if not we add some extra edges.

The roads in the network are assigned costs based on their type and importance. The highways will have lower cost than streets or rural roads. There is five different kind of roads in the graph. These are highways, main roads, minor roads, rural roads, slow roads and streets.

## Visual examples
![Screenshot from 2024-05-10 17-09-17](https://github.com/alexandengstrom/road-network-generator/assets/123507241/d8fbbce8-b12f-42a1-956a-80963ac56047)
![Screenshot from 2024-05-10 17-10-14](https://github.com/alexandengstrom/road-network-generator/assets/123507241/24d1688f-1824-42fa-997f-993905c66b67)
![Screenshot from 2024-05-10 17-11-37](https://github.com/alexandengstrom/road-network-generator/assets/123507241/02e89d19-1875-4f5d-bb81-3a3f5bfd95c9)


## Contributing
If you have enhancements, bug fixes, or improvements to propose, feel free to send a pull request for review. For any questions or discussions about contributions, feel free to open an issue in the repository to begin the conversation.
