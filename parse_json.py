import json
import re


class ParserJSON:
  def parse(self, input_data):
    try:
      return json.loads(input_data)
    except:
      data = re.sub(r',([^,]*)$', r'\1', input_data)
      return json.loads(data)
