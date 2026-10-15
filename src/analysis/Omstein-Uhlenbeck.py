
import glob
import os

import numpy as np
import pandas as pd
import statsmodels.api as sm

from config.settings import DATA_RAW_DIR


def estimate_ou(series, dt=1.0):
    x = np.asarray(series, dtype=float)
    x = x[np.isfinite(x)]

    if len(x) < 30:
        return None

    x_prev = x[:-1]
    x_next = x[1:]

    model = sm.OLS(
        x_next,
        sm.add_constant(x_prev)
    ).fit()

    a, b = model.params

    if not 0 < b < 1:
        return {
            "theta": np.nan,
            "mu": np.nan,
            "sigma": np.nan,
            "half_life": np.inf,
            "r_squared": model.rsquared,
            "mean_reverting": False,
        }

    theta = -np.log(b) / dt
    mu = a / (1 - b)

    residual_var = np.mean(model.resid**2)
    sigma = np.sqrt(
        residual_var * 2 * theta / (1 - b**2)
    )

    return {
        "theta": theta,
        "mu": mu,
        "sigma": sigma,
        "half_life": np.log(2) / theta,
        "r_squared": model.rsquared,
        "mean_reverting": True,
    }


pattern = os.path.join(DATA_RAW_DIR, "*_4h.csv")
files = glob.glob(pattern)

results = []

for filepath in files:
    ticker = os.path.basename(filepath).replace(".csv", "")

    df = pd.read_csv(filepath)

    if "Close" not in df.columns:
        print(f"{ticker}: falta la columna Close")
        continue

    prices = pd.to_numeric(df["Close"], errors="coerce")
    prices = prices.dropna()

    if len(prices) < 30:
        print(f"{ticker}: datos insuficientes")
        continue

    # Serie inicial para probar el estimador.
    # Luego podemos reemplazarla por la desviación
    # respecto del VWAP móvil.
    result = estimate_ou(prices)

    if result is None:
        continue

    results.append({
        "ticker": ticker,
        "observations": len(prices),
        **result,
    })

if results:
    report = pd.DataFrame(results)
    print(report.to_string(index=False))
else:
    print("No se pudieron estimar modelos OU.")
