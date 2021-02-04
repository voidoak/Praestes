import json

def load_data(file):
    """ return data found in file """
    with open(file, "r") as json_file:
        return json.load(json_file)


def dump_data(data, file):
    """ write data to file """
    with open(file, "w") as json_file:
        json.dump(data, json_file)
