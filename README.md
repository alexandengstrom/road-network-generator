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
The algorithm starts by constructing a graph representing a network of cities categorized by their size and importance. Each city type is initialized with specific properties and randomly placed within a designated area, ensuring a minimum distance between them to prevent overlap. The main infrastructure begins by connecting larger cities—such as metropolises and urban centers—via highways that mimic major traffic arteries. These connections are planned to ensure they are geographically logical and minimize detours. As the primary highway network takes shape, the algorithm integrates smaller towns, villages, and hamlets, connecting them to the nearest larger city or directly to the highway network through minor roads.

The next phase involves subdividing the map into a 10x10 grid, placing each city within these squares. This aids in managing distances between smaller cities, ensuring that while they are distanced enough to prevent congestion, they don't face excessively long routes to reach one another. At this stage, additional connections are made between neighboring squares. The method for creating these connections varies: without the `-x` flag, the algorithm selects a random point in one square and connects it to the nearest point in a neighboring square, resulting in a time complexity of $O(n)$. With the `-x` flag, it identifies and connects the closest pair of points across the squares, resulting in a time complexity of $O(n\log_2(n))$.

After that we make sure the graph is connected. We will start by deciding which component is our largest component by looking at the size of each disconnected component. After that we will loop through every disconnected component and connect it to the largest component. In this step there is also a difference in time complexity depending on if the `-x` flag has been used. If the flag is not used, we will just pick a random city from both components and connect them, giving us a time complexity of $O(1)$. If the flag is used, we will again find the closest pair which gives us a time complexity of $O(n\log_2(n))$.

Finally, the algorithm cleans up the graph by removing any unnecessary nodes—those with only two neighbors and no special significance.

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
