from pdf_annotate import PdfAnnotator, Location, Appearance

from measurement import Measurement
from transformation import Axis, Transformation


class Drawer:
    def __init__(self, paper_config, grid_config, drawing_config) -> None:
        self.a = PdfAnnotator(paper_config['file'])
        self.a.set_page_dimensions(
            (paper_config['width'], paper_config['height']), 0)

        # outsource should_contain_origin (see "False" params here)
        self.transformation = Transformation(grid_config, False, False)

        self.cross_size = drawing_config['cross_size']
        self.axis_tick_size = drawing_config['axis_tick_size']
        self.num_x_blocks = grid_config['num_x_blocks']
        self.num_y_blocks = grid_config['num_y_blocks']
        self.num_x_block_per_super_block = grid_config['num_x_blocks_per_super_block']
        self.num_y_blocks_per_super_block = grid_config['num_y_blocks_per_super_block']

    def save(self, path: str):
        self.a.write(path)

    def draw(self, measurements: list[Measurement]):
        measurements = self.transformation.analyze_and_offset_measurements(
            measurements)

        for i in range(int(self.num_x_blocks / self.num_x_block_per_super_block) + 1):
            self._draw_horizontal_axis_number(
                i * self.num_x_block_per_super_block)

        for i in range(int(self.num_y_blocks / self.num_y_blocks_per_super_block) + 1):
            self._draw_vertical_axis_number(
                i * self.num_y_blocks_per_super_block)

        self._draw_axis(Axis.HORIZONTAL)
        self._draw_axis(Axis.VERTICAL)

        for m in measurements:
            self._draw_datapoint(m)
            if m.has_error_bounds():
                self._draw_error_bar(m)

    def _draw_error_bar(self, m: Measurement):
        coords_top = self.transformation.get_pdf_coords_from_data_point(
            m.x, m.y + m.upper_error)
        coords_bottom = self.transformation.get_pdf_coords_from_data_point(
            m.x, m.y - m.lower_error)

        # vertical line
        self.a.add_annotation(
            'line',
            Location(points=[coords_bottom, coords_top], page=0),
            Appearance(stroke_color=(1, 0, 0), stroke_width=0.5)
        )

        # lower line
        points = [(coords_bottom[0]-self.cross_size/2, coords_bottom[1]),
                  (coords_bottom[0]+self.cross_size/2, coords_bottom[1])]
        self.a.add_annotation(
            'line',
            Location(points=points, page=0),
            Appearance(stroke_color=(1, 0, 0), stroke_width=0.5)
        )

        # upper line
        points = [(coords_top[0]-self.cross_size/2, coords_top[1]),
                  (coords_top[0]+self.cross_size/2, coords_top[1])]
        self.a.add_annotation(
            'line',
            Location(points=points, page=0),
            Appearance(stroke_color=(1, 0, 0), stroke_width=0.5)
        )

    def _draw_datapoint(self, m: Measurement):
        coords = self.transformation.get_pdf_coords_from_data_point(m.x, m.y)
        points = [(coords[0]-self.cross_size/2, coords[1]-self.cross_size/2),
                  (coords[0]+self.cross_size/2, coords[1]+self.cross_size/2)]
        self.a.add_annotation(
            'line',
            Location(points=points, page=0),
            Appearance(stroke_color=(1, 0, 0), stroke_width=0.5)
        )

        points = [(coords[0]+self.cross_size/2, coords[1]-self.cross_size/2),
                  (coords[0]-self.cross_size/2, coords[1]+self.cross_size/2)]
        self.a.add_annotation(
            'line',
            Location(points=points, page=0),
            Appearance(stroke_color=(1, 0, 0), stroke_width=0.5)
        )

    def _draw_vertical_axis_number(self, num_grid):
        # TODO: I don't understand this
        # num_data = (num_grid-offset_y)/scale_y + points_offset_y
        # if num_data == 0:
        #     return

        coords = self.transformation.get_pdf_coords_from_grid_coords(
            Axis.VERTICAL, num_grid)
        points = [(coords[0]-self.axis_tick_size/2, coords[1]),
                  (coords[0]+self.axis_tick_size/2, coords[1])]
        self.a.add_annotation(
            'line',
            Location(points=points, page=0),
            Appearance(stroke_color=(0, 0, 0), stroke_width=1)
        )
        # label = "{:.2e}".format(num_data)
        label = 'TODO'
        x1, y1 = coords[0]-200, coords[1]-50
        x2, y2 = coords[0] - self.axis_tick_size/2, coords[1]+50
        self.a.add_annotation(
            'text',
            Location(x1=x1, y1=y1, x2=x2, y2=y2, page=0),
            Appearance(content=label, fill=[0, 0, 0],
                       stroke_width=1,
                       font_size=40, text_align='right')
        )

    def _draw_horizontal_axis_number(self, num_grid):
        # num_data = (num_grid-self.offset_x)/self.scale_x + self.points_offset_x
        # if num_data == 0:
        #     return

        coords = self.transformation.get_pdf_coords_from_grid_coords(
            Axis.HORIZONTAL, num_grid)

        points = [(coords[0], coords[1]-self.axis_tick_size/2),
                  (coords[0], coords[1]+self.axis_tick_size/2)]
        self.a.add_annotation(
            'line',
            Location(points=points, page=0),
            Appearance(stroke_color=(0, 0, 0), stroke_width=1)
        )
        # label = "{:.2e}".format(num_data)
        label = 'TODO'
        x1, y1 = coords[0]-100, coords[1]-100-self.axis_tick_size/2
        x2, y2 = coords[0]+100, coords[1]-self.axis_tick_size/2
        self.a.add_annotation(
            'text',
            Location(x1=x1, y1=y1, x2=x2, y2=y2, page=0),
            Appearance(content=label, fill=[0, 0, 0],
                       stroke_width=1,
                       font_size=40, text_align='center')
        )

    def _draw_axis(self, axis: Axis):
        num_blocks = self.num_x_blocks if axis == Axis.HORIZONTAL else self.num_y_blocks

        coords_start = self.transformation.get_pdf_coords_from_grid_coords(
            axis, 0)
        coords_end = self.transformation.get_pdf_coords_from_grid_coords(
            axis, num_blocks)

        self.a.add_annotation(
            'line',
            Location(points=[coords_start, coords_end], page=0),
            Appearance(stroke_color=(0, 0, 0), stroke_width=1)
        )
