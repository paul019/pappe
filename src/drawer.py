from pdf_annotate import PdfAnnotator, Location, Appearance

from src.measurement import Measurement
from src.linear_regressor import LinearFunction
from src.axis_transformer.axis_transformer import AxisTransformer
from src.models.axis_direction import AxisDirection
from src.axis_transformer_maker.linear_axis_transformer_maker import (
    LinearAxisTranformerMaker,
)
from src.linear_regressor import do_linear_regression

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

    def __init__(
        self,
        paper_config,
        grid_config,
        drawing_config,
        x_axis_config,
        y_axis_config,
        regression_config,
    ) -> None:
        self.regression_config = regression_config

        self.a = PdfAnnotator(paper_config["file"])
        self.a.set_page_dimensions((paper_config["width"], paper_config["height"]), 0)

        if x_axis_config["type"] == "linear":
            self.trafo_maker_x = LinearAxisTranformerMaker(
                AxisDirection.HORIZONTAL,
                grid_config["num_x_blocks"],
                grid_config["num_x_tiny_blocks_per_block"],
                grid_config["width"],
                grid_config["x"],
                x_axis_config["factors"],
                x_axis_config["offset_exponent"],
                x_axis_config["show_origin"],
            )
        else:
            raise NotImplementedError
        
        if y_axis_config["type"] == "linear":
            self.trafo_maker_y = LinearAxisTranformerMaker(
                AxisDirection.VERTICAL,
                grid_config["num_y_blocks"],
                grid_config["num_y_tiny_blocks_per_block"],
                grid_config["height"],
                grid_config["y"],
                y_axis_config["factors"],
                y_axis_config["offset_exponent"],
                y_axis_config["show_origin"],
            )
        else:
            raise NotImplementedError

        self.cross_size = drawing_config["cross_size"]
        self.axis_tick_size = drawing_config["axis_tick_size"]

    def save(self, path: str):
        self.a.write(path)

    def should_do_regression(self):
        return (
            self.regression_config["print_parameters"]
            or self.regression_config["draw_curve_of_best_fit"]
            or self.regression_config["draw_error_curve_low_slope"]
            or self.regression_config["draw_error_curve_high_slope"]
        )

    def draw_all(self, measurements: list[Measurement]):
        self.trafo_x = self.trafo_maker_x.make([m.x for m in measurements])
        self.trafo_y = self.trafo_maker_y.make([m.y for m in measurements])

        if self.should_do_regression():
            self.regression = do_linear_regression(measurements)

        # Draw axes
        self._draw_axis(AxisDirection.HORIZONTAL)
        self._draw_axis(AxisDirection.VERTICAL)
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
                self._draw_error_bar(m, AxisDirection.HORIZONTAL)
            if m.y_error.exists():
                self._draw_error_bar(m, AxisDirection.VERTICAL)

    def _draw_axes_numbers(self):
        for i in range(self.trafo_x.num_blocks + 1):
            self._draw_horizontal_axis_number(i * self.trafo_x.num_tiny_blocks_per_block)

        for i in range(self.trafo_y.num_blocks + 1):
            self._draw_vertical_axis_number(i * self.trafo_y.num_tiny_blocks_per_block)

    def _draw_error_bar(self, m: Measurement, axis: AxisDirection):
        # helping variable:
        x = self.cross_size / 2

        if axis == AxisDirection.VERTICAL:
            coords_start = (
                self.trafo_x.get_pdf_coord_from_data_coord(m.x),
                self.trafo_y.get_pdf_coord_from_data_coord(m.y - m.y_error.lower_error),
            )
            coords_end = (
                self.trafo_x.get_pdf_coord_from_data_coord(m.x),
                self.trafo_y.get_pdf_coord_from_data_coord(m.y + m.y_error.upper_error),
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
            coords_start = (
                self.trafo_x.get_pdf_coord_from_data_coord(m.x - m.x_error.lower_error),
                self.trafo_y.get_pdf_coord_from_data_coord(m.y),
            )
            coords_end = (
                self.trafo_x.get_pdf_coord_from_data_coord(m.x + m.x_error.upper_error),
                self.trafo_y.get_pdf_coord_from_data_coord(m.y),
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
        coords = (
            self.trafo_x.get_pdf_coord_from_data_coord(m.x),
            self.trafo_y.get_pdf_coord_from_data_coord(m.y),
        )

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
        num_data = self.trafo_y.get_data_coord_from_grid_coord(num_grid)
        label = f"{num_data:.3e}"

        coords = (
            self.trafo_x.get_pdf_coord_of_axis(),
            self.trafo_y.get_pdf_coord_from_grid_coord(num_grid),
        )

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
        num_data = self.trafo_x.get_data_coord_from_grid_coord(num_grid)
        label = f"{num_data:.3e}"

        coords = (
            self.trafo_x.get_pdf_coord_from_grid_coord(num_grid),
            self.trafo_y.get_pdf_coord_of_axis(),
        )

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

    def _draw_axis(self, axis: AxisDirection):
        if axis == AxisDirection.HORIZONTAL:
            coords_start = (
                self.trafo_x.get_pdf_coord_from_grid_coord(0),
                self.trafo_y.get_pdf_coord_of_axis(),
            )
            coords_end = (
                self.trafo_x.get_pdf_coord_from_grid_coord(
                    self.trafo_x.num_total_blocks
                ),
                self.trafo_y.get_pdf_coord_of_axis(),
            )
        else:
            coords_start = (
                self.trafo_x.get_pdf_coord_of_axis(),
                self.trafo_y.get_pdf_coord_from_grid_coord(0),
            )
            coords_end = (
                self.trafo_x.get_pdf_coord_of_axis(),
                self.trafo_y.get_pdf_coord_from_grid_coord(
                    self.trafo_y.num_total_blocks
                ),
            )

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
        Draws a linear function of the form y = m * x + b.
        """

        grid_start_x = self.trafo_x.get_data_coord_from_grid_coord(0)
        grid_end_x = self.trafo_x.get_data_coord_from_grid_coord(
            self.trafo_x.num_total_blocks
        )

        start_y = f.eval(grid_start_x)
        end_y = f.eval(grid_end_x)

        coords_start = (
            self.trafo_x.get_pdf_coord_from_grid_coord(0),
            self.trafo_y.get_pdf_coord_from_data_coord(start_y),
        )

        coords_end = (
            self.trafo_x.get_pdf_coord_from_grid_coord(self.trafo_x.num_total_blocks),
            self.trafo_y.get_pdf_coord_from_data_coord(end_y),
        )

        location = Location(points=[coords_start, coords_end], page=0)
        self.a.add_annotation(
            "line",
            location,
            Appearance(stroke_color=color, stroke_width=REGRESSION_STROKE_WIDTH),
        )
