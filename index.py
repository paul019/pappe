from pdf_annotate import PdfAnnotator, Location, Appearance
import math
import csv
import random
import tomllib

# Read config:

with open('config.toml', 'rb') as f:
    config = tomllib.load(f)

paper_config = config['paper']
grid_config = config['grid']
drawing_config = config['drawing']

csvFilePath = 'input/data.csv';
inputFilePath = 'input/a.pdf';
outputFilePath = 'output/b.pdf';

factors = [2, 4, 5]

####################################

# Read CSV-file:

file = open(csvFilePath)
csvReader = csv.reader(file)

points = [];

for row in csvReader:
    points.append((float(row[0]), float(row[1])))

####################################

# Analyze data and choose axis scale and offset:

minX = points[0][0]
minY = points[0][1]
maxX = points[0][0]
maxY = points[0][1]

for point in points:
    minX = min(minX, point[0])
    minY = min(minY, point[1])
    maxX = max(maxX, point[0])
    maxY = max(maxY, point[1])

scaleX = 1;
scaleY = 1;

offsetX = 0;
offsetY = 0;

if minX >= 0:
    offsetX = 0
    scaleX = (grid_config['num_x_blocks']-offsetX) / maxX
elif maxX <= 0:
    offsetX = grid_config['num_x_blocks']
    scaleX = offsetX / (-minX)
else:
    offsetX = minX/(minX-maxX) * (grid_config['num_x_blocks']/grid_config['num_x_sub_blocks_per_block'])
    if offsetX < grid_config['num_x_blocks']/grid_config['num_x_sub_blocks_per_block']/2:
        offsetX = math.ceil(offsetX) * grid_config['num_x_sub_blocks_per_block']
    else:
        offsetX = math.floor(offsetX) * grid_config['num_x_sub_blocks_per_block']
    scaleX = min( offsetX / (-minX), (grid_config['num_x_blocks']-offsetX) / maxX )

if minY >= 0:
    offsetY = 0
    scaleY = (grid_config['num_y_blocks']-offsetY) / maxY
elif maxY <= 0:
    offsetY = grid_config['num_y_blocks']
    scaleY = offsetY / (-minY)
else:
    offsetY = minY/(minY-maxY) * (grid_config['num_y_blocks']/grid_config['num_y_sub_blocks_per_block'])
    if offsetY < grid_config['num_y_blocks']/grid_config['num_y_sub_blocks_per_block']/2:
        offsetY = math.ceil(offsetY) * grid_config['num_y_sub_blocks_per_block']
    else:
        offsetY = math.floor(offsetY) * grid_config['num_y_sub_blocks_per_block']
    scaleY = min( offsetY / (-minY), (grid_config['num_y_blocks']-offsetY) / maxY )


scaleX = pow(10, math.floor(math.log10(scaleX)));
scaleY = pow(10, math.floor(math.log10(scaleY)));

newScaleX = scaleX
newScaleY = scaleY

factors.sort();

for factor in factors:
    scaleX_ = scaleX * factor
    if maxX * scaleX_ + offsetX <= grid_config['num_x_blocks'] and minX * scaleX_ + offsetX >= 0:
        newScaleX = scaleX_

for factor in factors:
    scaleY_ = scaleY * factor
    if maxY * scaleY_ + offsetY <= grid_config['num_y_blocks'] and minY * scaleY_ + offsetY >= 0:
        newScaleY = scaleY_

scaleX = newScaleX
scaleY = newScaleY

####################################

# Open pdf annotator:

a = PdfAnnotator(inputFilePath)
a.set_page_dimensions((paper_config['width'], paper_config['height']), 0)

####################################

# Define functions for annotation:

def getPdfCoordsFromDataPoint(x, y):
    grid_x = (x*scaleX+offsetX) * grid_config['width'] / grid_config['num_x_blocks'] + grid_config['x'];
    grid_y = (y*scaleY+offsetY) * grid_config['height'] / grid_config['num_y_blocks'] + grid_config['y']; 
    return (grid_x, grid_y);

def getPdfCoordsFromGridCoords(x, y):
    grid_x = x * grid_config['width'] / grid_config['num_x_blocks'] + grid_config['x'];
    grid_y = y * grid_config['height'] / grid_config['num_y_blocks'] + grid_config['y']; 
    return (grid_x, grid_y);

