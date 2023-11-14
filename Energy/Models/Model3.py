import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm
import sklearn
from math import sqrt
import holidays
from datetime import date

from Energy.HelpFunctions import import_csv_data
from Energy.HelpFunctions.get_energy_data import get_energy_data, prepare_data


def model3(energyconsumption):
    energyconsumption = energyconsumption.rename(columns={"gesamt": "energy_consumption"})

    energyconsumption = add_dummies(energyconsumption)

    model, y_ec, X_ec = fit_model(energyconsumption)

    # Calculate Forecasts
    # create new dataframe containing future date_times and indepentent variables

    last_ts = energyconsumption.index[-1]
    horizon = pd.date_range(start=last_ts + pd.DateOffset(
        hours=1), periods=200, freq='H')

    energy_forecast = pd.DataFrame({'date_time': horizon})
    energy_forecast.set_index('date_time', inplace=True)

    energy_forecast = add_dummies(energy_forecast)

    # Point forecasts
    X_fc = energy_forecast.drop(columns=['low_consumption_time'])
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

    indexes = [36, 40, 44, 60, 64, 68]

    forecasting_results = energy_forecast.iloc[indexes,
                          energy_forecast.columns.get_loc('q0.025'):energy_forecast.columns.get_loc('q0.975') + 1]

    forecasting_results = forecasting_results.reset_index(drop=False)
    forecasting_results = forecasting_results.rename(columns={"date_time": "forecast_date"})
    forecasting_results['horizon'] = ['36 hour', '40 hour', '44 hour', '60 hour', '64 hour', '68 hour']
    forecasting_results['target'] = ["energy" for _ in range(6)]

    return forecasting_results


def add_dummies(df):
    # Prepare df (add dummies)
    df['weekday'] = df.index.weekday
    df['hour'] = df.index.hour
    df['month'] = df.index.month
    df['timestamp'] = df.index

    holidays_de = holidays.DE()
    df['holiday'] = df['timestamp'].apply(
        lambda x: 1 if x in holidays_de else 0)

    # create winter/cold dummy variable
    df['winter'] = df['month'].apply(
        lambda x: 1 if x in [10, 11, 12, 1, 2, 3] else 0)

    # Define mapping of hours to timeframes (based on graph) and create dummy variable
    time_mapping = {
        'low_consumption_time': list(range(7)),  # differs a lot weekend/weekday
        'high_consumption_time': list(range(7, 20)),
        'transition_time': [6, 20, 21, 22, 23]}

    for timeframe, hours in time_mapping.items():
        df[timeframe] = df['hour'].apply(
            lambda x: 1 if x in hours else 0)

    # create weekend day dummy variable
    df['weekend_day'] = df['weekday'].apply(
        lambda x: 1 if x in [5, 6] else 0)

    # drop unneccesary columns
    df = df.drop(columns=['weekday', 'hour', 'month', 'timestamp'])
    return df


def fit_model(df):
    # Fit model*****
    y_ec = df['energy_consumption']
    X_ec = df.drop(
        columns=['energy_consumption', 'low_consumption_time'])  # low consumption time as reference time --> drop

    # add constant for the intercept term
    X_ec = sm.add_constant(X_ec)

    # fit seasonal linear regression model
    model = sm.OLS(y_ec, X_ec).fit()
    return model, y_ec, X_ec