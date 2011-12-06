
import argparse
import datetime
import sys

import pmet

def process_args():
    parser = argparse.ArgumentParser(description='Access to trimet arrivals.')
    parser.add_argument('--api-key', metavar='APIKEY', type=str, action='store',
                        help='Provide an API key to use when accessing the Trimet'
                        ' web service.')
    parser.add_argument('-s','--stop-id', metavar='STOP_ID', type=int, action='store',
                        help='A stop id to fetch arrivals for')
    options = parser.parse_args()
    return options, parser

def get_scheduled_date(scheduled_time):
    today = datetime.datetime.today()
    if today.day != scheduled_time.day:
        return scheduled_time.strftime("%H:%M, %Y/%m/%d")
    else:
        return scheduled_time.strftime("%H:%M")

def get_estimated_duration(estimated_time):
    now = datetime.datetime.now()
    duration = estimated_time - now
    minutes = duration.seconds / 60
    return "%d minutes" % minutes

def run():
    options, parser = process_args()

    api = pmet.Api(options.api_key)

    result = api.arrivals([ options.stop_id ])

    if 'query_time' in result:
        print "[data as of: %s]" % result['query_time'].strftime('%a, %B %d %Y, %H:%M')
    else:
        print "[data as of: <unavailable>]"

    print "\nArrivals (Stop ID: %s):" % options.stop_id
    for arrival in result['arrivals']:
        if arrival.status == 'estimated':
            print " %2.2s minutes  (scheduled at %s) -- %s" % (
                    get_estimated_duration(arrival.estimated_arrival).strip(),
                    get_scheduled_date(arrival.scheduled_arrival),
                    arrival.fullsign
                    )
        else:
            print " %2.2s minutes* (scheduled at %s) -- %s" % (
                    get_estimated_duration(arrival.scheduled_arrival).strip(),
                    get_scheduled_date(arrival.scheduled_arrival),
                    arrival.fullsign
                    )


    print "\n * calculated from scheduled time, no estimated available."

if __name__ == '__main__':
    try:
        run()
    except KeyboardInterrupt:
        sys.exit(">> User Interrupt <<")
