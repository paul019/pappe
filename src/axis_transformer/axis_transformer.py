from src.models.axis_direction import AxisDirection


class AxisTransformer:
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

    def get_pdf_coord_from_grid_coord(self, grid_coord) -> float:
        return grid_coord * self.grid_size / self.num_total_blocks + self.grid_start

    def get_grid_coord_from_pdf_coord(self, pdf_coord) -> float:
        return (pdf_coord - self.grid_start) / self.grid_size * self.num_total_blocks

    def get_grid_coord_from_data_coord(self, data_coord: float) -> float:
        raise NotImplementedError

    def get_data_coord_from_grid_coord(self, grid_coord: float) -> float:
        raise NotImplementedError

    def get_pdf_coord_from_data_coord(self, data_coord: float) -> float:
        return self.get_pdf_coord_from_grid_coord(
            self.get_grid_coord_from_data_coord(data_coord)
        )
    
    def get_data_coord_from_pdf_coord(self, pdf_coord: float) -> float:
        return self.get_data_coord_from_grid_coord(
            self.get_grid_coord_from_pdf_coord(pdf_coord)
        )
    
    def get_pdf_coord_of_axis(self) -> float:
        raise NotImplementedError
