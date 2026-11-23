import os
import time
from datetime import datetime, timezone
import pandas as pd
import requests
from config.settings import DATA_RAW_DIR

BINANCE_KLINES_URL = "https://api.binance.com/api/v3/klines"

TICKERS_CRYPTO = [
    "BTCUSDT",
    "LTCUSDT",
]

TIMEFRAMES = ["1d", "4h", "1h", "30m", "15m", "5m"]

TF_TO_MS = {
    "5m": 5 * 60 * 1000,
    "15m": 15 * 60 * 1000,
    "30m": 30 * 60 * 1000,
    "1h": 60 * 60 * 1000,
    "4h": 4 * 60 * 60 * 1000,
    "1d": 24 * 60 * 60 * 1000,
}

KLINE_COLUMNS = [
    "Open_time",
    "Open",
    "High",
    "Low",
    "Close",
    "Volume",
    "Close_time",
    "Quote_volume",
    "Count",
    "Taker_buy_base",
    "Taker_buy_quote",
    "Ignore",
]


def fecha_a_ms(fecha_str):
    """Convierte 'YYYY-MM-DD' a timestamp Unix en milisegundos UTC."""
    return int(pd.Timestamp(fecha_str, tz="UTC").timestamp() * 1000)


def _ahora_ms():
    return int(datetime.now(timezone.utc).timestamp() * 1000)


def pedir_klines_directo(symbol, interval, start_ms, end_ms):
    """Hace peticiones paginadas directamente al endpoint HTTP de Binance."""
    all_klines = []
    current_start = start_ms
    backoff = 1.0

    while current_start <= end_ms:
        params = {
            "symbol": symbol,
            "interval": interval,
            "startTime": current_start,
            "endTime": end_ms,
            "limit": 1000,
        }

        try:
            res = requests.get(BINANCE_KLINES_URL, params=params, timeout=10)
            if res.status_code in (429, 418):
                retry_after = float(res.headers.get("Retry-After", backoff))
                print(f"    [Rate limit {res.status_code}] Esperando {retry_after:.1f}s...")
                time.sleep(retry_after)
                backoff = min(backoff * 2, 30.0)
                continue

            res.raise_for_status()
            data = res.json()
            backoff = 1.0
        except Exception as e:
            print(f"    [Error de red] Reintentando en {backoff:.1f}s... ({e})")
            time.sleep(backoff)
            backoff = min(backoff * 2, 30.0)
            continue

        if not data:
            break

        all_klines.extend(data)

        last_open_time = data[-1][0]

        if len(data) < 1000 or last_open_time >= end_ms:
            break

        current_start = last_open_time + 1
        time.sleep(0.05)

    return all_klines


def _klines_a_df(klines, solo_cerradas=True):
    if not klines:
        return pd.DataFrame(columns=["Date", "Open", "High", "Low", "Close", "Volume"])

    df = pd.DataFrame(klines, columns=KLINE_COLUMNS)
    if solo_cerradas:
        ahora = _ahora_ms()
        df = df[df["Close_time"] <= ahora]

    if df.empty:
        return pd.DataFrame(columns=["Date", "Open", "High", "Low", "Close", "Volume"])

    df["Date"] = pd.to_datetime(df["Open_time"], unit="ms", utc=True)
    features = ["Open", "High", "Low", "Close", "Volume"]
    df[features] = df[features].astype(float)

    return (
        df[["Date"] + features]
        .sort_values("Date")
        .drop_duplicates(subset=["Date"], keep="last")
        .reset_index(drop=True)
    )


