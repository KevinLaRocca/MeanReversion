import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_RAW_DIR = os.path.join(BASE_DIR, 'data', 'raw')
OUTPUTS_DIR = os.path.join(BASE_DIR, 'outputs')
OUTPUTS_PLOTS_DIR = os.path.join(BASE_DIR, 'outputs', 'plots')
LOGS_DIR = os.path.join(BASE_DIR, 'logs')

for carpeta in [DATA_RAW_DIR, OUTPUTS_DIR, OUTPUTS_PLOTS_DIR, LOGS_DIR]:
    os.makedirs(carpeta, exist_ok=True)

SYMBOLS = ['BTC-USD', 'LTC-USD']

K_CLUSTERS = 3
RANDOM_STATE = 42