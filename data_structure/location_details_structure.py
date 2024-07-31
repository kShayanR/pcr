"""
    INPUT PARAMS
    - key : The Partner API Key.
    - locationId : A unique identifier for a location on Tripadvisor. The location ID can be obtained using the Location Search.
    
    OUTPUT FORMAT
    {
        "location_id": 0,
        "name": "string",
        "description": "string",
        "web_url": "string",
        "address_obj": {
            "street1": "string",
            "street2": "string",
            "city": "string",
            "state": "string",
            "country": "string",
            "postalcode": "string",
            "address_string": "string"
        },
        "ancestors": [
            {
            "abbrv": "string",
            "level": "string",
            "name": "string",
            "location_id": 0
            }
        ],
        "latitude": 0,
        "longitude": 0,
        "timezone": "string",
        "write_review": "string",
        "ranking_data": {
            "geo_location_id": 0,
            "ranking_string": "string",
            "geo_location_name": "string",
            "ranking_out_of": 0,
            "ranking": 0
        },
        "rating": 0,
        "rating_image_url": "string",
        "num_reviews": "string",
        "review_rating_count": {
            "additionalProp": "string"
        },
        "subratings": {
            "additionalProp": {
                "name": "string",
                "localized_name": "string",
                "rating_image_url": "string",
                "value": 0
            }
        },
        "photo_count": 0,
        "see_all_photos": "string",
        "price_level": "string",
        "hours": {
            "periods": [
                {
                    "open": {
                        "day": 0,
                        "time": "string"
                    },
                    "close": {
                        "day": 0,
                        "time": "string"
                    }
                }
            ],
            "weekday_text": [
                "string"
            ],
        },
        "amenities": [
            "string"
        ],
        "cuisine": [
            {
                "name": "string",
                "localized_name": "string"
            }
        ],
        "parent_brand": "string",
        "brand": "string",
        "category": {
            "name": "string",
            "localized_name": "string"
        },
        "subcategory": [
            {
                "name": "string",
                "localized_name": "string"
            }
        ],
        "groups": [
            {
                "name": "string",
                "localized_name": "string",
                "categories": [
                    {
                        "name": "string",
                        "localized_name": "string"
                    }
                ]
            }
        ],
        "styles": [
            "string"
        ],
        "neighborhood_info": [
            {
                "location_id": "string",
                "name": "string"
            }
        ],
        "trip_types": [
            {
                "name": "string",
                "localized_name": "string",
                "value": "string"
            }
        ],
        "awards": [
            {
                "award_type": "string",
                "year": 0,
                "images": {
                    "tiny": "string",
                    "small": "string",
                    "large": "string"
                },
                "categories": [
                    "string"
                ],
                "display_name": "string"
            }
        ],
        "error": {
            "message": "string",
            "type": "string",
            "code": 0
        }
    }

"""