def descargar_datos_binance(fecha_inicio, fecha_fin):
    print("=" * 60)
    print("DOWNLOADER BINANCE DIRECTO (HTTP REST API)")
    print(f"RANGO SOLICITADO: {fecha_inicio} -> {fecha_fin}")
    print("=" * 60)

    os.makedirs(DATA_RAW_DIR, exist_ok=True)

    start_ms_global = fecha_a_ms(fecha_inicio)
    end_ms = fecha_a_ms(fecha_fin)

    dt_end = pd.Timestamp(fecha_fin, tz="UTC")
    dt_1y_ago = dt_end - pd.DateOffset(years=1)
    start_ms_1y = int(dt_1y_ago.timestamp() * 1000)

    for symbol in TICKERS_CRYPTO:
        for tf in TIMEFRAMES:
            if tf in ["1d", "4h"]:
                start_ms = start_ms_1y
                f_inicio_str = dt_1y_ago.strftime("%Y-%m-%d")
            else:
                start_ms = start_ms_global
                f_inicio_str = fecha_inicio

            print(
                f"Descargando {symbol} | TF: {tf} | {f_inicio_str} -> {fecha_fin}..."
            )

            klines = pedir_klines_directo(symbol, tf, start_ms, end_ms)
            df_final = _klines_a_df(klines, solo_cerradas=False)

            if df_final.empty:
                print(f"  -> [SIN DATOS] {symbol} ({tf})")
                continue

            output_file = os.path.join(DATA_RAW_DIR, f"{symbol}_{tf}.csv")
            df_final.to_csv(output_file, index=False)

            print(
                f"  -> OK: {len(df_final)} velas | Primera: {df_final['Date'].iloc[0]} | Última: {df_final['Date'].iloc[-1]}"
            )


def actualizar_datos_binance(symbols=None, timeframes=None, dias_inicial=7, solo_cerradas=True):
    """Actualiza incrementalmente los CSV existentes hasta el momento actual."""
    symbols = symbols or TICKERS_CRYPTO
    timeframes = timeframes or ["5m", "15m"]

    os.makedirs(DATA_RAW_DIR, exist_ok=True)
    fin_ms = _ahora_ms()

    for symbol in symbols:
        for tf in timeframes:
            output_file = os.path.join(DATA_RAW_DIR, f"{symbol}_{tf}.csv")
            tf_ms = TF_TO_MS.get(tf, 5 * 60 * 1000)

            if os.path.exists(output_file):
                df_prev = pd.read_csv(output_file)
                if not df_prev.empty and "Date" in df_prev.columns:
                    df_prev["Date"] = pd.to_datetime(df_prev["Date"], utc=True)
                    ultimo_ms = int(df_prev["Date"].iloc[-1].timestamp() * 1000)
                    inicio_ms = max(0, ultimo_ms - 3 * tf_ms)
                else:
                    df_prev = pd.DataFrame()
                    inicio_ms = fin_ms - dias_inicial * 24 * 60 * 60 * 1000
            else:
                df_prev = pd.DataFrame()
                inicio_ms = fin_ms - dias_inicial * 24 * 60 * 60 * 1000

            klines = pedir_klines_directo(symbol, tf, inicio_ms, fin_ms)
            df_new = _klines_a_df(klines, solo_cerradas=solo_cerradas)

            if df_prev.empty:
                df_combinado = df_new
            elif df_new.empty:
                df_combinado = df_prev
            else:
                df_combinado = (
                    pd.concat([df_prev, df_new], ignore_index=True)
                    .sort_values("Date")
                    .drop_duplicates(subset=["Date"], keep="last")
                    .reset_index(drop=True)
                )

            if not df_combinado.empty:
                df_combinado.to_csv(output_file, index=False)
                print(
                    f"[{symbol} | {tf}] Total: {len(df_combinado)} velas | "
                    f"Última: {df_combinado['Date'].iloc[-1]}"
                )


def vigilar_klines_binance(symbols=None, timeframes=None, intervalo_seg=15):
    """Mantiene actualizados los archivos de velas cerradas en bucle."""
    symbols = symbols or ["LTCUSDT"]
    timeframes = timeframes or ["5m", "15m"]

    print(f"Vigilando {symbols} {timeframes} cada {intervalo_seg}s (Ctrl+C para salir)...")
    while True:
        try:
            actualizar_datos_binance(
                symbols=symbols,
                timeframes=timeframes,
                solo_cerradas=True,
            )
        except KeyboardInterrupt:
            print("\nVigilancia detenida por el usuario.")
            break
        except Exception as e:
            print(f"[Error en loop] {e}")

        time.sleep(intervalo_seg)


if __name__ == "__main__":
    descargar_datos_binance(fecha_inicio="2026-07-10", fecha_fin="2026-08-08")