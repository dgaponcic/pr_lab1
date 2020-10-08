import re
import csv
import json
import yaml
import xml.etree.ElementTree as ET
from io import StringIO

class ParserCSV:
  def parse(self, input_data):
    data = []
    reader = csv.DictReader(StringIO(input_data), delimiter=',')

    for row in reader:
      person = {}
      for key in row.keys():
        person[key] = row[key]
      data.append(person)

      return data


class ParserJSON:
  def parse(self, input_data):
    try:
      return json.loads(input_data)
    except:
      data = re.sub(r',([^,]*)$', r'\1', input_data)
      return json.loads(data)


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


class ParserYAML:
  def parse(self, input_data):
    return yaml.load(input_data, Loader=yaml.FullLoader)
