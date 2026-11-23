import numpy as np
import matplotlib.pyplot as plt

def simular_trading(capital_inicial=5000, n_trades=100, n_simulaciones=150, p=0.5, win_pago=0.8, riesgo_pct=0.02):
    capitales = np.zeros((n_simulaciones, n_trades + 1))
    capitales[:, 0] = capital_inicial
    
    for t in range(1, n_trades + 1):
        exitos = np.random.binomial(1, p, n_simulaciones)
        monto_riesgo = capitales[:, t-1] * riesgo_pct
        cambio = np.where(exitos == 1, monto_riesgo * win_pago, -monto_riesgo)
        capitales[:, t] = capitales[:, t-1] + cambio
        capitales[:, t] = np.maximum(capitales[:, t], 0)
        
    return capitales

n_ops = 100
sims_negativo = simular_trading(n_trades=n_ops, p=0.40, win_pago=1.5)
sims_positivo = simular_trading(n_trades=n_ops, p=0.45, win_pago=1.5)

plt.figure(figsize=(12, 6))
plt.plot(np.mean(sims_negativo, axis=0), label='Escenario A: 40% Win | Pago 1.5 (EV Negativo)', color='red', linewidth=2)
plt.plot(np.mean(sims_positivo, axis=0), label='Escenario B: 60% Win | Pago 0.8 (EV Positivo)', color='green', linewidth=2)

plt.axhline(y=5000, color='gray', linestyle='--', alpha=0.7, label='Capital Inicial ($5,000 USD)')
plt.title('Simulación Monte Carlo: Evolución del Capital Promedio tras 100 Trades')
plt.xlabel('Número de Operaciones (Trades)')
plt.ylabel('Capital Promedio ($)')
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()