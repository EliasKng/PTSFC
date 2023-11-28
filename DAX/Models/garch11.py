import pandas as pd
from arch import arch_model
from scipy.stats import norm
import math
from HelpFunctions.date_and_time import next_working_days


# Runs GARCH(1,1) for each horizon
def garch11(df):
    variances = [garch11_one_horizon(df[f'ret{h}'], h) for h in range(1 ,6)]
    quantiles = [get_norm_quantiles(v) for v in variances]
    column_names = [f'q{q}' for q in [0.025 ,0.25 ,0.5 ,0.75 ,0.975]]
    dates = next_working_days(max(df.index).date(), 5)
    horizon_column = [f'{h} day' for h in [1,2,5,6,7]]

    quantile_df = pd.DataFrame(quantiles, columns=column_names)
    quantile_df['forecast_date'] = dates
    quantile_df['horizon'] = horizon_column
    quantile_df['target'] = ["DAX" for _ in range(5)]
    # quantile_df.set_index('forecast_date', inplace=True)

    quantile_df = quantile_df[
        ['forecast_date', 'target', 'horizon', 'q0.025', 'q0.25', 'q0.5', 'q0.75', 'q0.975']]

    return quantile_df


# df should only contain one column (the log-returns of the horizon to predict)
def garch11_one_horizon(df, horizon):
    train = df.dropna()
    model = arch_model(train, mean='zero', p=1, q=1)
    model_fit = model.fit(disp='off')
    predictions = model_fit.forecast(horizon=horizon)
    return predictions.variance.values[0][-1]


def get_norm_quantiles(variance):
    return norm.ppf([0.025 ,0.25 ,0.5 ,0.75 ,0.975], loc=0, scale=math.sqrt(variance))