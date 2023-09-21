import math

from src.axis_transformer_maker.axis_transformer_maker import AxisTransformerMaker
from src.models.axis_direction import AxisDirection
from src.axis_transformer.axis_transformer import AxisTransformer
from src.axis_transformer.linear_axis_transformer import LinearAxisTransformer


class LinearAxisTranformerMaker(AxisTransformerMaker):
    def __init__(
        self,
        axisDirection: AxisDirection,
        num_blocks: int,
        num_tiny_blocks_per_block: int,
        grid_size: float,
        grid_start: float,
        factors: list[float],
        offset_exponent: int,
        should_contain_origin: bool,
    ) -> None:
        AxisTransformerMaker.__init__(
            self,
            axisDirection,
            num_blocks,
            num_tiny_blocks_per_block,
            grid_size,
            grid_start,
        )

        self.factors = factors
        self.factors.sort()

        self.offset_exponent = offset_exponent
        self.should_contain_origin = should_contain_origin

    def make(self, values: list[float]) -> AxisTransformer:
        # Min/Max values
        min_v, max_v = min(values), max(values)

        # Data points offset (depending on whether data origin should be shown)
        points_offset = 0.0
        if not self.should_contain_origin and (min_v <= 0 and max_v >= 0):
            self.should_contain_origin = True
        if not self.should_contain_origin:
            points_offset = self._calc_data_points_offset(
                min_v, max_v, self.offset_exponent
            )

        # Apply offsets
        for v in values:
            v -= points_offset
        min_v -= points_offset
        max_v -= points_offset

        # Estimate offset and scale
        offset, scale = self._calc_offset_estimate_scale(min_v, max_v)

        # Refine scale
        scale = self._refine_scale(scale, self.factors)

        return LinearAxisTransformer(
            self.axisDirection,
            self.num_blocks,
            self.num_tiny_blocks_per_block,
            self.grid_size,
            self.grid_start,
            scale,
            offset,
            points_offset,
            self.should_contain_origin
        )

    def _calc_data_points_offset(
        self, min_value: float, max_value: float, offset_exponent: int
    ) -> float:
        """
        Calculates the offset of data points inside their own reference system.

        This is useful if the origin is not to be shown.
        """
        # TODO: Refactoring by Paul ;)

        if min_value <= 0:
            points_offset = -pow(10, math.floor(math.log10(-max_value))) / pow(
                10, offset_exponent
            )
            points_offset_trial = points_offset

            for i in range(2, pow(10, offset_exponent + 1)):
                if i * points_offset >= max_value:
                    points_offset_trial = i * points_offset

            points_offset = points_offset_trial

        else:
            points_offset = pow(10, math.floor(math.log10(min_value))) / pow(
                10, offset_exponent
            )
            points_offset_trial = points_offset

            for i in range(2, pow(10, offset_exponent + 1)):
                if i * points_offset <= min_value:
                    points_offset_trial = i * points_offset

            points_offset = points_offset_trial

        return points_offset

    def _calc_offset_estimate_scale(
        self, min_value: float, max_value: float
    ) -> tuple[float, float]:
        """
        Calculates the final offset and gives a first estimate for scale.

        Offset: offset of data points to grid in grid coordinates (is always positive)
        Scale: ratio between data scaling and grid scaling
        """
        if min_value >= 0:
            offset = 0
            scale = self.num_total_blocks / max_value
        elif max_value <= 0:
            offset = self.num_total_blocks
            scale = self.num_total_blocks / (-min_value)
        else:
            offset = min_value / (min_value - max_value) * self.num_blocks
            offset = (
                math.ceil(offset)
                if offset < self.num_blocks / 2
                else math.floor(offset)
            )
            offset *= self.num_tiny_blocks_per_block
            scale = min(
                offset / (-min_value), (self.num_total_blocks - offset) / max_value
            )

        return offset, scale

    def _refine_scale(self, scale: float, factors: list[int]) -> float:
        scale_rounded_down = pow(10, math.floor(math.log10(scale)))
        scale_refined = scale_rounded_down

        ratio = scale / scale_rounded_down
        for factor in factors:
            if factor <= ratio:
                scale_refined = scale_rounded_down * factor

        return scale_refined
