class Measurement:
    """
    One point of a data series, e.g. temperature for a specific time.
    "Data point" is used interchangeably with "measurement".

    A measurement may define error bounds. If not specified, they default to 0.0
    and are not drawn.
    """

    def __init__(self, x: float, y: float):
        self.x: float = x
        self.y: float = y
        self.lower_error: float = 0.0
        self.upper_error: float = 0.0

    def add_error_bounds(self, lower_error: float, upper_error: float):
        self.lower_error = lower_error
        self.upper_error = upper_error

    def data(self) -> tuple[float, float]:
        return (self.x, self.y)

    def error_bounds(self) -> tuple[float, float]:
        return (self.lower_error, self.upper_error)

    def has_error_bounds(self) -> bool:
        return self.lower_error != 0.0 or self.upper_error != 0.0

    def __str__(self):
        errors_str = f' Errors: ({self.lower_error}, {self.upper_error})'\
            if self.has_error_bounds() else ''
        return f'Point ({self.x}, {self.y}) {errors_str}'
