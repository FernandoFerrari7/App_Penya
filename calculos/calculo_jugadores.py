"""
Cálculos relacionados con estadísticas de jugadores
"""
import pandas as pd
import numpy as np

def calcular_estadisticas_jugador(actas_df, jugador_nombre):
    """
    Calcula estadísticas generales para un jugador específico
    
    Args:
        actas_df: DataFrame con los datos de actas
        jugador_nombre: Nombre del jugador
        
    Returns:
        dict: Diccionario con las estadísticas del jugador
    """
    # Filtrar datos del jugador
    datos_jugador = actas_df[actas_df['jugador'] == jugador_nombre]
    
    if datos_jugador.empty:
        return None
    
    # Cálculos básicos
    goles = datos_jugador['goles'].sum()
    tarjetas_amarillas = datos_jugador['Tarjetas Amarillas'].sum()
    tarjetas_rojas = datos_jugador['Tarjetas Rojas'].sum()
    minutos_jugados = datos_jugador['minutos_jugados'].sum()
    partidos_jugados = len(datos_jugador)
    
    # Calcular titularidades y suplencias
    titularidades = datos_jugador[datos_jugador['status'] == 'Titular'].shape[0]
    suplencias = partidos_jugados - titularidades
    
    # Minutos por partido
    minutos_por_partido = minutos_jugados / partidos_jugados if partidos_jugados > 0 else 0
    
    # Recopilar resultados
    estadisticas = {
        'nombre': jugador_nombre,
        'goles': int(goles),
        'tarjetas_amarillas': int(tarjetas_amarillas),
        'tarjetas_rojas': int(tarjetas_rojas),
        'minutos_jugados': int(minutos_jugados),
        'partidos_jugados': partidos_jugados,
        'titularidades': titularidades,
        'suplencias': suplencias,
        'minutos_por_partido': round(minutos_por_partido, 1)
    }
    
    return estadisticas

def obtener_minutos_por_jornada(actas_df, jugador_nombre):
    """
    Obtiene los minutos jugados por jornada para un jugador específico
    
    Args:
        actas_df: DataFrame con los datos de actas
        jugador_nombre: Nombre del jugador
        
    Returns:
        DataFrame: DataFrame con los minutos por jornada
    """
    # Filtrar datos del jugador
    datos_jugador = actas_df[actas_df['jugador'] == jugador_nombre]
    
    if datos_jugador.empty:
        return pd.DataFrame()
    
    # Seleccionar columnas relevantes
    minutos_por_jornada = datos_jugador[['jornada', 'minutos_jugados', 'rival', 'status']]
    
    # Agregar columna booleana para titular
    minutos_por_jornada['es_titular'] = minutos_por_jornada['status'] == 'Titular'
    
    # Ordenar por jornada
    minutos_por_jornada = minutos_por_jornada.sort_values('jornada')
    
    return minutos_por_jornada

def obtener_top_goleadores(actas_df, top_n=10):
    """
    Obtiene los jugadores con más goles
    
    Args:
        actas_df: DataFrame con los datos de actas
        top_n: Número de jugadores a mostrar
        
    Returns:
        DataFrame: DataFrame con los goleadores
    """
    # Agrupar por jugador y sumar goles
    goles_por_jugador = actas_df.groupby('jugador')['goles'].sum().reset_index()
    
    # Filtrar jugadores con al menos 1 gol
    goles_por_jugador = goles_por_jugador[goles_por_jugador['goles'] > 0]
    
    # Ordenar por goles (descendente)
    goles_por_jugador = goles_por_jugador.sort_values('goles', ascending=False)
    
    # Limitar al número especificado
    return goles_por_jugador.head(top_n)

def obtener_top_amonestados(actas_df, top_n=10):
    """
    Obtiene los jugadores con más tarjetas
    
    Args:
        actas_df: DataFrame con los datos de actas
        top_n: Número de jugadores a mostrar
        
    Returns:
        DataFrame: DataFrame con los jugadores más amonestados
    """
    # Agrupar por jugador y sumar tarjetas
    tarjetas_por_jugador = actas_df.groupby('jugador').agg({
        'Tarjetas Amarillas': 'sum',
        'Tarjetas Rojas': 'sum'
    }).reset_index()
    
    # Calcular un puntaje total (1 punto por amarilla, 3 por roja)
    tarjetas_por_jugador['total_puntos'] = (
        tarjetas_por_jugador['Tarjetas Amarillas'] + 
        3 * tarjetas_por_jugador['Tarjetas Rojas']
    )
    
    # Filtrar jugadores con al menos 1 tarjeta
    tarjetas_por_jugador = tarjetas_por_jugador[tarjetas_por_jugador['total_puntos'] > 0]
    
    # Ordenar por puntos totales (descendente)
    tarjetas_por_jugador = tarjetas_por_jugador.sort_values('total_puntos', ascending=False)
    
    # Limitar al número especificado
    return tarjetas_por_jugador.head(top_n)

