from src.axis_transformer.axis_transformer import AxisTransformer
from src.models.axis_direction import AxisDirection


class AxisTransformerMaker:
    def __init__(
        self,
        axisDirection: AxisDirection,
        grid_size: float,
        grid_start: float,
    ):
        self.axisDirection = axisDirection

        self.grid_size = grid_size
        self.grid_start = grid_start

    def make(self, values: list[float]) -> AxisTransformer:
        raise NotImplementedError