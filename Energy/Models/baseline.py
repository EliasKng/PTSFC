import pandas as pd
import numpy as np
from datetime import datetime, date
import matplotlib.pyplot as plt
import seaborn as sns


# Expected a prepared df (date, gesamt). Calculates the baseline-predictions for the next [36, 40, 44, 60, 64, 68]h
# Offtest the data by LAST_IDX
def baseline(df, LAST_IDX=-1, offset_horizons=0):
    horizons_def = [36, 40, 44, 60, 64, 68]  # [24 + 12*i for i in range(5)]
    horizons = [h + 1 + offset_horizons for h in horizons_def]
    LAST_DATE = df.iloc[LAST_IDX].name
    horizon_date = [get_date_from_horizon(LAST_DATE, h) for h in horizons]
    tau = [.025, .25, .5, .75, .975]
    pred_baseline = np.zeros((6, 5))
    last_t = 100
    df["weekday"] = df.index.weekday  # Monday=0, Sunday=6
    for i, d in enumerate(horizon_date):
        weekday = d.weekday()
        hour = d.hour

        df_tmp = df.iloc[:LAST_IDX]

        cond = (df_tmp.weekday == weekday) & (df_tmp.index.time == d.time())

        pred_baseline[i, :] = np.quantile(df_tmp[cond].iloc[-last_t:]["gesamt"], q=tau)

    df_sub = pd.DataFrame({
        "forecast_date": horizon_date,
        "target": "energy",
        "horizon": [str(h) + " hour" for h in horizons_def],
        "q0.025": pred_baseline[:, 0],
        "q0.25": pred_baseline[:, 1],
        "q0.5": pred_baseline[:, 2],
        "q0.75": pred_baseline[:, 3],
        "q0.975": pred_baseline[:, 4]})
    return df_sub


def get_date_from_horizon(last_ts, horizon):
    return last_ts + pd.DateOffset(hours=horizon)
