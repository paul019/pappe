from pdf_annotate import PdfAnnotator, Location, Appearance

from src.measurement import Measurement
from src.transformer import Axis, Transformer
from src.linear_regressor import LinearFunction

INDICATOR_COLOR = (0, 0, 1)
AXIS_COLOR = (0, 0, 0)
LINE_OF_BEST_FIT_COLOR = (0, 0, 0)
ERROR_COLOR = (1, 0, 0)
INDICATOR_STROKE_WIDTH = 0.5
AXIS_STROKE_WIDTH = 1.0
REGRESSION_STROKE_WIDTH = 0.25


class Drawer:
    """
    Draws measurements onto a PDF file. Uses a Transformer to transform
    measurements into PDF coordinates.
    """

    def __init__(self, trafo: Transformer, config, regression_config) -> None:
        self.regression_config = regression_config

        paper_config = config["paper"]
        grid_config = config["grid"]
        drawing_config = config["drawing"]

        self.a = PdfAnnotator(paper_config["file"])
        self.a.set_page_dimensions((paper_config["width"], paper_config["height"]), 0)

        self.trafo = trafo

        self.cross_size = drawing_config["cross_size"]
        self.axis_tick_size = drawing_config["axis_tick_size"]

        self.num_x_blocks = grid_config["num_x_blocks"]
        self.num_y_blocks = grid_config["num_y_blocks"]
        self.num_x_tiny_blocks_per_block = grid_config["num_x_tiny_blocks_per_block"]
        self.num_y_tiny_blocks_per_block = grid_config["num_y_tiny_blocks_per_block"]

    def save(self, path: str):
        self.a.write(path)

    def draw_all(self, measurements: list[Measurement]):
        measurements = self.trafo.analyze_and_offset_measurements(measurements)
        self.regression = self.trafo.get_linear_regression()

        # Draw axes
        self._draw_axis(Axis.HORIZONTAL)
        self._draw_axis(Axis.VERTICAL)
        self._draw_axes_numbers()

        # Regression
        if self.regression_config["print_parameters"]:
            self._print_regression()
        if self.regression_config["draw_curve_of_best_fit"]:
            self._draw_curve_of_best_fit()
        if self.regression_config["draw_error_curve_low_slope"]:
            self._draw_error_curve_low_slope()
        if self.regression_config["draw_error_curve_high_slope"]:
            self._draw_error_curve_high_slope()

        # Draw measurements
        for m in measurements:
            self._draw_datapoint(m)
            if m.x_error.exists():
                self._draw_error_bar(m, Axis.HORIZONTAL)
            if m.y_error.exists():
                self._draw_error_bar(m, Axis.VERTICAL)

    def _draw_axes_numbers(self):
        for i in range(self.num_x_blocks + 1):
            self._draw_horizontal_axis_number(i * self.num_x_tiny_blocks_per_block)

        for i in range(self.num_y_blocks + 1):
            self._draw_vertical_axis_number(i * self.num_y_tiny_blocks_per_block)

    def _draw_error_bar(self, m: Measurement, axis: Axis):
        # helping variable:
        x = self.cross_size / 2

        if axis == Axis.VERTICAL:
            coords_start = self.trafo.get_pdf_coords_from_offset_data_point(
                m.x, m.y - m.y_error.lower_error
            )
            coords_end = self.trafo.get_pdf_coords_from_offset_data_point(
                m.x, m.y + m.y_error.upper_error
            )
            coords_start_tick = [
                (coords_start[0] - x, coords_start[1]),
                (coords_start[0] + x, coords_start[1]),
            ]
            coords_end_tick = [
                (coords_end[0] - x, coords_end[1]),
                (coords_end[0] + x, coords_end[1]),
            ]
        else:
            coords_start = self.trafo.get_pdf_coords_from_offset_data_point(
                m.x - m.x_error.lower_error, m.y
            )
            coords_end = self.trafo.get_pdf_coords_from_offset_data_point(
                m.x + m.x_error.upper_error, m.y
            )
            coords_start_tick = [
                (coords_start[0], coords_start[1] - x),
                (coords_start[0], coords_start[1] + x),
            ]
            coords_end_tick = [
                (coords_end[0], coords_end[1] - x),
                (coords_end[0], coords_end[1] + x),
            ]

        # error line
        location = Location(points=[coords_start, coords_end], page=0)
        self.a.add_annotation(
            "line",
            location,
            Appearance(
                stroke_color=INDICATOR_COLOR, stroke_width=INDICATOR_STROKE_WIDTH
            ),
        )

        # start tick
        self.a.add_annotation(
            "line",
            Location(points=coords_start_tick, page=0),
            Appearance(
                stroke_color=INDICATOR_COLOR, stroke_width=INDICATOR_STROKE_WIDTH
            ),
        )

        # end tick
        self.a.add_annotation(
            "line",
            Location(points=coords_end_tick, page=0),
            Appearance(
                stroke_color=INDICATOR_COLOR, stroke_width=INDICATOR_STROKE_WIDTH
            ),
        )

    def _draw_datapoint(self, m: Measurement):
        coords = self.trafo.get_pdf_coords_from_offset_data_point(m.x, m.y)

        # One side of cross
        points = [
            (coords[0] - self.cross_size / 2, coords[1] - self.cross_size / 2),
            (coords[0] + self.cross_size / 2, coords[1] + self.cross_size / 2),
        ]
        self.a.add_annotation(
            "line",
            Location(points=points, page=0),
            Appearance(
                stroke_color=INDICATOR_COLOR, stroke_width=INDICATOR_STROKE_WIDTH
            ),
        )

        # Other side of cross
        points = [
            (coords[0] + self.cross_size / 2, coords[1] - self.cross_size / 2),
            (coords[0] - self.cross_size / 2, coords[1] + self.cross_size / 2),
        ]
        self.a.add_annotation(
            "line",
            Location(points=points, page=0),
            Appearance(
                stroke_color=INDICATOR_COLOR, stroke_width=INDICATOR_STROKE_WIDTH
            ),
        )

    def _draw_vertical_axis_number(self, num_grid):
        num_data = self.trafo.grid_coord_to_data_label(num_grid, Axis.VERTICAL)
        label = f"{num_data:.2e}"

        coords = self.trafo.get_pdf_coords_for_point_on_axis(Axis.VERTICAL, num_grid)

        # Line
        points = [
            (coords[0] - self.axis_tick_size / 2, coords[1]),
            (coords[0] + self.axis_tick_size / 2, coords[1]),
        ]
        self.a.add_annotation(
            "line",
            Location(points=points, page=0),
            Appearance(stroke_color=AXIS_COLOR, stroke_width=AXIS_STROKE_WIDTH),
        )

        # Text
        x1, y1 = coords[0] - 200, coords[1] - 50
        x2, y2 = coords[0] - self.axis_tick_size / 2, coords[1] + 50
        location = Location(x1=x1, y1=y1, x2=x2, y2=y2, page=0)
        self.a.add_annotation(
            "text",
            location,
            Appearance(
                content=label,
                fill=[0, 0, 0],
                stroke_width=1,
                font_size=40,
                text_align="right",
            ),
        )

    def _draw_horizontal_axis_number(self, num_grid):
        num_data = self.trafo.grid_coord_to_data_label(num_grid, Axis.HORIZONTAL)
        label = f"{num_data:.2e}"

        coords = self.trafo.get_pdf_coords_for_point_on_axis(Axis.HORIZONTAL, num_grid)

        # Line
        points = [
            (coords[0], coords[1] - self.axis_tick_size / 2),
            (coords[0], coords[1] + self.axis_tick_size / 2),
        ]
        self.a.add_annotation(
            "line",
            Location(points=points, page=0),
            Appearance(stroke_color=AXIS_COLOR, stroke_width=AXIS_STROKE_WIDTH),
        )

        # Text
        x1, y1 = coords[0] - 100, coords[1] - 100 - self.axis_tick_size / 2
        x2, y2 = coords[0] + 100, coords[1] - self.axis_tick_size / 2
        location = Location(x1=x1, y1=y1, x2=x2, y2=y2, page=0)
        self.a.add_annotation(
            "text",
            location,
            Appearance(
                content=label,
                fill=[0, 0, 0],
                stroke_width=1,
                font_size=40,
                text_align="center",
            ),
        )

    def _draw_axis(self, axis: Axis):
        if axis == Axis.HORIZONTAL:
            num_blocks = self.num_x_blocks * self.num_x_tiny_blocks_per_block
        else:
            num_blocks = self.num_y_blocks * self.num_y_tiny_blocks_per_block

        coords_start = self.trafo.get_pdf_coords_for_point_on_axis(axis, 0)
        coords_end = self.trafo.get_pdf_coords_for_point_on_axis(axis, num_blocks)

        location = Location(points=[coords_start, coords_end], page=0)
        self.a.add_annotation(
            "line",
            location,
            Appearance(stroke_color=AXIS_COLOR, stroke_width=AXIS_STROKE_WIDTH),
        )

    def _print_regression(self):
        m, dm, n, dn = (
            self.regression.m,
            self.regression.m_error,
            self.regression.n,
            self.regression.n_error,
        )

        print()
        print("Linear regression:")
        print("y = m * x + n")
        print("m  = {}".format(m))
        print("Δm = {}".format(dm))
        print("n  = {}".format(n))
        print("Δn = {}".format(dn))
        print()

    def _draw_curve_of_best_fit(self):
        self._draw_linear_function(self.regression.best_fit(), LINE_OF_BEST_FIT_COLOR)

    def _draw_error_curve_low_slope(self):
        self._draw_linear_function(self.regression.error_curve_low_slope(), ERROR_COLOR)

    def _draw_error_curve_high_slope(self):
        self._draw_linear_function(
            self.regression.error_curve_high_slope(), ERROR_COLOR
        )

    def _draw_linear_function(
        self, f: LinearFunction, color: tuple[float, float, float]
    ):
        """
        Draw linear function of the form y = m * x + b.
        """

        grid_start_x = self.trafo.get_data_point_from_grid_coords(0, 0)[0]
        grid_end_x = self.trafo.get_data_point_from_grid_coords(
            self.num_x_blocks * self.num_x_tiny_blocks_per_block, 0
        )[0]

        start_y = f.eval(grid_start_x)
        end_y = f.eval(grid_end_x)

        coords_start = [
            self.trafo.get_pdf_coords_from_grid_coords(0, 0)[0],
            self.trafo.get_pdf_coords_from_data_point(0, start_y)[1],
        ]

        coords_end = [
            self.trafo.get_pdf_coords_from_grid_coords(
                self.num_x_blocks * self.num_x_tiny_blocks_per_block, 0
            )[0],
            self.trafo.get_pdf_coords_from_data_point(
                self.num_x_blocks * self.num_x_tiny_blocks_per_block, end_y
            )[1],
        ]

        location = Location(points=[coords_start, coords_end], page=0)
        self.a.add_annotation(
            "line",
            location,
            Appearance(stroke_color=color, stroke_width=REGRESSION_STROKE_WIDTH),
        )
