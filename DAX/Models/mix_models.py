import numpy as np


def mix_models(models, weights, df):
    # Check that all weights sum to 1, otherwise normalize them
    total_weight = sum(weights)
    if total_weight != 1:
        weights = [w / total_weight for w in weights]

    forecast_dates = []
    model_forecasts = []
    horizons = []
    for m in models:
        forecast = m(df)
        model_forecasts.append(forecast.loc[:, ['q0.025', 'q0.25', 'q0.5', 'q0.75', 'q0.975']])
        forecast_dates = forecast['forecast_date']
        horizons = forecast['horizon']

    mixed_forecasts = np.zeros(model_forecasts[0].shape)
    for f, w in zip(model_forecasts, weights):
        mixed_forecasts += f * w
    mixed_forecasts['forecast_date'] = forecast_dates
    mixed_forecasts['horizon'] = horizons
    mixed_forecasts = mixed_forecasts[['forecast_date', 'horizon', 'q0.025', 'q0.25', 'q0.5', 'q0.75', 'q0.975']]
    return mixed_forecasts