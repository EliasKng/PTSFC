import ephem
from datetime import datetime
import pytz


def calculate_sun_hours(date_str, latitude=51.116557, longitude=9.658664):
    """
    Returns the sun-hours for a given Date. The lat&long are set to the centroid of the german population:
    Spangenberg, Hessen
    """
    # Convert date string to a datetime object
    date = datetime.strptime(date_str, '%Y-%m-%d')
    date_utc = pytz.utc.localize(date)

    # Set observer location
    observer = ephem.Observer()
    observer.lat = str(latitude)
    observer.lon = str(longitude)

    # Set date for calculation
    observer.date = date_utc

    # Compute sunrise and sunset
    sunrise = observer.previous_rising(ephem.Sun())  # Previous rising gives the sunrise of the given day
    sunset = observer.next_setting(ephem.Sun())  # Next setting gives the sunset of the given day

    # Calculate the duration of sunlight in hours
    daylight_hours = sunset - sunrise
    daylight_hours_in_seconds = daylight_hours * 86400  # Convert from days to seconds
    daylight_hours_float = daylight_hours_in_seconds / 3600  # Convert from seconds to hours

    if daylight_hours_float > 24:
        daylight_hours_float -= 24

    return daylight_hours_float
