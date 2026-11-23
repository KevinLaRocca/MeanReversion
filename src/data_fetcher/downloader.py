# filepath: src/data_fetcher/downloader.py
import os
import yfinance as yf
import pandas as pd
from config.settings import TICKERS_TECH, DATA_RAW_DIR

def limpiar_yahoo(df):
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df = df.reset_index()
    return df

def descargar_datos_intradia():
    print("=" * 60)
    print("DATA FETCHER: EXTRAYENDO HISTÓRICOS INTRADÍA")
    print("=" * 60)
    
    fecha_ini = "2026-06-25"
    fecha_fin = "2026-07-24"
    
    for ticker in TICKERS_TECH:
        print(f"Descargando {ticker}...")

        data_1d = yf.download(ticker, interval='1d', period='2y')
        data_4h = yf.download(ticker, interval='4h', period='2y')
        data_1h = yf.download(ticker, start=fecha_ini, end=fecha_fin, interval='1h')
        data_30m = yf.download(ticker, start=fecha_ini, end=fecha_fin, interval='30m')
        data_15m = yf.download(ticker, start=fecha_ini, end=fecha_fin, interval='15m')
        data_5m = yf.download(ticker, start=fecha_ini, end=fecha_fin, interval='5m')

        data_1d = limpiar_yahoo(data_1d)
        data_4h = limpiar_yahoo(data_4h)
        data_1h = limpiar_yahoo(data_1h)
        data_30m = limpiar_yahoo(data_30m)
        data_15m = limpiar_yahoo(data_15m)
        data_5m = limpiar_yahoo(data_5m)

        data_1d.to_csv(os.path.join(DATA_RAW_DIR, f"{ticker}_1d.csv"), index=False)
        data_4h.to_csv(os.path.join(DATA_RAW_DIR, f"{ticker}_4h.csv"), index=False)
        data_1h.to_csv(os.path.join(DATA_RAW_DIR, f"{ticker}_1h.csv"), index=False)
        data_30m.to_csv(os.path.join(DATA_RAW_DIR, f"{ticker}_30m.csv"), index=False)
        data_15m.to_csv(os.path.join(DATA_RAW_DIR, f"{ticker}_15m.csv"), index=False)
        data_5m.to_csv(os.path.join(DATA_RAW_DIR, f"{ticker}_5m.csv"), index=False)

if __name__ == "__main__":
    descargar_datos_intradia()
