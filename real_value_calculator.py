import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from pandas_datareader import data as pdr
import datetime

"""
Este script analiza el rendimiento real de un activo financiero
ajustando su precio nominal por la inflación histórica de EE.UU. (CPI).

Permite visualizar cuánto del crecimiento de una acción es valor intrínseco 
y cuánto es simplemente depreciación de la moneda.
"""

# Configuración de los datos
ticker = "AAPL"
inicio = "2000-01-01"
# Obtenemos la fecha actual
fin = datetime.datetime.now().strftime('%Y-%m-%d')

# Descarga de datos del mercado
df_raw = yf.download(ticker, start=inicio, end=fin, auto_adjust=True)
df = pd.DataFrame(df_raw['Close']) 
df.columns = ['Close']

# Descarga de datos macroeconomicos
try:
    cpi_data = pdr.get_data_fred('CPIAUCSL', start=inicio, end=fin)
except Exception as e:
    print(f"Error al conectar con FRED: {e}")
    exit()

# Normalización de los datos
cpi_daily = cpi_data.reindex(df.index, method='ffill')

# Definimos el CPI base (el valor del dólar al inicio del periodo de estudio)
cpi_inicio = cpi_daily.iloc[0].values[0]
df['CPI'] = cpi_daily.iloc[:, 0]

# Cálculo del valor real
df['Real_Price'] = df['Close'] * (cpi_inicio / df['CPI'])

def calcular_retorno_real(df, dias_atras=None):
    """
    Calcula el rendimiento porcentual ajustado por inflación en periodos específicos.
    """
    precio_actual = df['Real_Price'].iloc[-1]
    if dias_atras is None:
        precio_inicial = df['Real_Price'].iloc[0]
        periodo = "Desde el inicio"
    else:
        # Buscamos la fecha exacta o la más cercana disponible en el mercado
        fecha_objetivo = df.index[-1] - pd.Timedelta(days=dias_atras)
        idx_cercano = df.index.get_indexer([fecha_objetivo], method='nearest')[0]
        precio_inicial = df['Real_Price'].iloc[idx_cercano]
        if dias_atras <= 365: 
            periodo = "Últimos 12 meses"
        else: 
            periodo = f"Últimos {int(dias_atras/365)} años"
    # Cálculo del cambio porcentual
    variacion = ((precio_actual - precio_inicial) / precio_inicial) * 100
    return periodo, variacion

# Definimos los horizontes temporales para el reporte
periodos = [365, 365*5, 365*10, None]

print(f"\n--- REPORTE DE RENDIMIENTO REAL ({ticker}) ---")
print(f"Base de comparación: Dólares de {inicio[:4]}")
print("-" * 55)

for p in periodos:
    nombre, var = calcular_retorno_real(df, p)
    print(f"{nombre:20}: {var:>8.2f}%")
print("-" * 55)

# Visualización de los datos
plt.figure(figsize=(12, 6), dpi=100)

# Precio Nominal
plt.plot(df.index, df['Close'], 
         label='Precio Nominal (Dólares corrientes)', color='gray', alpha=0.3, linestyle='--')

# Precio Real
plt.plot(df.index, df['Real_Price'], 
         label=f'Precio Real (Poder de compra de {inicio[:4]})', color='#d62728', linewidth=2)

plt.title(f'{ticker}: Erosión por Inflación vs Crecimiento Nominal', fontsize=15, fontweight='bold')
plt.ylabel('Valor en USD ($)')
plt.xlabel('Año')
plt.legend(loc='upper left')
plt.grid(True, linestyle=':', alpha=0.6)
plt.fill_between(df.index, df['Close'], df['Real_Price'], color='red', alpha=0.05, label='Erosión Inflacionaria')
plt.tight_layout()
plt.show()
