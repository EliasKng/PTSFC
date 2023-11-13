import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm
import sklearn
from math import sqrt

from Energy.HelpFunctions import import_csv_data
from Energy.HelpFunctions.get_energy_data import get_energy_data, prepare_data


def model1(energyconsumption):
    energyconsumption = energyconsumption.rename(columns={"gesamt": "energy_consumption"})

    # Prepare df (add dummies)
    energyconsumption['weekday'] = energyconsumption.index.weekday
    energyconsumption['hour'] = energyconsumption.index.hour
    energyconsumption['month'] = energyconsumption.index.month

    # create winter/cold dummy variable
    energyconsumption['winter'] = energyconsumption['month'].apply(
        lambda x: 1 if x in [10, 11, 12, 1, 2, 3] else 0)

    # Define mapping of hours to timeframes (based on graph) and create dummy variable
    time_mapping = {
        'low_consumption_time': list(range(7)),  # differs a lot weekend/weekday
        'high_consumption_time': list(range(7, 20)),
        'transition_time': [6, 20, 21, 22, 23]}

    for timeframe, hours in time_mapping.items():
        energyconsumption[timeframe] = energyconsumption['hour'].apply(
            lambda x: 1 if x in hours else 0)

    # create weekend day dummy variable
    energyconsumption['weekend_day'] = energyconsumption['weekday'].apply(
        lambda x: 1 if x in [5, 6] else 0)

    # drop unneccesary columns
    energyconsumption = energyconsumption.drop(columns=['weekday', 'hour', 'month'])

    # Fit model*****
    y_ec = energyconsumption['energy_consumption']
    X_ec = energyconsumption.drop(
        columns=['energy_consumption', 'low_consumption_time'])  # low consumption time as reference time --> drop

    # add constant for the intercept term
    X_ec = sm.add_constant(X_ec)

    # fit seasonal linear regression model
    model = sm.OLS(y_ec, X_ec).fit()
    model.summary()

    # Calculate Forecasts
    # create new dataframe containing future date_times and indepentent variables

    last_ts = energyconsumption.index[-1]
    horizon = pd.date_range(start=last_ts + pd.DateOffset(
        hours=1), periods=200, freq='H')

    energy_forecast = pd.DataFrame({'date_time': horizon})
    energy_forecast.set_index('date_time', inplace=True)

    energy_forecast['weekday'] = energy_forecast.index.weekday
    energy_forecast['hour'] = energy_forecast.index.hour
    energy_forecast['month'] = energy_forecast.index.month

    # create winter/cold dummy variable
    energy_forecast['winter'] = energy_forecast['month'].apply(
        lambda x: 1 if x in [10, 11, 12, 1, 2, 3] else 0)

    # time mapping already initialized
    for timeframe, hours in time_mapping.items():
        energy_forecast[timeframe] = energy_forecast['hour'].apply(
            lambda x: 1 if x in hours else 0)

    # create weekend day dummy variable
    energy_forecast['weekend_day'] = energy_forecast['weekday'].apply(
        lambda x: 1 if x in [5, 6] else 0)

    # Point forecasts
    X_fc = energy_forecast.drop(columns=['weekday', 'hour', 'month', 'low_consumption_time'])
    X_fc = sm.add_constant(X_fc, has_constant='add')

    # Make predictions
    predictions_ec = model.predict(X_fc)

    # Quantile Regression
    quantiles = [0.025, 0.25, 0.5, 0.75, 0.975]

    model_qr = sm.QuantReg(y_ec, X_ec)

    for q in quantiles:
        model_temp = model_qr.fit(q=q)

        # Calculate forecasts for X_fc using the fitted model for the current quantile
        forecast_temp = model_temp.predict(X_fc)

        # Add the forecasts to the energy_forecast DataFrame with a label like 'forecast025'
        energy_forecast[f'q{q}'] = forecast_temp

    # Format Results
    # Define the specific date and time combinations
    # selected_dates = ['2023-11-14 12:00:00', '2023-11-14 16:00:00', '2023-11-14 20:00:00',
    #                   '2023-11-15 12:00:00', '2023-11-15 16:00:00', '2023-11-15 20:00:00']

    indexes = [28, 32, 36, 52, 56, 60]

    forecasting_results = energy_forecast.iloc[indexes,
                          energy_forecast.columns.get_loc('q0.025'):energy_forecast.columns.get_loc('q0.975') + 1]

    forecasting_results = forecasting_results.reset_index(drop=False)
    forecasting_results = forecasting_results.rename(columns={"date_time": "forecast_date"})

    return forecasting_results
