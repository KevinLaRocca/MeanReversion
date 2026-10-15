import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm
from config.settings import DATA_RAW_DIR

archivo_csv = os.path.join(DATA_RAW_DIR, "BCHUSDT_4h.csv")
archivo_csv_2 = os.path.join(DATA_RAW_DIR,"SOLUSDT_4h.csv")

def main():
    df = pd.read_csv(archivo_csv)

    columna_fecha = df.columns[0]
    df[columna_fecha] = pd.to_datetime(df[columna_fecha])

    df["Return"] = df["Close"].pct_change()
    df = df.dropna()

    print(df.tail())

    mean_return = np.mean(df["Return"])
    std_return = np.std(df["Return"])

    print(f"La media de retornos es: {mean_return:.5f}")
    print(f"Desviación estandar cada 4hs: {std_return:.5f}")

    plt.figure(figsize=(12, 5))
    plt.plot(df[columna_fecha], df["Return"])
    plt.title("BCHUSDT - Precio de cierre ajustado")
    plt.xlabel("Fecha")
    plt.ylabel("Precio en USD")
    plt.grid(True)
    plt.show()

    print("Distribución de retornos mediante histograma")
    plt.figure(figsize = (12, 5))
    plt.hist(df["Return"], bins = 50, density=True)
    plt.title("Histograma de retornos de 4h de BCHUSDT")
    plt.xlabel("Retorno")
    plt.ylabel("Frecuencia")
    plt.show()

def correlacion():
    dfbch = pd.read_csv(archivo_csv)
    dfbtc = pd.read_csv(archivo_csv_2)

    retornos_bch = dfbch["Close"].pct_change().dropna()
    retornos_btc = dfbtc["Close"].pct_change().dropna()

    min_len = min(len(retornos_bch), len(retornos_btc))
    retornos_bch = retornos_bch.iloc[-min_len:]
    retornos_btc = retornos_btc.iloc[-min_len:]

    matriz_correlacion = np.corrcoef(retornos_bch, retornos_btc)
    coeficiente_correlacion = matriz_correlacion[0, 1]

    print(f"Matriz de correlación:\n{matriz_correlacion}")
    print(
        f"\nCoeficiente de correlación de Pearson: {coeficiente_correlacion:.4f}"
    )

def producto():
    activos = ["BTCUSDT", "SOLUSDT", "LTCUSDT"]
    pesos = np.array([0.40, 0.35, 0.25])
    retornos_esperados = np.array([0.12, 0.15, 0.09])

    retorno_portafolio = np.dot(pesos, retornos_esperados)
    print(f"El retorno esperado de tu cartera es: {retorno_portafolio:.2%}")

    cov_matrix = np.array(
        [[0.0004, 0.0003, 0.0002], [0.0003, 0.0008, 0.0004], [0.0002, 0.0004, 0.0005]]
    )
    varianza_portafolio = np.dot(pesos.T, np.dot(cov_matrix, pesos))
    volatilidad_portafolio = np.sqrt(varianza_portafolio)

    print(f"Volatilidad de la cartera: {volatilidad_portafolio:.2%}")

def optimizacion():
    tiempo = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    precios = (tiempo - 5) ** 2 + 20

    plt.figure(figsize=(10, 6))
    plt.plot(tiempo, precios, marker='o', linestyle='-', color='b')
    
    plt.title("Evolución de Precios Teórica (Ejemplo de Optimización)")
    plt.xlabel("Unidades de Tiempo")
    plt.ylabel("Precio Teórico")
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.show()

def calcular_retornos_logaritmicos():
    dfbch = pd.read_csv(archivo_csv)
    dfbch["Return"] = dfbch["Close"].pct_change()
    dfbch["LogReturn"] = np.log(dfbch["Close"] / dfbch["Close"].shift(1))
    dfbch = dfbch.dropna()
    dfbch.head()


    plt.figure(figsize=(12,4))
    plt.plot(dfbch["Return"], label="Simple Return")
    plt.plot(dfbch["LogReturn"], label="Log Return")
    plt.title("Retornos de 4h de BCH")
    plt.xlabel("Fecha")
    plt.ylabel("Retorno")
    plt.legend()
    plt.grid(True)
    plt.show()

def volatilidad():
    df = pd.read_csv(archivo_csv)

    df["Return"] = df["Close"].pct_change()
    df = df.dropna()

    std_4h = df["Return"].std()
    volatilidad_anual = std_4h * np.sqrt(365 * 6)

    print(f"Desviación estándar (4h): {std_4h:.5f}")
    print(f"Volatilidad anualizada (365 días): {volatilidad_anual:.2%}")


