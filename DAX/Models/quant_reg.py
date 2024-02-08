import pandas as pd
from datetime import timedelta, datetime
from DAX.HelpFunctions.get_dax_data import get_dax_data
import numpy as np
from HelpFunctions.date_and_time import most_recent_thursday
from HelpFunctions.date_and_time import next_working_days

import pandas as pd
import statsmodels.api as sm


def quant_reg_1d(df):
    return quant_reg(df, rolling_vol_days=1)


def quant_reg_3d(df):
    return quant_reg(df, rolling_vol_days=3)


def quant_reg_5d(df):
    return quant_reg(df, rolling_vol_days=5)


def quant_reg_10d(df):
    return quant_reg(df, rolling_vol_days=10)



def quant_reg(df, rolling_vol_days = 3):
    df = df[-1000:]
    df = df[['ret1', 'ret2', 'ret3', 'ret4', 'ret5']]
    df = df.dropna()
    df['volatility'] = _rolling_ret_volatility(df['ret1'], rolling_vol_days)

    horizons = np.arange(1, 6)

    forecasts = []
    for horizon in horizons:
        ret = df[f'ret{horizon}']
        vol = df['volatility']
        forecasts.append(_quant_reg_one_horizon(ret, vol, horizon))
    forecasts = pd.concat(forecasts)

    forecasts['horizon'] = [str(i) + " day" for i in (1, 2, 5, 6, 7)]
    return forecasts


def _quant_reg_one_horizon(ret, vol, horizon):
    df = pd.DataFrame()
    df['ret'] = ret
    df['volatility'] = vol

    y = df['ret']
    X = df.drop(columns=['ret'])
    X = sm.add_constant(X)

    last_ts = df.index[-1]
    fc_date = next_working_days(last_ts, num_days=5)[horizon - 1]

    print_horizon = (datetime.strptime(fc_date, '%Y-%m-%d')
                     - last_ts.replace(tzinfo=None)).days

    forecast = pd.DataFrame({'date_time': [fc_date]})
    forecast.set_index('date_time', inplace=True)

    forecast['volatility'] = df.loc[:, 'volatility'].iloc[-1]

    X_fc = forecast
    X_fc = sm.add_constant(X_fc, has_constant='add')

    quantiles = [0.025, 0.25, 0.5, 0.75, 0.975]
    model_qr = sm.QuantReg(y, X)

    for q in quantiles:
        model_temp = model_qr.fit(q=q)
        forecast_temp = model_temp.predict(X_fc)
        forecast[f'q{q}'] = forecast_temp

    fc_results = forecast.iloc[:,
                 forecast.columns.get_loc('q0.025'):forecast.columns.get_loc('q0.975') + 1]

    fc_results = fc_results.reset_index(drop=False)
    fc_results = fc_results.rename(columns={"date_time": "forecast_date"})
    fc_results['horizon'] = f'{print_horizon} day'
    fc_results['target'] = "DAX"
    fc_results = fc_results[
        ['forecast_date', 'target', 'horizon', 'q0.025', 'q0.25', 'q0.5', 'q0.75', 'q0.975']]
    return fc_results


def _rolling_ret_volatility(ret, days):
    volatility_measure = []
    for i in range(len(ret)):
        start_index = max(0, i - days + 1)
        end_index = i + 1

        vol = ret.iloc[start_index:end_index].abs().sum()

        volatility_measure.append(vol)
    return volatility_measure
