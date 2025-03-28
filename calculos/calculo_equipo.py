"""
Cálculos relacionados con estadísticas del equipo
"""
import pandas as pd
import numpy as np

def normalizar_nombre_equipo(nombre):
    """
    Normaliza el nombre del equipo para asegurar compatibilidad entre diferentes archivos.
    Elimina las comillas y normaliza el formato.
    
    Args:
        nombre: Nombre del equipo a normalizar
        
    Returns:
        str: Nombre normalizado
    """
    if not nombre:
        return nombre
    
    # Eliminar espacios adicionales
    nombre = nombre.strip()
    
    # Reemplazar comillas dobles por espacio
    nombre = nombre.replace('"', '')
    
    # Reemplazar barras invertidas
    nombre = nombre.replace('\\', '')
    
    # Ajuste específico para equipos con sufijo "A", "B", etc.
    if " A" in nombre or " B" in nombre:
        # Asegurar que hay un espacio antes de A/B
        nombre = nombre.replace("A", " A").replace("  A", " A")
        nombre = nombre.replace("B", " B").replace("  B", " B")
        
    return nombre

def ajustar_tarjetas_por_doble_amarilla(actas_df):
    """
    Ajusta el conteo de tarjetas para que cuando un jugador recibe 2 amarillas
    en una misma jornada, se cuente como una tarjeta roja en lugar de 2 amarillas.
    
    Args:
        actas_df: DataFrame con los datos de actas
        
    Returns:
        DataFrame: DataFrame con las tarjetas ajustadas
    """
    # Crear una copia del DataFrame para no modificar el original
    df_ajustado = actas_df.copy()
    
    # Agrupar por jugador y jornada para identificar casos de doble amarilla
    tarjetas_por_jugador_jornada = df_ajustado.groupby(['jugador', 'jornada']).agg({
        'Tarjetas Amarillas': 'sum',
        'Tarjetas Rojas': 'sum'
    }).reset_index()
    
    # Identificar jugadores con 2 o más amarillas en una jornada
    jugadores_doble_amarilla = tarjetas_por_jugador_jornada[
        (tarjetas_por_jugador_jornada['Tarjetas Amarillas'] >= 2)
    ]
    
    # Para cada caso de doble amarilla, ajustar en el DataFrame original
    for _, row in jugadores_doble_amarilla.iterrows():
        jugador = row['jugador']
        jornada = row['jornada']
        amarillas = row['Tarjetas Amarillas']
        
        # Si hay 2 o más amarillas, convertir cada par en una roja
        rojas_adicionales = amarillas // 2
        amarillas_restantes = amarillas % 2
        
        # Localizar registros del jugador en esa jornada
        mask = (df_ajustado['jugador'] == jugador) & (df_ajustado['jornada'] == jornada)
        
        # Actualizar el primer registro con los valores ajustados
        if any(mask):
            # Obtener el índice del primer registro que cumple con la condición
            primer_registro = df_ajustado[mask].index[0]
            
            # Actualizar tarjetas amarillas y rojas
            df_ajustado.loc[primer_registro, 'Tarjetas Amarillas'] = amarillas_restantes
            df_ajustado.loc[primer_registro, 'Tarjetas Rojas'] += rojas_adicionales
            
            # Si hay más registros del mismo jugador en la misma jornada, poner a cero sus tarjetas
            otros_registros = df_ajustado[mask].index[1:]
            if len(otros_registros) > 0:
                df_ajustado.loc[otros_registros, 'Tarjetas Amarillas'] = 0
                df_ajustado.loc[otros_registros, 'Tarjetas Rojas'] = 0
    
    return df_ajustado

def contar_partidos_jugados(partidos_df, equipo_seleccionado="PENYA INDEPENDENT"):
    """
    Cuenta los partidos jugados, verificando que tengan un enlace de acta válido
    
    Args:
        partidos_df: DataFrame con datos de partidos
        equipo_seleccionado: Nombre del equipo para filtrar los partidos (default: "PENYA INDEPENDENT")
        
    Returns:
        int: Número de partidos jugados
    """
    # Los partidos ya deberían estar filtrados, solo contar los que tienen acta válida
    partidos_jugados = partidos_df[
        partidos_df['link_acta'].notna() & 
        (partidos_df['link_acta'] != '')
    ].shape[0]
    
    return partidos_jugados

