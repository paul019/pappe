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

csv_file_path = 'input/data.csv'
output_file_path = 'output/output.pdf'
factors = [2, 4, 5]
should_contain_origin_x = False
should_contain_origin_y = False

####################################

# Read CSV-file:

file = open(csv_file_path)
csv_reader = csv.reader(file)

points = []
errors = []

for row in csv_reader:
    points.append((float(row[0]), float(row[1])))

    if len(row) == 2:
        errors.append((-1, -1))
    elif len(row) == 3:
        errors.append((float(row[2]), float(row[2])))
    else:
        errors.append((float(row[2]), float(row[3])))

####################################

# Analyze data:

min_x = points[0][0]
min_y = points[0][1]
max_x = points[0][0]
max_y = points[0][1]

for point in points:
    min_x = min(min_x, point[0])
    min_y = min(min_y, point[1])
    max_x = max(max_x, point[0])
    max_y = max(max_y, point[1])

points_offset_x = 0
points_offset_y = 0

# Handle case of not including the origin (currently bad documentation):

if not should_contain_origin_x and min_x <= 0 and max_x >= 0:
    should_contain_origin_x = True

if not should_contain_origin_x:
    if min_x <= 0:
        points_offset_x = -pow(10, math.floor(math.log10(-max_x)))
        new_points_offset_x = points_offset_x

        for i in range(2, 10):
            if i*points_offset_x >= max_x:
                new_points_offset_x = i*points_offset_x

        points_offset_x = new_points_offset_x
    else:
        points_offset_x = pow(10, math.floor(math.log10(min_x)))
        new_points_offset_x = points_offset_x

        for i in range(2, 10):
            if i*points_offset_x <= min_x:
                new_points_offset_x = i*points_offset_x

        points_offset_x = new_points_offset_x

if not should_contain_origin_y and min_y <= 0 and max_y >= 0:
    should_contain_origin_y = True

if not should_contain_origin_y:
    if min_y <= 0:
        points_offset_y = -pow(10, math.floor(math.log10(-max_y)))
        new_points_offset_y = points_offset_y

        for i in range(2, 10):
            if i*points_offset_y >= max_y:
                new_points_offset_y = i*points_offset_y

        points_offset_y = new_points_offset_y
    else:
        points_offset_y = pow(10, math.floor(math.log10(min_y)))
        new_points_offset_y = points_offset_y

        for i in range(2, 10):
            if i*points_offset_y <= min_y:
                new_points_offset_y = i*points_offset_y
        
        points_offset_y = new_points_offset_y

for i in range(len(points)):
    points[i] = (points[i][0] - points_offset_x, points[i][1] - points_offset_y)

min_x -= points_offset_x
max_x -= points_offset_x

min_y -= points_offset_y
max_y -= points_offset_y

# Choose coordinate axis scaling and offset:

scale_x = 1
scale_y = 1

offset_x = 0
offset_y = 0

if min_x >= 0:
    offset_x = 0
    scale_x = (grid_config['num_x_blocks']-offset_x) / max_x
elif max_x <= 0:
    offset_x = grid_config['num_x_blocks']
    scale_x = offset_x / (-min_x)
else:
    offset_x = min_x/(min_x-max_x) * (grid_config['num_x_blocks']/grid_config['num_x_blocks_per_super_block'])
    if offset_x < grid_config['num_x_blocks']/grid_config['num_x_blocks_per_super_block']/2:
        offset_x = math.ceil(offset_x) * grid_config['num_x_blocks_per_super_block']
    else:
        offset_x = math.floor(offset_x) * grid_config['num_x_blocks_per_super_block']
    scale_x = min( offset_x / (-min_x), (grid_config['num_x_blocks']-offset_x) / max_x )

if min_y >= 0:
    offset_y = 0
    scale_y = (grid_config['num_y_blocks']-offset_y) / max_y
elif max_y <= 0:
    offset_y = grid_config['num_y_blocks']
    scale_y = offset_y / (-min_y)
else:
    offset_y = min_y/(min_y-max_y) * (grid_config['num_y_blocks']/grid_config['num_y_blocks_per_super_block'])
    if offset_y < grid_config['num_y_blocks']/grid_config['num_y_blocks_per_super_block']/2:
        offset_y = math.ceil(offset_y) * grid_config['num_y_blocks_per_super_block']
    else:
        offset_y = math.floor(offset_y) * grid_config['num_y_blocks_per_super_block']
    scale_y = min( offset_y / (-min_y), (grid_config['num_y_blocks']-offset_y) / max_y )


scale_x = pow(10, math.floor(math.log10(scale_x)))
scale_y = pow(10, math.floor(math.log10(scale_y)))

new_scale_x = scale_x
new_scale_y = scale_y

factors.sort()

for factor in factors:
    scale_x_2 = scale_x * factor
    if max_x * scale_x_2 + offset_x <= grid_config['num_x_blocks'] and min_x * scale_x_2 + offset_x >= 0:
        new_scale_x = scale_x_2

for factor in factors:
    scale_y_2 = scale_y * factor
    if max_y * scale_y_2 + offset_y <= grid_config['num_y_blocks'] and min_y * scale_y_2 + offset_y >= 0:
        new_scale_y = scale_y_2

scale_x = new_scale_x
scale_y = new_scale_y

####################################

# Open pdf annotator:

a = PdfAnnotator(paper_config['file'])
a.set_page_dimensions((paper_config['width'], paper_config['height']), 0)

####################################

