import pandas as pd
import statsmodels.api as sm
from Energy.HelpFunctions.get_energy_data import get_energy_data, prepare_data
from Energy.HelpFunctions.date_and_time import most_recent_thursday

def model2(df):
    df = df.rename(columns={"gesamt": "energy_consumption"})

    # Prepare df (add dummies)
    df['weekday'] = df.index.weekday
    df['hour'] = df.index.hour
    df['month'] = df.index.month

    # create winter/cold dummy variable
    df['winter'] = df['month'].apply(
        lambda x: 1 if x in [10, 11, 12, 1, 2, 3] else 0)

    df['working_day'] = df['weekday'].apply(
        lambda x: 1 if x <= 4 else 0
    )

    df['saturday'] = df['weekday'].apply(
        lambda x: 1 if x == 5 else 0
    )

    df['sunday'] = df['weekday'].apply(
        lambda x: 1 if x == 6 else 0
    )

    for hour in range(12):
        df[f'hour {hour}'] = df['hour'].apply(
            lambda x: 1 if x == hour else 0
        )

    # drop unneccesary columns
    df = df.drop(columns=['weekday', 'hour', 'month'])

    # Fit model*****
    y_ec = df['energy_consumption']
    X_ec = df.drop(
        columns=['energy_consumption'])  # low consumption time as reference time --> drop

    # Those stay: ['winter', 'working_day', 'saturday', 'sunday',
    #    'hour 0', 'hour 1', 'hour 2', 'hour 3', 'hour 4', 'hour 5', 'hour 6',
    #    'hour 7', 'hour 8', 'hour 9', 'hour 10', 'hour 11']

    # add constant for the intercept term
    X_ec = sm.add_constant(X_ec)

    # fit seasonal linear regression model
    model = sm.OLS(y_ec, X_ec).fit()
    model.summary()

    # Calculate Forecasts
    # create new dataframe containing future date_times and indepentent variables

    last_ts = df.index[-1]
    horizon = pd.date_range(start=last_ts + pd.DateOffset(
        hours=1), periods=200, freq='H')

    energy_forecast = pd.DataFrame({'date_time': horizon})
    energy_forecast.set_index('date_time', inplace=True)

    energy_forecast['weekday'] = energy_forecast.index.weekday
    energy_forecast['hour'] = energy_forecast.index.hour
    energy_forecast['month'] = energy_forecast.index.month

    # create winter dummy variable
    energy_forecast['winter'] = energy_forecast['month'].apply(
        lambda x: 1 if x in [10, 11, 12, 1, 2, 3] else 0)

    energy_forecast['working_day'] = energy_forecast['weekday'].apply(
        lambda x: 1 if x <= 4 else 0
    )

    energy_forecast['saturday'] = energy_forecast['weekday'].apply(
        lambda x: 1 if x == 5 else 0
    )

    energy_forecast['sunday'] = energy_forecast['weekday'].apply(
        lambda x: 1 if x == 6 else 0
    )

    for hour in range(12):
        energy_forecast[f'hour {hour}'] = energy_forecast['hour'].apply(
            lambda x: 1 if x == hour else 0
        )

    # Point forecasts
    X_fc = energy_forecast.drop(columns=['weekday', 'hour', 'month'])
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

    indexes = [36, 40, 44, 60, 64, 68]

    forecasting_results = energy_forecast.iloc[indexes,
                          energy_forecast.columns.get_loc('q0.025'):energy_forecast.columns.get_loc('q0.975') + 1]

    forecasting_results = forecasting_results.reset_index(drop=False)
    forecasting_results = forecasting_results.rename(columns={"date_time": "forecast_date"})
    forecasting_results['horizon'] = ['36 hour', '40 hour', '44 hour', '60 hour', '64 hour', '68 hour']
    forecasting_results['target'] = ["energy" for _ in range(6)]

    return forecasting_results
