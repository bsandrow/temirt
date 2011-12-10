from lxml import etree

import temirt.utils
import temirt.elements
from temirt.errors import TemirtParseError

class BaseResult(dict):
    """The base class for handling <resultSet> responses from the Trimet API
    service. Subclasses can define the _process_result_xml() method to hook
    into initialization processing, and get passed the root ElementTree."""

    def __init__(self, content):
        """Initialize the result. If there is an <errorMessage> element, then
        don't bother to do anymore processing. """
        dict.__init__(self)
        tree = etree.fromstring(content)
        self._get_error_message(tree)
        if 'error_message' not in self:
            self._process_result_xml(tree)

    def _get_error_message(self, tree):
        error_messages = tree.xpath("./*[local-name()='errorMessage']")
        if error_messages:
            if len(error_messages) > 1:
                raise TemirtParseError("Error: Too many <errorMessage> elements")
            else:
                self['error_message'] = error_messages[0].text

    def _process_result_xml(self, tree):
        pass

class ArrivalsResult(BaseResult):
    def _process_result_xml(self, tree):
        self['query_time']     = temirt.utils.get_datetime_from_milliseconds( tree.get('queryTime') )
        self['locations']      = [ temirt.elements.Location(location) for location in tree.xpath("./*[local-name()='location']") ]
        self['arrivals']       = [ temirt.elements.Arrival(arrival) for arrival in tree.xpath("./*[local-name()='arrival']") ]
        self['route_statuses'] = [ temirt.elements.RouteStatus(route_status) for route_status in tree.xpath("./*[local-name()='routeStatus']") ]

class DetoursResult(BaseResult):
    def _process_result_xml(self, tree):
        self['detours'] = [ temirt.elements.Detour(detour) for detour in tree.xpath("./*[local-name()='detour']") ]
