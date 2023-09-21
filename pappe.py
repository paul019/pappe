import argparse

from src.pappe_parser import parse_csv, parse_config
from src.drawer import Drawer
from src.axis_transformer_maker.linear_axis_transformer_maker import (
    LinearAxisTranformerMaker,
)
from src.models.axis_direction import AxisDirection


def main():
    # Parse CLI arguments
    cli_parser = argparse.ArgumentParser(
        prog="pappe",
        description="A CLI to draw your data on top of millimeter paper.",
        add_help=True,
    )
    cli_parser.add_argument("input", help="path to input CSV file")
    cli_parser.add_argument("output", help="path to output pdf")
    cli_parser.add_argument(
        "-c", "--config", help="path to TOML config file", default="config.toml"
    )
    args = cli_parser.parse_args()

    # Master config
    config = parse_config(args.config)
    grid_no: int = config["grid_variant"]
    config_path_grid = f"grids/grid{grid_no}.toml"
    complete_grid_config = parse_config(config_path_grid)

    paper_config = complete_grid_config["paper"]
    grid_config = complete_grid_config["grid"]
    drawing_config = complete_grid_config["drawing"]

    regression_config = config["linear_regression"]
    x_axis_config = config["x_axis"]
    y_axis_config = config["y_axis"]

    # Parse input CSV
    measurements = parse_csv(args.input)

    drawer = Drawer(
        paper_config,
        grid_config,
        drawing_config,
        x_axis_config,
        y_axis_config,
        regression_config,
    )
    drawer.draw_all(measurements)

    # Output
    drawer.save(args.output)


if __name__ == "__main__":
    main()
