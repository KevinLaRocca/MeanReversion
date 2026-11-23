import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def calcularBollingerBands(df, window=20, num_std=2.0):
    df = df.copy()
    mid = df["Close"].rolling(window=window).mean()
    std = df["Close"].rolling(window=window).std()
    df["bb_mid"] = mid
    df["bb_upper"] = mid + num_std * std
    df["bb_lower"] = mid - num_std * std
    return df


def calcularZScoreRetornos(df, window=20):
    df = df.copy()
    log_ret = np.log(df["Close"] / df["Close"].shift(1))
    mean_ret = log_ret.rolling(window=window).mean()
    std_ret = log_ret.rolling(window=window).std()
    df["zscore"] = np.where(std_ret > 0, (log_ret - mean_ret) / std_ret, 0.0)
    return df


def main():
    df = pd.read_csv("data/raw/LTCUSDT_5m.csv")
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], utc=True)

    df = calcularBollingerBands(df, window=20, num_std=2.0)
    df = calcularZScoreRetornos(df, window=20)

    umbral_z = 2.0
    cond_long = (df["zscore"] <= -umbral_z) & (df["Close"] <= df["bb_lower"])
    cond_short = (df["zscore"] >= umbral_z) & (df["Close"] >= df["bb_upper"])

    df["chance"] = 0
    df.loc[cond_long, "chance"] = 1
    df.loc[cond_short, "chance"] = -1

    chances = df[df["chance"] != 0]
    cols = [c for c in ["Date", "Close", "zscore", "bb_lower", "bb_mid", "bb_upper", "chance"] if c in df.columns]
    print(f"Total de chances: {len(chances)}")
    print(chances[cols].to_string(index=False))

    x = df["Date"] if "Date" in df.columns else df.index

    fig, (ax_top, ax_z) = plt.subplots(
        2, 1, figsize=(12, 7), sharex=True, gridspec_kw={"height_ratios": [3, 1.2]}
    )

    # Panel 1: Precio + Bollinger + Chances
    ax_top.plot(x, df["Close"], label="Close", linewidth=1.3)
    ax_top.plot(x, df["bb_mid"], label="BB Mid", linestyle="--", alpha=0.7)
    ax_top.plot(x, df["bb_upper"], label="BB Upper", linestyle=":", alpha=0.8)
    ax_top.plot(x, df["bb_lower"], label="BB Lower", linestyle=":", alpha=0.8)

    longs = df[df["chance"] == 1]
    shorts = df[df["chance"] == -1]
    ax_top.scatter(
        longs["Date"] if "Date" in df.columns else longs.index,
        longs["Close"],
        marker="^",
        color="green",
        label="Chance Long",
        zorder=5,
    )
    ax_top.scatter(
        shorts["Date"] if "Date" in df.columns else shorts.index,
        shorts["Close"],
        marker="v",
        color="red",
        label="Chance Short",
        zorder=5,
    )

    ax_top.set_title("Precio, Bollinger Bands y Z-Score")
    ax_top.legend(loc="best")
    ax_top.grid(True, alpha=0.3)

    # Panel 2: Z-Score
    ax_z.plot(x, df["zscore"], label="Z-Score (log ret)", color="purple", linewidth=1.1)
    ax_z.axhline(0, color="gray", linestyle="--", linewidth=0.8)
    ax_z.axhline(umbral_z, color="red", linestyle=":", linewidth=1.0, label=f"+{umbral_z}")
    ax_z.axhline(-umbral_z, color="green", linestyle=":", linewidth=1.0, label=f"-{umbral_z}")
    ax_z.set_ylabel("Z-Score")
    ax_z.legend(loc="best")
    ax_z.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()