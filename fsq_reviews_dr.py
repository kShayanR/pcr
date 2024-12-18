import pandas as pd
from playwright.sync_api import sync_playwright
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
parser.add_argument('--start', type=int, default=3600, help='Element to start calling API with')
parser.add_argument('--stop', type=int, default=3650, help='Element to stop calling API with. Note that this element is not included to be called.')
parser.add_argument('--overwrite', type=str, default="NO", help='Indicates whether overwrite the existing file reviews.csv or not.')
args = parser.parse_args()

csv_details = 'datasets/details.csv'
csv_reviews = 'datasets/reviews.csv'

def get_scraping_params(config_data, total_files):
    start_at = args.start
    stop_at = args.stop
    n_calls = stop_at - start_at
    current_date = datetime.today()
    if config_data.get("first_call_at") != "":
        starting_date = datetime.strptime(config_data.get("first_call_at"), "%Y-%m-%d")
    else:
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

    if day_diff <= 30:
        done_calls = config_data.get("done_calls")
    else:
        done_calls = 0
        new_config['first_call_at'] = datetime.today().strftime('%Y-%m-%d')

    remaining_calls = max_n_calls - done_calls
    if n_calls > remaining_calls:
        n_calls = remaining_calls
        if n_calls <= 0:
            date_of_reset = starting_date + relativedelta(months=1) # Add one month
            print("You cannot make any more free API calls until " + date_of_reset.strftime('%Y-%m-%d') + ".")
            sys.exit()
        stop_at = start_at + n_calls
        print("It exceeds the maximum number of calls per month, stopping element modified to " + str(stop_at) + ".")
    new_config['done_calls'] += n_calls
    new_config['reviews']['last_stopping_at'] = stop_at
    print("Total number of calls for this execution: " + str(n_calls) + ".")
    
    return start_at, stop_at, n_calls, new_config

def scrape_data(start_at, stop_at, n_calls, page, search_data, review_data):
    results = []
    no_locations = 0
    search_data = pd.DataFrame(search_data)
    review_data = pd.DataFrame(review_data)
    
    scraped_ids = review_data['location_id'].unique().tolist()

    subset_data = search_data.iloc[start_at:stop_at]
    for idx, row in tqdm(subset_data.iterrows(), total=n_calls, unit="location"):
        reviews_url = row['reviews_url']
        location_id = row['location_id']
        num_reviews = row['num_reviews']
        source = row['source']

        if location_id not in scraped_ids and source == 'FourSquare' and num_reviews != '0':
        # if location_id not in scraped_ids and source == 'FourSquare':

            # page.route("**/*", lambda route, request: route.abort() if request.resource_type in ["image", "stylesheet", "font"] else route.continue_())
            page.route("**/*", lambda route: route.abort() if route.request.resource_type in ["image", "font", "stylesheet"] else route.continue_())
            # page.wait_for_selector("li.tipWithLogging")
            
            no_locations += 1

            page_num = 1

            while True:
                url = reviews_url if page_num == 1 else f"{reviews_url}?tipsPage={page_num}"
                page.goto(url, timeout=100000000)

                review_elements = page.query_selector_all("li.tipWithLogging")
                if not review_elements:
                    break
                for review in review_elements:
                    url_elem = review.query_selector("span.userName a")
                    suffix = url_elem.get_attribute("href") if url_elem else None
                    agree_count_elem = review.query_selector("span.tipUpvoteCount")
                    result = {
                        "status": "",
                        "rating": None,
                        "title": None,
                        "sentiment": None,
                        "visit_type": None,
                        "review_id": review.get_attribute('data-id'),
                        "user_id": suffix.strip('/') if suffix else None,
                        "location_id": location_id,
                        "agree_count": agree_count_elem.inner_text() if agree_count_elem else '0',
                        "published_date": review.query_selector("span.tipDate").inner_text(),
                        "text": review.query_selector("div.tipText").inner_text(),
                        "visit_date": review.query_selector("span.tipDate").inner_text(),
                        "review_url": f"https://foursquare.com{suffix}",
                    }
                    results.append(result)
                
                page_num += 1

            scraped_ids.append(location_id)

    return results, no_locations

def update_reviews(matched_reviews, review_data, csv_file):
    headers = ['status', 'review_id', 'location_id', 'user_id', 'rating', 'agree_count', 'published_date', 'title', 'text', 'sentiment', 'visit_type', 'visit_date', 'review_url']

    file_exists = os.path.exists(csv_file)
    existing_reviews = []
    if file_exists and args.overwrite == "NO":
        existing_reviews = review_data
        repeated_indexes = []        
        for ereview in existing_reviews:
            ereview['status'] = "OLD"
            for mreview in matched_reviews:
                if str(ereview['review_id']) == str(mreview['review_id']):
                    ereview['status'] = "REPEATED"
                    repeated_indexes.append(matched_reviews.index(mreview))
        for mreview in matched_reviews:
            if matched_reviews.index(mreview) not in repeated_indexes:
                mreview['status'] = "NEW"
                existing_reviews += [mreview]
    else:
        for mreview in matched_reviews:
            mreview['status'] = "NEW"
            existing_reviews += [mreview]

    with open(csv_file, "w", newline="", encoding="utf-8") as csv_file: 
        writer = csv.DictWriter(csv_file, fieldnames=headers)
        writer.writeheader()
        for review in existing_reviews:
            writer.writerow(review)

with sync_playwright() as page:
    browser = page.chromium.launch(headless=True)
    page = browser.new_page()

    try:
        search_data = fs.read_csv(csv_details)
        review_data = fs.read_csv(csv_reviews)
        config_data = fs.read_json(fs.json_config)

        location_ids = []
        for location in search_data:
            location_ids.append(location['location_id'])
        u_location_ids = list(dict.fromkeys(location_ids))
        total_files = len(u_location_ids)

        start_at, stop_at, n_calls, new_config = get_scraping_params(config_data, total_files)
        reviews, n_locations = scrape_data(start_at, stop_at, n_calls, page, search_data, review_data)
        update_reviews(reviews, review_data, csv_reviews)
        data = fs.read_csv(csv_reviews)
        n_search = len(data)

        fs.write_json(new_config, fs.json_config)

        print("DONE!")
        print("Number of scrapped locations: " + str(n_locations))
        print("Number of reviews added: " + str(len(reviews)))
        print("Total number of reviews in datasets/reviews.csv: " + str(n_search))

    finally:
        browser.close()
