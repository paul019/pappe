from pdf_annotate import PdfAnnotator, Location, Appearance
import math
import csv
import tomllib

# Read config:

with open('grids/grid1.toml', 'rb') as f:
    config = tomllib.load(f)

paper_config = config['paper']
grid_config = config['grid']
drawing_config = config['drawing']

csvFilePath = 'input/data.csv';
outputFilePath = 'output/output.pdf';
factors = [2, 4, 5]
shouldContainOriginX = False;
shouldContainOriginY = False;

####################################

# Read CSV-file:

file = open(csvFilePath)
csvReader = csv.reader(file)

points = [];
errors = [];

for row in csvReader:
    points.append((float(row[0]), float(row[1])))

    if len(row) == 2:
        errors.append((-1, -1))
    elif len(row) == 3:
        errors.append((float(row[2]), float(row[2])))
    else:
        errors.append((float(row[2]), float(row[3])))

####################################

# Analyze data:

minX = points[0][0]
minY = points[0][1]
maxX = points[0][0]
maxY = points[0][1]

for point in points:
    minX = min(minX, point[0])
    minY = min(minY, point[1])
    maxX = max(maxX, point[0])
    maxY = max(maxY, point[1])

pointsOffsetX = 0;
pointsOffsetY = 0;

# Handle case of not including the origin (currently bad documentation):

if not shouldContainOriginX and minX <= 0 and maxX >= 0:
    shouldContainOriginX = True

if not shouldContainOriginX:
    if minX <= 0:
        pointsOffsetX = -pow(10, math.floor(math.log10(-maxX)));
        newPointsOffsetX = pointsOffsetX;

        for i in range(2, 10):
            if i*pointsOffsetX >= maxX:
                newPointsOffsetX = i*pointsOffsetX

        pointsOffsetX = newPointsOffsetX;
    else:
        pointsOffsetX = pow(10, math.floor(math.log10(minX)));
        newPointsOffsetX = pointsOffsetX;

        for i in range(2, 10):
            if i*pointsOffsetX <= minX:
                newPointsOffsetX = i*pointsOffsetX

        pointsOffsetX = newPointsOffsetX;

if not shouldContainOriginY and minY <= 0 and maxY >= 0:
    shouldContainOriginY = True

if not shouldContainOriginY:
    if minY <= 0:
        pointsOffsetY = -pow(10, math.floor(math.log10(-maxY)));
        newPointsOffsetY = pointsOffsetY;

        for i in range(2, 10):
            if i*pointsOffsetY >= maxY:
                newPointsOffsetY = i*pointsOffsetY

        pointsOffsetY = newPointsOffsetY;
    else:
        pointsOffsetY = pow(10, math.floor(math.log10(minY)));
        newPointsOffsetY = pointsOffsetY;

        for i in range(2, 10):
            if i*pointsOffsetY <= minY:
                newPointsOffsetY = i*pointsOffsetY
        
        pointsOffsetY = newPointsOffsetY;

for i in range(len(points)):
    points[i] = (points[i][0] - pointsOffsetX, points[i][1] - pointsOffsetY)

minX -= pointsOffsetX
maxX -= pointsOffsetX

minY -= pointsOffsetY
maxY -= pointsOffsetY

# Choose coordinate axis scaling and offset:

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
    offsetX = minX/(minX-maxX) * (grid_config['num_x_blocks']/grid_config['num_x_blocks_per_super_block'])
    if offsetX < grid_config['num_x_blocks']/grid_config['num_x_blocks_per_super_block']/2:
        offsetX = math.ceil(offsetX) * grid_config['num_x_blocks_per_super_block']
    else:
        offsetX = math.floor(offsetX) * grid_config['num_x_blocks_per_super_block']
    scaleX = min( offsetX / (-minX), (grid_config['num_x_blocks']-offsetX) / maxX )

if minY >= 0:
    offsetY = 0
    scaleY = (grid_config['num_y_blocks']-offsetY) / maxY
