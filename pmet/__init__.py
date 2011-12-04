import datetime
import sys

import requests
from lxml import etree

base_urls = {
    'arrivals': 'http://developer.trimet.org/ws/V1/arrivals',
}

class TrimetParseError(Exception):
    pass

class TrimetHTTPError(Exception):
    pass

class TrimetLocation(object):
    def __init__(self, loc_element):
        self.description       = loc_element.get('desc')
        self.latitude          = loc_element.get('lat')
        self.longitude         = loc_element.get('lng')
        self.traffic_direction = loc_element.get('dir')
        self.location_id       = loc_element.get('locid')

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "TrimetLocation<%s,'%s',%s,%s,'%s'>" % (
                    self.location_id, self.description, self.latitude,
                    self.longitude, self.traffic_direction )

class TrimetArrival(object):

    def __init__(self, element):
        self.block       = element.get('block')
        self.departed    = element.get('departed')
        self.detour      = element.get('detour')
        self.direction   = element.get('dir')
        self.fullsign    = element.get('fullsign')
        self.shortsign   = element.get('shortSign')
        self.location_id = element.get('location_id')
        self.piece       = element.get('piece')
        self.route_number= element.get('route')
        self.status      = element.get('status')

        self.scheduled_arrival = element.get('scheduled')
        if self.scheduled_arrival:
            self.scheduled_arrival = datetime.datetime.fromtimestamp( float(self.scheduled_arrival) / 1000 )

        self.estimated_arrival = element.get('estimated')
        if self.estimated_arrival:
            self.estimated_arrival = datetime.datetime.fromtimestamp( float(self.estimated_arrival) / 1000 )

        block_positions = element.xpath("./*[local-name()='blockPosition']")
        if len(block_positions) > 1:
            raise TrimetParseError("Error: Too many <blockPosition> elements")
        self.block_position = TrimetBlockPosition(block_positions[0])

    def __repr__(self):
        return "TrimetArrival<%s>" % (self.__str__())

    def __str__(self):
        d = dict(self.__dict__)
        return str(d)

class TrimetBlockPosition(object):
    def __init__(self, element):
        self.latitude  = element.get('lat')
        self.longitude = element.get('lng')
        self.heading   = element.get('heading')
        self.at        = element.get('at')
        self.feet      = element.get('feet')
        self.trips     = [ TrimetTrip(trip) for trip in element.xpath("./*[local-name()='trip']") ]
        self.layovers  = [ TrimetLayover(layover) for layover in element.xpath("./*[local-name()='layover']") ]

    def __str__(self):
        d = dict(self.__dict__)
        d['trips']    = [ trip.__str__() for trip in self.trips ]
        d['layovers'] = [ layover.__str__() for layover in self.layovers ]
        return str(d)

    def __repr__(self):
        return "TrimetBlockPosition<%s>" % self.__str__()

class TrimetTrip(object):
    def __init__(self, element):
        self.description = element.get('desc')
        self.destination_distance = element.get('destDist')
        self.direction = element.get('dir')
        self.pattern = element.get('pattern')
        self.progress = element.get('progress')
        self.route = element.get('route')
        self.trip_number = element.get('tripNum')

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return "TrimetTrip<%s>" % str(self.__dict__)

class TrimetLayover(object):
    def __init__(self, element):
        self.start = element.get('start')
        self.end   = element.get('end')

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return "TrimetLayover<%s>" % str(self.__dict__)

class TrimetRouteStatus(object):
    def __init__(self, element):
        self.route  = element.get('route')
        self.status = element.get('status')

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return "TrimetRouteStatus<%s>" % str(self.__dict__)

class TrimetResult(dict):
    def __init__(self, content):
        dict.__init__(self)
        self._process_result(content)

    def _parse_error_message(self, tree):
        """ Parse out the <errorMessage> in the <resultSet>. """
        elements = tree.xpath("./*[local-name()='errorMessage']")
        if elements:
            if len(elements) > 1:
                raise TrimetParseError("Error: Too many <errorMessage> elements")
            else:
                self['error_message'] = elements[0].text

    def _parse_query_time(self, tree):
        """ Parse out the queryTime attribute on the resultSet. """
        query_time_in_ms = tree.get('queryTime')
        if query_time_in_ms:
            self['query_time'] = datetime.datetime.fromtimestamp( float(query_time_in_ms) / 1000)
        else:
            self['query_time'] = None

    def _process_result(self, content):
        tree = etree.fromstring(content)

        self._parse_query_time(tree)
        self._parse_error_message(tree)

        self['locations']      = [ TrimetLocation(location) for location in tree.xpath("./*[local-name()='location']") ]
        self['arrivals']       = [ TrimetArrival(arrival) for arrival in tree.xpath("./*[local-name()='arrival']") ]
        self['route_statuses'] = [ TrimetRouteStatus(route_status) for route_status in tree.xpath("./*[local-name()='routeStatus']") ]

class TrimetApi(object):
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
            return TrimetResult(response.content)
        else:
            raise TrimetHTTPError("HTTP Code: %d" % (response.status_code))

if __name__ == '__main__':
    api = TrimetApi('YOUR_API_KEY_HERE')
    from pprint import pprint as PP
    PP(api.arrivals(['6849']))

    # with open('test-arrival.xml') as xmlfh:
    #     from pprint import pprint as PP
    #     PP(TrimetResult(xmlfh.read()))
