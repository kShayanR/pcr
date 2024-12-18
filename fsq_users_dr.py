import pandas as pd
import requests
from bs4 import BeautifulSoup
import os
import argparse
from tqdm import tqdm

def validate_overwrite(value):
    if value not in ['YES', 'NO']:
        raise argparse.ArgumentTypeError("Argument --overwrite must be 'YES' or 'NO'")
    return value

parser = argparse.ArgumentParser()
parser.add_argument("--start", type=int, default=0, help="Starting index for rows in reviews.csv")
parser.add_argument("--stop", type=int, default=68953, help="Stopping index for rows in reviews.csv")
parser.add_argument("--overwrite", type=validate_overwrite, default='NO', help="Overwrite users.csv: 'YES' or 'NO'")
args = parser.parse_args()

reviews_df = pd.read_csv('datasets/reviews.csv')

if os.path.exists('datasets/users.csv') and args.overwrite == 'NO':
    users_df = pd.read_csv('datasets/users.csv')
else:
    users_df = pd.DataFrame(columns=["user_id", "name", "username", "bio", "location", "profile_url"])

scraped_ids = [id for id in users_df['user_id']]

start = args.start
stop = args.stop if args.stop is not None else len(reviews_df)

new_user_data = []
subset = reviews_df.iloc[start:stop]
for _, row in tqdm(subset.iterrows(), total=stop - start, desc="Processing Reviews", unit="review"):
    user_id = row['user_id']
    author_url = row['review_url']
    
    if user_id in scraped_ids:
        continue

    try:
        response = requests.get(author_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        name = soup.find('h1', class_='name').text.strip() if soup.find('h1', class_='name') else None
        bio = soup.find('p', class_='userBio').text.strip() if soup.find('p', class_='userBio') else None
        location = soup.find('span', class_='userLocation').text.strip() if soup.find('span', class_='userLocation') else None
        new_user_data.append({
            "user_id": user_id,
            "name": name,
            "username": user_id,
            "bio": bio,
            "location": location,
            "profile_url": author_url,
        })
        scraped_ids.append(user_id)

    except Exception as e:
        print(f"Error processing user {user_id} from URL {author_url}: {e}")

if new_user_data:
    new_users_df = pd.DataFrame(new_user_data)
    users_df = pd.concat([users_df, new_users_df], ignore_index=True)

users_df.to_csv('datasets/users.csv', index=False)
print(f"Users data saved to users.csv")
