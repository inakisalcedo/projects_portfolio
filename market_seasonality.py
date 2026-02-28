import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import datetime

"""
Este script descarga datos históricos de Yahoo Finance y genera un gráfico 
de estacionalidad comparando el rendimiento promedio histórico contra 
el desempeño del año actual.
"""

# Ingresar datos
ticker_symbol = "BTC-USD"
fecha_hoy = datetime.datetime.now()
anio_actual = fecha_hoy.year
inicio_hist = "2000-01-01"  # Fecha de inicio

# Procesamiento de datos
df_raw = yf.download(ticker_symbol, start=inicio_hist, auto_adjust=True)

# Limpieza de los datos
df = pd.DataFrame(df_raw['Close'])
df.columns = ['Close']
df['Pct_Change'] = df['Close'].pct_change()

# Construcción del patrón estacional
df_hist = df[df.index.year < anio_actual].copy()

seasonal_map = df_hist.groupby([df_hist.index.month, df_hist.index.day])['Pct_Change'].mean()
seasonal_map.index = [datetime.datetime(2024, m, d).timetuple().tm_yday for m, d in seasonal_map.index]
seasonal_map = seasonal_map.sort_index().cumsum() * 100

# Datos del año actual
df_curr = df[df.index.year == anio_actual].copy()
df_curr['DayIdx'] = [d.timetuple().tm_yday for d in df_curr.index]
current_perf = df_curr['Pct_Change'].cumsum() * 100

# Visualización de datos
plt.figure(figsize=(14, 7), dpi=100)

# Dibujamos la tendencia histórica
plt.plot(seasonal_map.index, seasonal_map.values, 
         label='Tendencia Histórica Promedio', color='gray', linestyle='--', alpha=0.5)

# Dibujamos el rendimiento real del año actual
plt.plot(df_curr['DayIdx'], current_perf.values, 
         label=f'Rendimiento Real {anio_actual}', color='#1f77b4', linewidth=3)

plt.xlim(1, 366)

# Definición de marcas de tiempo para los meses
month_starts = [1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335]
month_names = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
plt.xticks(month_starts, month_names)

# Elementos informativos del gráfico
plt.title(f'Análisis de Estacionalidad: {ticker_symbol} (Histórico vs {anio_actual})', 
          fontsize=16, fontweight='bold', pad=20)
plt.ylabel('Rendimiento Acumulado (%)', fontsize=12)
plt.xlabel('Mes del Año', fontsize=12)
plt.axhline(0, color='black', lw=1, alpha=0.5)
plt.grid(True, linestyle=':', alpha=0.4)
plt.legend(frameon=True, loc='best')
plt.tight_layout()
plt.show()
