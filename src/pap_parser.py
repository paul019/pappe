import tomllib
import csv

from measurement import Measurement


def parse_csv(path: str) -> list[Measurement]:
    """
    Parses the given CSV file into a list of measurements.

    Note that this does not check for validity of the CSV file, e.g. we assume
    that the file is well-formed according to the documentation.
    """
    measurements: list[Measurement] = []

    # open file
    f = open(path, 'r')
    reader = csv.reader(f)

    for row in reader:
        x, y = float(row[0]), float(row[1])
        measurement = Measurement(x, y)

        # Optional error bars
        if len(row) == 4:
            lower_error, upper_error = float(row[2]), float(row[3])
            measurement.add_error(lower_error, upper_error)

        measurements.append(measurement)

    return measurements


def parse_config(path: str):
    with open(path, 'rb') as f:
        return tomllib.load(f)
