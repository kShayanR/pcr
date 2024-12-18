from tqdm import tqdm
import requests
import json
import argparse
from datetime import datetime
from dateutil.relativedelta import relativedelta
import sys

parser = argparse.ArgumentParser(description='Search locations on TripAdvisor or Foursquare')
parser.add_argument('--start', type=int, default=0, help='Element to start calling API with')
parser.add_argument('--stop', type=int, default=239, help='Element to stop calling API with. The stop element is not included.')
parser.add_argument('--source', type=str, default="tripadvisor", help='Choose platform: tripadvisor or foursquare')
parser.add_argument('--category', type=str, default="restaurants", help='Category to gather information about. (e.g. restaurants, hotels)')
parser.add_argument('--overwrite', type=str, default="NO", help='Whether to overwrite the existing search.json file.')
args = parser.parse_args()

API_KEYS = {
    "ta": "BC073290243D4F699FDBC9BA4204A72C",
    "fsq": "QCE4QMYEP0BZ1NTIHOASAJ2KO5YSAMDF0PGRKHBGGELYDPQQ"
}
json_dataset = 'locations/lga-scc-pairs.json'
json_search = 'datasets/search.json'
json_config = 'config.json'

def api_request(url, headers, params=None):
    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            return response.json()
        print(f"API error. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    return None

def read_json(file):
    with open(file, 'r', encoding='utf-8') as f:
        return json.load(f)

def write_json(data, json_file):
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def get_scraping_params(config_data, total_files):
    start_at, stop_at = args.start, args.stop
    n_calls = stop_at - start_at
    current_date = datetime.today()
    starting_date = datetime.strptime(config_data.get("first_call_at", current_date.strftime('%Y-%m-%d')), "%Y-%m-%d")
    day_diff = (current_date - starting_date).days
    max_n_calls, done_calls = config_data.get("max_n_calls"), config_data.get("done_calls", 0)
    
    if day_diff > 30:
        done_calls, config_data['first_call_at'] = 0, current_date.strftime('%Y-%m-%d')
    
    remaining_calls = max_n_calls - done_calls
    if n_calls > remaining_calls:
        n_calls = remaining_calls
        stop_at = start_at + n_calls
        if n_calls <= 0:
            print(f"No more API calls until {(starting_date + relativedelta(months=1)).strftime('%Y-%m-%d')}.")
            sys.exit()
        print(f"Modified stop_at to {stop_at} due to API limit.")
    
    config_data.update({
        "done_calls": done_calls + n_calls,
        "last_call_at": current_date.strftime('%Y-%m-%d'),
        "search": {
            "n_elements": total_files,
            "last_starting_at": start_at,
            "last_stopping_at": stop_at
        }
    })
    return start_at, stop_at, n_calls, config_data

def tripadvisor_search(query, category, address):
    url = f"https://api.content.tripadvisor.com/api/v1/location/search?key={API_KEYS['ta']}&searchQuery={query}&category={category}&address={address}&language=en"
    headers = {"accept": "application/json"}
    return api_request(url, headers)

def foursquare_search(query, catcode, address):
    url = f"https://api.foursquare.com/v2/search/recommendations?oauth_token={API_KEYS['fsq']}"
    headers = {"Accept": "application/json"}
    params = {
        "v": "20241020",
        "query": query,
        "near": address,
        "section": "food",
        "categoryId": catcode,
        "time": "any",
        "day": "any",
        "sortByPopularity": False,
        "limit": 50,
        "offset": 50
    }
    return api_request(url, headers, params)

def platform_search(query, category, address):
    if args.platform == "foursquare":
        catcode = "4d4b7105d754a06374d81259" if category == "restaurant" else "4bf58dd8d48988d1fa931735"
        return foursquare_search(query, catcode, address)
    else:
        return tripadvisor_search(query, category, address)

def scrape_data(start_at, stop_at, n_calls, pairs):
    existing_ids = []
    if args.overwrite == "NO":
        existing_data = read_json(json_search)
        existing_ids = [item['location_id'] for item in existing_data]
    
    all_data_scraped, scraped_ids = [], []
    category = args.category
    source = args.source
    with tqdm(total=n_calls, unit='call') as pbar:
        for element in range(start_at, stop_at):
            result = platform_search(pairs[element]['scc'], category, pairs[element]["lga"])
            data_list = result.get('response', {}).get('group', {}).get('results', []) if source == 'foursquare' else result.get('data', [])
            
            for item in data_list:
                location_id = item['venue']['id'] if source == 'foursquare' else item['location_id']
                if location_id not in existing_ids and location_id not in scraped_ids:
                    location_data = {
                        'location_id': location_id,
                        'category': category,
                        'name': item['venue'].get('name', "") if source == 'foursquare' else item.get('name', ""),
                        'address_obj': {
                            'city': item['venue']['location'].get('city', "") if source == 'foursquare' else item['address_obj'].get('city', ""),
                            'state': item['venue']['location'].get('state', "") if source == 'foursquare' else item['address_obj'].get('state', ""),
                            'country': item['venue']['location'].get('country', "") if source == 'foursquare' else item['address_obj'].get('country', ""),
                            'address': item['venue']['location'].get('formattedAddress', [""])[0] if source == 'foursquare' else item['address_obj'].get('address_string', "")
                        }
                    }
                    scraped_ids.append(location_id)
                    all_data_scraped.append(location_data)
            pbar.update(1)
    
    return all_data_scraped

def write_locations(data):
    if args.overwrite == "NO":
        existing_data = read_json(json_search)
        data = existing_data + data
    write_json(data, json_search)

if __name__ == "__main__":
    pairs = read_json(json_dataset)
    config_data = read_json(json_config)
    total_files = len(pairs)
    
    start_at, stop_at, n_calls, new_config = get_scraping_params(config_data, total_files)
    all_data_scraped = scrape_data(start_at, stop_at, n_calls, pairs)
    
    write_locations(all_data_scraped)
    new_config['details']['n_elements'] = len(read_json(json_search))
    write_json(new_config, json_config)

    print(f"DONE! Added {len(all_data_scraped)} new locations.")
