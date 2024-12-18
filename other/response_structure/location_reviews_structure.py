"""
    INPUT PARAMS
    - key : The Partner API Key.
    - locationId : A unique identifier for a location on Tripadvisor. The location ID can be obtained using the Location Search.
    
    OUTPUT FORMAT
    {
        "data": [
            {
                "id": 0,
                "lang": "string",
                "location_id": 0,
                "published_date": "string",
                "rating": 0,
                "helpful_votes": 0,
                "rating_image_url": "string",
                "url": "string",
                "trip_type": "string",
                "travel_date": "string",
                "text": "string",
                "title": "string",
                "owner_response": {
                    "id": 0,
                    "lang": string,
                    "text": "string",
                    "title": "string",
                    "author": "string",
                    "published_date": "string",
                },
                "is_machine_translated": true,
                "user": {
                    "username": "string",
                    "user_location": {
                        "name": "string",
                        "id": "string"
                    },
                    "review_count": 0,
                    "reviewer_badge": "string",
                    "avatar": {
                        "additionalProp": "string"
                    }
                },
                "subratings": {
                    "additionalProp": {
                        "name": "string",
                        "localized_name": "string",
                        "rating_image_url": "string",
                        "value": 0
                    }
                }
            }
        ],
        "error": {
            "message": "string",
            "type": "string",
            "code": 0
        }
    }
    
"""
    

    


"""
e.g.

'id' = 952222529
'lang' = 'en'
'location_id' = 287023
'published_date' = '2024-05-24T21:28:40Z'
'rating' = 3
'helpful_votes' = 0
'rating_image_url' = 'https://www.tripadvisor.com/img/cdsi/img2/ratings/traveler/s3.0-66827-5.svg'
'url' = 'https://www.tripadvisor.com/ShowUserReviews-g255060-d287023-r952222529-Reviews-Rydges_Camperdown-Sydney_New_South_Wales.html?m=66827#review952222529'
'text' = 'There is no decent Wi-Fi coverage in the rooms and the TV the streaming TV did not work I reported it several times nothing was done no concessions were offered except a breakfast The staff was very nice But it appeared they could do nothing to help....'
'title' = 'Wi-Fi ridiculous !'
'trip_type' = 'Business'
'travel_date' = '2024-05-31'
'user' = {'username': 'discoqueen49', 'user_location': {'id': '56003', 'name': 'Houston, Texas'}, 'avatar': {'thumbnail': 'https://media-cdn.tripadvisor.com/media/photo-t/1a/f6/e2/11/default-avatar-2020-41.jpg', 'small': 'https://media-cdn.tripadvisor.com/media/photo-l/1a/f6/e2/11/default-avatar-2020-41.jpg', 'medium': 'https://media-cdn.tripadvisor.com/media/photo-f/1a/f6/e2/11/default-avatar-2020-41.jpg', 'large': 'https://media-cdn.tripadvisor.com/media/photo-p/1a/f6/e2/11/default-avatar-2020-41.jpg', 'original': 'https://media-cdn.tripadvisor.com/media/photo-o/1a/f6/e2/11/default-avatar-2020-41.jpg'}}
'subratings' = {}
'owner_response' = {'id': 954613153, 'title': 'Owner response', 'text': 'Dear Discoqueen49,\n\nThank you for taking the time to review your guest experience at ...ervices.\nKind Regards.\nMitch Mclachlan\nGM\n', 'lang': 'en', 'author': 'Mitchell Mclachlan', 'published_date': '2024-06-11T01:42:55Z'}

"""