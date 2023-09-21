from src.models.axis_direction import AxisDirection
from src.axis_transformer.axis_transformer import AxisTransformer


class LinearAxisTransformer(AxisTransformer):
    def __init__(
        self,
        axisDirection: AxisDirection,
        num_blocks: int,
        num_tiny_blocks_per_block: int,
        grid_size: float,
        grid_start: float,
        scale: float,
        offset: float,
        points_offset: float,
        contains_origin: bool,
    ):
        AxisTransformer.__init__(
            self,
            axisDirection,
            num_blocks,
            num_tiny_blocks_per_block,
            grid_size,
            grid_start,
        )

        self.scale = scale
        self.offset = offset
        self.points_offset = points_offset
        self.contains_origin = contains_origin

    def get_grid_coord_from_data_coord(self, data_coord: float) -> float:
        return (data_coord - self.points_offset) * self.scale + self.offset
    
    def get_data_coord_from_grid_coord(self, grid_coord: float) -> float:
        return (grid_coord - self.offset) / self.scale + self.points_offset
    
    def get_pdf_coord_of_axis(self) -> float:
        if self.contains_origin:
            return self.get_pdf_coord_from_data_coord(0)
        else:
            return self.get_pdf_coord_from_grid_coord(0)
