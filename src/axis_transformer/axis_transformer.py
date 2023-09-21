from src.models.axis_direction import AxisDirection


class AxisTransformer:
    def __init__(
        self,
        axisDirection: AxisDirection,
        grid_size: float,
        grid_start: float,
    ):
        self.axisDirection = axisDirection

        self.grid_size = grid_size
        self.grid_start = grid_start

    def get_pdf_coord_from_data_coord(self, data_coord: float) -> float:
        raise NotImplementedError
    
    def get_data_coord_from_pdf_coord(self, pdf_coord: float) -> float:
        raise NotImplementedError
    
    def get_pdf_coord_of_axis(self) -> float:
        raise NotImplementedError
    
    def get_min_pdf_coord(self) -> float:
        raise NotImplementedError
    
    def get_max_pdf_coord(self) -> float:
        raise NotImplementedError
    
    def get_axis_numbers_data_coords(self) -> list[float]:
        raise NotImplementedError
