import pmet.api as api

if __name__ == '__main__':
    import os
    api.application_id = os.environ['TRIMET_API_KEY']

    # from pprint import pprint as PP
    # PP(api.arrivals(['6849']))

    from pprint import pprint as PP
    PP(api.detours(['44']))
