import search
import os
import csv
from tqdm import tqdm
import argparse
from datetime import datetime
from dateutil.relativedelta import relativedelta
import sys

parser = argparse.ArgumentParser(description='Scrape details from TripAdvisor or Foursquare')
parser.add_argument('--start', type=int, default=0, help='Element to start calling API with')
parser.add_argument('--stop', type=int, default=100, help='Element to stop calling API with. This element is not included.')
parser.add_argument('--source', type=str, choices=['tripadvisor', 'foursquare'], required=True, help='Source platform to scrape (tripadvisor/foursquare)')
parser.add_argument('--overwrite', type=str, default="NO", help='Indicates whether to overwrite the existing file details.csv or not.')
args = parser.parse_args()

csv_details = 'datasets/details.csv'

def get_scraping_params(config_data, total_files):
    start_at = args.start
    stop_at = args.stop
    n_calls = stop_at - start_at
    current_date = datetime.today()
    starting_date = datetime.strptime(config_data.get("first_call_at", ""), "%Y-%m-%d") if config_data.get("first_call_at") else current_date
    day_diff = (current_date - starting_date).days
    max_n_calls = config_data.get("max_n_calls")
    
    if day_diff > 30:
        done_calls = 0
        starting_date = current_date
    else:
        done_calls = config_data.get("done_calls")
    
    remaining_calls = max_n_calls - done_calls
    if n_calls > remaining_calls:
        n_calls = remaining_calls
        if n_calls <= 0:
            date_of_reset = starting_date + relativedelta(months=1)
            print(f"You cannot make any more free API calls until {date_of_reset.strftime('%Y-%m-%d')}.")
            sys.exit()
        stop_at = start_at + n_calls
        print(f"Exceeded max calls per month, modifying stop_at to {stop_at}.")
    
    new_config = {
        **config_data,
        "done_calls": done_calls + n_calls,
        "details": {
            "n_elements": total_files,
            "last_starting_at": start_at,
            "last_stopping_at": stop_at
        },
        "first_call_at": starting_date.strftime('%Y-%m-%d'),
        "last_call_at": current_date.strftime('%Y-%m-%d')
    }
    
    return start_at, stop_at, n_calls, new_config

def read_csv(csv_file):
    with open(csv_file, mode="r", newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))

def overwrite(csv_file=csv_details):
    headers = ["location_id", "category", "name", "description", "reviews_url", "address", "city", "state", "country", "working_hours", "popular_hours", "timezone", "email", "phone", "website", "amenities", "cuisine", "ranking", "total_rating", "num_reviews", "price_level", "source"]
    with open(csv_file, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()

def process_and_store_data(data_json, csv_file):
    file_exists = os.path.exists(csv_file)
    mode = "a" if file_exists else "w"
    with open(csv_file, mode, newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=data_json[0].keys())
        if not file_exists:
            writer.writeheader()
        writer.writerows(data_json)

def format_hours(timeframes):
    return "; ".join(f"{tf.get('days', '')}: {', '.join(ot.get('renderedTime', '') for ot in tf.get('open', []))}" for tf in timeframes)

def format_attributes(attributes):
    return ", ".join(f"{item.get('displayName', '')}: {item.get('displayValue', '')}" for group in attributes.get('groups', []) for item in group.get('items', []))

def format_cuisine(categories, attributes):
    cuisine_list = [cat.get("shortName", "") for cat in categories]
    cuisine_list += [item.get("displayName", "") for group in attributes.get('groups', []) for item in group.get('items', []) if group.get('type') in ["serves", "drinks"]]
    return ", ".join(cuisine_list)

def scrape_data(source, start_at, stop_at, n_calls, search_data):
    with tqdm(total=n_calls, unit='location') as pbar:
        for element in range(start_at, stop_at):
            location_id = search_data[element].get("location_id")
            category = search_data[element].get("category")
            if location_id:
                details_json_data = getattr(search, f"{source}_details")(location_id)
                if details_json_data:
                    if source == 'tripadvisor':
                        data = {
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
                            "source": "TripAdvisor"
                        }
                    elif source == 'foursquare':
                        venue = details_json_data['response']['venue']
                        data = {
                            "location_id": venue.get("id", ""),
                            "category": category,
                            "name": venue.get("name", ""),
                            "description": venue.get("description", ""),
                            "reviews_url": venue.get("shortUrl", ""),
                            "address": venue.get("location", {}).get("formattedAddress", [""])[0],
                            "city": venue.get("location", {}).get("city", ""),
                            "state": venue.get("location", {}).get("state", ""),
                            "country": venue.get("location", {}).get("country", ""),
                            "working_hours": format_hours(venue.get("hours", {}).get("timeframes", [])),
                            "popular_hours": format_hours(venue.get("popular", {}).get("timeframes", [])),
                            "timezone": venue.get("timeZone", ""),
                            "email": venue.get("contact", {}).get("email", ""),
                            "phone": venue.get("contact", {}).get("formattedPhone", ""),
                            "website": venue.get("url", ""),
                            "amenities": format_attributes(venue.get("attributes", {})),
                            "cuisine": format_cuisine(venue.get("categories", []), venue.get("attributes", {})),
                            "total_rating": venue.get("rating", ""),
                            "num_reviews": venue.get("stats", {}).get("tipCount", ""),
                            "price_level": venue.get("price", {}).get("currency", "") * venue.get("price", {}).get("tier", 0),
                            "source": "FourSquare"
                        }
                    process_and_store_data([data], csv_details)
            else:
                print(f"'location_id' not found for element {element}")
            pbar.update(1)

if __name__ == "__main__":
    search_data = search.read_json('search.json')
    config_data = search.read_json('config.json')
    
    total_files = len(search_data)
    start_at, stop_at, n_calls, new_config = get_scraping_params(config_data, total_files)

    if args.overwrite == "YES":
        overwrite()
    
    scrape_data(args.source, start_at, stop_at, n_calls, search_data)

    search.update_config(args.source, 'config', new_config)
