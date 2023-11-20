import pandas as pd
from arch import arch_model
from scipy.stats import norm, t
import math
from HelpFunctions.date_and_time import next_working_days


# Runs GARCH(1,1) for each horizon with t-distribution
def garch11_t(df):
    nus = [garch11_t_one_horizon(df[f'ret{h}'],h) for h in range(1, 6)]
    quantiles = [get_t_quantiles(n) for n in nus]
    column_names = [f'q{q}' for q in [0.025, 0.25, 0.5, 0.75, 0.975]]
    dates = next_working_days(max(df.index).date(), 5)
    horizon_column = [f'{h} day' for h in [1, 2, 5, 6, 7]]

    quantile_df = pd.DataFrame(quantiles, columns=column_names)
    quantile_df['forecast_date'] = dates
    quantile_df['horizon'] = horizon_column
    return quantile_df


# df should only contain one column (the log-returns of the horizon to predict)
def garch11_t_one_horizon(df, horizon):
    train = df.dropna()
    model = arch_model(train, mean='zero', dist='studentst', p=1, q=1)
    model_fit = model.fit(disp='off')
    # print(f'Horizon: {horizon}: nu: {model_fit.params["nu"]}')
    return model_fit.params['nu']  # return the nu value of the t-distribution


def get_norm_quantiles(variance):
    return norm.ppf([0.025, 0.25, 0.5, 0.75, 0.975], loc=0, scale=math.sqrt(variance))


def get_t_quantiles(nu):
    return t.ppf([0.025, 0.25, 0.5, 0.75, 0.975], df=nu, loc=0, scale=1)