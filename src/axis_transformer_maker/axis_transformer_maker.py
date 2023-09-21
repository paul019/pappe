import math
from enum import Enum
import copy

from src.axis_transformer.axis_transformer import AxisTransformer
from src.models.axis_direction import AxisDirection


class AxisTransformerMaker:
    def __init__(
        self,
        axisDirection: AxisDirection,
        num_blocks: int,
        num_tiny_blocks_per_block: int,
        grid_size: float,
        grid_start: float,
    ):
        self.axisDirection = axisDirection

        self.num_blocks = num_blocks
        self.num_tiny_blocks_per_block = num_tiny_blocks_per_block
        self.num_total_blocks = num_blocks * num_tiny_blocks_per_block

        self.grid_size = grid_size
        self.grid_start = grid_start

    def make(self, values: list[float]) -> AxisTransformer:
        raise NotImplementedError