import ephem
from datetime import datetime
import pytz

class SunHoursCalculator:
    latitude = 51.116557  # Default latitude for Spangenberg, Hessen
    longitude = 9.658664  # Default longitude for Spangenberg, Hessen
    cached_results = {}  # Dictionary to store cached results

    @staticmethod
    def calculate_sun_hours(date_str):
        # Check if the result is already cached
        if date_str in SunHoursCalculator.cached_results:
            return SunHoursCalculator.cached_results[date_str]

        # Convert date string to a datetime object
        date = datetime.strptime(date_str, '%Y-%m-%d')
        date_utc = pytz.utc.localize(date)

        # Set observer location
        observer = ephem.Observer()
        observer.lat = str(SunHoursCalculator.latitude)
        observer.lon = str(SunHoursCalculator.longitude)

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

        # Cache the result
        SunHoursCalculator.cached_results[date_str] = daylight_hours_float

        return daylight_hours_float

