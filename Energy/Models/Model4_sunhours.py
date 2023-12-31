import pandas as pd
import statsmodels.api as sm

from Energy.HelpFunctions.dummy_mapping import get_winter_dummy, get_day_mapping, \
    get_holiday_dummy, get_population, get_day_mapping_detailed, get_hour_mapping, get_2022_mapping, \
    get_consumption_time_mapping_4_ways, get_sun_hours


def model4_sunhours(energyconsumption, offset_horizons=0):
    energyconsumption = energyconsumption.rename(columns={"gesamt": "energy_consumption"})

    energyconsumption = add_dummies(energyconsumption)

    y_ec = energyconsumption['energy_consumption']
    X_ec = energyconsumption.drop(columns=['energy_consumption'])


    # add constant for the intercept term
    X_ec = sm.add_constant(X_ec)

    # Calculate Forecasts
    # create new dataframe containing future date_times and indepentent variables

    last_ts = energyconsumption.index[-1]
    horizon = pd.date_range(start=last_ts + pd.DateOffset(
        hours=1), periods=200, freq='H')

    energy_forecast = pd.DataFrame({'date_time': horizon})
    energy_forecast.set_index('date_time', inplace=True)

    energy_forecast = add_dummies(energy_forecast)

    # Point forecasts
    X_fc = energy_forecast
    X_fc = sm.add_constant(X_fc, has_constant='add')

    # Quantile Regression
    quantiles = [0.025, 0.25, 0.5, 0.75, 0.975]

    model_qr = sm.QuantReg(y_ec, X_ec)
    # fit = model_qr.fit(q=0.5)
    # print(fit.summary())

    for q in quantiles:
        model_temp = model_qr.fit(q=q)

        # Calculate forecasts for X_fc using the fitted model for the current quantile
        forecast_temp = model_temp.predict(X_fc)

        # Add the forecasts to the energy_forecast DataFrame with a label like 'forecast025'
        energy_forecast[f'q{q}'] = forecast_temp

    indexes = [36, 40, 44, 60, 64, 68]
    indexes = [i + offset_horizons for i in indexes]

    forecasting_results = energy_forecast.iloc[indexes,
                          energy_forecast.columns.get_loc('q0.025'):energy_forecast.columns.get_loc('q0.975') + 1]

    forecasting_results = forecasting_results.reset_index(drop=False)
    forecasting_results = forecasting_results.rename(columns={"date_time": "forecast_date"})
    forecasting_results['horizon'] = ['36 hour', '40 hour', '44 hour', '60 hour', '64 hour', '68 hour']
    forecasting_results['target'] = ["energy" for _ in range(6)]
    forecasting_results = forecasting_results[
        ['forecast_date', 'target', 'horizon', 'q0.025', 'q0.25', 'q0.5', 'q0.75', 'q0.975']]

    return forecasting_results


def add_dummies(df):
    df = get_winter_dummy(df)
    df = get_consumption_time_mapping_4_ways(df)
    df = get_day_mapping(df)
    df = get_holiday_dummy(df)
    df = get_sun_hours(df)
    # df = get_population(df)

    return df
