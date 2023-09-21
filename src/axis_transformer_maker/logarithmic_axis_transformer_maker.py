import numpy as np

from src.axis_transformer.axis_transformer import AxisTransformer
from src.models.axis_direction import AxisDirection
from src.axis_transformer_maker.axis_transformer_maker import AxisTransformerMaker
from src.axis_transformer.logarithmic_axis_transformer import LogarithmicAxisTransformer


class LogarithmicAxisTransformerMaker(AxisTransformerMaker):
    def __init__(
        self,
        axisDirection: AxisDirection,
        grid_size: float,
        grid_start: float,
        num_decades: int,
    ):
        AxisTransformerMaker.__init__(self, axisDirection, grid_size, grid_start)

        self.num_decades = num_decades

    def make(self, values: list[float]) -> AxisTransformer:
        # Min/Max values
        min_v, max_v = min(values), max(values)

        if min_v <= 0:
            raise "Non-positive values not allowed for logarithmic axis."

        log_offset = np.floor(np.log10(min_v))

        return LogarithmicAxisTransformer(
            self.axisDirection,
            self.grid_size,
            self.grid_start,
            self.num_decades,
            log_offset,
        )
