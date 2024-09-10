import ta_search
import csv
import argparse
import os
from tqdm import tqdm
import datetime
from datetime import datetime
from dateutil.relativedelta import relativedelta
import sys

parser = argparse.ArgumentParser(description='Description of your input arguments')
parser.add_argument('--start', type=int, default=2300, help='Element to start calling API with')
parser.add_argument('--stop', type=int, default=2400, help='Element to stop calling API with. Note that this element is not included to be called.')
parser.add_argument('--overwrite', type=str, default="NO", help='Indicates whether overwrite the existing file reviews.csv or not.')
args = parser.parse_args()

csv_details = 'datasets/details.csv'
csv_reviews = 'datasets/reviews.csv'
csv_users = 'datasets/users.csv'

def read_csv(csv_file) :
    data = []
    with open(csv_file, mode="r", newline="", encoding="utf-8") as file: 
        reader = csv.DictReader(file)
        
        for row in reader :
            data.append(row)
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
            "n_elements": config_data['search']['n_elements'],
            "last_starting_at": config_data['search']['last_starting_at'],
            "last_stopping_at": config_data['search']['last_stopping_at']
        },
        "details": {
            "n_elements": config_data['details']['n_elements'],
            "last_starting_at": config_data['details']['last_starting_at'],
            "last_stopping_at": config_data['details']['last_stopping_at']
        },
        "reviews": {
            "n_elements": total_files,
            "last_starting_at": start_at,
            "last_stopping_at": stop_at
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
    new_config['reviews']['last_stopping_at'] = stop_at
    print("Total number of calls for this execution: " + str(n_calls) + ".")
    
    return start_at, stop_at, n_calls, new_config

def scrape_data(start_at, stop_at, n_calls, search_data) :
    results = []
    scraped_ids = []
    users_data = read_csv(csv_users)
    users_dict = {user['username']: user['user_id'] for user in users_data}
    user_id_counter = max([int(user['user_id']) for user in users_data], default=0) + 1

    with tqdm(total=n_calls, unit='restaurant') as pbar:

        for element in range(start_at, stop_at):
            if element not in range(len(search_data)) :
                break
            location_id = search_data[element]['location_id']
            if location_id is not None and location_id not in scraped_ids :
                scraped_ids.append(location_id)
                reviews_json_data = ta_search.location_reviews(ta_search._key, location_id)
                
                if reviews_json_data :
                    for item in reviews_json_data['data']:
                        if item['rating'] > 3:
                            sentiment = "positive" 
                        elif item['rating'] == 3:
                            sentiment = "neutral" 
                        elif item['rating'] < 3:
                            sentiment = "negative" 
                        else:
                            sentiment = "undefined"
                        username = item['user']['username']
                        # review_count = item['user']['review_count']
                        user_location = item['user']['user_location'].get('name', '') if item['user'].get('user_location') else ''
                        if username not in users_dict:
                            user_info = {
                                "user_id": user_id_counter,
                                "name": username,
                                "username": username,
                                "gender": "",
                                "location": user_location,
                                "preferences": "",
                            }
                            users_data.append(user_info)
                            users_dict[username] = user_id_counter
                            user_id_counter += 1

                        result = {
                            "status": "",
                            "review_id": item.get("id",""),
                            "location_id": location_id,
                            "user_id": users_dict[username],
                            "rating": item.get("rating", ""),
                            "agree_count": item.get("helpful_votes", ""),
                            "published_date": item.get("published_date", ""),
                            "title": item.get("title", ""),
                            "text": item.get("text", ""),
                            "sentiment": sentiment,
                            "visit_type": item.get("trip_type", ""),
                            "visit_date": item.get("travel_date", ""),
                            "review_url": item.get("url", ""),
                        }
                        results.append(result)
            
            pbar.update(1)

    with open(csv_users, "w", newline="", encoding="utf-8") as csv_file: 
        user_headers = ["user_id", "name", "username", "gender", "location", "preferences"]
        writer = csv.DictWriter(csv_file, fieldnames=user_headers)
        writer.writeheader()
        for user in users_data:
            writer.writerow(user)

    return results

def update_reviews(matched_reviews, csv_file=csv_reviews) :
    headers = ["status", "review_id", "location_id", "user_id", "rating", "agree_count", "published_date", "title", "text", "sentiment", "visit_type", "visit_date", "review_url"]

    file_exists = os.path.exists(csv_file)
    existing_reviews = []
    if file_exists and args.overwrite == "NO" :
        existing_reviews = read_csv(csv_reviews)
        repeated_indexes = []        
        for ereview in existing_reviews :
            ereview['status'] = "OLD"
            for mreview in matched_reviews :
                if str(ereview['review_id']) == str(mreview['review_id']) :
                    ereview['status'] = "REPEATED"
                    repeated_indexes.append(matched_reviews.index(mreview))
        for mreview in matched_reviews :
            if matched_reviews.index(mreview) not in repeated_indexes :
                mreview['status'] = "NEW"
                existing_reviews = [mreview] + existing_reviews
    else :
        for mreview in matched_reviews :
            mreview['status'] = "NEW"
            existing_reviews += [mreview]

    with open(csv_file, "w", newline="", encoding="utf-8") as csv_file: 
        writer = csv.DictWriter(csv_file, fieldnames=headers)
        writer.writeheader()
        for review in existing_reviews :
            writer.writerow(review)


if __name__ == "__main__":

    search_data = read_csv(csv_details)
    config_data = ta_search.read_json(ta_search.json_config)

    location_ids = []
    for search_element in search_data :
        location_ids.append(search_element['location_id'])
    u_location_ids = list(dict.fromkeys(location_ids))
    total_files = len(u_location_ids)
    start_at, stop_at, n_calls, new_config = get_scraping_params(config_data, total_files)

    reviews = scrape_data(start_at, stop_at, n_calls, search_data)

    update_reviews(reviews)

    data = read_csv(csv_reviews)
    n_search = len(data)

    ta_search.write_json(new_config, ta_search.json_config)

    print("DONE!")
    print("Number of reviews added: " + str(len(reviews)))
    print("Total number of reviews in datasets/reviews.csv: " + str(n_search))
