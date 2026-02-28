import yfinance as yf

def calcular_vp_crecimiento(fc_inicial, g, wacc, t):
    """
    Calcula el Valor Presente de una serie de flujos con crecimiento constante.
    Fórmula: VP = [FC * (1 + g) / (wacc - g)] * [1 - ((1 + g) / (1 + wacc))^t]
    """
    # Evitar división por cero si wacc es igual a g
    if wacc == g: 
        return fc_inicial * t / (1 + wacc)    
    factor_crecimiento = (1 + g) / (1 + wacc)
    pv = (fc_inicial * (1 + g) / (wacc - g)) * (1 - (factor_crecimiento ** t))
    return pv

# Configuración de datos
ticker = 'HRMY'
fc_base = 296.894   # Flujo de caja inicial (millones)
shares = 57.6       # Acciones en circulación (millones)
wacc = 0.1104       # Tasa de descuento (WACC)

# Definición de fases: (tasa de crecimiento, duración en años)
fases = [
    (0.1611, 5),   # Fase 1
    (0.14, 5),     # Fase 2
    (0.10, 20)     # Fase 3
]
g_perpetuidad = 0.06

try:
    ticker = yf.Ticker(ticker)
    current_price = ticker.info.get('currentPrice', 0)
    vp_total = 0
    fc_actual = fc_base
    factor_descuento_acumulado = 1
    for g, t in fases:
        # Calculamos el VP de la fase actual y lo descontamos al presente
        vp_fase = calcular_vp_crecimiento(fc_actual, g, wacc, t)
        vp_total += vp_fase / factor_descuento_acumulado
        # Actualizamos el flujo de caja y el factor de descuento para la siguiente fase
        fc_actual = fc_actual * ((1 + g) ** t)
        factor_descuento_acumulado *= ((1 + wacc) ** t)
    # Cálculo del valor terminal
    valor_terminal = (fc_actual * (1 + g_perpetuidad)) / (wacc - g_perpetuidad)
    vp_total += valor_terminal / factor_descuento_acumulado
    # Valores finales
    fair_price = vp_total / shares
    fair_per = vp_total / fc_base
    upside = (fair_price - current_price) / current_price
    estado = "INFRAVALORADA" if upside > 0 else "SOBREVALORADA"
    # Resultados
    print(f"--- Análisis de Valoración: {ticker} ---")
    print(f"Precio Actual:     {current_price:.2f}")
    print(f"Precio Justo:      {fair_price:.2f}")
    print(f"Estado:            {estado} ({abs(upside)*100:.2f}%)")
    print(f"PER Justo:         {fair_per:.2f}")
except Exception as e:
    print(f"Error al obtener datos de {ticker_symbol}: {e}")