def obtener_jugadores_mas_minutos(actas_df, top_n=10):
    """
    Obtiene los jugadores con más minutos jugados
    
    Args:
        actas_df: DataFrame con los datos de actas
        top_n: Número de jugadores a mostrar
        
    Returns:
        DataFrame: DataFrame con los jugadores con más minutos
    """
    # Agrupar por jugador y sumar minutos
    minutos_por_jugador = actas_df.groupby('jugador')['minutos_jugados'].sum().reset_index()
    
    # Ordenar por minutos (descendente)
    minutos_por_jugador = minutos_por_jugador.sort_values('minutos_jugados', ascending=False)
    
    # Limitar al número especificado
    return minutos_por_jugador.head(top_n)

def analizar_goles_por_tiempo(goles_df):
    """
    Analiza la distribución de goles por rango de minutos
    
    Args:
        goles_df: DataFrame con los datos de goles
        
    Returns:
        Series: Serie con conteo de goles por rango de minutos
    """
    # Crear rangos de minutos para agrupar
    goles_df = goles_df.copy()
    goles_df['rango_minuto'] = pd.cut(
        goles_df['Minuto'], 
        bins=[0, 15, 30, 45, 60, 75, 90, 105],
        labels=['0-15', '16-30', '31-45', '46-60', '61-75', '76-90', '91+']
    )
    
    # Contar goles por rango de minutos
    goles_por_minuto = goles_df['rango_minuto'].value_counts().sort_index()
    
    return goles_por_minuto

def analizar_goles_por_jugador(goles_df, actas_df):
    """
    Analiza los goles marcados por cada jugador
    
    Args:
        goles_df: DataFrame con los datos de goles
        actas_df: DataFrame con los datos de actas para información adicional
        
    Returns:
        DataFrame: DataFrame con goles por jugador ordenado de mayor a menor
    """
    # Contar goles por jugador
    goles_por_jugador = goles_df['jugador'].value_counts().reset_index()
    goles_por_jugador.columns = ['jugador', 'goles']
    
    # Ordenar por número de goles (descendente)
    goles_por_jugador = goles_por_jugador.sort_values('goles', ascending=False)
    
    return goles_por_jugador

def analizar_tarjetas_por_jugador(actas_df):
    """
    Analiza las tarjetas recibidas por cada jugador
    
    Args:
        actas_df: DataFrame con los datos de actas
        
    Returns:
        DataFrame: DataFrame con tarjetas por jugador
    """
    # Agrupar por jugador y sumar tarjetas
    tarjetas_por_jugador = actas_df.groupby('jugador').agg({
        'Tarjetas Amarillas': 'sum',
        'Tarjetas Rojas': 'sum'
    }).reset_index()
    
    # Calcular el total de tarjetas (1 punto por amarilla, 3 por roja)
    tarjetas_por_jugador['Total Puntos'] = (
        tarjetas_por_jugador['Tarjetas Amarillas'] + 
        3 * tarjetas_por_jugador['Tarjetas Rojas']
    )
    
    # Filtrar jugadores con al menos 1 tarjeta
    tarjetas_por_jugador = tarjetas_por_jugador[tarjetas_por_jugador['Total Puntos'] > 0]
    
    # Ordenar por puntos totales (descendente)
    tarjetas_por_jugador = tarjetas_por_jugador.sort_values('Total Puntos', ascending=False)
    
    return tarjetas_por_jugador

