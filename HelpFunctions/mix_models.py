import numpy as np


def mix_models(models, weights, df, target):
    # Check that all weights sum to 1, otherwise normalize them
    total_weight = sum(weights)
    if total_weight != 1:
        weights = [w / total_weight for w in weights]

    model_forecasts, forecast_dates, horizons = _run_models(models, df)

    mixed_forecasts = np.zeros(model_forecasts[0].shape)
    for f, w in zip(model_forecasts, weights):
        mixed_forecasts += f * w
    mixed_forecasts['forecast_date'] = forecast_dates
    mixed_forecasts['horizon'] = horizons

    mixed_forecasts['target'] = [target for _ in range(len(mixed_forecasts))]
    mixed_forecasts = mixed_forecasts[
        ['forecast_date', 'target', 'horizon', 'q0.025', 'q0.25', 'q0.5', 'q0.75', 'q0.975']]


    return mixed_forecasts


# Now weights should contain a list of lists of weights per horizon e.g., for five horizons with two models:
# [ [ 1, 0.5, 0.5, 0.5, 0.5], [0, 0.5, 0.5, 0.5, 0.5]]
def mix_models_per_horizon(models, weights, df, target, offset_horizons = 0):
    weights, did_normalize = _normalize_columns(np.array(weights))
    if did_normalize:
        print("Used normalized weights instead:")
        print(weights)

    model_forecasts, forecast_dates, horizons = _run_models(models, df, offset_horizons)

    mixed_forecasts = np.zeros(model_forecasts[0].shape)
    for F, w in zip(model_forecasts, weights):
        mixed_forecasts += F * w[:, np.newaxis]
    mixed_forecasts['forecast_date'] = forecast_dates
    mixed_forecasts['horizon'] = horizons

    mixed_forecasts['target'] = [target for _ in range(len(mixed_forecasts))]
    mixed_forecasts = mixed_forecasts[
        ['forecast_date', 'target', 'horizon', 'q0.025', 'q0.25', 'q0.5', 'q0.75', 'q0.975']]

    return mixed_forecasts


def _run_models(models, df, offset_horizons = 0):
    forecast_dates = []
    model_forecasts = []
    horizons = []
    for m in models:
        if offset_horizons == 0:
            forecast = m(df)
        else:
            forecast = m(df, offset_horizons=offset_horizons)
        model_forecasts.append(forecast.loc[:, ['q0.025', 'q0.25', 'q0.5', 'q0.75', 'q0.975']])
        forecast_dates = forecast['forecast_date']
        horizons = forecast['horizon']
    return model_forecasts, forecast_dates, horizons


def _normalize_columns(array):
    normalized_weights = False
    # Iterate through each column
    for col_idx in range(array.shape[1]):
        col_sum = np.sum(array[:, col_idx])

        # Check if the sum is not equal to 1
        if not np.isclose(col_sum, 1.0):
            # Normalize the column values to make the sum 1
            array[:, col_idx] /= col_sum
            normalized_weights = True

    return array, normalized_weights
