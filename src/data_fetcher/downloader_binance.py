# filepath: src/data_fetcher/downloader_binance.py
import os
import pandas as pd
from binance.client import Client
from config.settings import DATA_RAW_DIR

def descargar_datos_binance():
    print("=" * 60)
    print("DATA FETCHER: EXTRAYENDO HISTÓRICOS DESDE PYTHON-BINANCE")
    print("=" * 60)
    
    client = Client()
    
    TICKERS_CRYPTO = ["BTCUSDT", "ETHUSDT", "LTCUSDT", "SOLUSDT", "BNBUSDT"]
    
    # Definir los intervalos a descargar con sus nombres
    TIMEFRAMES = [
        ("1d", Client.KLINE_INTERVAL_1DAY, "6 months ago UTC"),
        ("1h", Client.KLINE_INTERVAL_1HOUR, "1 months ago UTC"),
        ("30m", Client.KLINE_INTERVAL_30MINUTE, "10 days ago UTC"),
        ("4h", Client.KLINE_INTERVAL_4HOUR, "15 days ago UTC"),
    ]
    
    for symbol in TICKERS_CRYPTO:
        for timeframe_name, kline_interval, lookback in TIMEFRAMES:
            print(f"Descargando {symbol} desde Binance ({timeframe_name})...")
            try:
                klines = client.get_historical_klines(
                    symbol, 
                    kline_interval, 
                    lookback
                )
                
                if not klines:
                    print(f"  -> Sin datos para {symbol} ({timeframe_name})")
                    continue
                    
                df = pd.DataFrame(klines, columns=[
                    'Open_time', 'Open', 'High', 'Low', 'Close', 'Volume',
                    'Close_time', 'Quote_volume', 'Count', 'Taker_buy_base', 'Taker_buy_quote', 'Ignore'
                ])
                
                df['Datetime'] = pd.to_datetime(df['Open_time'], unit='ms')
                df.set_index('Datetime', inplace=True)
                
                features_precio = ['Open', 'High', 'Low', 'Close', 'Volume']
                df = df[features_precio].astype(float)
                
                output_path = os.path.join(DATA_RAW_DIR, f"{symbol}_{timeframe_name}_historical.csv")
                df.to_csv(output_path)
                print(f"  -> {len(df)} velas registradas en: {output_path}")
                
            except Exception as e:
                print(f"  -> Error con {symbol} ({timeframe_name}): {str(e)}")

if __name__ == "__main__":
    descargar_datos_binance()