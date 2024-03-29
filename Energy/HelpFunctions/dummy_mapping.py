from datetime import date

import holidays
import pandas as pd
import numpy as np

from Energy.HelpFunctions.sun_hours import SunHoursCalculator


def get_season_mapping(data_df):
    data_df.loc[:, 'month'] = data_df.index.month

    # define the mapping of months to seasons
    season_mapping = {
        'winter': [12, 1, 2],
        'spring': [3, 4, 5],
        'summer': [6, 7, 8],
        'autumn': [9, 10, 11]
    }

    # suppress copy warning
    pd.options.mode.chained_assignment = None

    # create season dummy variable
    for season, months in season_mapping.items():
        data_df.loc[:, season] = data_df['month'].apply(
            lambda x: 1 if x in months else 0)

    data_df = data_df.drop(columns=['month'])

    return (data_df)


def get_day_mapping(df):
    df['weekday'] = df.index.weekday
    # create weekend day dummy variable
    df['weekend_day'] = df['weekday'].apply(
        lambda x: 1 if x in [5, 6] else 0)
    df = df.drop(columns=['weekday'])
    return df


def get_day_mapping_detailed(df):
    df['weekday'] = df.index.weekday
    df['sturday'] = df['weekday'].apply(
        lambda x: 1 if x == 5 else 0)
    df['sunday'] = df['weekday'].apply(
        lambda x: 1 if x == 6 else 0)
    df = df.drop(columns=['weekday'])
    return df


def get_winter_dummy(df):
    df['month'] = df.index.month
    df['winter'] = df['month'].apply(
        lambda x: 1 if x in [10, 11, 12, 1, 2, 3] else 0)
    df = df.drop(columns=['month'])
    return df


def get_consumption_time_mapping_3_ways(df):
    df['hour'] = df.index.hour
    time_mapping = {
        'low_consumption_time': list(range(7)),  # differs a lot weekend/weekday
        'high_consumption_time': list(range(7, 20)),
        'transition_time': [6, 20, 21, 22, 23]}
    for timeframe, hours in time_mapping.items():
        df[timeframe] = df['hour'].apply(
            lambda x: 1 if x in hours else 0)
    # Drop Low consumption time, because knowledge about the other two accounts for that
    df = df.drop(columns=['hour', 'low_consumption_time'])

    return df

def get_consumption_time_mapping_4_ways(df):
    df['hour'] = df.index.hour
    time_mapping = {
        'low_consumption_time': list(range(6)),  # differs a lot weekend/weekday
        'high_consumption_time': list(range(7, 15)),
        'medium_high_consumption_time': [14, 15, 16, 17, 18],
        'transition_time': [6, 20, 21, 22, 23]}
    for timeframe, hours in time_mapping.items():
        df[timeframe] = df['hour'].apply(
            lambda x: 1 if x in hours else 0)
    # Drop Low consumption time, because knowledge about the other two accounts for that
    df = df.drop(columns=['hour', 'low_consumption_time'])

    return df


def get_hour_mapping(df):
    df['hour'] = df.index.hour

    for hour in range(24):
        df[f'hour: {hour}'] = df['hour'].apply(
            lambda x: 1 if x == hour else 0
        )
    df = df.drop(columns=['hour'])
    return df


def get_holiday_dummy(df):
    df['timestamp'] = df.index

    holidays_de = holidays.DE()
    df['holiday'] = df['timestamp'].apply(
        lambda x: 1 if x in holidays_de else 0)
    df = df.drop(columns=['timestamp'])
    return df


def get_holiday_dummy_advanced(df):
    """Diese Funktion bezieht jetzt auch noch Brückentage mit ein"""
    df['timestamp'] = df.index

    # holidays_de = holidays.DE()

    # Create a custom holidays object that includes 31-12 as a holiday
    years = [2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
    holidays_de = holidays.Germany(years=years)
    for y in years:
        holidays_de.append({date(y, 12, 31): "New Year's Eve"})

    # Mark actual holidays
    df['holiday'] = df['timestamp'].apply(lambda x: 1 if x in holidays_de else 0)

    # Identify bridge days (Monday)
    df['bridge_day_monday'] = df['timestamp'].apply(
        lambda x: 1 if x.weekday() == 0 and (x + pd.DateOffset(days=1)) in holidays_de else 0)

    # Identify bridge days (Friday)
    df['bridge_day_friday'] = df['timestamp'].apply(
        lambda x: 1 if x.weekday() == 4 and (x + pd.DateOffset(days=-1)) in holidays_de else 0)

    # Combine actual holidays and bridge days
    df['holiday'] = df['holiday'] | df['bridge_day_monday'] | df['bridge_day_friday']

    df = df.drop(columns=['timestamp', 'bridge_day_monday', 'bridge_day_friday'])
    return df


def get_population(df):
    df['year'] = df.index.year

    population_mapping = {
        2017: 82.792,
        2018: 83.019,
        2019: 83.167,
        2020: 83.155,
        2021: 83.237,
        2022: 84.359,
        2023: 84.61,
        2024: 84.70
    }
    df['population'] = df['year'].map(population_mapping)
    df = df.drop(columns=['year'])
    return df


def get_2022_mapping(df):
    df['year'] = df.index.year

    df['is2022'] = df['year'].apply(
        lambda x: 1 if x == 2022 else 0
    )

    df = df.drop(columns=['year'])
    return df


def get_sun_hours(df):
    df['sun_hours'] = [SunHoursCalculator.calculate_sun_hours(date.strftime('%Y-%m-%d')) for date in df.index]
    return df
