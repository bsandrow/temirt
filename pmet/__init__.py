import datetime
import sys

import requests

import pmet.results
from pmet.errors import PmetHTTPError, PmetParseError

base_urls = {
    'arrivals': 'http://developer.trimet.org/ws/V1/arrivals',
    'detours' : 'http://developer.trimet.org/ws/V1/detours',
}

class Api(object):
    application_id = None

    def __init__(self, appid):
        self.application_id = appid

    def _build_url(self, key, params):
        params['appID'] = self.application_id

        query_params = []
        for k,v in params.iteritems():
            if type(v) == list:
                query_params += [ (k,value) for value in v ]
            else:
                query_params.append((k,v))

        query_string = '&'.join([ '='.join(kvpair) for kvpair in query_params ])

        return "%s?%s" % (base_urls[key], query_string)

    def arrivals(self, location_ids):
        params = { 'locIDs': ','.join(location_ids) }
        url = self._build_url('arrivals', params)

        response = requests.get(url)
        if response.status_code == 200:
            return pmet.results.ArrivalsResult(response.content)
        else:
            raise PmetHTTPError("HTTP Code: %d" % (response.status_code))

    def detours(self, routes):
        params = { 'routes': ','.join(routes) }
        url = self._build_url('detours', params)

        response = requests.get(url)
        if response.status_code == 200:
            return pmet.results.DetoursResult(response.content)
        else:
            raise PmetHTTPError("HTTP Code: %d" % (response.status_code))

if __name__ == '__main__':
    # api = TrimetApi('YOUR_API_KEY_HERE')
    # from pprint import pprint as PP
    # PP(api.arrivals(['6849']))

    # with open('test-arrival.xml') as xmlfh:
    #     from pprint import pprint as PP
    #     PP(TrimetResult(xmlfh.read()))

    api = TrimetApi('YOUR_API_KEY_HERE')
    from pprint import pprint as PP
    PP(api.detours(['44']))
