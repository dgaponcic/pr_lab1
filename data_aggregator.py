from parser import Parser

class DataAggregator:
  def __init__(self):
    self.parser = Parser()


  def create_unique_id(self, person):
    unique_id = None
    if "full_name" in person.keys():
      unique_id = person["full_name"].lower().replace(" ", "")
    elif "username" in person.keys():
      unique_id = person["username"]
    else:
      unique_id = f'{person["first_name"].lower()}{person["last_name"].lower()}'
    return unique_id


  def get_new_person(self, person_id):
    fields = [
      "first_name", "last_name", "employee_id", "email", "organization",
      "username", "created_account_data", "card_number", "card_balance",
      "card_currency", "gender", "ip_address", "bitcoin_address"
    ]
    person = {"id": person_id}
    for field in fields:
      person[field] = None
    return person


  def add_keys(self, person, base_item):
    for key in person.keys():
      if key != "id":
        base_item[key] = person[key]


  def get_person_index(self, all_data, unique_id):
    person_id = None
    for index, person in enumerate(all_data):
      if person["id"] == unique_id:
        person_id = index
        break

    return person_id


  def join_data(self, all_data, chunk):
    for person in chunk:
      unique_id = self.create_unique_id(person)
      person_index = self.get_person_index(all_data, unique_id)
      if person_index:
        self.add_keys(person, all_data[person_index])
      else:
        item = self.get_new_person(unique_id)
        self.add_keys(person, item)
        all_data.append(item)

    return all_data


  def parse_data(self, all_data):
    res = []
    for data in all_data:
      data_type = data["data_type"]
      data = self.parser.parse(data_type, data["text"])
      res = self.join_data(res, data)

    return res
