import datetime

import pmet.utils

class Location(object):
    def __init__(self, loc_element):
        self.description       = loc_element.get('desc')
        self.latitude          = loc_element.get('lat')
        self.longitude         = loc_element.get('lng')
        self.traffic_direction = loc_element.get('dir')
        self.location_id       = loc_element.get('locid')

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "Location<%s,'%s',%s,%s,'%s'>" % (
                    self.location_id, self.description, self.latitude,
                    self.longitude, self.traffic_direction )

class Arrival(object):

    def __init__(self, element):
        self.block       = element.get('block')
        self.departed    = element.get('departed')
        self.detour      = element.get('detour')
        self.direction   = element.get('dir')
        self.fullsign    = element.get('fullSign')
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
            raise PmetParseError("Error: Too many <blockPosition> elements")
        self.block_position = BlockPosition(block_positions[0])

    def __repr__(self):
        return "Arrival<%s>" % (self.__str__())

    def __str__(self):
        d = dict(self.__dict__)
        return str(d)

class BlockPosition(object):
    def __init__(self, element):
        self.latitude  = element.get('lat')
        self.longitude = element.get('lng')
        self.heading   = element.get('heading')
        self.at        = element.get('at')
        self.feet      = element.get('feet')
        self.trips     = [ Trip(trip) for trip in element.xpath("./*[local-name()='trip']") ]
        self.layovers  = [ Layover(layover) for layover in element.xpath("./*[local-name()='layover']") ]

    def __str__(self):
        d = dict(self.__dict__)
        d['trips']    = [ trip.__str__() for trip in self.trips ]
        d['layovers'] = [ layover.__str__() for layover in self.layovers ]
        return str(d)

    def __repr__(self):
        return "BlockPosition<%s>" % self.__str__()

class Trip(object):
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
        return "Trip<%s>" % str(self.__dict__)

class Layover(object):
    def __init__(self, element):
        self.start = element.get('start')
        self.end   = element.get('end')

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return "Layover<%s>" % str(self.__dict__)

class RouteStatus(object):
    def __init__(self, element):
        self.route  = element.get('route')
        self.status = element.get('status')

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return "RouteStatus<%s>" % str(self.__dict__)

class Route(object):
    def __init__(self, element):
        self.decription = element.get('desc')
        self.route_id   = element.get('route')

        # B => Bus, R => Rail or Aerial Tram
        self.type = element.get('type')

    @property
    def is_bus(self):
        return self.type == 'B'

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return "%s<%s>" % (self.__class__.__name__, self.__str__())

class Detour(object):
    def __init__(self, element):
        self.begin = pmet.utils.get_datetime_from_milliseconds( element.get('begin') )
        self.end   = pmet.utils.get_datetime_from_milliseconds( element.get('end') )

        self.description = element.get('desc')
        self.detour_id   = element.get('id')
        self.phonetic    = element.get('phonetic')

        self.routes = [ Route(route) for route in element.xpath("./*[local-name()='route']") ]

    def __repr__(self):
        return "%s<%s>" % (self.__class__.__name__, self.__str__())

    def __str__(self):
        return str(self.__dict__)

