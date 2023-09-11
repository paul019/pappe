import argparse

from src.pappe_parser import parse_csv, parse_config
from src.drawer import Drawer
from src.transformer import Transformer


def main():
    print('🙌 pappe started')

    # Parse CLI arguments
    cli_parser = argparse.ArgumentParser(
        prog='pappe',
        description='A CLI to draw your data on top of millimeter paper.',
        add_help=True)
    cli_parser.add_argument('input', help='path to input CSV file')
    cli_parser.add_argument('output', help='path to output PDF')
    cli_parser.add_argument('-c', '--config',
                            help='path to TOML config file',
                            default='config.toml')
    args = cli_parser.parse_args()

    # Master config
    config = parse_config(args.config)
    grid_no: int = config['grid_variant']
    config_path_grid = f'grids/grid{grid_no}.toml'
    complete_grid_config = parse_config(config_path_grid)

    # Parse input CSV
    measurements = parse_csv(args.input)

    # Setup drawing
    trafo = Transformer(complete_grid_config['grid'],
                        config['factors'], config['origins'])
    drawer = Drawer(trafo, complete_grid_config)
    drawer.draw_all(measurements)

    # Output
    drawer.save(args.output)
    print(f'Successfully saved PDF to {args.output}')


if __name__ == '__main__':
    main()
