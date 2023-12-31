import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import timedelta, datetime
import seaborn as sns


def baseline_300(df):
    # quantile levels
    tau = [.025, .25, .5, .75, .975]

    # define prediction array
    # cols are quantile levels, rows are horizons
    pred_baseline = np.zeros((5, 5))

    last_t = 300

    for i in range(5):
        ret_str = "ret" + str(i + 1)

        pred_baseline[i, :] = np.quantile(df[ret_str].iloc[-last_t:], q=tau)

    return create_submission_df(df, pred_baseline)


# Returns the five next working days as string
def get_forecast_dates(most_recent_date):
    working_days = []
    current_date = most_recent_date

    while len(working_days) < 5:
        # Increment the current date by one day
        current_date += timedelta(days=1)

        # Check if the current date is a working day (Monday to Friday)
        if current_date.weekday() < 5:
            working_days.append(current_date.date().strftime('%Y-%m-%d'))

    return working_days

def create_submission_df(df, pred_baseline):
    df_sub = pd.DataFrame({
        "forecast_date": get_forecast_dates(max(df.index)),
        "target": "DAX",
        "horizon": [str(i) + " day" for i in (1, 2, 5, 6, 7)],
        "q0.025": pred_baseline[:, 0],
        "q0.25": pred_baseline[:, 1],
        "q0.5": pred_baseline[:, 2],
        "q0.75": pred_baseline[:, 3],
        "q0.975": pred_baseline[:, 4]})
    return df_sub