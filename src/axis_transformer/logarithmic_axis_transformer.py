import numpy as np

from src.models.axis_direction import AxisDirection
from src.axis_transformer.axis_transformer import AxisTransformer


class LogarithmicAxisTransformer(AxisTransformer):
    def __init__(
        self,
        axisDirection: AxisDirection,
        grid_size: float,
        grid_start: float,
        num_decades: int,
        log_offset: int,
    ):
        AxisTransformer.__init__(
            self,
            axisDirection,
            grid_size,
            grid_start,
        )

        self.num_decades = num_decades
        self.log_offset = log_offset

    def get_grid_coord_from_data_coord(self, data_coord: float) -> float:
        return (np.log10(data_coord) - self.log_offset) / self.num_decades

    def get_data_coord_from_grid_coord(self, grid_coord: float) -> float:
        return np.pow(10, grid_coord * self.num_decades + self.log_offset)

    def get_pdf_coord_of_axis(self) -> float:
        return self.get_pdf_coord_from_grid_coord(0)

    def get_pdf_coord_from_grid_coord(self, grid_coord) -> float:
        return grid_coord * self.grid_size + self.grid_start

    def get_grid_coord_from_pdf_coord(self, pdf_coord) -> float:
        return (pdf_coord - self.grid_start) / self.grid_size

    def get_pdf_coord_from_data_coord(self, data_coord: float) -> float:
        return self.get_pdf_coord_from_grid_coord(
            self.get_grid_coord_from_data_coord(data_coord)
        )

    def get_data_coord_from_pdf_coord(self, pdf_coord: float) -> float:
        return self.get_data_coord_from_grid_coord(
            self.get_grid_coord_from_pdf_coord(pdf_coord)
        )
    
    def get_min_pdf_coord(self) -> float:
        return self.get_pdf_coord_from_grid_coord(0)
    
    def get_max_pdf_coord(self) -> float:
        return self.get_pdf_coord_from_grid_coord(1)

    def get_axis_numbers_data_coords(self) -> list[float]:
        return []