from datetime import datetime
from dateutil import parser
import pytz

def parse_dt(text, tz_name="America/Los_Angeles"):
    tz = pytz.timezone(tz_name)
    dt = parser.parse(text, fuzzy=True)

    # If user entered no year, dateutil will choose current year; acceptable.
    # Ensure timezone-aware:
    if dt.tzinfo is None:
        dt = tz.localize(dt)
    else:
        dt = dt.astimezone(tz)

    return dt

def hours_until(dt, now=None):
    if now is None:
        now = datetime.now(dt.tzinfo)
    delta = dt - now
    return delta.total_seconds() / 3600

def requires_deposit(booking_type, booking_dt, incall_threshold_hours=6):
    # Outcalls always require deposit
    if booking_type == "outcall":
        return True

    # Incalls require deposit if booked >= threshold hours in advance
    h = hours_until(booking_dt)
    if booking_type == "incall" and h >= incall_threshold_hours:
        return True

    return False

def deposit_amount(duration_hours, per_hour=100):
    # duration_hours can be 1.5 etc.
    return int(round(duration_hours * per_hour))