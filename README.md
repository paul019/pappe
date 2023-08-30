# A helping tool to create diagrams in PAP1
 
## Installation

First, install the necessary python package:

`pip3 install pdf_annotate`

Now, clone this repository on your local machine:

`git clone https://github.com/paul019/pap1-helper`

To run the script, use:

`python3 index.py`


## Documentation

### Coordinate systems

In this project, there are three distinct coordinate systems:

- The coordinate system of the paper (e. g. `4133 x 5846 px`).
- The coordinate system of the grid on the paper (e. g. `180 x 270`).
- The coordinate system of the data that is displayed on the grid (this depends on the actual data; e. g. the data's maximum value in x direction might be $10^6$).

All coordinate systems are oriented with numbers increasing upwards and rightwards.

### Config file

| Parameter | Coordinate system | Meaning |
| --- | --- | --- |
| `paper/file` | - | relative path of your input pdf file (usually either a blank paper or millimeter paper) |
| `paper/width` | paper | paper width in `px` |
| `paper/height` | paper | paper height in `px` |
| `grid/width` | paper | width of the bottom left corner of the grid on the paper |
| `grid/height` | paper | height of the bottom left corner of the grid on the paper |
| `grid/x` | paper | x-position of the bottom left corner of the grid on the paper |
| `grid/y` | paper | y-position of the bottom left corner of the grid on the paper |
| `grid/num_x_blocks` | grid | number of grid boxes in the horizontal direction |
| `grid/num_y_blocks` | grid | number of grid boxes in the vertical direction |
| `grid/num_x_blocks_per_super_block` | grid | number of grid boxes per horizontal grid block (usually this is 10); this number should divide `grid/num_x_blocks` |
| `grid/num_y_blocks_per_super_block` | grid | number of grid boxes per vertical grid block (usually this is 10); this number should divide `grid/num_y_blocks` |
| `drawing/cross_size` | paper | Size of the displayed data points |
| `drawing/axis_tick_size` | paper | Size of the axis ticks |
| `csvFilePath` | - | relative path of your csv file (see below for more information on the csv file) |
| `outputFilePath` | - | relative path of your output pdf file |
| `factors` | - | array of coordinate axis scale factors (TODO: explain!) |
| `shouldContainOriginX` | - | whether the origin of the x axis should be included |
| `shouldContainOriginY` | - | whether the origin of the y axis should be included |

### Other important variables

| Variable | Coordinate system | Meaning |
| --- | --- | --- |
| `minX` etc. | data | maximum x value in the dataset (including error bars!) |
| `scaleX` etc. | grid, data | scale factor between the grid coordinate system and the data coordinate system |
| `offsetX` etc. | grid | x-location of the data coordinate system origin within the grid coordinate system |
| `pointsOffsetX` etc. | data | if the user decides to not include the origin (see `shouldContainOriginX`), this variable adds an offset to the data to create a 'virtual' origin to the data; otherwise this variable is `0` |
| `points` | - | array of data points; each entry is a tupel of x and y values |
| `errors` | - | array of errors; each entry is a tupel of lower and upper errors; if there is no error value, the tupel contains `-1` |

### CSV file structure

Depending on how many rows the csv file has, its content is interpreted differently:

#### 2 Rows

- 1st row: values for x-axis
- 2nd row: values for y-axis

#### 3 Rows

- 1st row: values for x-axis
- 2nd row: values for y-axis
- 3rd row: errors for y-axis values

#### 4 Rows

- 1st row: values for x-axis
- 2nd row: values for y-axis
- 3rd row: lower errors for y-axis values
- 4th row: upper errors for y-axis values
