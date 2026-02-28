import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

def calcular_rsi_semanal(ticker, periodos=14):
    """
    Calcula y grafica el RSI semanal con una Media Móvil para un ticker dado.
    """
    print(f"Descargando datos para {ticker}...")
    
    # Descarga de datos históricos (5 años de historial diario)
    data = yf.download(ticker, period="5y", interval="1d", auto_adjust=True)
    if data.empty:
        print("No se encontraron datos.")
        return
    # Limpieza de estructura de columnas
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)
    # Convertimos la frecuencia de diaria a semanal tomando el último dato de cada viernes
    serie_cierre = data['Close'].resample('W-FRI').last()
    # Cálculo del RSI
    delta = serie_cierre.diff()
    # Separamos las ganancias de las pérdidas
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    # Aplicamos la Media Móvil Exponencial
    avg_gain = gain.ewm(alpha=1/periodos, min_periods=periodos).mean()
    avg_loss = loss.ewm(alpha=1/periodos, min_periods=periodos).mean()
    # Cálculo de la Fuerza Relativa (RS) y el índice RSI
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))    
    # Cálculo de la Media Móvil del propio RSI
    rsi_ma = rsi.rolling(window=periodos).mean()
    # Configuración de la visualización gráfica
    plt.figure(figsize=(14, 7))
    # Graficar el RSI y su Media Móvil
    plt.plot(rsi.index, rsi, label=f'RSI Semanal ({periodos})', color='#1f77b4', linewidth=2)
    plt.plot(rsi_ma.index, rsi_ma, label='Media Móvil RSI', color='#ff7f0e', linestyle='--')
    # Dibujar líneas horizontales de niveles críticos (70 y 30)
    plt.axhline(70, color='red', linestyle='-', alpha=0.6, label='Sobrecompra (70)')
    plt.axhline(30, color='green', linestyle='-', alpha=0.6, label='Sobreventa (30)')
    # Rellenar zonas de sobrecompra y sobreventa para mayor claridad visual
    plt.fill_between(rsi.index, 70, 100, color='red', alpha=0.07)
    plt.fill_between(rsi.index, 0, 30, color='green', alpha=0.07)    
    # Títulos y etiquetas
    plt.title(f'RSI Semanal con Media Móvil: {ticker}', fontsize=14)
    plt.ylabel('Nivel de RSI')
    plt.grid(True, alpha=0.3)
    plt.legend(loc='upper left')
    plt.ylim(0, 100) # El RSI es un oscilador acotado entre 0 y 100
    plt.tight_layout()
    plt.show()

# Entradas del programa
ticker_user = input("Introduce el ticker: ").upper() or "AAPL"
periodos_user = input("Semanas para el cálculo (14): ")

# Conversión de la entrada de periodos a entero, con respaldo en 14 si está vacío o es inválido
periodos_val = int(periodos_user) if periodos_user.isdigit() else 14

# Llamada a la función principal
calcular_rsi_semanal(ticker_user, periodos_val)
