import os


base_url = os.environ.get('HYPERTRACK_API_BASE_URL')
secret_key = os.environ.get('HYPERTRACK_SECRET_KEY')

DUMMY_CUSTOMER = {
    'phone': '+16502469293',
    'name': 'Tapan Pandita',
    'email': 'tapan@hypertrack.io',
}

DUMMY_DESTINATION = {
    'city': 'San Francisco',
    'country': 'US',
    'state': 'California',
    'address': '270 Linden Street',
    'customer_id': 'f3ead2ae-dc0a-4a7e-85be-74ee51d9d70a',
    'zip_code': '94102',
}

DUMMY_FLEET = {
    'name': 'San Francisco',
}

DUMMY_DRIVER = {
    'name': 'Tapan Pandita',
    'phone': '+16502469293',
    'vehicle_type': 'car',
}

DUMMY_HUB = {
    'city': 'San Francisco',
    'name': 'SF Financial District',
    'country': 'US',
    'state': 'California',
    'location': {
        'type': 'Point',
        'coordinates': [
            -122.402248,
            37.78929
        ]
    },
    'address': '1 Montgomery Street',
    'zip_code': '94104'
}

DUMMY_TASK = {
    'action': 'pickup',
    'hub_id': '26be07ec-a054-4506-9709-6d3ca3eb0df7',
    'order_id': 'abc123'
}

DUMMY_TRIP = {
    'tasks': [
        '77b9a3fa-a3ab-4840-aadb-cd33442ca45b'
    ],
    'start_location': {
        'type': 'Point',
        'coordinates': [
            -122.420044,
            37.774543
        ]
    },
    'driver_id': 'd0ae4912-2074-45ef-a7c0-76be58639ea9'
}

DUMMY_GPSLOG = {
    'bearing': 70,
    'trip_id': '41caa9f2-ad63-4a8b-98ed-1414c372e1ce',
    'altitude': 80,
    'location': {
        'type': 'Point',
        'coordinates': [
            -122.421196,
            37.773769
        ]
    },
    'recorded_at': '2016-03-09T07:13:05.026316Z',
    'speed': 7,
    'location_accuracy': 20.0
}

DUMMY_EVENT = {
}
