import concrete_parsers as parsers 

class Parser:
  def __init__(self):
    self.strategy = None

  def get_strategy(self, data_type):
    switcher = {
      "application/x-yaml": parsers.ParserYAML(),
      "text/csv": parsers.ParserCSV(),
      "application/json": parsers.ParserJSON(),
      "application/xml": parsers.ParserXML()
    }
    
    return switcher.get(data_type, "Invalid type")


  def parse(self, data_type, data):
    # print("Egrd")
    strategy = self.get_strategy(data_type)
    # print("ger")
    return strategy.parse(data)