def analizar_minutos_por_jugador(actas_df):
    """
    Analiza los minutos jugados por cada jugador con diferentes desgloses
    
    Args:
        actas_df: DataFrame con los datos de actas
        
    Returns:
        DataFrame: DataFrame con análisis detallado de minutos por jugador
    """
    # Crear un DataFrame para almacenar los resultados
    minutos_jugador = pd.DataFrame()
    
    # Calcular minutos totales por jugador
    minutos_totales = actas_df.groupby('jugador')['minutos_jugados'].sum().reset_index()
    minutos_totales.columns = ['jugador', 'minutos_totales']
    
    # Contar partidos jugados por jugador
    partidos_jugados = actas_df.groupby('jugador').size().reset_index(name='partidos')
    
    # Contar partidos como titular
    titularidades = actas_df[actas_df['status'] == 'Titular'].groupby('jugador').size().reset_index(name='titular')
    
    # Contar partidos como suplente
    suplencias = actas_df[actas_df['status'] != 'Titular'].groupby('jugador').size().reset_index(name='suplente')
    
    # Calcular minutos como local
    minutos_local = actas_df[actas_df['localizacion'] == 'Local'].groupby('jugador')['minutos_jugados'].sum().reset_index()
    minutos_local.columns = ['jugador', 'minutos_local']
    
    # Calcular minutos como visitante
    minutos_visitante = actas_df[actas_df['localizacion'] == 'Visitante'].groupby('jugador')['minutos_jugados'].sum().reset_index()
    minutos_visitante.columns = ['jugador', 'minutos_visitante']
    
    # Calcular minutos como titular
    minutos_titular = actas_df[actas_df['status'] == 'Titular'].groupby('jugador')['minutos_jugados'].sum().reset_index()
    minutos_titular.columns = ['jugador', 'minutos_titular']
    
    # Calcular minutos como suplente
    minutos_suplente = actas_df[actas_df['status'] != 'Titular'].groupby('jugador')['minutos_jugados'].sum().reset_index()
    minutos_suplente.columns = ['jugador', 'minutos_suplente']
    
    # Unir todos los DataFrames
    minutos_jugador = pd.merge(minutos_totales, partidos_jugados, on='jugador', how='left')
    minutos_jugador = pd.merge(minutos_jugador, titularidades, on='jugador', how='left')
    minutos_jugador = pd.merge(minutos_jugador, suplencias, on='jugador', how='left')
    minutos_jugador = pd.merge(minutos_jugador, minutos_local, on='jugador', how='left')
    minutos_jugador = pd.merge(minutos_jugador, minutos_visitante, on='jugador', how='left')
    minutos_jugador = pd.merge(minutos_jugador, minutos_titular, on='jugador', how='left')
    minutos_jugador = pd.merge(minutos_jugador, minutos_suplente, on='jugador', how='left')
    
    # Calcular promedios y porcentajes
    minutos_jugador['promedio_por_partido'] = minutos_jugador['minutos_totales'] / minutos_jugador['partidos']
    
    # Llenar valores NaN con 0
    minutos_jugador = minutos_jugador.fillna(0)
    
    # Calcular porcentaje del total de minutos del equipo
    total_minutos_equipo = minutos_jugador['minutos_totales'].sum()
    minutos_jugador['porcentaje_del_total'] = (minutos_jugador['minutos_totales'] / total_minutos_equipo) * 100
    
    # Ordenar por minutos totales (descendente)
    minutos_jugador = minutos_jugador.sort_values('minutos_totales', ascending=False)
    
    return minutos_jugador

def analizar_minutos_por_jornada(actas_df):
    """
    Analiza los minutos jugados por jornada y condición
    
    Args:
        actas_df: DataFrame con los datos de actas
        
    Returns:
        DataFrame: DataFrame con minutos por jornada y condición
    """
    # Calcular minutos por jornada
    minutos_jornada = actas_df.groupby(['jornada', 'localizacion'])['minutos_jugados'].sum().reset_index()
    
    # Pivotear para tener local y visitante como columnas
    minutos_pivot = minutos_jornada.pivot(index='jornada', columns='localizacion', values='minutos_jugados').reset_index()
    minutos_pivot = minutos_pivot.rename(columns={'Local': 'minutos_local', 'Visitante': 'minutos_visitante'})
    
    # Llenar valores NaN con 0
    minutos_pivot = minutos_pivot.fillna(0)
    
    # Calcular total por jornada
    minutos_pivot['total'] = minutos_pivot['minutos_local'] + minutos_pivot['minutos_visitante']
    
    return minutos_pivot

