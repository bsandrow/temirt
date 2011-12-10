import datetime
import sys

import requests

import temirt.results
from temirt.errors import TemirtHTTPError, TemirtParseError

application_id = None
base_urls      = {
    'arrivals': 'http://developer.trimet.org/ws/V1/arrivals',
    'detours' : 'http://developer.trimet.org/ws/V1/detours',
}

def _build_url(key, params):
    params['appID'] = application_id

    query_params = []
    for k,v in params.iteritems():
        if type(v) == list:
            query_params += [ (k,value) for value in v ]
        else:
            query_params.append((k,v))

    query_string = '&'.join([ '='.join(kvpair) for kvpair in query_params ])

    return "%s?%s" % (base_urls[key], query_string)

def arrivals(location_ids):
    params = { 'locIDs': ','.join(str(locid) for locid in location_ids) }
    url = _build_url('arrivals', params)

    response = requests.get(url)
    if response.status_code == 200:
        return temirt.results.ArrivalsResult(response.content)
    else:
        raise TemirtHTTPError("HTTP Code: %d" % (response.status_code))

def detours(routes):
    params = { 'routes': ','.join(str(route) for route in routes) }
    url = _build_url('detours', params)

    response = requests.get(url)
    if response.status_code == 200:
        return temirt.results.DetoursResult(response.content)
    else:
        raise TemirtHTTPError("HTTP Code: %d" % (response.status_code))

