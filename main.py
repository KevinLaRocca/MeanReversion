import pandas as pd
from src.data_fetcher.downloader_binance import (
    descargar_datos_binance,
    vigilar_klines_binance,
)


def main():
    print("=== INICIANDO SISTEMA QUANT ===\n")
    pd.set_option("display.float_format", lambda x: f"{x:.6f}")
    vigilar_klines_binance(symbols=["LTCUSDT"], timeframes=["5m", "15m"], intervalo_seg=15)


if __name__ == "__main__":
    main()