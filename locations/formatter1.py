import json

input_path = 'lga-scc-pairs-new.json'

with open(input_path, 'r', encoding='utf-8') as file:
    data = json.load(file)

def merge_neighborhoods_streets(data):
    for city in data:
        city["lga"] = city.get("neighborhoods", []) + city.get("streets", [])
        if "neighborhoods" in city:
            del city["neighborhoods"]
        if "streets" in city:
            del city["streets"]

merge_neighborhoods_streets(data)

with open(input_path, 'w', encoding='utf-8') as file:
    json.dump(data, file, ensure_ascii=False, indent=4)

print("Data has been updated and saved successfully.")
