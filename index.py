from pdf_annotate import PdfAnnotator, Location, Appearance
import math
import csv
import random

pageWidth = 4133;
pageHeight = 5846;

crossSize = 10;
axisTickSize = 20;

gridX = 406;
gridY = 264;
gridWidth = 3543;
gridHeight = 5318;

gridHorCount = 180;
gridHorBlockCount = 10;
gridVertCount = 270;
gridVertBlockCount = 10;

scaleX = 1;
scaleY = 1;

offsetX = 0;
offsetY = 0;

####################################

file = open('data.csv')
csvReader = csv.reader(file)

points = [];

for row in csvReader:
    points.append((float(row[0]), float(row[1])))

#for i in range(100):
    #points.append((random.uniform(-10000, 10000),random.uniform(-10000, 10000)))

minX = float(points[0][0])
minY = float(points[0][1])
maxX = float(points[0][0])
maxY = float(points[0][1])

for point in points:
    minX = min(minX, float(point[0]))
    minY = min(minY, float(point[1]))
    maxX = max(maxX, float(point[0]))
    maxY = max(maxY, float(point[1]))

if minX >= 0:
    offsetX = 0
    scaleX = (gridHorCount-offsetX) / maxX
elif maxX <= 0:
    offsetX = gridHorCount
    scaleX = offsetX / (-minX)
else:
    offsetX = minX/(minX-maxX) * (gridHorCount/gridHorBlockCount)
    if offsetX < gridHorCount/gridHorBlockCount/2:
        offsetX = math.ceil(offsetX) * gridHorBlockCount
    else:
        offsetX = math.floor(offsetX) * gridHorBlockCount
    scaleX = min( offsetX / (-minX), (gridHorCount-offsetX) / maxX )

if minY >= 0:
    offsetY = 0
    scaleY = (gridVertCount-offsetY) / maxY
elif maxY <= 0:
    offsetY = gridVertCount
    scaleY = offsetY / (-minY)
else:
    offsetY = minY/(minY-maxY) * (gridVertCount/gridVertBlockCount)
    if offsetY < gridVertCount/gridVertBlockCount/2:
        offsetY = math.ceil(offsetY) * gridVertBlockCount
    else:
        offsetY = math.floor(offsetY) * gridVertBlockCount
    scaleY = min( offsetY / (-minY), (gridVertCount-offsetY) / maxY )


scaleX = pow(10, math.floor(math.log10(scaleX)));
scaleY = pow(10, math.floor(math.log10(scaleY)));

newScaleX = scaleX
newScaleY = scaleY

factors = [2, 4, 5]

for factor in factors:
    scaleX_ = scaleX * factor
    if maxX * scaleX_ + offsetX <= gridHorCount and minX * scaleX_ + offsetX >= 0:
        newScaleX = scaleX_

for factor in factors:
    scaleY_ = scaleY * factor
    if maxY * scaleY_ + offsetY <= gridVertCount and minY * scaleY_ + offsetY >= 0:
        newScaleY = scaleY_

scaleX = newScaleX
scaleY = newScaleY


####################################

gridDataWidth = gridWidth * scaleX;

a = PdfAnnotator('a.pdf')
a.set_page_dimensions((pageWidth, pageHeight), 0)

def getPdfCoordsFromDataPoint(x, y):
    grid_x = (x*scaleX+offsetX) * gridWidth / gridHorCount + gridX;
    grid_y = (y*scaleY+offsetY) * gridHeight / gridVertCount + gridY; 
    return (grid_x, grid_y);

def getPdfCoordsFromGridCoords(x, y):
    grid_x = x * gridWidth / gridHorCount + gridX;
    grid_y = y * gridHeight / gridVertCount + gridY; 
    return (grid_x, grid_y);

def printDatapoint(x, y):
    coords = getPdfCoordsFromDataPoint(x,y);
    a.add_annotation(
        'line',
        Location(points=[(coords[0]-crossSize/2,coords[1]-crossSize/2),(coords[0]+crossSize/2,coords[1]+crossSize/2)], page=0),
        Appearance(stroke_color=(1, 0, 0), stroke_width=0.5)
    )
    a.add_annotation(
        'line',
        Location(points=[(coords[0]+crossSize/2,coords[1]-crossSize/2),(coords[0]-crossSize/2,coords[1]+crossSize/2)], page=0),
        Appearance(stroke_color=(1, 0, 0), stroke_width=0.5)
    )

def printVertAxisNumber(gridNum):
    dataNum = (gridNum-offsetY)/scaleY
    if dataNum == 0:
        return
    coords = getPdfCoordsFromGridCoords(offsetX, gridNum);
    a.add_annotation(
        'line',
        Location(points=[(coords[0]-axisTickSize/2,coords[1]),(coords[0]+axisTickSize/2,coords[1])], page=0),
        Appearance(stroke_color=(0, 0, 0), stroke_width=1)
    )
    label = "{:.2e}".format(dataNum)
    a.add_annotation(
        'text',
        Location(x1=coords[0]-200,y1=coords[1]-50,x2=coords[0]-axisTickSize/2,y2=coords[1]+50, page=0),
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
        Location(points=[(coords[0],coords[1]-axisTickSize/2),(coords[0],coords[1]+axisTickSize/2)], page=0),
        Appearance(stroke_color=(0, 0, 0), stroke_width=1)
    )
    label = "{:.2e}".format(dataNum)
    a.add_annotation(
        'text',
        Location(x1=coords[0]-100,y1=coords[1]-100-axisTickSize/2,x2=coords[0]+100,y2=coords[1]-axisTickSize/2, page=0),
        Appearance(content = label,fill=[0, 0, 0],
                stroke_width=1,
                font_size=40,text_align='center')
    )

def printVertAxis():
    coordsStart = getPdfCoordsFromGridCoords(offsetX, 0);
    coordsEnd = getPdfCoordsFromGridCoords(offsetX, gridVertCount);
    a.add_annotation(
        'line',
        Location(points=[coordsStart, coordsEnd], page=0),
        Appearance(stroke_color=(0, 0, 0), stroke_width=1)
    )

def printHorAxis():
    coordsStart = getPdfCoordsFromGridCoords(0, offsetY);
    coordsEnd = getPdfCoordsFromGridCoords(gridHorCount, offsetY);
    a.add_annotation(
        'line',
        Location(points=[coordsStart, coordsEnd], page=0),
        Appearance(stroke_color=(0, 0, 0), stroke_width=1)
    )


for i in range(int(gridVertCount / gridVertBlockCount) + 1):
    printVertAxisNumber(i * gridVertBlockCount)

for i in range(int(gridHorCount / gridHorBlockCount) + 1):
    printHorAxisNumber(i * gridHorBlockCount)

printVertAxis()

printHorAxis()

for point in points:
    printDatapoint(point[0], point[1])

a.write('b.pdf')