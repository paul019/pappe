import tomllib
import csv

from src.measurement import Measurement


def parse_csv(path: str) -> list[Measurement]:
    """
    Parses the given CSV file into a list of measurements.

    Note that this does not check for validity of the CSV file, i.e. we assume
    that the file is well-formed according to the documentation.
    """
    measurements: list[Measurement] = []

    # open file
    f = open(path, 'r')
    reader = csv.reader(f)

    for row in reader:
        x, y = float(row[0]), float(row[1])
        m = Measurement(x, y)

        # Symmetric error
        if len(row) == 3:
            error = float(row[2])
            m.add_error_bounds(error, error)

        # Asymmetric errors
        if len(row) == 4:
            lower_error, upper_error = float(row[2]), float(row[3])
            m.add_error_bounds(lower_error, upper_error)

        measurements.append(m)

    return measurements


def parse_config(path: str):
    with open(path, 'rb') as f:
        return tomllib.load(f)
