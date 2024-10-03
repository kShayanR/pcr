from tqdm import tqdm
import requests
import json
import argparse
import datetime
from datetime import datetime
from dateutil.relativedelta import relativedelta
import sys

parser = argparse.ArgumentParser(description='Description of your input arguments')
parser.add_argument('--start', type=int, default=0, help='Element to start calling API with')
parser.add_argument('--stop', type=int, default=239, help='Element to stop calling API with. Note that this element is not included to be called.')
parser.add_argument('--category', type=str, default="restaurant", help='Indicates which category to gather the Information about. (e.g. hotel or restaurant)')
parser.add_argument('--overwrite', type=str, default="NO", help='Indicates whether overwrite the existing file search.json or not.')
args = parser.parse_args()

_key = 'QCE4QMYEP0BZ1NTIHOASAJ2KO5YSAMDF0PGRKHBGGELYDPQQ'

json_dataset = 'locations/lga-scc-pairs.json'
json_search = 'datasets/search.json'
json_config = 'config.json'


def location_search(key, category, catcode, query, address):
    
    url  = f"https://api.foursquare.com/v2/search/recommendations?oauth_token={key}"

    headers = { "Accept": "application/json" }
    
    params = {
        "v": "20241020",
        # "query": f"{category} in {query}",
        "query": query,
        "near": address,
        # "section": "food", #,drinks,coffee",
        # "categoryId": catcode,
        "time": "any",
        "day": "any",
        # "sortByPopularity": False,
        "limit": 50,
        # "offset": 1,
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Couldn't obtain data from Tripadvisor API. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error in API request: {e}")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def location_details(key, locationId):
    url = f"https://api.foursquare.com/v2/venues/{locationId}/?oauth_token={key}"
    headers = { "Accept": "application/json" }
    params = { "v": "20241020" }
    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Couldn't obtain data from Tripadvisor API. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error in API request: {e}")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def location_reviews(key, locationId):
    url = f"https://api.foursquare.com/v2/venues/{locationId}/tips?oauth_token={key}"
    headers = { "Accept": "application/json" }
    params = {
        "v": "20241010"
    }
    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Couldn't obtain data from Tripadvisor API. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error in API request: {e}")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def read_json(file) :
    with open(file, 'r', encoding='utf-8') as archive_json:
        data = json.load(archive_json)
    return data

def get_scraping_params(config_data, total_files) :
    start_at = args.start
    stop_at = args.stop
    n_calls = stop_at - start_at
    current_date = datetime.today()
    if config_data.get("first_call_at") != "" :
        starting_date = datetime.strptime(config_data.get("first_call_at"), "%Y-%m-%d")
    else :
        starting_date = datetime.today()
    day_diff = (current_date - starting_date).days
    max_n_calls = config_data.get("max_n_calls")

    new_config = {
        "max_n_calls": config_data['max_n_calls'],
        "done_calls": config_data['done_calls'],
        "first_call_at": starting_date.strftime('%Y-%m-%d'),
        "last_call_at": datetime.today().strftime('%Y-%m-%d'),
        "search": {
            "n_elements": total_files,
            "last_starting_at": start_at,
            "last_stopping_at": stop_at
        },
        "details": {
            "n_elements": config_data['details']['n_elements'],
            "last_starting_at": config_data['details']['last_starting_at'],
            "last_stopping_at": config_data['details']['last_stopping_at']
        },
        "reviews": {
            "n_elements": config_data['reviews']['n_elements'],
            "last_starting_at": config_data['reviews']['last_starting_at'],
            "last_stopping_at": config_data['reviews']['last_stopping_at']
        }
    }

    if day_diff <= 30 :
        done_calls = config_data.get("done_calls")
    else:
        done_calls = 0
        new_config['first_call_at'] = datetime.today().strftime('%Y-%m-%d')

    remaining_calls = max_n_calls - done_calls
    if n_calls > remaining_calls :
        n_calls = remaining_calls
        if n_calls <= 0 :
            date_of_reset = starting_date + relativedelta(months=1) # Add one month
            print("You cannot make any more free API calls until " + date_of_reset.strftime('%Y-%m-%d') + ".")
            sys.exit()
        stop_at = start_at + n_calls
        print("It exceeds the maximum number of calls per month, stopping element modified to " + str(stop_at) + ".")
    new_config['done_calls'] += n_calls
    new_config['search']['last_stopping_at'] = stop_at
    print("Total number of calls for this execution: " + str(n_calls) + ".")
    
    return start_at, stop_at, n_calls, new_config

def scrape_data(start_at, stop_at, n_calls, pairs):
    existing_ids = []
    if args.overwrite == "NO" :
        existing_data = read_json(json_search)
        existing_ids = [item['location_id'] for item in existing_data]

    all_data_scraped = []
    scraped_ids = []

    n_elements_added = 0
    category = args.category
    catcode = "4d4b7105d754a06374d81259" if category == "restaurant" else "4bf58dd8d48988d1d5941735" # For Hotel Bars & "4bf58dd8d48988d1fa931735" for Hotels & "63be6904847c3692a84b9bb5" for Dining and Drinking
    with tqdm(total=n_calls, unit='call') as pbar:
        for element in range(start_at, stop_at):
            search_json_data = location_search(_key, category, catcode, pairs[element]['scc'], pairs[element]["lga"])

            data_list = search_json_data['response']['group'].get('results', [])

            response_data = []
            for item in data_list:
                venue = item['venue']
                location_id = venue.get('id', "")
                cats = "restaurant,cafe, coffee, and tea house,burger joint,fast food restaurant,turkish restaurant,rooftop bar,bar,lounge,night club,food court,hotel,middle eastern restaurant,italian restaurant,american restaurant,spa,seafood restaurant,cocktail bar,brasserie,plaza,french restaurant,hotel bar,steakhouse,chinese restaurant,asian restaurant,mediterranean restaurant,beach bar,lebanese restaurant,coffee shop,breakfast spot,hookah bar,syrian restaurant,egyptian restaurant,greek restaurant,japanese restaurant,sandwich spot,bakery,theme restaurant,vr cafe,other great outdoors,arcade,food truck,gaming cafe,iraqi restaurant,bistro,dessert shop,tea room,australian restaurant,ice cream parlor,mexican restaurant,pastry shop,moroccan restaurant,english restaurant,gluten-free restaurant,german restaurant,kebab restaurant,dumpling restaurant,café"
                cat = venue['categories'][0].get('name', "").lower() if venue.get('categories') and len(venue['categories']) > 0 else "undefined"
                if location_id not in existing_ids and location_id not in scraped_ids and cat in cats:
                    response_data = [
                        {
                            'location_id': location_id,
                            'category': cat,
                            'name': venue.get('name', ""),
                            'address_obj': {
                                'city': venue['location'].get('city', ""),
                                'state': venue['location'].get('state', ""),
                                'country': venue['location'].get('country', ""),
                                'address': venue['location'].get('formattedAddress', [])[0],
                            }
                        }
                    ]
                    scraped_ids.append(location_id)
                    all_data_scraped.append(response_data[0])   
                    n_elements_added += 1

            pbar.update(1)
    return all_data_scraped, n_elements_added

def write_json(data, json_file) :
    with open(json_file, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)

def write_locations(data) :
    if args.overwrite == "NO" :
        existing_data = read_json(json_search)
        existing_data += data
        write_json(existing_data, json_search)
    else :
        write_json(data, json_search)

if __name__ == "__main__":

    data = read_json(json_dataset)

    config_data = read_json(json_config)

    total_files = len(data)
    start_at, stop_at, n_calls, new_config = get_scraping_params(config_data, total_files)

    all_data_scraped, n_elements_added = scrape_data(start_at, stop_at, n_calls, data)

    write_locations(all_data_scraped)

    data = read_json(json_search)
    n_search = len(data)
    new_config['details']['n_elements'] = n_search
    write_json(new_config, json_config)

    print("DONE!")
    print("Number of locations added: " + str(n_elements_added))
    print("Total number of locations in datasets/search.json: " + str(n_search))