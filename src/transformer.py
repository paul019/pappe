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
        # TODO: clean up this horror function ;)

        x_values = [m.x for m in measurements]
        y_values = [m.y for m in measurements]
        min_x, max_x = min(x_values), max(x_values)
        min_y, max_y = min(y_values), max(y_values)

        points_offset_x = 0
        points_offset_y = 0

        if not self.should_contain_origin_x and min_x <= 0 and max_x >= 0:
            self.should_contain_origin_x = True

        if not self.should_contain_origin_x:
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

        if not self.should_contain_origin_y and min_y <= 0 and max_y >= 0:
            self.should_contain_origin_y = True

        if not self.should_contain_origin_y:
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

        for m in measurements:
            m.x -= points_offset_x
            m.y -= points_offset_y

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
            scale_x = self.num_total_x_blocks / max_x
        elif max_x <= 0:
            offset_x = self.num_total_x_blocks
            scale_x = self.num_total_x_blocks / (-min_x)
        else:
            offset_x = min_x/(min_x-max_x) * self.grid_config['num_x_blocks']
            if offset_x < self.grid_config['num_x_blocks']/2:
                offset_x = math.ceil(offset_x)\
                    * self.grid_config['num_x_tiny_blocks_per_block']
            else:
                offset_x = math.floor(offset_x)\
                    * self.grid_config['num_x_tiny_blocks_per_block']
            scale_x = min(offset_x / (-min_x),
                          (self.num_total_x_blocks - offset_x) / max_x)

        if min_y >= 0:
            offset_y = 0
            scale_y = (self.num_total_y_blocks - offset_y) / max_y
        elif max_y <= 0:
            offset_y = self.num_total_y_blocks
            scale_y = offset_y / (-min_y)
        else:
            offset_y = min_y/(min_y-max_y) * self.grid_config['num_y_blocks']
            if offset_y < self.grid_config['num_y_blocks']/2:
                offset_y = math.ceil(offset_y) *\
                    self.grid_config['num_y_tiny_blocks_per_block']
            else:
                offset_y = math.floor(offset_y) *\
                    self.grid_config['num_y_tiny_blocks_per_block']
            scale_y = min(offset_y / (-min_y),
                          (self.num_total_y_blocks - offset_y) / max_y)

        scale_x = pow(10, math.floor(math.log10(scale_x)))
        scale_y = pow(10, math.floor(math.log10(scale_y)))
        new_scale_x = scale_x
        new_scale_y = scale_y

        # TODO: outsource
        factors = [2, 4, 5]
        factors.sort()

        for factor in factors:
            scale_x_2 = scale_x * factor
            if max_x * scale_x_2 + offset_x <= self.num_total_x_blocks and min_x * scale_x_2 + offset_x >= 0:
                new_scale_x = scale_x_2

        for factor in factors:
            scale_y_2 = scale_y * factor
            if max_y * scale_y_2 + offset_y <= self.num_total_y_blocks and min_y * scale_y_2 + offset_y >= 0:
                new_scale_y = scale_y_2

        self.offset_x = offset_x
        self.offset_y = offset_y
        self.scale_x = new_scale_x
        self.scale_y = new_scale_y
        self.points_offset_x = points_offset_x
        self.points_offset_y = points_offset_y

        return measurements

    def get_pdf_coords_from_data_point(self, x: float, y: float) -> tuple[float, float]:
        grid_x = (x*self.scale_x+self.offset_x) * \
            self.grid_config['width'] / \
            self.num_total_x_blocks + self.grid_config['x']
        grid_y = (y*self.scale_y+self.offset_y) * \
            self.grid_config['height'] / \
            self.num_total_y_blocks + self.grid_config['y']
        return (grid_x, grid_y)

    def _get_pdf_coords_from_grid_coords(self, x: float, y: float) -> tuple[float, float]:
        grid_x = x * self.grid_config['width'] / \
            self.num_total_x_blocks + self.grid_config['x']
        grid_y = y * self.grid_config['height'] / \
            self.num_total_y_blocks + self.grid_config['y']
        return (grid_x, grid_y)

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
