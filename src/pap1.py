from pap_parser import parse_csv, parse_config
from drawing import Drawer
from transformer import Transformer


def main():
    config_path = 'config.toml'
    config = parse_config(config_path)

    grid_no: int = config['grid_variant']
    config_path_grid = f'grids/grid{grid_no}.toml'
    complete_grid_config = parse_config(config_path_grid)

    csv_path = 'input/data.csv'  # TODO: will become CLI param
    measurements = parse_csv(csv_path)

    trafo = Transformer(complete_grid_config['grid'],
                        config['factors'], config['origins'])
    drawer = Drawer(trafo, complete_grid_config)
    drawer.draw_all(measurements)

    output_path = 'output/output.pdf'  # TODO: will become CLI param
    drawer.save(output_path)


if __name__ == '__main__':
    main()
