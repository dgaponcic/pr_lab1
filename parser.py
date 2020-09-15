from parse_xml import ParserXML
from parse_yaml import ParserYAML
from parse_csv import ParserCSV
from parse_json import ParserJSON


class Parser:
    def __init__(self):
        self.strategy = None

    def set_strategy(self, data_type):
        switcher = {
            "application/x-yaml": ParserYAML(),
            "text/csv": ParserCSV(),
            "application/json": ParserJSON(),
            "application/xml": ParserXML()
        }
        self.strategy = switcher.get(data_type, "Invalid type")

    def parse(self, data):
        return self.strategy.parse(data)