def calcular_estadisticas_generales(actas_df, goles_df, partidos_df, equipo_seleccionado="PENYA INDEPENDENT"):
    """
    Calcula estadísticas generales del equipo
    
    Args:
        actas_df: DataFrame con datos de actas
        goles_df: DataFrame con datos de goles
        partidos_df: DataFrame con datos de partidos
        equipo_seleccionado: Nombre del equipo para filtrar los cálculos (default: "PENYA INDEPENDENT")
        
    Returns:
        dict: Diccionario con estadísticas generales
    """
    # Usar la función común para contar partidos jugados
    total_partidos = contar_partidos_jugados(partidos_df, equipo_seleccionado)
    
    # Ajustar tarjetas (convertir dobles amarillas en rojas)
    actas_ajustadas = ajustar_tarjetas_por_doble_amarilla(actas_df)
    
    total_goles = len(goles_df)
    total_tarjetas_amarillas = actas_ajustadas['Tarjetas Amarillas'].sum()
    total_tarjetas_rojas = actas_ajustadas['Tarjetas Rojas'].sum()
    
    # Minutos jugados por todos los jugadores
    total_minutos = actas_df['minutos_jugados'].sum()
    
    # Calculamos el promedio de goles por partido
    promedio_goles = total_goles / total_partidos if total_partidos > 0 else 0
    
    # Recopilar resultados
    estadisticas = {
        'partidos_jugados': total_partidos,
        'goles_marcados': int(total_goles),
        'tarjetas_amarillas': int(total_tarjetas_amarillas),
        'tarjetas_rojas': int(total_tarjetas_rojas),
        'promedio_goles': round(promedio_goles, 2),
        'total_minutos': int(total_minutos)
    }
    
    return estadisticas

def analizar_tarjetas_por_jornada(actas_df):
    """
    Analiza la distribución de tarjetas por jornada
    
    Args:
        actas_df: DataFrame con los datos de actas
        
    Returns:
        DataFrame: DataFrame con tarjetas por jornada
    """
    # Aplicar ajuste de tarjetas
    actas_ajustadas = ajustar_tarjetas_por_doble_amarilla(actas_df)
    
    # Agrupar por jornada y sumar tarjetas
    tarjetas_por_jornada = actas_ajustadas.groupby('jornada').agg({
        'Tarjetas Amarillas': 'sum',
        'Tarjetas Rojas': 'sum'
    }).reset_index()
    
    return tarjetas_por_jornada

def obtener_rivales_con_goles(actas_df, goles_df):
    """
    Obtiene los rivales contra los que se marcaron goles
    
    Args:
        actas_df: DataFrame con datos de actas
        goles_df: DataFrame con datos de goles
        
    Returns:
        DataFrame: DataFrame con goles por rival
    """
    # Mapear jornadas a rivales
    jornada_rival = {}
    
    # Para cada jornada única en los datos de goles
    for jornada in goles_df['Jornada'].unique():
        # Encontrar el rival en esa jornada
        rival_jornada = actas_df[actas_df['jornada'] == jornada]['rival'].iloc[0] if any(actas_df['jornada'] == jornada) else 'Desconocido'
        jornada_rival[jornada] = rival_jornada
    
    # Agregar columna de rival a los datos de goles
    goles_df_con_rival = goles_df.copy()
    goles_df_con_rival['rival'] = goles_df_con_rival['Jornada'].map(jornada_rival)
    
    # Contar goles por rival
    goles_por_rival = goles_df_con_rival.groupby('rival').size().reset_index(name='goles')
    
    # Ordenar por número de goles (descendente)
    goles_por_rival = goles_por_rival.sort_values('goles', ascending=False)
    
    return goles_por_rival

def analizar_tipos_goles(goles_df):
    """
    Analiza los tipos de goles marcados
    
    Args:
        goles_df: DataFrame con datos de goles
        
    Returns:
        Series: Serie con conteo de goles por tipo
    """
    # Contar goles por tipo
    tipos_goles = goles_df['Tipo de Gol'].value_counts()
    
    return tipos_goles

