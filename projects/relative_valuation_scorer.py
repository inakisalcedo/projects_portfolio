import yfinance as yf
import pandas as pd
import numpy as np

def valuation(ratio, num):
    """
    Determina si una acción está barata o cara basándose en un ratio 
    y un valor de referencia.
    Categorías: UNDER (Infravalorada), FAIR (Precio Justo), EXPENSIVE (Cara), OVER (Sobrevalorada).
    """
    a = num
    b = 2 * num
    c = 3 * num
    
    if 0 < ratio < a:
        value = 'UNDER'
    elif a <= ratio < b:
        value = 'FAIR'
    elif b <= ratio < c:
        value = 'EXPENSIVE'
    elif ratio >= c:
        value = 'OVER'
    else:
        # En caso de valores negativos o errores, devuelve NaN
        ratio = np.nan
        num = np.nan
        value = np.nan
    return ratio, num, value

escape = ''
print("\n" + "-" * 40)
print("        RELATIVE VALUATION TOOL")

while escape != '0':
    print("-" * 40 + "\n")
    # INPUTS: Los crecimientos/márgenes deben ser ingresados como números enteros o decimales, por ejemplo si el valor es 15% se debe poner 15
    try:
        symbol = input('Introduzca Ticker (ej: AAPL): ').upper() or np.nan 
        earnings_growth = float(input('Crecimiento esperado de Ganancias (EPS Growth %): ') or 0)
        revenue_growth = float(input('Crecimiento esperado de Ingresos (Revenue Growth %): ') or 0)
        profit_margin = float(input('Margen de Beneficio Neto (Profit Margin %): ') or 0)
        # Conexión con Yahoo Finance para obtener precio actual y datos históricos
        ticker = yf.Ticker(symbol)
        info = ticker.info
        current_price = info['currentPrice']
        # El PEG mide la relación entre el PER y el crecimiento de ganancias
        if earnings_growth > 0:
            eps = info['trailingEps']          # Ganancias por acción (últimos 12 meses)
            forward_eps = info['forwardEps']    # Ganancias por acción estimadas (futuro)
            pe = current_price / eps            # Ratio P/E actual
            forward_pe = current_price / forward_eps  # Ratio P/E futuro
            peg = pe / earnings_growth          # PEG actual
            peg_adj = forward_pe / earnings_growth  # PEG ajustado al futuro
            num_peg = 1  # Referencia estándar, un PEG menor a 1 suele considerarse barato            
            # Clasificamos los resultados
            peg, _, value_peg = valuation(peg, num_peg)
            peg_adj, _, value_peg_adj = valuation(peg_adj, num_peg)
        else:
            peg = peg_adj = num_peg = value_peg = value_peg_adj = np.nan
        # Relación entre el ratio Precio/Ventas y el crecimiento de los ingresos
        if revenue_growth > 0:
            rps = info['revenuePerShare']       # Ventas por acción
            ps = current_price / rps            # Ratio P/S
            psg = ps / revenue_growth           # PSG simple
            num_psg = 0.6                       # Referencia para PSG
            psg, _, value_psg = valuation(psg, num_psg)
            # PSG Ajustado por el Margen de Beneficio
            if profit_margin > 0:
                psg_adj = ps / (revenue_growth * (profit_margin / 100))
                num_psg_adj = 2                 # Referencia para PSG ajustado
                psg_adj, _, value_psg_adj = valuation(psg_adj, num_psg_adj)
            else:
                psg_adj = num_psg_adj = value_psg_adj = np.nan
        else:
            psg = psg_adj = num_psg = value_psg = value_psg_adj = np.nan
        # Consolidamos todos los ratios calculados para dar una valoración final
        lista_ratios = pd.Series([peg, peg_adj, psg, psg_adj]).dropna().tolist()
        lista_num = pd.Series([num_peg, num_peg, num_psg, num_psg_adj]).dropna().tolist()       
        if lista_ratios:
            ratio_prom = np.mean(lista_ratios)
            num_prom = np.mean(lista_num)
            ratio_prom, _, value_prom = valuation(ratio_prom, num_prom)
        else:
            ratio_prom = value_prom = np.nan
        # Tabla de resultados
        df = pd.DataFrame()
        df.index = ['PEG (Actual)', 'PEG (Forward)', 'PSG', 'PSG (Margin Adj)', 'AVERAGE']
        # Ratios de precio (P/E o P/S)
        df['Price_Ratio'] = [round(pe, 2), round(forward_pe, 2), round(ps, 2), round(ps, 2), '--']
        df['Growth(%)'] = [earnings_growth, earnings_growth, revenue_growth, revenue_growth, '--']
        df['Margin(%)'] = ['--', '--', '--', profit_margin, '--']
        # El 'Score' es el resultado de dividir el ratio por el crecimiento
        df['Score'] = [round(peg, 2), round(peg_adj, 2), round(psg, 2), round(psg_adj, 2), round(ratio_prom, 2)]
        df['Valuation'] = [value_peg, value_peg_adj, value_psg, value_psg_adj, value_prom]
        print(f'\n{df.dropna()}')
    except Exception as e:
        print(f"Error al procesar los datos: {e}. Asegúrate de que el Ticker sea correcto.")
    print("\n" + "-" * 40)
    escape = input("Presiona ENTER para otra consulta o '0' para salir: ")
