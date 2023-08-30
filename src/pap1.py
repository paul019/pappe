from pap_parser import parse_csv, parse_config
from drawing import Drawer


def main():
    config_path = 'grids/grid1.toml'  # TODO: will become CLI param
    config = parse_config(config_path)

    csv_path = 'input/data.csv'  # TODO: will become CLI param
    measurements = parse_csv(csv_path)

    drawer = Drawer(config)
    drawer.draw(measurements)

    output_path = 'output/output.pdf'  # TODO: will become CLI param
    drawer.save(output_path)


if __name__ == '__main__':
    main()
