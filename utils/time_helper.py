from datetime import datetime
import pytz


def utc_now():
    # add time zone "utc" to it
    return datetime.now().replace(tzinfo=pytz.utc)