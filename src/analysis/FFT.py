import glob
import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from config.settings import DATA_RAW_DIR

# --- Parámetros y Timeframe ---
TIMEFRAME = "4h"

if TIMEFRAME == "1h":
    N, W, M = 64, 16, 7
    keep_fraction = 0.06
    file_pattern = "*1h.csv"
else:
    N, W, M = 256, 42, 6
    keep_fraction = 0.10
    file_pattern = "*4h.csv"

search_pattern = os.path.join(DATA_RAW_DIR, file_pattern)
file_list = glob.glob(search_pattern)

for file_path in file_list:
    ticker = os.path.basename(file_path).replace(".csv", "")
    data = pd.read_csv(file_path)

    # Carga de datos (Close y Volume)
    if "Close" in data.columns and "Volume" in data.columns:
        prices, volumes = data["Close"].values, data["Volume"].values
    else:
        prices, volumes = data.iloc[:, 4].values, data.iloc[:, 5].values

    if len(prices) < N:
        continue

    prices, volumes = prices[-N:], volumes[-N:]

    # 1. Rolling VWAP (Línea base)
    vwap = np.zeros(N)
    pv = prices * volumes

    for t in range(N):
        start_idx = max(0, t - W + 1)
        vol_sum = np.sum(volumes[start_idx : t + 1])
        vwap[t] = np.sum(pv[start_idx : t + 1]) / (vol_sum if vol_sum != 0 else 1e-8)

    # 2. Z-Score Móvil (Estacionarización de la serie)
    diff = prices - vwap
    z_score = np.zeros(N)

    for t in range(N):
        start_idx = max(0, t - W + 1)
        std_window = np.std(diff[start_idx : t + 1])
        z_score[t] = diff[t] / (std_window if std_window > 1e-8 else 1e-8)

    # 3. FFT y Filtrado por Potencia (Pasa-bajos)
    fft_coeffs = np.fft.fft(z_score)
    psd = np.abs(fft_coeffs) ** 2
    freqs = np.fft.fftfreq(N)

    threshold = np.percentile(psd[1 : N // 2], (1 - keep_fraction) * 100)

    fft_filtered = fft_coeffs.copy()
    fft_filtered[psd < threshold] = 0

    # 4. IDFT (Reconstrucción limpia)
    z_score_clean = np.real(np.fft.ifft(fft_filtered))

    # 5. Proyección Armónica Futura
    t_future = np.arange(N, N + M)
    idx_top = np.where(psd >= threshold)[0]

    z_score_future = np.zeros(M)
    for i in idx_top:
        amp = np.abs(fft_coeffs[i]) / N
        phase = np.angle(fft_coeffs[i])
        freq = freqs[i]
        z_score_future += amp * np.cos(2 * np.pi * freq * t_future + phase)

    # --- Gráficos ---
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

    ax1.plot(prices, label="Precio (Close)", color="#1f77b4", alpha=0.7)
    ax1.plot(vwap, label=f"Rolling VWAP ({W} p)", color="#ff7f0e", linewidth=1.8)
    ax1.set_title(f"Precio vs Rolling VWAP ({TIMEFRAME}) - {ticker}")
    ax1.set_ylabel("Precio")
    ax1.legend(loc="upper left")
    ax1.grid(True, linestyle="--", alpha=0.4)

    ax2.plot(z_score, label="Z-Score Raw", color="gray", alpha=0.35)
    ax2.plot(z_score_clean, label="Z-Score Suave (FFT)", color="#d62728", linewidth=1.8)
    ax2.plot(
        range(N, N + M),
        z_score_future,
        label=f"Proyección ({M} velas)",
        color="#2ca02c",
        linestyle="--",
        linewidth=2,
    )

    ax2.axhline(2, color="red", linestyle=":", alpha=0.7, label="+2σ")
    ax2.axhline(-2, color="green", linestyle=":", alpha=0.7, label="-2σ")
    ax2.axhline(0, color="black", linestyle="-", alpha=0.3)

    ax2.set_title("Oscilador Z-Score - Filtrado y Proyección Fourier")
    ax2.set_xlabel("Velas")
    ax2.set_ylabel("Desviación (σ)")
    ax2.legend(loc="upper left")
    ax2.grid(True, linestyle="--", alpha=0.4)

    plt.tight_layout()
    plt.show()