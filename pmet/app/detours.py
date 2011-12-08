
import argparse
import datetime
import sys
import textwrap

import pmet

def process_args():
    parser = argparse.ArgumentParser(description='Access to trimet arrivals.')
    parser.add_argument('--api-key', metavar='APIKEY', type=str, action='store',
                        help='Provide an API key to use when accessing the Trimet'
                        ' web service.')
    parser.add_argument('-r','--route-id', metavar='ROUTE_ID', type=int, action='store',
                        nargs='+', help='Filter the results to only detours affecting these routes')
    options = parser.parse_args()
    return options, parser

def format_route(route):
    return "%s" % (route.route_id if route.is_bus else route.description)

def format_detour(detour):
    routes = ', '.join(format_route(route) for route in detour.routes)
    desc   = '\n             '.join(textwrap.wrap(detour.description, 80))
    return ( "TIME       : %s to %s\n" % (detour.begin, detour.end)
           + "ROUTES     : %s\n" % routes
           + "DESCRIPTION: %s\n" % desc )

def run():
    options, parser = process_args()

    pmet.api.application_id = options.api_key
    result = pmet.api.detours(options.route_id or [])

    if 'error_message' in result:
        sys.exit("Error: %s" % result['error_message'])

    print ('--' * 20 + "\n").join(format_detour(detour) for detour in result['detours'])

if __name__ == '__main__':
    try:
        run()
    except KeyboardInterrupt:
        sys.exit(">> User Interrupt <<")
