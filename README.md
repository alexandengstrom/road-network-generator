# Road Network Generator
Road Network Generator is a command line tool designed to generate graph representations that resemble road networks. This tool is configurable through various flags allowing users to specify the size of the graph, utilize seeds for reproducible results, save graphs in different formats, and plot the graph visually. It guarantees the generation of a connected graph. The tool is great for things like simulations, academic studies, and testing pathfinding algorithms.

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
