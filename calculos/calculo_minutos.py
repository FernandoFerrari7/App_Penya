import pandas as pd

def obtener_minutos_por_jornada(actas_df, jugador):
    """
    Obtiene los minutos jugados por jornada para un jugador específico
    """
    # Filtrar datos del jugador
    minutos_jugador = actas_df[actas_df['jugador'] == jugador].copy()
    
    if minutos_jugador.empty:
        return pd.DataFrame()
    
    # Ordenar por jornada
    minutos_jugador = minutos_jugador.sort_values('jornada')
    
    # Añadir información de titular/suplente
    minutos_jugador['es_titular'] = minutos_jugador['status'] == 'Titular'
    
    return minutos_jugador
