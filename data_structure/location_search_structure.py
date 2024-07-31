"""
    INPUT PARAMS
    - key : The Partner API Key.
    - searchQuery : Text to use for searching based on the name of the location.
    
    OUTPUT FORMAT
    {
        "data": [
            {
                "location_id": 0,
                "name": "string",
                "distance": "string",
                "bearing": "string",
                "address_obj": {
                    "street1": "string",
                    "street2": "string",
                    "city": "string",
                    "state": "string",
                    "country": "string",
                    "postalcode": "string",
                    "address_string": "string",
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
    