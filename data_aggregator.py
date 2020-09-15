from parser import Parser


class DataAggregator:
    def __init__(self):
        self.parser = Parser()

    def get_unique_id(self, person):
        unique_id = None
        if "full_name" in person.keys():
            unique_id = person["full_name"].lower().replace(" ", "")
        elif "username" in person.keys():
            unique_id = person["username"]
        else:
            unique_id = f'{person["first_name"].lower()}{person["last_name"].lower()}'
        return unique_id

    def get_new_person(self, id):
        fields = [
            "first_name", "last_name", "employee_id", "email", "organization",
            "username", "created_account_data", "card_number", "card_balance",
            "card_currency", "gender", "ip_address", "bitcoin_address"
        ]
        person = {"id": id}
        for field in fields:
            person[field] = None
        return person

    def add_keys(self, person, base_item):
        for key in person.keys():
            if key != "id":
                base_item[key] = person[key]

    def join_data(self, all_data, chuck):
        for person in chuck:
            unique_id = self.get_unique_id(person)

            val = next((i for i, item in enumerate(all_data)
                        if item["id"] == unique_id), None)
            if val:
                self.add_keys(person, all_data[val])
            else:
                item = self.get_new_person(unique_id)
                self.add_keys(person, item)
                all_data.append(item)
        return all_data

    def parse_data(self, all_data):
        res = []
        for data in all_data:
            data_type = data["data_type"]
            self.parser.set_strategy(data_type)
            data = self.parser.parse(data["text"])
            res = self.join_data(res, data)
        return res