def calcular_goles_contra(actas_df, partidos_df, actas_completas_df, equipo_seleccionado="PENYA INDEPENDENT"):
    """
    Calcula los goles en contra basado en los datos de las actas
    
    Args:
        actas_df: DataFrame con datos de actas del equipo seleccionado
        partidos_df: DataFrame con datos de partidos
        actas_completas_df: DataFrame con todas las actas
        equipo_seleccionado: Nombre del equipo para filtrar los cálculos (default: "PENYA INDEPENDENT")
        
    Returns:
        int: Total de goles en contra
    """
    # Normalizar nombre del equipo seleccionado para comparaciones
    equipo_normalizado = normalizar_nombre_equipo(equipo_seleccionado)
    
    # Enfoque 1: Buscar actas donde el equipo seleccionado aparece como rival
    actas_contra_equipo = actas_completas_df[
        actas_completas_df['rival'].apply(lambda x: normalizar_nombre_equipo(x)).str.contains(equipo_normalizado, na=False)
    ]
    
    # Sumar los goles de esas actas
    goles_contra = actas_contra_equipo['goles'].sum()
    
    # Si no encontramos resultados con este método, intentar otro enfoque
    if goles_contra == 0:
        # Enfoque 2: Usar las jornadas y partidos para identificar rivales
        
        # Identificar jornadas donde juega el equipo seleccionado
        jornadas_equipo = actas_df['jornada'].unique()
        
        # Filtrar partidos con el equipo seleccionado
        partidos_equipo = partidos_df.copy()  # Ya está filtrado en equipos.py
        
        # Mapear jornadas a rivales
        jornada_rival = {}
        for _, partido in partidos_equipo.iterrows():
            if pd.isna(partido['jornada']):
                continue
                
            jornada = partido['jornada']
            
            if normalizar_nombre_equipo(partido['equipo_local']).find(equipo_normalizado) >= 0:
                jornada_rival[jornada] = partido['equipo_visitante']
            else:
                jornada_rival[jornada] = partido['equipo_local']
        
        # Contar goles en contra (goles de los rivales)
        for jornada in jornadas_equipo:
            if jornada in jornada_rival:
                rival = jornada_rival[jornada]
                if pd.isna(rival):
                    continue
                
                rival_normalizado = normalizar_nombre_equipo(rival)
                
                # Buscar actas del rival en esta jornada
                actas_rival = actas_completas_df[
                    (actas_completas_df['jornada'] == jornada) & 
                    (actas_completas_df['equipo'].apply(lambda x: normalizar_nombre_equipo(x)).str.contains(rival_normalizado, na=False))
                ]
                
                # Sumar goles del rival
                goles_contra += actas_rival['goles'].sum()

    return int(goles_contra)

def calcular_tarjetas_rivales(actas_completas_df, partidos_df, equipo_seleccionado="PENYA INDEPENDENT"):
    """
    Calcula las tarjetas de los equipos rivales
    
    Args:
        actas_completas_df: DataFrame con todas las actas
        partidos_df: DataFrame con datos de partidos
        equipo_seleccionado: Nombre del equipo para filtrar los cálculos (default: "PENYA INDEPENDENT")
        
    Returns:
        dict: Diccionario con total de tarjetas amarillas y rojas de rivales
    """
    # Normalizar nombre del equipo seleccionado para comparaciones
    equipo_normalizado = normalizar_nombre_equipo(equipo_seleccionado)
    
    # Aplicar ajuste de tarjetas para los rivales también
    actas_completas_ajustadas = ajustar_tarjetas_por_doble_amarilla(actas_completas_df)
    
    # Enfoque 1: Buscar actas donde el equipo seleccionado aparece como rival
    actas_rivales = actas_completas_ajustadas[
        actas_completas_ajustadas['rival'].apply(lambda x: normalizar_nombre_equipo(x)).str.contains(equipo_normalizado, na=False)
    ]
    
    # Sumar tarjetas de esas actas
    ta_rival = actas_rivales['Tarjetas Amarillas'].sum()
    tr_rival = actas_rivales['Tarjetas Rojas'].sum()
    
    # Si no encontramos resultados con este método, intentar enfoque alternativo
    if ta_rival == 0 and tr_rival == 0:
        # Filtrar partidos del equipo seleccionado
        partidos_equipo = partidos_df.copy()  # Ya está filtrado en equipos.py
        
        # Mapear jornadas a rivales
        jornada_rival = {}
        for _, partido in partidos_equipo.iterrows():
            if pd.isna(partido['jornada']):
                continue
                
            jornada = partido['jornada']
            
            if normalizar_nombre_equipo(partido['equipo_local']).find(equipo_normalizado) >= 0:
                jornada_rival[jornada] = partido['equipo_visitante']
            else:
                jornada_rival[jornada] = partido['equipo_local']
        
        # Contar tarjetas de los rivales
        for jornada, rival in jornada_rival.items():
            if pd.isna(rival):
                continue
                
            rival_normalizado = normalizar_nombre_equipo(rival)
            
            # Buscar actas del rival en esta jornada
            actas_rival = actas_completas_ajustadas[
                (actas_completas_ajustadas['jornada'] == jornada) & 
                (actas_completas_ajustadas['equipo'].apply(lambda x: normalizar_nombre_equipo(x)).str.contains(rival_normalizado, na=False))
            ]
            # Sumar tarjetas del rival
            ta_rival += actas_rival['Tarjetas Amarillas'].sum()
            tr_rival += actas_rival['Tarjetas Rojas'].sum()
    
    return {
        'amarillas': int(ta_rival),
        'rojas': int(tr_rival)
    }

