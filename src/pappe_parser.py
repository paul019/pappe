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
    f = open(path, "r")
    reader = csv.reader(f)

    i = 0

    for row in reader:
        try:
            x, x_lower_error, x_upper_error = (
                float(row[0]),
                float(row[1]),
                float(row[2]),
            )
            y, y_lower_error, y_upper_error = (
                float(row[3]),
                float(row[4]),
                float(row[5]),
            )
            try:
                hide_for_regression = row[6] == "hide"
            except:
                hide_for_regression = False
            m = Measurement(
                x,
                x_lower_error,
                x_upper_error,
                y,
                y_lower_error,
                y_upper_error,
                hide_for_regression,
            )

            measurements.append(m)
        except:
            if i != 0:
                raise Exception("Wrong input format.")

        i += 1

    return measurements


def parse_config(path: str):
    with open(path, "rb") as f:
        return tomllib.load(f)
