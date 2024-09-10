import json

file_path = 'lga-scc-pairs-gen.json'

with open(file_path, 'r', encoding='utf-8') as file:
    data = json.load(file)

output = []
for city in data:
    scc = city['scc']
    for lga in city['lga']:
        output.append({
            'lga': scc,
            'scc': lga
        })

with open('lga-scc-pairs.json', 'w') as file:
    json.dump(output, file, indent=4)

print("Data has been formatted and saved to 'lga-scc-pairs.json'.")
