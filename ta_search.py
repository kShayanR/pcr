from tqdm import tqdm
import requests
import json
import argparse
import datetime
from datetime import datetime
from dateutil.relativedelta import relativedelta
import sys

# 50cb504ee4b0c490b6b7c432 >> last FSQ location (1829th element)

parser = argparse.ArgumentParser(description='Description of your input arguments')
parser.add_argument('--start', type=int, default=200, help='Element to start calling API with')
parser.add_argument('--stop', type=int, default=336, help='Element to stop calling API with. Note that this element is not included to be called.')
parser.add_argument('--category', type=str, default="restaurants", help='Indicates which category to gather the Information about. (e.g. hotels, restaurants, attractions, etc)')
parser.add_argument('--overwrite', type=str, default="NO", help='Indicates whether overwrite the existing file search.json or not.')
args = parser.parse_args()

_key = "BC073290243D4F699FDBC9BA4204A72C"

json_dataset = 'locations/lga-scc-pairs.json'
json_search = 'datasets/search.json'
json_config = 'config.json'


def location_search(key, category, query, address):
    _category = category
    _query = query.replace(" ", "%20")
    _address = address.replace(" ", "%20")
    url = f"https://api.content.tripadvisor.com/api/v1/location/search?key={key}&searchQuery={_query}&category={_category}&address={_address}&language=en"
    # url = "https://api.content.tripadvisor.com/api/v1/location/search?key=" + str(key) + "&searchQuery=" + _searchQuery + "&category=" + _category + "&language=en"
    headers = {"accept": "application/json"}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Couldn't obtain data from Tripadvisor API. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error in API request: {e}")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def location_details(key, locationId):
    
    url = f"https://api.content.tripadvisor.com/api/v1/location/{locationId}/details?key={key}&language=en"
    headers = {"accept": "application/json"}

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Couldn't obtain data from Tripadvisor API. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error in API request: {e}")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def location_reviews(key, locationId):
    url = f"https://api.content.tripadvisor.com/api/v1/location/{locationId}/reviews?key={key}&language=en"
    headers = {"accept": "application/json"}
    try:
        response = requests.get(url, headers=headers)
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

def scrape_data(start_at, stop_at, n_calls, pairs) :
    existing_ids = []
    if args.overwrite == "NO" :
        existing_data = read_json(json_search)
        existing_ids = [item['location_id'] for item in existing_data]

    all_data_scraped = []
    scraped_ids = []

    n_elements_added = 0
    category = args.category
    with tqdm(total=n_calls, unit='call') as pbar:
        for element in range(start_at, stop_at):
            search_json_data = location_search(_key, category, pairs[element]['scc'], pairs[element]["lga"])

            data_list = search_json_data.get('data', [])

            response_data = []
            for item in data_list :
                location_id = item['location_id']
                if location_id not in existing_ids and location_id not in scraped_ids:
                    response_data = [
                        {
                            'location_id': location_id,
                            'category': "restaurant",
                            'name': item.get('name', ""),
                            'address_obj': {
                                'city': item['address_obj'].get('city', ""),
                                'state': item['address_obj'].get('state', ""),
                                'country': item['address_obj'].get('country', ""),
                                'address': item['address_obj'].get('address_string', ""),
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
    # - LGA : Local Government Area
    # - SCC : State Suburbs

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