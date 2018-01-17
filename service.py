# -*- coding: utf-8 -*-

from json import loads as json_loads
from os import getenv

import urllib.parse
import urllib.request


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
        },
    ]

    for location in locations:
        if coordinates_in_bounding_box(latlng, location['latitude_bounds'], location['longitude_bounds']):
            return location['name']

    return None

def handler(event, context):
    headers = {
        'Authorization': 'Bearer {0}'.format(getenv('STRAVA_API_TOKEN'))
    }

    activities_endpoint = 'https://www.strava.com/api/v3/athlete/activities?per_page=1'

    req = urllib.request.Request(activities_endpoint, headers=headers)
    activity = json_loads(urllib.request.urlopen(req).read())[0]

    if activity['name'] not in ['Morning Ride', 'Afternoon Ride', 'Evening Ride']:
        print('No need to rename {0}, "{1}"'.format(activity['id'], activity['name']))
        return True

    start_location = get_location(activity['start_latlng'])
    end_location = get_location(activity['end_latlng'])

    if start_location == end_location:
        print('Activity {0} seems to be a loop'.format(activity['id']))
        return True

    if start_location and end_location:
        activity_url = 'https://www.strava.com/api/v3/activities/{0}'.format(activity['id'])
        activity_name = 'Commute from {0} to {1}'.format(start_location, end_location)
        data = urllib.parse.urlencode({
            'name': activity_name,
            'commute': 'true',
        })
        data = data.encode('ascii')
        req = urllib.request.Request(activity_url, headers=headers, data=data, method='PUT')
        response = urllib.request.urlopen(req).read()

        print('Commute {0} renamed to "{1}" successfully'.format(activity['id'], activity_name))
        return True

    print('No action taken for {0}'.format(activity['id']))
    return True
