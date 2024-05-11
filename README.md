# Road Network Generator
Road Network Generator is a command line tool designed to generate undirected weighted graphs $G = (V, E)$, where vertices $V$ represent intersections, and edges $E$ represent road segments between these points. Each edge has an associated weight representing the cost, or distance combined with speed limit. The tool is great for things like simulations, academic studies, and testing pathfinding algorithms.

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
| Flag                      | Description                                                                            | Default Value          |
|---------------------------|----------------------------------------------------------------------------------------|------------------------|
| `-s, --size [int]`        | Specifies the size of the graph. It should probably be between 1 and 50.                | 13                     |
| `-S, --seed [int]`        | Uses a specified seed for graph generation for reproducible results. With `-l` the seed used will be printed                     | Random seed            |
| `-W, --width [int]`       | Sets the width of the graph, defining the maximum X coordinate.                         | 1200                   |
| `-H, --height [int]`      | Sets the height of the graph, defining the maximum Y coordinate.                        | 800                    |
| `-c, --camera_density [int]` | Determines the density of traffic cameras in the road network.                         | 10                     |
| `-p, --plot`              | Plots the graph after generation.                                                       | Disabled               |
| `-C, --plot_cameras`      | If plotting is enabled, this flag will also display cameras on the plot.                | N/A                    |
| `-f, --file`              | Saves the generated graph to a file. Uses an own file format by default.                | Disabled        |
| `-o, --output [file path]`| Specifies the output file name for saving the graph. Requires `-f`.                    | Auto-generated filename|
| `-j, --json`              | Saves the output file in JSON format. Requires `-f`.                                    | N/A                    |
| `-l, --log`               | Enables logging of messages during graph generation.                                    | N/A                    |
| `-x, --complex`           | Generates a more complex and correct network at the expense of increased computational cost. | N/A              |
### Example:
Creates a graph with the dimensions 2000x1000 and saves it in JSON-format to my_graph.json. It will also plot the graph visually.
```
rd-gen -W 2000 -H 1000 -s 15 -f -o my_graph.json -j -p
```

### Save to file:
If the `-j` flag is not used, the output will be in -rn format. This works in the following way:
- First Line: Contains the graph's width and height separated by a space.
- Second Line: Contains the total number of nodes ($|V|$) and edges ($|E|$) in the graph, separated by a space.
- Following $|V|$ Lines: Each line represents one node with its **x-coordinate**, **y-coordinate**, and **node type** (like a traffic camera or regular intersection), separated by spaces.
- Remaining $|E|$ Lines: Each edge is represented by a line that includes the **x** and **y** coordinates of the starting node (u), the **x** and **y** coordinates of the ending node (v) and the **weight** of the edge (e.g., representing the cost or distance), formatted to two decimal place.

If the `-j` flag i used, the output will be in JSON-format:
- Graph Dimensions: Encoded as properties **width** and **height**.
- Nodes: A list of node objects, each containing **x**: The x-coordinate of the node, **y**: The y-coordinate of the node and **type**: The type of the node (like a traffic camera or regular intersection).
- Edges: A list of edge objects, each describing a connection between two nodes and containing: **u**: An object with properties **x** and **y**, representing the starting node's coordinates, **v**: An object with properties **x** and **y**, representing the ending node's coordinates and **weight**: The weight of the edge, indicating the cost or distance.

## Algorithm
The generator begins by creating a graph structure where different city types are instantiated with predefined properties based on their size and importance. Cities are placed randomly within a defined area while ensuring they maintain a minimum distance from each other to avoid overlap. The backbone of the network is formed by connecting major cities (metropolises and urban centers) with highways. These connections are designed to simulate main traffic routes and are the first to be laid out. The generator ensures these connections make geographical sense and avoid unnecessary detours. Once the primary connections are established, the generator begins to incorporate towns, villages, and hamlets. These smaller cities are connected to the nearest larger cities or directly to the highway system, using minor roads. 

At this stage. The map will be divided into squares. The current config is to create a 10x10 grid and place all cities, villages etc in one of these squares. Then we create one more connections from each square to its neighbour squares. This is because we want to avoid smaller villages being close to each other but have a very long road to reach each other. At this stage there is a difference when using the `-x` flag. If the flag is not used, we will pick a random point from the first square and then search for the closest point in the second square, resulting in a time complexity of $O(n)$. If the flag is used we will make sure we find the closest pair from both squares resulting in a time complexity of $O(n^2)$.

At last last we delete all unnecessary nodes in the graph, this means all nodes which have just two neighbours and doesnt have a special meaning. After that we make sure the graph is connected. We will start by deciding which component is our main component by looking at the cardinality of each disconnected component. After that we will loop through every disconnected component and connect it to the main component. In this step there is also a difference in time complexity depending on if the `-x` flag has been used. If the flag is not used, we will just pick a random city from both components and connect them, giving us a time complexity of $O(1)$. If the flag is used, we will pick a random city from the disconnected component and connect it to the closest point in the main component, giving us a time complexity of $O(n)$. I have experimented with choosing a correct pair here with time complexity of $O(n^2)$ at this point but it is too expensive, we cannot afford that here.

The roads in the network are assigned costs based on their type and importance. The highways will have lower cost than streets or rural roads. There is five different kind of roads in the graph. These are highways, main roads, minor roads, rural roads, slow roads and streets.

The figure and table below shows how the number of nodes and edges grows as the variable size increases. This data was collected with a random seed for every generation which is why sometimes the number of edges decreases while the size increases.

![Screenshot from 2024-05-10 19-38-51](https://github.com/alexandengstrom/road-network-generator/assets/123507241/970a6c17-8aea-457e-8c43-cb7df06f4ef1)


| Size | Nodes  | Edges  |
|------|--------|--------|
| 1    | 20     | 20     |
| 3    | 65     | 69     |
| 5    | 894    | 1326   |
| 10   | 10998  | 19289  |
| 15   | 75129  | 135502 |
| 20   | 170630 | 320529 |
| 25   | 213142 | 408277 |

## Visual examples
![Screenshot from 2024-05-10 17-09-17](https://github.com/alexandengstrom/road-network-generator/assets/123507241/d8fbbce8-b12f-42a1-956a-80963ac56047)
![Screenshot from 2024-05-10 17-10-14](https://github.com/alexandengstrom/road-network-generator/assets/123507241/24d1688f-1824-42fa-997f-993905c66b67)
![Screenshot from 2024-05-10 17-11-37](https://github.com/alexandengstrom/road-network-generator/assets/123507241/02e89d19-1875-4f5d-bb81-3a3f5bfd95c9)


## Contributing
If you have enhancements, bug fixes, or improvements to propose, feel free to send a pull request for review. For any questions or discussions about contributions, feel free to open an issue in the repository to begin the conversation.
