import math
from src.measurement import Measurement


class LinearRegression:
    """
    Stores a linear regression of the form y = m * x + n
    """

    def __init__(self, m: float, m_error: float, n: float, n_error: float) -> None:
        self.m = m
        self.m_error = m_error
        self.n = n
        self.n_error = n_error

    def best_fit(self):
        return LinearFunction(self.m, self.n)

    def error_curve_high_slope(self):
        return LinearFunction(self.m + self.m_error, self.n - self.n_error)

    def error_curve_low_slope(self):
        return LinearFunction(self.m - self.m_error, self.n + self.n_error)


class LinearFunction:
    """
    Stores a linear function of the form y = m * x + n
    """

    def __init__(self, m: float, n: float) -> None:
        self.m = m
        self.n = n

    def eval(self, x: float) -> float:
        return self.m * x + self.n


def do_linear_regression(measurements: list[Measurement]):
    """
    Makes a linear regression.
    """
    x = [m.x for m in measurements]
    y = [m.y for m in measurements]
    dy = [m.y_error.avg_error() for m in measurements]
    num = len(measurements)

    # sum(1/dy^2)
    a = 0.0
    for i in range(num):
        a += 1 / pow(dy[i], 2)

    # sum(x^2/dy^2)
    b = 0.0
    for i in range(num):
        b += pow(x[i], 2) / pow(dy[i], 2)

    # sum(x/dy^2)
    c = 0.0
    for i in range(num):
        c += x[i] / pow(dy[i], 2)

    # sum(xy/dy^2)
    d = 0.0
    for i in range(num):
        d += x[i] * y[i] / pow(dy[i], 2)

    # sum(y/dy^2)
    e = 0.0
    for i in range(num):
        e += y[i] / pow(dy[i], 2)

    xi = a * b - pow(c, 2)

    m = 1 / xi * (a * d - c * e)
    n = 1 / xi * (b * e - c * d)

    dm = math.sqrt(1 / xi * a)
    dn = math.sqrt(1 / xi * b)

    return LinearRegression(m, dm, n, dn)
