# filepath: src/data_fetcher/downloader.py
from datetime import datetime, timedelta
import os
import pandas as pd
import yfinance as yf
from config.settings import DATA_RAW_DIR, TICKERS_TECH


def limpiar_yahoo(df):
    if df is None or df.empty:
        return pd.DataFrame()
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df = df.reset_index()

    # Normalizar columna temporal siempre a 'Date'
    if "Datetime" in df.columns:
        df = df.rename(columns={"Datetime": "Date"})
    elif "Date" not in df.columns and len(df.columns) > 0:
        df = df.rename(columns={df.columns[0]: "Date"})

    return df


def ajustar_rango_intradia(fecha_inicio_str, max_dias):
    """
    Si hay fecha_inicio, valida que no supere max_dias atrás respecto a hoy.
    Si se pasa, la ajusta al límite dinámico permitido por Yahoo Finance.
    """
    if not fecha_inicio_str:
        return None

    dt_inicio = datetime.strptime(fecha_inicio_str, "%Y-%m-%d")
    dt_limite = datetime.now() - timedelta(days=max_dias)

    if dt_inicio < dt_limite:
        print(
            f"   [!] Ajustando fecha de inicio para este intervalo "
            f"a {dt_limite.strftime('%Y-%m-%d')} (máximo {max_dias} días)."
        )
        return dt_limite.strftime("%Y-%m-%d")

    return fecha_inicio_str


def descargar_datos_intradia(fecha_inicio=None, fecha_fin=None):
    print("=" * 60)
    print("DATA FETCHER: EJECUTANDO DESCARGA MULTI-TIMEFRAME")
    print("=" * 60)

    os.makedirs(DATA_RAW_DIR, exist_ok=True)

    for ticker in TICKERS_TECH:
        print(f"\nDescargando {ticker}...")

        # 1. 1d y 4h: Fijos a 1 año (Sin tocar)
        data_1d = yf.download(
            ticker, interval="1d", period="1y", prepost=False, progress=False
        )
        data_4h = yf.download(
            ticker, interval="4h", period="1y", prepost=False, progress=False
        )

        # 2. 1h: Rango dinámico (Máximo 725 días)
        start_1h = ajustar_rango_intradia(fecha_inicio, max_dias=725)
        if start_1h or fecha_fin:
            data_1h = yf.download(
                ticker, interval="1h", start=start_1h, end=fecha_fin, prepost=False, progress=False
            )
        else:
            data_1h = yf.download(
                ticker, interval="1h", period="725d", prepost=False, progress=False
            )

        # 3. 30m y 15m: Rango dinámico (Máximo 58 días)
        start_30m_15m = ajustar_rango_intradia(fecha_inicio, max_dias=58)
        if start_30m_15m or fecha_fin:
            data_30m = yf.download(
                ticker, interval="30m", start=start_30m_15m, end=fecha_fin, prepost=False, progress=False
            )
            data_15m = yf.download(
                ticker, interval="15m", start=start_30m_15m, end=fecha_fin, prepost=False, progress=False
            )
        else:
            data_30m = yf.download(
                ticker, interval="30m", period="58d", prepost=False, progress=False
            )
            data_15m = yf.download(
                ticker, interval="15m", period="58d", prepost=False, progress=False
            )

        # 4. 5m: Rango dinámico (Máximo 28 días)
        start_5m = ajustar_rango_intradia(fecha_inicio, max_dias=28)
        if start_5m or fecha_fin:
            data_5m = yf.download(
                ticker, interval="5m", start=start_5m, end=fecha_fin, prepost=False, progress=False
            )
        else:
            data_5m = yf.download(
                ticker, interval="5m", period="28d", prepost=False, progress=False
            )

        dict_datasets = {
            "1d": data_1d,
            "4h": data_4h,
            "1h": data_1h,
            #"30m": data_30m,
            #"15m": data_15m,
            #"5m": data_5m,
        }

        for tf, df in dict_datasets.items():
            df_clean = limpiar_yahoo(df)
            filename = f"{ticker}_{tf}.csv"
            filepath = os.path.join(DATA_RAW_DIR, filename)

            if not df_clean.empty and len(df_clean) > 0:
                df_clean.to_csv(filepath, index=False)
                print(f"   [+] {filename} -> Guardado ({len(df_clean)} filas)")
            else:
                print(f"   [!] {filename} -> Sin datos generados.")


if __name__ == "__main__":
    # Ejemplo de ejecución desde inicio hasta hoy respetando los límites
    descargar_datos_intradia(fecha_inicio="2024-01-01", fecha_fin="2026-10-08")