def analizar_distribucion_sustituciones(sustituciones_df, rango_minutos=5):
    """
    Analiza la distribución de sustituciones por minuto de juego
    
    Args:
        sustituciones_df: DataFrame con datos de sustituciones
        rango_minutos: Rango de minutos para agrupar las sustituciones
        
    Returns:
        dict: Diccionario con diferentes análisis de sustituciones
    """
    import pandas as pd
    import numpy as np
    
    if sustituciones_df.empty:
        return {}
    
    # Crear intervalos para agrupar los minutos
    sustituciones_df = sustituciones_df.copy()
    
    # Definir dos conjuntos separados de rangos para primer y segundo tiempo
    # Primer tiempo
    primer_tiempo_df = sustituciones_df[sustituciones_df['Minuto'] <= 45].copy()
    primer_tiempo_df['rango_minuto'] = '1-45'  # Asignar etiqueta directamente
    
    # Segundo tiempo
    segundo_tiempo_df = sustituciones_df[sustituciones_df['Minuto'] > 45].copy()
    
    # Definir rangos para el segundo tiempo
    rangos_segundo = list(range(45, 95, rango_minutos))
    if rangos_segundo[-1] < 90 + rango_minutos:  # Asegurar que el último rango incluya posibles minutos de descuento
        rangos_segundo.append(rangos_segundo[-1] + rango_minutos)
    
    # Crear etiquetas para los rangos del segundo tiempo
    etiquetas_segundo = [f"{r}-{r+rango_minutos}" for r in rangos_segundo[:-1]]
    
    # Categorizar minutos del segundo tiempo
    if not segundo_tiempo_df.empty:
        # Asegurarse de que tengamos al menos un valor en segundo_tiempo_df
        segundo_tiempo_df['rango_minuto'] = pd.cut(
            segundo_tiempo_df['Minuto'], 
            bins=rangos_segundo, 
            labels=etiquetas_segundo, 
            include_lowest=True, 
            right=False
        )
    
    # Combinar los dataframes de primer y segundo tiempo
    sustituciones_df = pd.concat([primer_tiempo_df, segundo_tiempo_df])
    
    # Contar sustituciones por rango de minutos
    dist_por_minuto = sustituciones_df['rango_minuto'].value_counts().reset_index()
    dist_por_minuto.columns = ['rango', 'cantidad']
    
    # Ordenar por rango para que el primer tiempo aparezca primero
    rangos_ordenados = ['1-45'] + etiquetas_segundo
    dist_por_minuto['orden'] = dist_por_minuto['rango'].apply(lambda x: rangos_ordenados.index(x) if x in rangos_ordenados else 999)
    dist_por_minuto = dist_por_minuto.sort_values('orden').drop('orden', axis=1)
    
    # Análisis de sustituciones por jornada
    sustituciones_por_jornada = sustituciones_df.groupby('Jornada').size().reset_index(name='cantidad')
    sustituciones_por_jornada = sustituciones_por_jornada.sort_values('Jornada')
    
    # Estadísticas generales de sustituciones
    minuto_medio = sustituciones_df['Minuto'].mean()
    
    # Primera sustitución por jornada
    primera_sustitucion = sustituciones_df.groupby('Jornada')['Minuto'].min().mean()
    
    # Última sustitución por jornada
    ultima_sustitucion = sustituciones_df.groupby('Jornada')['Minuto'].max().mean()
    
    # Número medio de sustituciones por partido
    num_medio_sustituciones = sustituciones_df.groupby('Jornada').size().mean()
    
    # Top sustituciones más repetidas (jugador sale - jugador entra)
    sustituciones_df['dupla'] = sustituciones_df['jugador_sale'] + ' ⟶ ' + sustituciones_df['jugador_entra']
    top_sustituciones = sustituciones_df['dupla'].value_counts().head(5).reset_index()
    top_sustituciones.columns = ['Sustitución', 'Frecuencia']
    
    # Top jugadores más sustituidos
    top_sustituidos = sustituciones_df['jugador_sale'].value_counts().head(5).reset_index()
    top_sustituidos.columns = ['Jugador', 'Veces Sustituido']
    
    # Top jugadores con más minutos desde el banquillo
    # Para esto necesitamos calcular los minutos jugados para cada sustitución
    # Asumiremos que el partido dura 90 minutos a menos que tengamos datos más precisos
    sustituciones_df['minutos_jugados'] = 90 - sustituciones_df['Minuto']
    
    # Agrupar por jugador que entra y sumar minutos
    minutos_suplente = sustituciones_df.groupby('jugador_entra')['minutos_jugados'].sum().reset_index()
    top_suplentes = minutos_suplente.sort_values('minutos_jugados', ascending=False).head(5)
    top_suplentes.columns = ['Jugador', 'Minutos como Suplente']
    
    return {
        'distribucion_minutos': dist_por_minuto,
        'sustituciones_jornada': sustituciones_por_jornada,
        'minuto_medio': minuto_medio,
        'primera_sustitucion': primera_sustitucion,
        'ultima_sustitucion': ultima_sustitucion,
        'num_medio_sustituciones': num_medio_sustituciones,
        'top_sustituciones': top_sustituciones,
        'top_sustituidos': top_sustituidos,
        'top_suplentes': top_suplentes
    }