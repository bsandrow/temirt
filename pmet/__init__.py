import datetime
import sys

import requests
from lxml import etree

base_urls = {
    'arrivals': 'http://developer.trimet.org/ws/V1/arrivals',
}

layover_attributes = ['start','end']
arrival_attributes = ['block', 'departed', 'detour', 'dir', 'estimated', 'fullsign','locid','piece','route','scheduled', 'shortSign','status']
block_position_attributes = ['at','feet','heading','lat','lng']
trip_attributes = ['desc','destDist','dir','pattern','progress','route','tripNum']

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

class TrimetResult(dict):
    def __init__(self, content):
        dict.__init__(self)
        self._process_result(content)

    def _parse_arrival(self, element):
        arrival = dict((k, element.get(k)) for k in arrival_attributes)

        block_position_elements = element.xpath("./*[local-name()='blockPosition']")
        if block_position_elements:
            block_position_element = block_position_elements[0]
            if len(block_position_elements) > 1:
                raise TrimetParseError("Error: Too many <blockPosition> elements")

            block_position = dict((k, block_position_element.get(k)) for k in block_position_attributes)

            trip_elements = block_position_element.xpath("./*[local-name()='trip']")
            if trip_elements:
                block_position['trips'] = [
                    dict((k, trip_element.get(k)) for k in trip_attributes)
                    for trip_element in trip_elements
                ]

            layover_elements = block_position_element.xpath("./*[local-name()='layover']")
            if layover_elements:
                block_position['layovers'] = [
                    dict((k, layover_element.get(k)) for k in layover_attributes)
                    for layover_element in layover_elements
                ]

            arrival['block_position'] = block_position

        return arrival

    def _parse_error_message(self, tree):
        """ Parse out the <errorMessage> in the <resultSet>. """
        elements = tree.xpath("./*[local-name()='errorMessage']")
        if elements:
            if len(elements) > 1:
                raise TrimetParseError("Error: Too many <errorMessage> elements")
            else:
                self['error_message'] = elements[0].text()

    def _parse_query_time(self, tree):
        """ Parse out the queryTime attribute on the resultSet. """
        query_time_in_ms = float(tree.get('queryTime'))
        self['query_time'] = datetime.datetime.fromtimestamp(query_time_in_ms / 1000)

    def _parse_locations(self, tree):
        """ Parse out all of the <location> elements in the <resultSet> """
        self['locations'] = [ TrimetLocation(location) for location in tree.xpath("./*[local-name()='location']") ]

    def _process_result(self, content):
        tree = etree.fromstring(content)

        self._parse_query_time(tree)
        self._parse_error_message(tree)
        self._parse_locations(tree)

        arrival_elements = tree.xpath("./*[local-name()='arrival']")
        if arrival_elements:
            self['arrivals'] = [ self._parse_arrival(arrival_element)
                                    for arrival_element in arrival_elements ]

        route_status_elements = tree.xpath("./*[local-name()='routeStatus']")
        if route_status_elements:
            self['route-status'] = [
                    dict((k, route_status.get(k)) for k in ['route','status'])
                    for route_status in route_status_elements
                    ]

class TrimetApi(object):
    application_id = None

    def __init__(self, appid):
        self.application_id = appid

    def arrivals(self, location_ids):
        url = "%(baseurl)s?appID=%(appid)s&locIDs=%(locids)s" % {
                    'baseurl': base_urls['arrivals'],
                    'appid'  : self.application_id,
                    'locids' : ','.join(location_ids) }
        response = requests.get(url)
        if response.status_code == 200:
            return TrimetResult(response.content)
        else:
            raise TrimetHTTPError("HTTP Code: %d" % (response.status_code))

if __name__ == '__main__':
    api = TrimetApi()
    from pprint import pprint as PP
    PP(api.arrivals(['6849']))

    # with open('test-arrival.xml') as xmlfh:
    #     from pprint import pprint as PP
    #     PP(TrimetResult(xmlfh.read()))
