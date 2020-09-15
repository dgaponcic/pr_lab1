import yaml


class ParserYAML:
    def parse(self, input_data):
        return yaml.load(input_data, Loader=yaml.FullLoader)
