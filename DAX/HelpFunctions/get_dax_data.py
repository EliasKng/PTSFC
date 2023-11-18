import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import timedelta, datetime
import seaborn as sns
import yfinance as yf


def get_dax_data():
    msft = yf.Ticker("^GDAXI")
    hist = msft.history(period="max")
    for i in range(5):
        hist["ret" + str(i + 1)] = compute_return(hist["Close"].values, h=i + 1)
    return hist


# by hand, runs faster
def compute_return(y, r_type="log", h=1):
    # exclude first h observations
    y2 = y[h:]
    # exclude last h observations
    y1 = y[:-h]

    if r_type == "log":
        ret = np.concatenate(([np.nan] * h, 100 * (np.log(y2) - np.log(y1))))
    else:
        ret = np.concatenate(([np.nan] * h, 100 * (y2 - y1) / y1))

    return ret
