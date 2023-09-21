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
            grid_size,
            grid_start,
        )

        self.num_blocks = num_blocks
        self.num_tiny_blocks_per_block = num_tiny_blocks_per_block
        self.num_total_blocks = num_blocks * num_tiny_blocks_per_block

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

    def get_pdf_coord_from_grid_coord(self, grid_coord) -> float:
        return grid_coord * self.grid_size / self.num_total_blocks + self.grid_start

    def get_grid_coord_from_pdf_coord(self, pdf_coord) -> float:
        return (pdf_coord - self.grid_start) / self.grid_size * self.num_total_blocks

    def get_pdf_coord_from_data_coord(self, data_coord: float) -> float:
        return self.get_pdf_coord_from_grid_coord(
            self.get_grid_coord_from_data_coord(data_coord)
        )

    def get_data_coord_from_pdf_coord(self, pdf_coord: float) -> float:
        return self.get_data_coord_from_grid_coord(
            self.get_grid_coord_from_pdf_coord(pdf_coord)
        )

    def get_axis_numbers_data_coords(self) -> list[float]:
        return [
            self.get_data_coord_from_grid_coord(m * self.num_tiny_blocks_per_block)
            for m in range(self.num_blocks + 1)
        ]
    
    def get_min_pdf_coord(self) -> float:
        return self.get_pdf_coord_from_grid_coord(0)
    
    def get_max_pdf_coord(self) -> float:
        return self.get_pdf_coord_from_grid_coord(self.num_total_blocks)
