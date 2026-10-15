import os
import pandas as pd
from src.data_fetcher.downloader import descargar_datos_intradia
from config.settings import DATA_RAW_DIR


def main():
    print("=== INICIANDO SISTEMA QUANT ===\n")
    pd.set_option('display.float_format', lambda x: f'{x:.6f}')

    descargar_datos_intradia("2026-09-01", "2026-10-09")

if __name__ == "__main__":
    main()