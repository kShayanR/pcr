import json

def load_json(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        return []

def find_and_remove_duplicates(restaurants, search_data):
    # search_names = {item['name'] for item in search_data}
    names = [item['name'] for item in search_data]
    search_names = ",".join(names)
    duplicate_names = set()
    filtered_restaurants = []
    
    for restaurant in restaurants:
        if restaurant['scc'] in search_names:
            duplicate_names.add(restaurant['scc'])
        else:
            filtered_restaurants.append(restaurant)

    return filtered_restaurants, duplicate_names

def save_to_json(data, filename='locations_new.json'):
    try:
        with open(filename, 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, ensure_ascii=False, indent=4)
        print(f"Updated data successfully saved to {filename}.")
        print(f"Total number of restaurant names after removing duplicates: {len(data)}")
    except Exception as e:
        print(f"Error saving to JSON: {e}")

if __name__ == "__main__":
    restaurants = load_json('locations_new.json')
    search_data = load_json('search.json')

    filtered_restaurants, duplicate_names = find_and_remove_duplicates(restaurants, search_data)
    save_to_json(filtered_restaurants)
    
    if duplicate_names:
        print("Duplicate restaurant names found:")
        for name in duplicate_names:
            print(name)
    else:
        print("No duplicate restaurant names found.")
