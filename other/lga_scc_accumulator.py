import requests
import pandas as pd
from bs4 import BeautifulSoup
import json

csv_file_path = 'categories.csv'

def get_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching the URL: {e}")
        return []

    soup = BeautifulSoup(response.content, 'html.parser')
    name_elements = soup.find_all('a', class_='venueLink')
    address_elements = soup.find_all('span', class_='unlinkedCategory')

    location_names = []
    for element in name_elements:
        name = element.get_text(strip=True)
        name_parts = name.split('.', 1)
        if len(name_parts) > 1:
            location_names.append(name_parts[1].strip())

    if len(location_names) != len(address_elements):
        print("Mismatch between the number of two elements.")
        return []

    # categories_df = pd.read_csv(csv_file_path)

    # categories_df = categories_df.set_index('address Label')

    # def find_address_id(lga):
    #     try:
    #         return categories_df.loc[lga, 'address ID']
    #     except KeyError:
    #         return ""

    location_data = []
    for name, address in zip(location_names, address_elements):
        location_address = address.get_text(strip=True)
        # ls = str(location_address).split(' · ')
        # add = "Dubai"
        # if len(ls) > 1:
        #     add = ls[0]
        location_data.append({
            "lga": location_address,
            "scc": name
        })
    
    # structured_data = [{"lga": "", "scc": name} for name in location_names]
    
    # def remove_duplicate_words(location_names):
    #     unique_words = list(dict.fromkeys(location_names.split()))
    #     return ' '.join(unique_words)

    # for entry in location_data:
    #     entry['scc'] = remove_duplicate_words(entry['scc'])

    return location_data

def save_to_json(data, filename='locations.json'):
    try:
        with open(filename, 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, ensure_ascii=False, indent=4)
        print(f"Data successfully saved to {filename}.")
        print(f"Total number of restaurant names saved: {len(data)}")
    except Exception as e:
        print(f"Error saving to JSON: {e}")

if __name__ == "__main__":
    url = "https://foursquare.com/salah_aldin/list/dubai-restaurants"
    locations = get_data(url)

    if locations:
        save_to_json(locations)
    else:
        print("No restaurant data to save.")

