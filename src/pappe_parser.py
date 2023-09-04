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
        x, x_lower_error, x_upper_error = float(row[0]), float(row[1]), float(row[2])
        y, y_lower_error, y_upper_error = float(row[3]), float(row[4]), float(row[5])
        m = Measurement(x, x_lower_error, x_upper_error, y, y_lower_error, y_upper_error)

        measurements.append(m)

    return measurements


def parse_config(path: str):
    with open(path, 'rb') as f:
        return tomllib.load(f)
