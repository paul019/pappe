from pdf_annotate import PdfAnnotator, Location, Appearance

from measurement import Measurement
from transformer import Axis, Transformer


class Drawer:
    """
    Draws measurements onto a PDF file. Uses a Transformer to transform
    measurements into PDF coordinates.
    """

    def __init__(self, config) -> None:
        paper_config = config['paper']
        grid_config = config['grid']
        drawing_config = config['drawing']

        self.a = PdfAnnotator(paper_config['file'])
        self.a.set_page_dimensions(
            (paper_config['width'], paper_config['height']), 0)

        # outsource should_contain_origin (see "False" params here)
        self.trafo = Transformer(grid_config, False, False)

        self.cross_size = drawing_config['cross_size']
        self.axis_tick_size = drawing_config['axis_tick_size']

        self.num_x_blocks = grid_config['num_x_blocks']
        self.num_y_blocks = grid_config['num_y_blocks']
        self.num_x_tiny_blocks_per_block = grid_config['num_x_tiny_blocks_per_block']
        self.num_y_tiny_blocks_per_block = grid_config['num_y_tiny_blocks_per_block']

    def save(self, path: str):
        self.a.write(path)

    def draw(self, measurements: list[Measurement]):
        measurements = self.trafo.analyze_and_offset_measurements(measurements)

        self._draw_axis(Axis.HORIZONTAL)
        self._draw_axis(Axis.VERTICAL)
        self._draw_axes_numbers()

        for m in measurements:
            self._draw_datapoint(m)
            if m.has_error_bounds():
                self._draw_error_bar(m)

    def _draw_axes_numbers(self):
        for i in range(self.num_x_blocks + 1):
            self._draw_horizontal_axis_number(
                i * self.num_x_tiny_blocks_per_block)

        for i in range(self.num_y_blocks + 1):
            self._draw_vertical_axis_number(
                i * self.num_y_tiny_blocks_per_block)

    def _draw_error_bar(self, m: Measurement):
        coords_top = self.trafo.get_pdf_coords_from_data_point(
            m.x, m.y + m.upper_error)
        coords_bottom = self.trafo.get_pdf_coords_from_data_point(
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
        coords = self.trafo.get_pdf_coords_from_data_point(m.x, m.y)
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
        num_data = self.trafo.grid_to_num_data(num_grid, Axis.VERTICAL)
        label = f'{num_data:.2e}'

        coords = self.trafo.get_pdf_coords_from_grid_coords(
            Axis.VERTICAL, num_grid)

        points = [(coords[0]-self.axis_tick_size/2, coords[1]),
                  (coords[0]+self.axis_tick_size/2, coords[1])]
        self.a.add_annotation(
            'line',
            Location(points=points, page=0),
            Appearance(stroke_color=(0, 0, 0), stroke_width=1)
        )

        x1, y1 = coords[0] - 200, coords[1] - 50
        x2, y2 = coords[0] - self.axis_tick_size/2, coords[1] + 50
        self.a.add_annotation(
            'text',
            Location(x1=x1, y1=y1, x2=x2, y2=y2, page=0),
            Appearance(content=label, fill=[0, 0, 0],
                       stroke_width=1,
                       font_size=40, text_align='right')
        )

    def _draw_horizontal_axis_number(self, num_grid):
        num_data = self.trafo.grid_to_num_data(num_grid, Axis.HORIZONTAL)
        label = f'{num_data:.2e}'

        coords = self.trafo.get_pdf_coords_from_grid_coords(
            Axis.HORIZONTAL, num_grid)

        points = [(coords[0], coords[1] - self.axis_tick_size/2),
                  (coords[0], coords[1] + self.axis_tick_size/2)]
        self.a.add_annotation(
            'line',
            Location(points=points, page=0),
            Appearance(stroke_color=(0, 0, 0), stroke_width=1)
        )

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
        if axis == Axis.HORIZONTAL:
            num_blocks = self.num_x_blocks * self.num_x_tiny_blocks_per_block
        else:
            num_blocks = self.num_y_blocks * self.num_y_tiny_blocks_per_block

        coords_start = self.trafo.get_pdf_coords_from_grid_coords(
            axis, 0)
        coords_end = self.trafo.get_pdf_coords_from_grid_coords(
            axis, num_blocks)

        self.a.add_annotation(
            'line',
            Location(points=[coords_start, coords_end], page=0),
            Appearance(stroke_color=(0, 0, 0), stroke_width=1)
        )
