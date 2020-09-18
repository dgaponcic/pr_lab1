import csv
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
