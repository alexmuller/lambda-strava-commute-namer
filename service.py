# -*- coding: utf-8 -*-

import json

from urllib.parse import urlencode
from urllib.request import Request, urlopen

from os import getenv


def coordinates_in_bounding_box(coords, latitude_bounds, longitude_bounds):
    return all([
        latitude_bounds[0] < coords[0] < latitude_bounds[1],
        longitude_bounds[0] < coords[1] < longitude_bounds[1],
    ])

def get_location(latlng):
    locations = [
        {
            'name': 'Chiswick',
            'latitude_bounds': (51.488, 51.492),
            'longitude_bounds': (-0.273, -0.265),
        }, {
            'name': 'Putney',
            'latitude_bounds': (51.454, 51.458),
            'longitude_bounds': (-0.227, -0.219),
        }, {
            'name': 'Victoria',
            'latitude_bounds': (51.496, 51.500),
            'longitude_bounds': (-0.145, -0.134),
        }, {
            'name': 'Soho',
            'latitude_bounds': (51.511, 51.515),
            'longitude_bounds': (-0.142, -0.135),
        }, {
            'name': 'Broadcasting House',
            'latitude_bounds': (51.516, 51.522),
            'longitude_bounds': (-0.148, -0.138),
        },
    ]

    for location in locations:
        if coordinates_in_bounding_box(latlng, location['latitude_bounds'], location['longitude_bounds']):
            return location['name']

    return None

def build_response(status, body_json):
    return {
        "statusCode": status,
        "headers": {"Content-type": "application/json"},
        "body": json.dumps(body_json)
    }

def lambda_handler(event, context):
    headers = {
        'Authorization': 'Bearer {0}'.format(getenv('STRAVA_API_TOKEN'))
    }

    if event['httpMethod'] == 'GET':
        challenge = event['queryStringParameters']['hub.challenge']
        return build_response(200, {'hub.challenge': challenge})

    if event['httpMethod'] == 'POST':
        post_data = json.loads(event['body'])

        if post_data['object_type'] != 'activity':
            return build_response(200, {'message': 'Not an activity, no action taken'})

        if post_data['aspect_type'] != 'create':
            return build_response(200, {'message': 'Not an activity creation, no action taken'})

        new_activity_id = post_data['object_id']
        activity_url = 'https://www.strava.com/api/v3/activities/{0}'.format(new_activity_id)
        req = Request(activity_url, headers=headers)
        activity = json.loads(urlopen(req).read())

        if activity['name'] not in ['Morning Ride', 'Afternoon Ride', 'Evening Ride']:
            return build_response(200, {
                'message': 'No need to rename {0}, "{1}"'.format(activity['id'], activity['name'])
            })

        start_location = get_location(activity['start_latlng'])
        end_location = get_location(activity['end_latlng'])

        if start_location == end_location:
            return build_response(200, {
                'message': 'Activity {0} seems to be a loop'.format(activity['id'])
            })

        if start_location and end_location:
            activity_name = 'Commute from {0} to {1}'.format(start_location, end_location)
            data = urlencode({
                'name': activity_name,
                'commute': 'true',
            })
            data = data.encode('ascii')
            req = Request(activity_url, headers=headers, data=data, method='PUT')
            response = urlopen(req).read()

            return build_response(200, {
                'message': 'Commute {0} renamed to "{1}" successfully'.format(activity['id'], activity_name)
            })

        return build_response(200, {
            'message': 'No action taken for {0}'.format(activity['id']),
            'data': post_data
        })

    return build_response(400, {'message': 'Unknown method'})
