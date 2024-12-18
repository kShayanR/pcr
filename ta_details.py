import ta_search as ts
import os
import csv
from tqdm import tqdm
import argparse
import datetime
from datetime import datetime
from dateutil.relativedelta import relativedelta
import sys

parser = argparse.ArgumentParser(description='Description of your input arguments')
parser.add_argument('--start', type=int, default=2300, help='Element to start calling API with')
parser.add_argument('--stop', type=int, default=2400, help='Element to stop calling API with. Note that this element is not included to be called.')
parser.add_argument('--overwrite', type=str, default="NO", help='Indicates whether overwrite the existing file details.csv or not.')
args = parser.parse_args()

csv_details = 'datasets/details.csv'

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
            "n_elements": config_data['search']['n_elements'],
            "last_starting_at": config_data['search']['last_starting_at'],
            "last_stopping_at": config_data['search']['last_stopping_at']
        },
        "details": {
            "n_elements": total_files,
            "last_starting_at": start_at,
            "last_stopping_at": stop_at
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
            date_of_reset = starting_date + relativedelta(months=1)
            print("You cannot make any more free API calls until " + date_of_reset.strftime('%Y-%m-%d') + ".")
            sys.exit()
        stop_at = start_at + n_calls
        print("It exceeds the maximum number of calls per month, stopping element modified to " + str(stop_at) + ".")
    new_config['done_calls'] += n_calls
    new_config['details']['last_stopping_at'] = stop_at
    print("Total number of calls for this execution: " + str(n_calls) + ".")
    
    return start_at, stop_at, n_calls, new_config

def read_csv(csv_file) :
    list_of_hotels = []
    with open(csv_file, mode="r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        
        for row in reader :
            list_of_hotels.append(row)
    return list_of_hotels

def overwrite (csv_file=csv_details) :
    headers = ["location_id", "category", "name", "description", "reviews_url", "address", "city", "state", "country", "working_hours", "popular_hours", "timezone", "email", "phone", "website", "amenities", "cuisine", "ranking", "total_rating", "num_reviews", "price_level", "source"]
    with open(csv_file, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=headers)
        writer.writeheader()

def scrape_data(start_at, stop_at, n_calls, search_data) :

    with tqdm(total=n_calls, unit='location') as pbar:

        for element in range(start_at, stop_at):
            location_id = search_data[element].get("location_id")
            # location_type = search_data[element].get("category")
            if location_id is not None:
                details_json_data = ts.location_details(ts._key, location_id)
                if details_json_data is not None:
                    filtered_data = [{
                        "location_id": details_json_data.get("location_id", ""),
                        "category": details_json_data.get("category", {}).get("name", ""),
                        "name": details_json_data.get("name", ""),
                        "description": details_json_data.get("description", ""),
                        "reviews_url": details_json_data.get("web_url", ""),
                        "address": details_json_data.get("address_obj", {}).get("address_string", ""),
                        "city": details_json_data.get("address_obj", {}).get("city", ""),
                        "state": details_json_data.get("address_obj", {}).get("state", ""),
                        "country": details_json_data.get("address_obj", {}).get("country", ""),
                        "working_hours": ", ".join(details_json_data.get("hours", {}).get("weekday_text", [])),
                        "popular_hours": "",
                        "timezone": details_json_data.get("timezone", ""),
                        "email": details_json_data.get("email", ""),
                        "phone": details_json_data.get("phone", ""),
                        "website": details_json_data.get("website", ""),
                        "amenities": ", ".join(details_json_data.get("features", [])),
                        "cuisine": ", ".join([cuisine.get("name", "") for cuisine in details_json_data.get("cuisine", [])]),
                        "ranking": details_json_data.get("ranking_data", {}).get("ranking_string", ""),
                        "total_rating": details_json_data.get("rating", ""),
                        "num_reviews": details_json_data.get("num_reviews", ""),
                        "price_level": details_json_data.get("price_level", ""),
                        "source": "TripAdvisor",
                    }]
                    process_and_store_data(filtered_data, csv_details)

            else:
                print("'location_id' was not found on this item!")

            pbar.update(1)

def process_and_store_data(data_json, csv_file):
    file_exists = os.path.exists(csv_file)
    mode = "a" if file_exists else "w"
    with open(csv_file, mode, newline="", encoding="utf-8") as csv_file:
        fields = data_json[0].keys()
        writer = csv.DictWriter(csv_file, fieldnames=fields)

        if not file_exists:
            writer.writeheader()

        for row in data_json:
            writer.writerow(row)

if __name__ == "__main__":
    search_data = ts.read_json(ts.json_search)
    config_data = ts.read_json(ts.json_config)

    total_files = len(search_data)
    start_at, stop_at, n_calls, new_config = get_scraping_params(config_data, total_files)

    if args.overwrite == "YES":
        overwrite()

    scrape_data(start_at, stop_at, n_calls, search_data)

    data = read_csv(csv_details)
    n_search = len(data)
    new_config['reviews']['n_elements'] = n_search

    ts.write_json(new_config, ts.json_config)

    print("DONE!")
    print("Number of hotels' details added: " + str(n_calls))
    print("Total number of locations in datasets/details.csv: " + str(n_search))