# Define functions for annotation:

def get_pdf_coords_from_data_point(x, y):
    grid_x = (x*scale_x+offset_x) * grid_config['width'] / grid_config['num_x_blocks'] + grid_config['x']
    grid_y = (y*scale_y+offset_y) * grid_config['height'] / grid_config['num_y_blocks'] + grid_config['y'] 
    return (grid_x, grid_y)

def get_pdf_coords_from_grid_coords(x, y):
    grid_x = x * grid_config['width'] / grid_config['num_x_blocks'] + grid_config['x']
    grid_y = y * grid_config['height'] / grid_config['num_y_blocks'] + grid_config['y'] 
    return (grid_x, grid_y)

def draw_datapoint(x, y):
    coords = get_pdf_coords_from_data_point(x,y)
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

def draw_error_bar(x, y, lower_error, uperr_error):
    if lower_error == -1 or uperr_error == -1:
        return

    coords_top = get_pdf_coords_from_data_point(x,y+uperr_error)
    coords_bottom = get_pdf_coords_from_data_point(x,y-lower_error)

    a.add_annotation(
        'line',
        Location(points=[coords_bottom, coords_top], page=0),
        Appearance(stroke_color=(1, 0, 0), stroke_width=0.5)
    )
    a.add_annotation(
        'line',
        Location(points=[(coords_bottom[0]-drawing_config['cross_size']/2, coords_bottom[1]), (coords_bottom[0]+drawing_config['cross_size']/2, coords_bottom[1])], page=0),
        Appearance(stroke_color=(1, 0, 0), stroke_width=0.5)
    )
    a.add_annotation(
        'line',
        Location(points=[(coords_top[0]-drawing_config['cross_size']/2, coords_top[1]), (coords_top[0]+drawing_config['cross_size']/2, coords_top[1])], page=0),
        Appearance(stroke_color=(1, 0, 0), stroke_width=0.5)
    )

def draw_vertical_axis_number(num_grid):
    num_data = (num_grid-offset_y)/scale_y + points_offset_y
    if num_data == 0:
        return
    coords = get_pdf_coords_from_grid_coords(offset_x if should_contain_origin_x else 0, num_grid)
    a.add_annotation(
        'line',
        Location(points=[(coords[0]-drawing_config['axis_tick_size']/2,coords[1]),(coords[0]+drawing_config['axis_tick_size']/2,coords[1])], page=0),
        Appearance(stroke_color=(0, 0, 0), stroke_width=1)
    )
    label = "{:.2e}".format(num_data)
    a.add_annotation(
        'text',
        Location(x1=coords[0]-200,y1=coords[1]-50,x2=coords[0]-drawing_config['axis_tick_size']/2,y2=coords[1]+50, page=0),
        Appearance(content = label,fill=[0, 0, 0],
                stroke_width=1,
                font_size=40,text_align='right')
    )

def draw_horizontal_axis_number(num_grid):
    num_data = (num_grid-offset_x)/scale_x + points_offset_x
    if num_data == 0:
        return
    coords = get_pdf_coords_from_grid_coords(num_grid, offset_y if should_contain_origin_y else 0)
    a.add_annotation(
        'line',
        Location(points=[(coords[0],coords[1]-drawing_config['axis_tick_size']/2),(coords[0],coords[1]+drawing_config['axis_tick_size']/2)], page=0),
        Appearance(stroke_color=(0, 0, 0), stroke_width=1)
    )
    label = "{:.2e}".format(num_data)
    a.add_annotation(
        'text',
        Location(x1=coords[0]-100,y1=coords[1]-100-drawing_config['axis_tick_size']/2,x2=coords[0]+100,y2=coords[1]-drawing_config['axis_tick_size']/2, page=0),
        Appearance(content = label,fill=[0, 0, 0],
                stroke_width=1,
                font_size=40,text_align='center')
    )

def print_vertical_axis():
    coords_start = get_pdf_coords_from_grid_coords(offset_x if should_contain_origin_x else 0, 0)
    coords_end = get_pdf_coords_from_grid_coords(offset_x if should_contain_origin_x else 0, grid_config['num_y_blocks'])
    a.add_annotation(
        'line',
        Location(points=[coords_start, coords_end], page=0),
        Appearance(stroke_color=(0, 0, 0), stroke_width=1)
    )

def print_horizontal_axis():
    coords_start = get_pdf_coords_from_grid_coords(0, offset_y if should_contain_origin_y else 0)
    coords_end = get_pdf_coords_from_grid_coords(grid_config['num_x_blocks'], offset_y if should_contain_origin_y else 0)
    a.add_annotation(
        'line',
        Location(points=[coords_start, coords_end], page=0),
        Appearance(stroke_color=(0, 0, 0), stroke_width=1)
    )

####################################

# Do annotation:

for i in range(int(grid_config['num_y_blocks'] / grid_config['num_y_blocks_per_super_block']) + 1):
    draw_vertical_axis_number(i * grid_config['num_y_blocks_per_super_block'])

for i in range(int(grid_config['num_x_blocks'] / grid_config['num_x_blocks_per_super_block']) + 1):
    draw_horizontal_axis_number(i * grid_config['num_x_blocks_per_super_block'])

print_vertical_axis()
print_horizontal_axis()

for i in range(len(points)):
    point = points[i]
    error = errors[i]

    draw_datapoint(point[0], point[1])
    draw_error_bar(point[0], point[1], error[0], error[1])

####################################

# Export:

a.write(output_file_path)