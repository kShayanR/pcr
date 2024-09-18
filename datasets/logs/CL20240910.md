## Dataset Overview (Updated: September 10, 2024)

## Files:
- **[Details.csv](https://github.com/kShayanR/pcr/blob/master/datasets/details.csv)**
- **[Reviews.csv](https://github.com/kShayanR/pcr/blob/master/datasets/reviews.csv)**
- **[Users.csv](https://github.com/kShayanR/pcr/blob/master/datasets/users.csv)**
- **[Search.json](https://github.com/kShayanR/pcr/blob/master/datasets/search.json)**
  - *Note: The `Search.json` file was used in the data accumulation phase and is now obsolete. (It can be disregarded)*

---

## Change Log

### **Details.csv**

This file contains detailed information about various locations accumulated from [TripAdvisor](https://tripadvisor.com) & [FourSquare](https://foursquare.com). The changes include renaming of columns and addition of new columns to provide more comprehensive data.

| **#**  |    **Old**    |    **New**    |
| :----: | :-----------: | :-----------: |
| **1**  |  location_id  |  location_id  |
| **2**  |   category    |   category    |
| **3**  |     name      |     name      |
| **4**  |  description  |  description  |
| **5**  |  review_url   |  reviews_url  |
| **6**  |    address    |    address    |
| **7**  |     city      |     city      |
| **8**  |     state     |     state     |
| **9**  |    country    |    country    |
| **10** | working_hours | working_hours |
| **11** |       -       | popular_hours |
| **12** |   timezone    |   timezone    |
| **13** |     email     |     email     |
| **14** |     phone     |     phone     |
| **15** |    website    |    website    |
| **16** |   amenities   |   amenities   |
| **17** |   features    |       -       |
| **18** |    cuisine    |    cuisine    |
| **19** |    styles     |       -       |
| **20** |  trip_types   |       -       |
| **21** |    ranking    |    ranking    |
| **22** | total_rating  | total_rating  |
| **23** |  num_reviews  |  num_reviews  |
| **24** |  price_level  |  price_level  |
| **25** |    source     |    source     |

*The dataset includes 2400 unique Restaurant enteries.*

**Column Definitions:**

1. **Identifying Information:**
   - **location_id**: Unique identifier for each restaurant in the dataset.
   - **category**: Indicates the type of location (e.g., "restaurant"). The current dataset only contains restaurants.

2. **Operational Details:**
   - **working_hours**: Specifies the operating hours of each restaurant, formatted as "Day: Opening - Closing" (e.g., "Monday: 10:00 - 00:00").
   - **popular_hours**: Newly added column capturing the most popular hours based on customer visits.

3. **Contact Information:**
   - **email**: Official email address of the restaurant.
   - **phone**: Contact number.
   - **website**: Official website URL for the restaurant.

4. **Location Information:**
   - **address, city, state, country**: Specifies the physical location details.
   - **timezone**: Timezone of the restaurant’s location.

5. **Amenities and Features:**
   - **amenities**: Lists the available amenities (e.g., "outdoor seating", "wheelchair accessibility").

6. **Review and Rating Information:**
   - **total_rating**: The overall rating of the restaurant, generally on a scale of 1 to 5 stars.
   - **num_reviews**: The total number of reviews for the restaurant.
   - **price_level**: Indicates the restaurant’s price category.


---

### **Reviews.csv**

This file includes user reviews for each of the specified locations in the `details.csv` dataset. The changes include renaming along with some modifications in data structure to enhance the review data.

| **#** | **Old** | **New** |
|:-----:|:--------------------:|:--------------:|
| **1** | status               | status         |
| **2** | review_id            | review_id      |
| **3** | location_id (fk)     | location_id (fk) |
| **4** | user_id (fk)         | user_id (fk)   |
| **5** | rating               | rating         |
| **6** | helpful_votes        | agree_count    |
| **7** | published_date       | published_date |
| **8** | title                | title          |
| **9** | text                 | text           |
| **10**| sentiment            | sentiment      |
| **11**| trip_type            | visit_type     |
| **12**| travel_date          | visit_date     |
| **13**| review_url           | review_url     |

*The dataset includes 6,822 unique reviews.*


**Column Definitions:**

1. **Identifying Information:**
   - **review_id**: Unique identifier for each review.
   - **location_id**: Foreign key referring to the restaurant being reviewed.
   - **user_id**: Foreign key identifying the user who wrote the review.

2. **Review Details:**
   - **rating**: The score (typically 1-5 stars) given by the user (This feature is only specified for the reviews which are gathered from TripAdvisor).
   - **agree_count**: Formerly known as `helpful_votes`, it captures the number of times other users found the review helpful.
   - **title**: The title of the User's review.
   - **text**: User's review.
   - **sentiment**: Indicates the tone of the review (e.g., "positive", "negative").

3. **Trip and Visit Details:**
   - **visit_type**: Formerly known as `trip_type`, it describes the nature of the user’s visit (e.g., "business", "family", "Couple", "Solo").
   - **visit_date**: The date when the user visited the the specified location.

---

### **Users.csv**

This file contains information about users who have written reviews. Some columns have been updated to reflect the absence of data.

| **#** | **Old** | **New** |
|:-----:|:--------------------:|:--------------:|
| **1** | user_id              | user_id        |
| **2** | -                    | name           |
| **3** | username             | username       |
| **4** | gender               | gender         |
| **5** | age (none)           | -              |
| **6** | location             | location       |
| **7** | preferences          | preferences (none) |

*The dataset consists of 5,289 unique users.*


**Column Definitions:**

1. **Identifying Information:**
   - **user_id**: Unique identifier for each user.
   - **name**: The combination of the first name and the last name of the user.
   - **username**: Public handle of the user.

2. **Personal Information:**
   - **gender**: The gender of the user (if available).
   - **location**: General geographic location of the user (Either specified as the Country Code, of a comma-separated address).

3. **Preferences:**
   - **preferences**: Intended to capture user preferences based on reviews (currently unavailable).


---

## Older Logs
- [CL20240901](https://github.com/kShayanR/pcr/blob/master/datasets/logs/CL20240901.md)