elif maxY <= 0:
    offsetY = grid_config['num_y_blocks']
    scaleY = offsetY / (-minY)
else:
    offsetY = minY/(minY-maxY) * (grid_config['num_y_blocks']/grid_config['num_y_blocks_per_super_block'])
    if offsetY < grid_config['num_y_blocks']/grid_config['num_y_blocks_per_super_block']/2:
        offsetY = math.ceil(offsetY) * grid_config['num_y_blocks_per_super_block']
    else:
        offsetY = math.floor(offsetY) * grid_config['num_y_blocks_per_super_block']
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

a = PdfAnnotator(paper_config['file'])
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

def printErrorBar(x, y, lowerError, upperError):
    if lowerError == -1 or upperError == -1:
        return;

    coordsTop = getPdfCoordsFromDataPoint(x,y+upperError);
    coordsBottom = getPdfCoordsFromDataPoint(x,y-lowerError);

    a.add_annotation(
        'line',
        Location(points=[coordsBottom, coordsTop], page=0),
        Appearance(stroke_color=(1, 0, 0), stroke_width=0.5)
    )
    a.add_annotation(
        'line',
        Location(points=[(coordsBottom[0]-drawing_config['cross_size']/2, coordsBottom[1]), (coordsBottom[0]+drawing_config['cross_size']/2, coordsBottom[1])], page=0),
        Appearance(stroke_color=(1, 0, 0), stroke_width=0.5)
    )
    a.add_annotation(
        'line',
        Location(points=[(coordsTop[0]-drawing_config['cross_size']/2, coordsTop[1]), (coordsTop[0]+drawing_config['cross_size']/2, coordsTop[1])], page=0),
        Appearance(stroke_color=(1, 0, 0), stroke_width=0.5)
    )

def printVertAxisNumber(gridNum):
    dataNum = (gridNum-offsetY)/scaleY + pointsOffsetY
    if dataNum == 0:
        return
    coords = getPdfCoordsFromGridCoords(offsetX if shouldContainOriginX else 0, gridNum);
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
    dataNum = (gridNum-offsetX)/scaleX + pointsOffsetX
    if dataNum == 0:
        return
    coords = getPdfCoordsFromGridCoords(gridNum, offsetY if shouldContainOriginY else 0);
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
    coordsStart = getPdfCoordsFromGridCoords(offsetX if shouldContainOriginX else 0, 0);
    coordsEnd = getPdfCoordsFromGridCoords(offsetX if shouldContainOriginX else 0, grid_config['num_y_blocks']);
    a.add_annotation(
        'line',
        Location(points=[coordsStart, coordsEnd], page=0),
        Appearance(stroke_color=(0, 0, 0), stroke_width=1)
    )

def printHorAxis():
    coordsStart = getPdfCoordsFromGridCoords(0, offsetY if shouldContainOriginY else 0);
    coordsEnd = getPdfCoordsFromGridCoords(grid_config['num_x_blocks'], offsetY if shouldContainOriginY else 0);
    a.add_annotation(
        'line',
        Location(points=[coordsStart, coordsEnd], page=0),
        Appearance(stroke_color=(0, 0, 0), stroke_width=1)
    )

####################################

# Do annotation:

for i in range(int(grid_config['num_y_blocks'] / grid_config['num_y_blocks_per_super_block']) + 1):
    printVertAxisNumber(i * grid_config['num_y_blocks_per_super_block'])

for i in range(int(grid_config['num_x_blocks'] / grid_config['num_x_blocks_per_super_block']) + 1):
    printHorAxisNumber(i * grid_config['num_x_blocks_per_super_block'])

printVertAxis()

printHorAxis()

for i in range(len(points)):
    point = points[i]
    error = errors[i]

    printDatapoint(point[0], point[1])
    printErrorBar(point[0], point[1], error[0], error[1])

####################################

# Export:

a.write(outputFilePath)