#Comenzamos con movimiento browniano y browniano geometrico.
def movimiento_browniano():
    #Utilizamos datos desde el 10-05 al 31-07
    T = 1.0  # Tiempo total en años
    N = 1000  # Número de pasos
    dt = T / N  # Tamaño del paso de tiempo

    np.random.seed(42)
    W = np.zeros(N)
    for t in range(1, N):
        W[t] = W[t - 1] + np.sqrt(dt) * np.random.randn()

    plt.plot(W)
    plt.title("Movimiento Browniano Simulado")
    plt.xlabel("Tiempo")
    plt.ylabel("Posición")
    plt.grid()
    plt.show()

def movimiento_browniano_geometrico():
    S0 = 100  # Precio inicial
    mu = 0.05  # Tasa de retorno esperada
    sigma = 0.2  # Volatilidad
    T = 1.0  # Tiempo total en años
    N = 1000  # Número de pasos
    dt = T / N  # Tamaño del paso de tiempo
    S = np.zeros(N)
    S[0] = S0

    np.random.seed(42)
    for t in range(1, N):
        S[t] = S[t - 1] * np.exp((mu - 0.5 * sigma ** 2) * dt + sigma * np.sqrt(dt) * np.random.randn())

    plt.plot(S)
    plt.title("Movimiento Browniano Geométrico Simulado")
    plt.xlabel("Tiempo")
    plt.ylabel("Precio")
    plt.grid()
    plt.show()

def movimiento_browniano_geometrico_multiple():
    M = 1000
    S_matrix = np.zeros((1000, M))
    S_matrix[0] = 100

    for i in range(M):
        for t in range(1, 1000):
            S_matrix[t, i] = S_matrix[t - 1, i] * np.exp((0.05 - 0.5 * 0.2 ** 2) * (1 / 1000) + 0.2 * np.sqrt(1 / 1000) * np.random.randn())

    plt.plot(S_matrix)
    plt.title("Movimiento Browniano Geométrico Múltiple Simulado")
    plt.xlabel("Tiempo")
    plt.ylabel("Precio")
    plt.grid()
    plt.show()

#BLACK-SCHOLES: Pricing, Greeks and Delta-Hedging
 
def black_scholes(S, K, T, r, sigma, option_type="call"):
    print(f"Parámetros recibidos -> S: {S}, K: {K}, T: {T}, r: {r}, sigma: {sigma}, tipo: {option_type}")

    price = 0.0
    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)

    print(f"El valor de d1 y de d2, respectivamente, es: {d1:.2f}, {d2:.2f}")

    if option_type.lower() == "call":
        price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    elif option_type.lower() == "put":
        price = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)

    return price

#Montecarlo para calcular la tasa de éxito.
def evaluar_probabilidad_simple(precio_actual, meta_arriba, meta_abajo, volatilidad, sesgo_tendencia=0.0, semilla = 42):
    if semilla is not None:
        np.random.seed(semilla)

    pasos = 20
    simulaciones = 10000
    dt = 1

    movimiento = volatilidad * 0.2
    sesgo_total = movimiento * sesgo_tendencia
    shocks = np.random.randn(pasos, simulaciones)

    movimientos = np.exp(
        (sesgo_total - 0.5 * (volatilidad**2)) * dt
        + volatilidad * np.sqrt(dt) * shocks
    )

    caminos = np.zeros((pasos + 1, simulaciones))
    caminos[0] = precio_actual
    caminos[1:] = precio_actual * np.cumprod(movimientos, axis=0)

    tocos_arriba_primero = 0
    tocos_abajo_primero = 0

    for i in range(simulaciones):
        partida = caminos[:, i]

        paso_arriba = np.where(partida >= meta_arriba)[0]
        paso_abajo = np.where(partida <= meta_abajo)[0]

        turno_arriba = paso_arriba[0] if len(paso_arriba) > 0 else 999
        turno_abajo = paso_abajo[0] if len(paso_abajo) > 0 else 999

        if turno_arriba < turno_abajo:
            tocos_arriba_primero += 1
        elif turno_abajo < turno_arriba:
            tocos_abajo_primero += 1

    prob_arriba = (tocos_arriba_primero / simulaciones) * 100
    prob_abajo = (tocos_abajo_primero / simulaciones) * 100

    print(f"Probabilidad de tocar 103 primero: {prob_arriba:.1f}%")
    print(f"Probabilidad de tocar 98 primero: {prob_abajo:.1f}%")


if __name__ == "__main__":
    """main()
    correlacion()
    producto()
    optimizacion()
    calcular_retornos_logaritmicos()
    volatilidad()
    movimiento_browniano()
    movimiento_browniano_geometrico()"""
    
    #price = black_scholes(100, 105.0, 0.25, 0.05, 0.2, "call")
    #print(f"El precio es: {price:.4f}")
   #evaluar_probabilidad_simple(precio_actual=100, meta_arriba=102, meta_abajo=98, volatilidad=0.01, sesgo_tendencia = 1)
