class Error:
    def __init__(self, lower_error: float, upper_error: float):
        self.lower_error: float = lower_error
        self.upper_error: float = upper_error

    def exists(self):
        return self.lower_error != 0.0 or self.upper_error != 0.0

    def avg_error(self):
        return (self.lower_error + self.upper_error) / 2.0


class Measurement:
    """
    One point of a data series, e.g. temperature for a specific time.
    "Data point" is used interchangeably with "measurement".

    A measurement may define error bounds. If not specified, they default to 0.0
    and are not drawn.
    """

    def __init__(
        self,
        x: float,
        x_lower_error: float,
        x_upper_error: float,
        y: float,
        y_lower_error: float,
        y_upper_error: float,
    ):
        self.x: float = x
        self.y: float = y
        self.x_error: Error = Error(x_lower_error, x_upper_error)
        self.y_error: Error = Error(y_lower_error, y_upper_error)

    def data(self) -> tuple[float, float]:
        return (self.x, self.y)

    def error_bounds(self) -> tuple[float, float]:
        return (self.lower_error, self.upper_error)

    # def has_error_bounds(self) -> bool:
    #    return self.lower_error != 0.0 or self.upper_error != 0.0

    def __str__(self):
        # errors_str = f' Errors: ({self.lower_error}, {self.upper_error})'\
        #    if self.has_error_bounds() else ''
        return f"Point ({self.x}, {self.y})"
