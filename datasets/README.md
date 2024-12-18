## Dataset Overview (Updated: December 17, 2024)

## Files:
- **[Details.csv](https://github.com/kShayanR/pcr/blob/master/datasets/details.csv)**
- **[Reviews.csv](https://github.com/kShayanR/pcr/blob/master/datasets/reviews.csv)**
- **[Users.csv](https://github.com/kShayanR/pcr/blob/master/datasets/users.csv)**
- **[Search.json](https://github.com/kShayanR/pcr/blob/master/datasets/search.json)**
  - *Note: The `Search.json` file was used in the data accumulation phase and is now obsolete. (It can be disregarded)*

---

## Change Log

### **Details.csv**

This file contains detailed information about various locations accumulated from [TripAdvisor](https://tripadvisor.com) & [FourSquare](https://foursquare.com).

| **#**  |    **Col**    |
| :----: | :-----------: |
| **1**  |  location_id  |
| **2**  |   category    |
| **3**  |     name      |
| **4**  |  description  |
| **5**  |  reviews_url  |
| **6**  |    address    |
| **7**  |     city      |
| **8**  |     state     |
| **9**  |    country    |
| **10** | working_hours |
| **11** | popular_hours |
| **12** |   timezone    |
| **13** |     email     |
| **14** |     phone     |
| **15** |    website    |
| **16** |   amenities   |
| **17** |    cuisine    |
| **18** |    ranking    |
| **19** | total_rating  |
| **20** |  num_reviews  |
| **21** |  price_level  |
| **22** |    source     |

*The dataset includes 3650 unique entries.*


**Column Definitions:**

1. **Identifying Information:**
   - **location_id**: Unique identifier for each restaurant in the dataset.
   - **category**: Indicates the type of location (e.g., "restaurant"). The current dataset contains locations from the following categories:
   ```
   restaurant,cafe, coffee, and tea house,burger joint,fast food restaurant,turkish restaurant,rooftop bar,bar,lounge,night club,food court,hotel,middle eastern restaurant,italian restaurant,american restaurant,spa,seafood restaurant,cocktail bar,brasserie,plaza,french restaurant,hotel bar,steakhouse,chinese restaurant,asian restaurant,mediterranean restaurant,beach bar,lebanese restaurant,coffee shop,breakfast spot,hookah bar,syrian restaurant,egyptian restaurant,greek restaurant,japanese restaurant,sandwich spot,bakery,theme restaurant,vr cafe,other great outdoors,arcade,food truck,gaming cafe,iraqi restaurant,bistro,dessert shop,tea room,australian restaurant,ice cream parlor,mexican restaurant,pastry shop,moroccan restaurant,english restaurant,gluten-free restaurant,german restaurant,kebab restaurant,dumpling restaurant,café
   ```

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

This file includes user reviews for each of the specified locations in the `details.csv` dataset.

| **#**  |     **Col**      |
| :----: | :--------------: |
| **1**  |      status      |
| **2**  |    review_id     |
| **3**  | location_id (fk) |
| **4**  |   user_id (fk)   |
| **5**  |      rating      |
| **6**  |   agree_count    |
| **7**  |  published_date  |
| **8**  |      title       |
| **9**  |       text       |
| **10** |    sentiment     |
| **11** |    visit_type    |
| **12** |    visit_date    |
| **13** |    review_url    |

*The dataset includes 71,260 unique reviews.*

**Column Definitions:**

1. **Identifying Information:**
   - **review_id**: Unique identifier for each review.
   - **location_id**: Foreign key referring to the restaurant being reviewed.
   - **user_id**: Foreign key identifying the user who wrote the review.

2. **Review Details:**
   - **rating**: The score (typically 1-5 stars) given by the user (This feature is only specified for the reviews which are gathered from TripAdvisor).
   - **agree_count**: Formerly known as `helpful_votes`, it captures the number of times other users found the review helpful.
   - **title**: The title of the User's review.
   - **text**: User's comment.
   - **sentiment**: Indicates the tone of the review (e.g., "positive", "negative"). (Currently not available for **Foursquare** reviews)

3. **Trip and Visit Details:**
   - **visit_type**: Formerly known as `trip_type`, it describes the nature of the user’s visit (e.g., "business", "family", "Couple", "Solo").
   - **visit_date**: The date when the user visited the specified location.

---

### **Users.csv**

This file contains information about users who have written reviews. Some columns have been updated (and renamed).

| **#** |   **Old**   |   **New**   |
| :---: | :---------: | :---------: |
| **1** |   user_id   |   user_id   |
| **2** |    name     |    name     |
| **3** |  username   |  username   |
| **4** |   gender    |     bio     |
| **5** |  location   |  location   |
| **6** | preferences | profile_url |

*The dataset consists of 33,044 unique users.*

**Column Definitions:**

1. **Identifying Information:**
   - **user_id**: Unique identifier for each user.
   - **name**: The combination of the first name and the last name of the user.
   - **username**: Public handle of the user in the specified source.

2. **Personal Information:**
   - **bio**: The biography of the user (if available).
   - **location**: General geographic location of the user (specified as comma-separated human-readable address).

3. **User's profile:**
   - **profile_url**: The canonical link to the user's profile in the specified source.

---

## Older Logs
- [CL20240910](https://github.com/kShayanR/pcr/blob/master/datasets/logs/CL20240910.md)
- [CL20240901](https://github.com/kShayanR/pcr/blob/master/datasets/logs/CL20240901.md)
- [CL20240918](https://github.com/kShayanR/pcr/blob/master/datasets/logs/CL20240918.md)
- [CL20241003](https://github.com/kShayanR/pcr/blob/master/datasets/logs/CL20241003.md)
