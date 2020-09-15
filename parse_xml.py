import xml.etree.ElementTree as ET
from io import StringIO


class ParserXML:
    def parse(self, input_data):
        tree = ET.parse(StringIO(input_data))
        root = tree.getroot()

        data = []
        for record in root:
            person = {}
            for value in record:
                person[value.tag] = value.text
            data.append(person)
        return data
