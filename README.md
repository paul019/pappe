# A helping tool to create diagrams in PAP1
 
## Run

Install the necessary python package:

`pip3 install pdf_annotate`

Run the script:

`python3 src/pap1.py`


## Documentation

### Coordinate systems

In this project, there are three distinct coordinate systems:

- The coordinate system of the page (e. g. `4133 x 5846 px`).
- The coordinate system of the grid on the paper (e. g. `180 x 270`).
- The coordinate system of the data that is displayed on the grid (this depends on the actual data; e. g. the data's maximum value in x direction might be $10^6$).

All coordinate systems are oriented with numbers increasing upwards and rightwards.

### Global input variables

| Parameter | Coordinate system | Meaning |
| --- | --- | --- |
| `pageWidth` | page | Page width in `px` |
| `pageHeight` | page | Page height in `px` |
| `crossSize` | page | Size of the displayed data points |
| `axisTickSize` | page | Size of the axis ticks |
| `gridX` | page | x-position of the bottom left corner of the grid on the page |
| `gridY` | page | y-position of the bottom left corner of the grid on the page |
| `gridWidth` | page | width of the bottom left corner of the grid on the page |
| `gridHeight` | page | height of the bottom left corner of the grid on the page |
| `gridHorCount` | grid | number of grid boxes in the horizontal direction |
| `gridHorBlockCount` | grid | number of grid boxes per horizontal grid block (usually this is 10); this number should divide `gridHorCount` |
| `gridVertBlockCount` | grid | number of grid boxes per vertical grid block (usually this is 10); this number should divide `gridVertCount` |
| `csvFilePath` | - | relative path of your csv file (see below for more information on the csv file) |
| `inputFilePath` | - | relative path of your input pdf file (usually either a blank page or millimeter paper) |
| `outputFilePath` | - | relative path of your output pdf file (this should be different from `inputFilePath`!) |
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
