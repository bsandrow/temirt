pmet
====

A Python library for interfacing with the [Trimet][1] [web api][2].

Note: An ApplicationID key is necessary to use the web API. This can be
obtained [here][3].

Other than the examples here, the submodules under `pmet.app.*` are good usage
examples in actual code.

Arrivals
========

    import pmet

    pmet.api.application_id = 'YOUR_API_KEY_HERE'
    result = pmet.api.arrivals([ 10577 ]) # Mt. Hood Ave MAX Stop

    # There should only be one location because the query only contained one
    # stop id.
    location = result['locations'][0]
    print "Stop %s: %s" % (location.location_id, location.description)

    for arrival in result['arrivals']:
        print "Route %s arriving at %s (%s)" % (arrival.route_number, result.estimated_arrival, result.status)
        # Note: When result.status = 'scehduled' (i.e. no estimated available),
        #       estimated_arrival seems to be equal to scheduled_arrival

Detours
=======

    import pmet

    pmet.api.application_id = 'YOUR_API_KEY_HERE'
    result = pmet.api.detours([ 77 ]) # Only detours affecting Route 77

    for detour in result['detours']:
        print "Detour: %s" % detour.description
        print "  -- starts at %s" % detour.begin
        print "  -- ends at %s" % detour.end

Notes
=====

I would have named the project pymet, as it is the named that jumps off the
paper, but there already is a project named [PyMET][4], which looks like an
abandoned attempt to do the same thing.

Credits
=======

Copyright 2011 Brandon Sandrowicz <brandon@sandrowicz.org>

See LICENSE file.

[1]: http://trimet.org
[2]: http://developer.trimet.org/ws_docs/
[3]: http://developer.trimet.org/registration/
[4]: https://github.com/dcolish/PyMET
