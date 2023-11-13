from datetime import datetime, timedelta

def most_recent_thursday(df):
    today = df.index.max()
    days_to_thursday = (today.weekday() - 3) % 7  # Calculate days to the most recent Thursday
    recent_thursday = today - timedelta(days=days_to_thursday, hours=today.hour, minutes=today.minute,
                                        seconds=today.second, microseconds=today.microsecond)

    # Set the time to 12:00 AM
    most_recent_thursday = recent_thursday.replace(hour=0, minute=0, second=0, microsecond=0)

    return most_recent_thursday