from sktime.forecasting.statsforecast import StatsForecastMSTL
from scipy.stats import norm
from datetime import timedelta
import pandas as pd


def mstl(df, offset_horizons=0):
    # Truncate to two years of training data
    start_date = max(df.index) - timedelta(days=365 * 2)
    df = df.loc[start_date:, :]

    model = StatsForecastMSTL(season_length=[24, 24 * 7])
    fitted_model = model.fit(y=df)

    y_pred = fitted_model.predict(fh=[i for i in range(1, 96)])

    # Define the indexes to take the values from
    indexes = [36, 40, 44, 60, 64, 68]
    indexes = [i + offset_horizons for i in indexes]

    # Reduce predictions to the relevant horizons
    y_pred = y_pred.iloc[indexes]

    forecasting_results = pd.DataFrame()
    for q in [0.025, 0.25, 0.5, 0.75, 0.975]:
        # mean & std-dev origin from distribution of past residuals
        quantile = norm.ppf(q, loc=-0.291818, scale=2.478695)
        forecasting_results[f'q{q}'] = y_pred + quantile

    forecasting_results = forecasting_results.reset_index(drop=False)
    forecasting_results = forecasting_results.rename(columns={"index": "forecast_date"})
    forecasting_results['horizon'] = ['36 hour', '40 hour', '44 hour', '60 hour', '64 hour', '68 hour']
    forecasting_results['target'] = ["energy" for _ in range(6)]
    forecasting_results = forecasting_results[
        ['forecast_date', 'target', 'horizon', 'q0.025', 'q0.25', 'q0.5', 'q0.75', 'q0.975']]

    print(forecasting_results)

    return None

