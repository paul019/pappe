from measurement import Measurement
import math
from enum import Enum


class Axis(Enum):
    VERTICAL = 0
    HORIZONTAL = 1


class Transformer:
    """
    Transforms measurements into PDF coordinates based on grid configuration.

    Note that analyze_and_offset_measurements must be called first.
    """

    def __init__(self, grid_config, should_contain_origin_x, should_contain_origin_y) -> None:
        self.grid_config = grid_config
        self.should_contain_origin_x = should_contain_origin_x
        self.should_contain_origin_y = should_contain_origin_y

        self.num_total_x_blocks = grid_config['num_x_blocks'] * \
            grid_config['num_x_tiny_blocks_per_block']
        self.num_total_y_blocks = grid_config['num_y_blocks'] *\
            grid_config['num_y_tiny_blocks_per_block']

    def analyze_and_offset_measurements(self, measurements: list[Measurement]):
        # Min/Max values
        x_values = [m.x for m in measurements]
        y_values = [m.y for m in measurements]
        min_x, max_x = min(x_values), max(x_values)
        min_y, max_y = min(y_values), max(y_values)

        # Data points offset (depending on whether data origin should be shown)
        points_offset_x, points_offset_y = 0.0, 0.0
        if not self.should_contain_origin_x and (min_x > 0 or max_x < 0):
            points_offset_x = self._get_data_points_offset(min_x, max_x)
        if not self.should_contain_origin_y and (min_y > 0 or max_y < 0):
            points_offset_y = self._get_data_points_offset(min_y, max_y)
        # Apply offsets
        for m in measurements:
            m.x -= points_offset_x
            m.y -= points_offset_y
        min_x -= points_offset_x
        max_x -= points_offset_x
        min_y -= points_offset_y
        max_y -= points_offset_y

        # Estimate offset and scale
        offset_x, scale_x = self._calc_offset_estimate_scale(min_x, max_x)
        offset_y, scale_y = self._calc_offset_estimate_scale(min_y, max_y)

        # Refine scale
        # TODO: outsource
        factors_x, factors_y = [2, 4, 5], [2, 4, 5]
        factors_x.sort()
        factors_y.sort()
        scale_x = self._refine_scale(scale_x, factors_x,
                                     min_x, max_x, offset_x, self.num_total_x_blocks)
        scale_y = self._refine_scale(scale_y, factors_y,
                                     min_y, max_y, offset_y, self.num_total_y_blocks)

        # Make accessible as instance variables
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.scale_x = scale_x
        self.scale_y = scale_y
        self.points_offset_x = points_offset_x
        self.points_offset_y = points_offset_y

        return measurements

    def _get_data_points_offset(self, min_value: float, max_value: float) -> float:
        if min_value <= 0:
            points_offset = -pow(10, math.floor(math.log10(-max_value)))
            points_offset_trial = points_offset

            for i in range(2, 10):
                if i * points_offset >= max_value:
                    points_offset_trial = i * points_offset

            points_offset = points_offset_trial

        else:
            points_offset = pow(10, math.floor(math.log10(min_value)))
            points_offset_trial = points_offset

            for i in range(2, 10):
                if i * points_offset <= min_value:
                    points_offset_trial = i * points_offset

            points_offset = points_offset_trial

        return points_offset

    def _calc_offset_estimate_scale(self, min_value: float, max_value: float) -> tuple[float, float]:
        """
        Calculates the final offset and gives a first estimate for scale.

        Offset: offset of data points to grid in grid coordinates (is always positive)
        Scale: ratio between data scaling and grid scaling
        """
        if min_value >= 0:
            offset = 0
            scale = self.num_total_x_blocks / max_value

        elif max_value <= 0:
            offset = self.num_total_x_blocks
            scale = self.num_total_x_blocks / (-min_value)

        else:
            offset = min_value/(min_value-max_value) * \
                self.grid_config['num_x_blocks']

            if offset < self.grid_config['num_x_blocks']/2:
                offset = math.ceil(offset)
            else:
                offset = math.floor(offset)
            offset *= self.grid_config['num_x_tiny_blocks_per_block']

            scale = min(offset / (-min_value),
                        (self.num_total_x_blocks - offset) / max_value)

        return offset, scale

    def _refine_scale(self, scale: float, factors: list[int],
                      min_value: float, max_value: float, offset: float, num_total_blocks: int) -> float:
        scale_rounded_down = pow(10, math.floor(math.log10(scale)))
        scale_refined = scale_rounded_down

        for factor in factors:
            scale_trial = scale_rounded_down * factor

            fits_min = min_value * scale_trial + offset >= 0
            fits_max = max_value * scale_trial + offset <= num_total_blocks

            if fits_min and fits_max:
                scale_refined = scale_trial

        return scale_refined

    def get_pdf_coords_from_data_point(self, x: float, y: float) -> tuple[float, float]:
        grid_x = (x*self.scale_x+self.offset_x) * \
            self.grid_config['width'] / \
            self.num_total_x_blocks + self.grid_config['x']
        grid_y = (y*self.scale_y+self.offset_y) * \
            self.grid_config['height'] / \
            self.num_total_y_blocks + self.grid_config['y']
        return grid_x, grid_y

    def _get_pdf_coords_from_grid_coords(self, x: float, y: float) -> tuple[float, float]:
        grid_x = x * self.grid_config['width'] / \
            self.num_total_x_blocks + self.grid_config['x']
        grid_y = y * self.grid_config['height'] / \
            self.num_total_y_blocks + self.grid_config['y']
        return grid_x, grid_y

    def get_pdf_coords_for_point_on_axis(self, axis: Axis, value: float) -> tuple[float, float]:
        if axis == Axis.VERTICAL:
            x = self.offset_x if self.should_contain_origin_x else 0
            y = value
        else:
            x = value
            y = self.offset_y if self.should_contain_origin_y else 0

        return self._get_pdf_coords_from_grid_coords(x, y)

    def grid_coord_to_data_label(self, grid_coord: int, axis: Axis) -> float:
        offset = self.offset_x if axis == Axis.HORIZONTAL else self.offset_y
        scale = self.scale_x if axis == Axis.HORIZONTAL else self.scale_y
        point_offset = self.points_offset_x if axis == Axis.HORIZONTAL else self.points_offset_y

        return (grid_coord-offset)/scale + point_offset
