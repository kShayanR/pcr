import fsq_search as fs
import csv
import argparse
import os
from tqdm import tqdm
import datetime
from datetime import datetime
from dateutil.relativedelta import relativedelta
import sys

parser = argparse.ArgumentParser(description='Description of your input arguments')
parser.add_argument('--start', type=int, default=1800, help='Element to start calling API with')
parser.add_argument('--stop', type=int, default=1829, help='Element to stop calling API with. Note that this element is not included to be called.')
parser.add_argument('--overwrite', type=str, default="NO", help='Indicates whether overwrite the existing file reviews.csv or not.')
args = parser.parse_args()

csv_details = 'datasets/details.csv'
csv_reviews = 'datasets/reviews.csv'
csv_users = 'datasets/users.csv'

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

def timestamp_to_iso(timestamp):
    return datetime.utcfromtimestamp(timestamp).isoformat() + 'Z'

def scrape_data(start_at, stop_at, n_calls, search_data) :
    results = []
    scraped_ids = []
    users_data = fs.read_csv(csv_users)
    users_dict = {user['username']: user['user_id'] for user in users_data}

    with tqdm(total=n_calls, unit='restaurant') as pbar:

        for element in range(start_at, stop_at):
            if element not in range(len(search_data)) :
                break
            location_id = search_data[element]['location_id']
            if location_id is not None and location_id not in scraped_ids :
                scraped_ids.append(location_id)
                reviews_json_data = fs.location_reviews(fs._key, location_id)
                tips = reviews_json_data['response']['tips']['items']
                if tips:
                    for tip in tips:
                        user_id = tip['user']['id']
                        username = tip['user'].get('handle', "")
                        fname = tip['user'].get('firstName', "")
                        lname = tip['user'].get('lastName', "")
                        gender = tip['user'].get('gender', "")
                        sentiment = ""

                        user_location = ""
                        if tip['user'].get('address'):
                            user_location = tip['user'].get('address', "")
                        elif tip['user'].get('city'):
                            city = tip['user'].get('city', "")
                            country_code = tip['user'].get('countryCode', "")
                            user_location = f"{city}, {country_code}"
                        else:
                            user_location = tip['user'].get('countryCode', "")

                        if user_id not in users_dict:
                            user_info = {
                                "user_id": user_id,
                                "name": f"{fname} {lname}",
                                "username": username,
                                "gender": gender,
                                "location": user_location,
                                "preferences": "",
                            }
                            users_data.append(user_info)
                            users_dict[username] = user_id

                        published_date = timestamp_to_iso(tip['createdAt'])

                        result = {
                            "status": "",
                            "review_id": tip.get("id",""),
                            "location_id": location_id,
                            "user_id": users_dict[username],
                            "rating": tip.get("rating", ""),
                            "agree_count": tip.get("agreeCount", ""),
                            "published_date": published_date,
                            "title": tip.get("title", ""),
                            "text": tip.get("text", ""),
                            "sentiment": sentiment,
                            "visit_type": tip.get("trip_type", ""),
                            "visit_date": published_date,
                            "review_url": tip.get("canonicalUrl", ""),
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

def update_reviews(matched_reviews, csv_file) :
    headers = ["status", "review_id", "location_id", "user_id", "rating", "agree_count", "published_date", "title", "text", "sentiment", "visit_type", "visit_date", "review_url"]

    file_exists = os.path.exists(csv_file)
    existing_reviews = []
    if file_exists and args.overwrite == "NO" :
        existing_reviews = fs.read_csv(csv_reviews)
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
                existing_reviews += [mreview]
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

    search_data = fs.read_csv(csv_details)

    config_data = fs.read_json(fs.json_config)

    location_ids = []
    for search_element in search_data :
        location_ids.append(search_element['location_id'])
    u_location_ids = list(dict.fromkeys(location_ids))
    total_files = len(u_location_ids)
    start_at, stop_at, n_calls, new_config = get_scraping_params(config_data, total_files)

    reviews = scrape_data(start_at, stop_at, n_calls, search_data)

    update_reviews(reviews, csv_reviews)

    data = fs.read_csv(csv_reviews)
    n_search = len(data)

    fs.write_json(new_config, fs.json_config)

    print("DONE!")
    print("Number of reviews added: " + str(len(reviews)))
    print("Total number of reviews in datasets/reviews.csv: " + str(n_search))
