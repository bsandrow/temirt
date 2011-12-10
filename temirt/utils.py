import datetime

def get_datetime_from_milliseconds(timestamp_in_ms):
    if timestamp_in_ms:
        return datetime.datetime.fromtimestamp( float(timestamp_in_ms) / 1000 )
    else:
        return None