def printDatapoint(x, y):
    coords = getPdfCoordsFromDataPoint(x,y);
    a.add_annotation(
        'line',
        Location(points=[(coords[0]-drawing_config['cross_size']/2,coords[1]-drawing_config['cross_size']/2),(coords[0]+drawing_config['cross_size']/2,coords[1]+drawing_config['cross_size']/2)], page=0),
        Appearance(stroke_color=(1, 0, 0), stroke_width=0.5)
    )
    a.add_annotation(
        'line',
        Location(points=[(coords[0]+drawing_config['cross_size']/2,coords[1]-drawing_config['cross_size']/2),(coords[0]-drawing_config['cross_size']/2,coords[1]+drawing_config['cross_size']/2)], page=0),
        Appearance(stroke_color=(1, 0, 0), stroke_width=0.5)
    )

def printVertAxisNumber(gridNum):
    dataNum = (gridNum-offsetY)/scaleY
    if dataNum == 0:
        return
    coords = getPdfCoordsFromGridCoords(offsetX, gridNum);
    a.add_annotation(
        'line',
        Location(points=[(coords[0]-drawing_config['axis_tick_size']/2,coords[1]),(coords[0]+drawing_config['axis_tick_size']/2,coords[1])], page=0),
        Appearance(stroke_color=(0, 0, 0), stroke_width=1)
    )
    label = "{:.2e}".format(dataNum)
    a.add_annotation(
        'text',
        Location(x1=coords[0]-200,y1=coords[1]-50,x2=coords[0]-drawing_config['axis_tick_size']/2,y2=coords[1]+50, page=0),
        Appearance(content = label,fill=[0, 0, 0],
                stroke_width=1,
                font_size=40,text_align='right')
    )

def printHorAxisNumber(gridNum):
    dataNum = (gridNum-offsetX)/scaleX
    if dataNum == 0:
        return
    coords = getPdfCoordsFromGridCoords(gridNum, offsetY);
    a.add_annotation(
        'line',
        Location(points=[(coords[0],coords[1]-drawing_config['axis_tick_size']/2),(coords[0],coords[1]+drawing_config['axis_tick_size']/2)], page=0),
        Appearance(stroke_color=(0, 0, 0), stroke_width=1)
    )
    label = "{:.2e}".format(dataNum)
    a.add_annotation(
        'text',
        Location(x1=coords[0]-100,y1=coords[1]-100-drawing_config['axis_tick_size']/2,x2=coords[0]+100,y2=coords[1]-drawing_config['axis_tick_size']/2, page=0),
        Appearance(content = label,fill=[0, 0, 0],
                stroke_width=1,
                font_size=40,text_align='center')
    )

def printVertAxis():
    coordsStart = getPdfCoordsFromGridCoords(offsetX, 0);
    coordsEnd = getPdfCoordsFromGridCoords(offsetX, grid_config['num_y_blocks']);
    a.add_annotation(
        'line',
        Location(points=[coordsStart, coordsEnd], page=0),
        Appearance(stroke_color=(0, 0, 0), stroke_width=1)
    )

def printHorAxis():
    coordsStart = getPdfCoordsFromGridCoords(0, offsetY);
    coordsEnd = getPdfCoordsFromGridCoords(grid_config['num_x_blocks'], offsetY);
    a.add_annotation(
        'line',
        Location(points=[coordsStart, coordsEnd], page=0),
        Appearance(stroke_color=(0, 0, 0), stroke_width=1)
    )

####################################

# Do annotation:

for i in range(int(grid_config['num_y_blocks'] / grid_config['num_y_sub_blocks_per_block']) + 1):
    printVertAxisNumber(i * grid_config['num_y_sub_blocks_per_block'])

for i in range(int(grid_config['num_x_blocks'] / grid_config['num_x_sub_blocks_per_block']) + 1):
    printHorAxisNumber(i * grid_config['num_x_sub_blocks_per_block'])

printVertAxis()

printHorAxis()

for point in points:
    printDatapoint(point[0], point[1])

####################################

# Export:

a.write(outputFilePath)