def calcular_metricas_avanzadas(partidos_df, goles_df, actas_df, actas_completas_df, equipo_seleccionado="PENYA INDEPENDENT"):
    """
    Calcula métricas avanzadas para mostrar en tarjetas
    
    Args:
        partidos_df: DataFrame con datos de partidos
        goles_df: DataFrame con datos de goles
        actas_df: DataFrame con datos de actas del equipo seleccionado
        actas_completas_df: DataFrame con todas las actas (todos los equipos)
        equipo_seleccionado: Nombre del equipo para filtrar los cálculos (default: "PENYA INDEPENDENT")
        
    Returns:
        dict: Diccionario con métricas para mostrar
    """
    # Normalizar nombre del equipo para comparaciones
    equipo_normalizado = normalizar_nombre_equipo(equipo_seleccionado)
    
    # Determinar partidos locales y visitantes
    partidos_df = partidos_df.copy()
    partidos_df['es_local'] = partidos_df['equipo_local'].apply(
        lambda x: normalizar_nombre_equipo(x)).str.contains(equipo_normalizado, na=False)
    
    # Contar partidos jugados (con link_acta) para el equipo seleccionado
    partidos_jugados = partidos_df[
        partidos_df['link_acta'].notna() & 
        (partidos_df['link_acta'] != '')
    ].shape[0]
    
    # Crear listas de jornadas por condición
    partidos_equipo = partidos_df.copy()
    jornadas_local = partidos_equipo[partidos_equipo['es_local']]['jornada'].tolist()
    jornadas_visitante = partidos_equipo[~partidos_equipo['es_local']]['jornada'].tolist()
    
    # Contar goles a favor (total de goles marcados por el equipo)
    goles_favor = len(goles_df)
    
    # Calcular los goles en contra
    goles_contra = calcular_goles_contra(actas_df, partidos_df, actas_completas_df, equipo_seleccionado)
    
    # Aplicar ajuste de tarjetas
    actas_ajustadas = ajustar_tarjetas_por_doble_amarilla(actas_df)
    actas_completas_ajustadas = ajustar_tarjetas_por_doble_amarilla(actas_completas_df)
    
    # Calcular tarjetas del equipo
    tarjetas_amarillas = int(actas_ajustadas['Tarjetas Amarillas'].sum())
    tarjetas_rojas = int(actas_ajustadas['Tarjetas Rojas'].sum())
    
    # Calcular tarjetas de los rivales
    tarjetas_rivales = calcular_tarjetas_rivales(actas_completas_ajustadas, partidos_df, equipo_seleccionado)
    ta_rival = tarjetas_rivales['amarillas']
    tr_rival = tarjetas_rivales['rojas']
    
    # Calcular número de jugadores y partidos
    num_jugadores = actas_df['jugador'].nunique()
    
    # Calcular valores de referencia (medias de la liga)
    # Calculamos la media de goles de todos los otros equipos
    goles_por_equipo = actas_completas_df.groupby('equipo')['goles'].sum()
    # Excluir al equipo seleccionado para calcular la media
    # Corregido: usar map() en lugar de apply() para objetos Index
    goles_otros_equipos = goles_por_equipo[goles_por_equipo.index.map(
        lambda x: equipo_normalizado not in normalizar_nombre_equipo(x))]
    ref_goles_favor = int(round(goles_otros_equipos.mean()))
    
    # Media de goles en contra (goles a favor de los otros equipos)
    ref_goles_contra = int(round(goles_otros_equipos.mean()))
    
    # Media de tarjetas amarillas de la liga
    tarjetas_por_equipo = actas_completas_ajustadas.groupby('equipo')['Tarjetas Amarillas'].sum()
    # Corregido: usar map() en lugar de apply() para objetos Index
    tarjetas_otros_equipos = tarjetas_por_equipo[tarjetas_por_equipo.index.map(
        lambda x: equipo_normalizado not in normalizar_nombre_equipo(x))]
    ref_tarjetas_amarillas = int(round(tarjetas_otros_equipos.mean()))
    
    # Media de tarjetas amarillas de la liga para rivales
    ref_ta_rival = int(round(tarjetas_otros_equipos.mean()))
    
    # Media de tarjetas rojas de la liga
    rojas_por_equipo = actas_completas_ajustadas.groupby('equipo')['Tarjetas Rojas'].sum()
    # Corregido: usar map() en lugar de apply() para objetos Index
    rojas_otros_equipos = rojas_por_equipo[rojas_por_equipo.index.map(
        lambda x: equipo_normalizado not in normalizar_nombre_equipo(x))]
    ref_tarjetas_rojas = round(rojas_otros_equipos.mean(), 1)
    
    # Media de tarjetas rojas de la liga para rivales
    ref_tr_rival = round(rojas_otros_equipos.mean(), 1)
    
    # Media de jugadores por equipo
    jugadores_por_equipo = actas_completas_df.groupby('equipo')['jugador'].nunique()
    # Corregido: usar map() en lugar de apply() para objetos Index
    jugadores_otros_equipos = jugadores_por_equipo[jugadores_por_equipo.index.map(
        lambda x: equipo_normalizado not in normalizar_nombre_equipo(x))]
    ref_num_jugadores = round(jugadores_otros_equipos.mean(), 1)
    
    # Crear métricas para sección de goles
    metricas_goles = [
        {
            'titulo': 'Goles a favor',
            'valor': goles_favor,
            'referencia': ref_goles_favor,
            'color': '#FF8C00'  # Naranja
        },
        {
            'titulo': 'Goles en contra',
            'valor': goles_contra,
            'referencia': ref_goles_contra,
            'color': '#FF4136'  # Rojo
        }
    ]
    
    # Crear métricas para sección de tarjetas
    metricas_tarjetas = [
        {
            'titulo': 'Tarjetas Amarillas',
            'valor': tarjetas_amarillas,
            'referencia': ref_tarjetas_amarillas,
            'color': '#FFD700'  # Amarillo
        },
        {
            'titulo': 'TA Rival',
            'valor': ta_rival,
            'referencia': ref_ta_rival,
            'color': '#FFD700'  # Amarillo
        },
        {
            'titulo': 'Tarjetas Rojas',
            'valor': tarjetas_rojas,
            'referencia': ref_tarjetas_rojas,
            'color': '#FF4136'  # Rojo
        },
        {
            'titulo': 'TR Rival',
            'valor': tr_rival,
            'referencia': ref_tr_rival,
            'color': '#FF4136'  # Rojo
        }
    ]
    
    # Crear métricas para sección general
    metricas_general = [
        {
            'titulo': 'Num. Jugadores',
            'valor': num_jugadores,
            'referencia': ref_num_jugadores,
            'color': '#000000'  # Negro
        },
        {
            'titulo': 'Partidos Jugados',
            'valor': partidos_jugados,
            'referencia': None,
            'color': '#000000'  # Negro
        }
    ]
    
    return {
        'goles': metricas_goles,
        'tarjetas': metricas_tarjetas,
        'general': metricas_general
    }