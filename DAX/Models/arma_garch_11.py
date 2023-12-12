import numpy as np
import pandas as pd
import rpy2
import rpy2.robjects as ro
import rpy2.robjects.pandas2ri as pandas2ri
from rpy2.robjects.conversion import localconverter

import rpy2.robjects.packages as rpackages
import rpy2.robjects as robjects

import rpy2.robjects.numpy2ri
from scipy.stats import t

from HelpFunctions.date_and_time import next_working_days


def arma_garch_11(df, deg_f = 3):
    quantiles = []

    for h in range(0, 5):
        y = df[f'ret{h + 1}'].dropna().to_numpy()
        forecast, sigma, mu = _arma_garch_11_one_horizon(y, deg_f)
        quantiles.append(_get_t_quantiles(sigma[h], mu[h], deg_f))

    column_names = [f'q{q}' for q in [0.025, 0.25, 0.5, 0.75, 0.975]]
    dates = next_working_days(max(df.index).date(), 5)
    horizon_column = [f'{h} day' for h in [1, 2, 5, 6, 7]]
    quantile_df = pd.DataFrame(quantiles, columns=column_names)
    quantile_df['forecast_date'] = dates
    quantile_df['horizon'] = horizon_column
    quantile_df['target'] = ["DAX" for _ in range(5)]
    quantile_df = quantile_df[
        ['forecast_date', 'target', 'horizon', 'q0.025', 'q0.25', 'q0.5', 'q0.75', 'q0.975']]

    return quantile_df


# Calculate forecast for one horizon
def _arma_garch_11_one_horizon(y, deg_f):
    rpy2.robjects.numpy2ri.activate()

    rugarch = rpackages.importr('rugarch')

    # GARCH(1,1)
    variance_model = robjects.ListVector({'model': "sGARCH",
                                          'garchOrder': robjects.IntVector([1, 1])})

    # ARMA(1,1)
    mean_model = robjects.ListVector({'armaOrder': robjects.IntVector([1, 1]),
                                      'include.mean': True})

    # defines the DoF for the t-Dist
    params = robjects.ListVector({'shape': deg_f})

    model = rugarch.ugarchspec(variance_model=variance_model,
                               mean_model=mean_model,
                               distribution_model="std",  # "std" -> student t, "norm" -> normal
                               fixed_pars=params)

    # In the following, I'm assuming that your timeseries is in a numpy array called "y"
    modelfit = rugarch.ugarchfit(spec=model,
                                 data=y,
                                 solver='hybrid',
                                 tol=1e-3)

    # historic mu and sigma
    sigma_hist = np.asarray(rugarch.sigma(modelfit))
    mu_hist = np.asarray(rugarch.fitted(modelfit))

    # 1-day ahead forecast mu and sigma
    forecast = rugarch.ugarchforecast(modelfit)
    sigma = np.asarray(rugarch.sigma(forecast))
    mu = np.asarray(rugarch.fitted(forecast))

    return forecast, sigma, mu


def _get_t_quantiles(sigma, mu, df_t):
    t_quantiles = t.ppf([0.025, 0.25, 0.5, 0.75, 0.975], df=df_t, loc=mu, scale=sigma)
    return t_quantiles
