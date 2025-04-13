"""
Análisis de Machine Learning para clustering de equipos
"""
import re
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

from utils.data import cargar_datos
from utils.constants import PENYA_PRIMARY_COLOR, PENYA_SECONDARY_COLOR
from utils.ui import page_config
from calculos.calculo_equipo import calcular_goles_contra
from utils.pdf_export import show_download_button  

def limpiar_nombre_equipo(nombre):
    """
    Limpia y normaliza el nombre de un equipo
    """
    if pd.isna(nombre):
        return ""
    
    nombre = str(nombre)
    nombre = re.sub(r'\s+', ' ', nombre).strip()
    nombre = nombre.split('(')[0].split('-')[0].strip()
    return nombre

def distribucion_goles_por_periodo(data, equipo):
    """
    Calcula la distribución de goles por periodos para un equipo
    """
    try:
        actas = data['actas']
        
        # Intentar encontrar el equipo exacto
        jugadores_equipo = actas[actas['equipo'] == equipo]['jugador'].unique()
        
        # Si no encontramos jugadores, intentar una búsqueda más flexible
        if len(jugadores_equipo) == 0:
            actas['equipo_normalizado'] = actas['equipo'].apply(limpiar_nombre_equipo)
            jugadores_equipo = actas[actas['equipo_normalizado'] == equipo]['jugador'].unique()
        
        # Si todavía no tenemos jugadores, devolver ceros
        if len(jugadores_equipo) == 0:
            return {
                'primer_cuarto': 0,
                'segundo_cuarto': 0,
                'tercer_cuarto': 0,
                'ultimo_cuarto': 0
            }
        
        # Filtrar goles por jugadores del equipo
        goles_equipo = data['goles'][data['goles']['jugador'].isin(jugadores_equipo)]
        
        # Definir periodos del partido (por cuartos)
        periodos = {
            'primer_cuarto': (0, 22),
            'segundo_cuarto': (23, 45),
            'tercer_cuarto': (46, 67),
            'ultimo_cuarto': (68, 90)
        }
        
        distribucion = {periodo: 0 for periodo in periodos.keys()}
        for nombre, (inicio, fin) in periodos.items():
            goles_periodo = goles_equipo[
                (goles_equipo['Minuto'] >= inicio) & 
                (goles_equipo['Minuto'] <= fin)
            ]
            distribucion[nombre] = len(goles_periodo)
        
        return distribucion
    
    except Exception:
        # En caso de error, devolver valores por defecto
        return {
            'primer_cuarto': 0,
            'segundo_cuarto': 0,
            'tercer_cuarto': 0,
            'ultimo_cuarto': 0
        }

def preparar_datos_clustering():
    """
    Prepara datos de rendimiento de equipos para análisis táctico
    """
    # Cargar datos
    data = cargar_datos()
    actas = data['actas'].copy()
    
    # Limpiar nombres de equipos
    actas['equipo_limpio'] = actas['equipo'].apply(limpiar_nombre_equipo)
    actas = actas[actas['equipo_limpio'] != '']
    
    # Calcular métricas por equipo
    metricas_equipo = actas.groupby('equipo_limpio').agg({
        'goles': 'sum',
        'Tarjetas Amarillas': 'sum',
        'Tarjetas Rojas': 'sum',
        'minutos_jugados': 'sum',
        'jugador': 'nunique'
    }).reset_index()
    
    # Añadir distribución de goles por periodos
    goles_por_periodo = {}
    for equipo in metricas_equipo['equipo_limpio']:
        goles_por_periodo[equipo] = distribucion_goles_por_periodo(data, equipo)
    
    # Añadir columnas de goles por periodo
    for periodo in ['primer_cuarto', 'segundo_cuarto', 'tercer_cuarto', 'ultimo_cuarto']:
        metricas_equipo[f'goles_{periodo}'] = metricas_equipo['equipo_limpio'].map(
            lambda x: goles_por_periodo.get(x, {}).get(periodo, 0)
        )
    
    # Calcular sustituciones
    sustituciones_por_equipo = data['sustituciones'].copy()
    sustituciones_por_equipo['equipo_limpio'] = sustituciones_por_equipo['equipo'].apply(limpiar_nombre_equipo)
    sustituciones_por_equipo = sustituciones_por_equipo[sustituciones_por_equipo['equipo_limpio'] != '']
    
    if not sustituciones_por_equipo.empty:
        sustituciones_agrupadas = sustituciones_por_equipo.groupby('equipo_limpio').agg({
            'jugador_sale': 'count'
        }).reset_index()
        sustituciones_agrupadas.columns = ['equipo_limpio', 'total_sustituciones']
        
        # Combinar métricas
        metricas_equipo = metricas_equipo.merge(
            sustituciones_agrupadas, 
            on='equipo_limpio', 
            how='left'
        )
    else:
        # Si no hay datos de sustituciones, añadir columna con ceros
        metricas_equipo['total_sustituciones'] = 0
    
    # Rellenar valores NaN con 0
    metricas_equipo = metricas_equipo.fillna(0)
    
    # Limpiar duplicados
    metricas_equipo = metricas_equipo.drop_duplicates(subset='equipo_limpio', keep='first')
    
    # Convertir todos los valores a numérico (excepto equipo_limpio)
    for col in metricas_equipo.columns:
        if col != 'equipo_limpio':
            metricas_equipo[col] = pd.to_numeric(metricas_equipo[col], errors='coerce').fillna(0)
    
    # Asegurarse de que no hay listas en equipo_limpio
    metricas_equipo = metricas_equipo[metricas_equipo['equipo_limpio'].apply(lambda x: not isinstance(x, list))]
    
    # Calcular goles en contra
    goles_contra = {}
    for equipo in metricas_equipo['equipo_limpio']:
        try:
            # Filtrar los datos del equipo específico
            actas_equipo = actas[actas['equipo_limpio'] == equipo]
            
            # Obtener partidos de este equipo
            jornadas_equipo = set(actas_equipo['jornada'].unique())
            partidos_equipo = data['jornadas'][data['jornadas']['jornada'].isin(jornadas_equipo)]
            
            # Calcular goles en contra
            goles_contra_equipo = calcular_goles_contra(
                actas_equipo, 
                partidos_equipo, 
                data['actas'], 
                equipo_seleccionado=equipo
            )
            
            goles_contra[equipo] = goles_contra_equipo
        except Exception:
            # Si falla, asignar un valor basado en la media
            goles_contra[equipo] = metricas_equipo[metricas_equipo['equipo_limpio'] == equipo]['goles'].iloc[0] * 0.8

    # Añadir columna de goles en contra
    metricas_equipo['goles_contra'] = metricas_equipo['equipo_limpio'].map(goles_contra)
    
    return metricas_equipo

def realizar_clustering(datos, n_clusters=4):
    """
    Realiza clustering de equipos
    """
    # Características para el clustering
    features = [
        'goles', 'goles_contra', 'Tarjetas Amarillas', 'Tarjetas Rojas', 
        'minutos_jugados', 'jugador', 'total_sustituciones',
        'goles_primer_cuarto', 'goles_segundo_cuarto', 
        'goles_tercer_cuarto', 'goles_ultimo_cuarto'
    ]
    
    # Preparar datos para clustering
    X = datos.copy()
    
    # Verificar que tenemos suficientes datos
    if len(X) < n_clusters:
        X['cluster'] = 1  # Comenzar desde 1 en lugar de 0
        return X
    
    # Verificar y limpiar tipos de datos
    for col in features:
        if col not in X.columns:
            X[col] = 0
        X[col] = pd.to_numeric(X[col], errors='coerce').fillna(0)
    
    # Preparar datos para clustering
    X_cluster = X[features]
    
    # Normalizar datos
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_cluster)
    
    # Realizar clustering
    try:
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        X['cluster'] = kmeans.fit_predict(X_scaled)
        
        # Ajustar los clusters para que comiencen desde 1 en lugar de 0
        X['cluster'] = X['cluster'] + 1
    except Exception:
        X['cluster'] = 1  # Si falla, todos pertenecen al cluster 1
    
    return X

def generar_caracteristicas_cluster(datos_clustered):
    """
    Genera descripciones de las características principales de cada cluster
    """
    # Obtener estadísticas globales para comparaciones
    medias_globales = {
        'goles': datos_clustered['goles'].mean(),
        'goles_contra': datos_clustered['goles_contra'].mean(),
        'Tarjetas Amarillas': datos_clustered['Tarjetas Amarillas'].mean(),
        'Tarjetas Rojas': datos_clustered['Tarjetas Rojas'].mean(),
        'jugador': datos_clustered['jugador'].mean(),
        'total_sustituciones': datos_clustered['total_sustituciones'].mean()
    }
    
    # Características por cluster
    caracteristicas_clusters = {}
    
    # Procesar cada cluster
    for cluster_id in datos_clustered['cluster'].unique():
        cluster_data = datos_clustered[datos_clustered['cluster'] == cluster_id]
        
        # Métricas promedio del cluster
        metricas_cluster = {
            'goles': cluster_data['goles'].mean(),
            'goles_contra': cluster_data['goles_contra'].mean(),
            'Tarjetas Amarillas': cluster_data['Tarjetas Amarillas'].mean(),
            'Tarjetas Rojas': cluster_data['Tarjetas Rojas'].mean(),
            'jugador': cluster_data['jugador'].mean(),
            'total_sustituciones': cluster_data['total_sustituciones'].mean()
        }
        
        # Calcular distribución de goles por periodo
        periodos = ['goles_primer_cuarto', 'goles_segundo_cuarto', 'goles_tercer_cuarto', 'goles_ultimo_cuarto']
        dist_periodos = {}
        for periodo in periodos:
            dist_periodos[periodo] = cluster_data[periodo].mean()
        
        # Determinar el periodo con más goles
        if sum(dist_periodos.values()) > 0:
            periodo_max = max(dist_periodos, key=dist_periodos.get)
            periodos_textos = {
                'goles_primer_cuarto': 'primeros minutos (0-22\')',
                'goles_segundo_cuarto': 'final del primer tiempo (23-45\')',
                'goles_tercer_cuarto': 'inicio del segundo tiempo (46-67\')',
                'goles_ultimo_cuarto': 'tramo final (68-90\')'
            }
            texto_periodo_max = periodos_textos.get(periodo_max, periodo_max)
        else:
            texto_periodo_max = None
        
        # Generar descripciones
        descripcion = []
        
        # Analizar ofensiva
        if metricas_cluster['goles'] > medias_globales['goles'] * 1.2:
            descripcion.append(f"Alta capacidad goleadora ({metricas_cluster['goles']:.1f} goles/equipo)")
        elif metricas_cluster['goles'] < medias_globales['goles'] * 0.8:
            descripcion.append(f"Baja producción ofensiva ({metricas_cluster['goles']:.1f} goles/equipo)")
        
        # Analizar goles en contra
        if metricas_cluster['goles_contra'] > medias_globales['goles_contra'] * 1.2:
            descripcion.append(f"Defensa vulnerable ({metricas_cluster['goles_contra']:.1f} goles recibidos/equipo)")
        elif metricas_cluster['goles_contra'] < medias_globales['goles_contra'] * 0.8:
            descripcion.append(f"Defensa sólida ({metricas_cluster['goles_contra']:.1f} goles recibidos/equipo)")
        
        # Analizar disciplina
        if metricas_cluster['Tarjetas Amarillas'] > medias_globales['Tarjetas Amarillas'] * 1.2:
            descripcion.append(f"Juego intenso/físico ({metricas_cluster['Tarjetas Amarillas']:.1f} TA/equipo)")
        elif metricas_cluster['Tarjetas Amarillas'] < medias_globales['Tarjetas Amarillas'] * 0.8:
            descripcion.append(f"Juego disciplinado ({metricas_cluster['Tarjetas Amarillas']:.1f} TA/equipo)")
        
        # Analizar plantilla
        if metricas_cluster['jugador'] > medias_globales['jugador'] * 1.2:
            descripcion.append(f"Amplia rotación de jugadores ({metricas_cluster['jugador']:.1f} jugadores/equipo)")
        elif metricas_cluster['jugador'] < medias_globales['jugador'] * 0.8:
            descripcion.append(f"Plantilla reducida ({metricas_cluster['jugador']:.1f} jugadores/equipo)")
        
        # Analizar momento de goles
        if texto_periodo_max:
            descripcion.append(f"Mayor efectividad en los {texto_periodo_max}")
        
        # Guardar características
        caracteristicas_clusters[cluster_id] = {
            'descripcion': descripcion,
            'metricas': metricas_cluster,
            'equipos': list(cluster_data['equipo_limpio'])
        }
    
    return caracteristicas_clusters

# Modificación para la función crear_mapa_equipos
def crear_mapa_equipos(datos_clustered, colores_cluster=None):
    """
    Crea una visualización 2D de los equipos usando PCA

    Args:
        datos_clustered: DataFrame con datos de los equipos
        colores_cluster: Lista de colores para los clusters (opcional)
    """
    # Características para PCA
    features = [col for col in datos_clustered.columns if col not in ['equipo_limpio', 'cluster']]
    
    # Preparar datos para PCA
    X = datos_clustered[features]
    
    # Reducir a 2 dimensiones
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(StandardScaler().fit_transform(X))
    
    # Crear DataFrame para visualización
    pca_df = pd.DataFrame({
        'PCA1': X_pca[:, 0],
        'PCA2': X_pca[:, 1],
        'Equipo': datos_clustered['equipo_limpio'],
        'Cluster': datos_clustered['cluster'].astype(int),
        'Goles': datos_clustered['goles']
    })
    
    # Encontrar Penya Independent
    penya_data = pca_df[pca_df['Equipo'].str.contains('PENYA INDEPENDENT', case=False)]
    
    # Definir colores más intensos para los clusters 
    if colores_cluster is None:
        colores_cluster = [
            '#00397A',  # Azul muy oscuro para el Grupo 1
            '#d62728',  # Rojo
            '#2ca02c',  # Verde
            '#9467bd',  # Púrpura
            '#8c564b',  # Marrón
            '#e377c2'   # Rosa
    ]
    
    # Crear gráfico con puntos del mismo tamaño (quitando size='Goles')
    fig = px.scatter(
        pca_df, 
        x='PCA1', 
        y='PCA2', 
        color='Cluster',
        text='Equipo',  
        hover_name='Equipo',
        color_discrete_sequence=colores_cluster
    )
    
    # Personalizar para mostrar solo el nombre del equipo y el cluster en el hover
    fig.update_traces(
        textposition='top center',  # Posición de las etiquetas de texto
        marker=dict(size=12),  # Tamaño fijo para todos los puntos
        hovertemplate='<b>%{hovertext}</b><br>Grupo: %{marker.color}<extra></extra>'
    )
    
    # Resaltar Penya Independent
    if not penya_data.empty:
        fig.add_trace(
            go.Scatter(
                x=penya_data['PCA1'], 
                y=penya_data['PCA2'], 
                mode='markers+text',
                name='Penya Independent',
                text=penya_data['Equipo'],
                textposition='top center',
                marker=dict(
                    color=PENYA_PRIMARY_COLOR, 
                    size=15, 
                    symbol='star',
                    line=dict(width=2, color='white')
                ),
                hovertext=penya_data['Equipo']
            )
        )
    
    # Ajustar la leyenda para separar Penya Independent de los clusters
    fig.update_layout(
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            itemsizing='constant',
            itemwidth=30,
            itemclick=False,
            itemdoubleclick=False
        ),
        title=None,  
        # Ampliar los límites del gráfico para evitar superposición de texto
        xaxis=dict(
            range=[pca_df['PCA1'].min() * 1.2, pca_df['PCA1'].max() * 1.2],
            showgrid=True,
            gridcolor='rgba(211,211,211,0.3)',
            title=None  
        ),
        yaxis=dict(
            range=[pca_df['PCA2'].min() * 1.2, pca_df['PCA2'].max() * 1.2],
            showgrid=True,
            gridcolor='rgba(211,211,211,0.3)',
            title=None  
        ),
        width=800,  
        height=600  
    )
    
    return fig, colores_cluster

# Modificación para la función graficar_comparativa
def graficar_comparativa(equipo_data, metricas_cluster, titulo=None):
    """
    Gráfico de barras comparando un equipo con la media de su cluster
    """
    # Seleccionar métricas relevantes para comparar
    metricas_comparar = [
        ('Goles a favor', 'goles'),
        ('Goles en contra', 'goles_contra'),
        ('Tarj. Amarillas', 'Tarjetas Amarillas'),
        ('Tarj. Rojas', 'Tarjetas Rojas'),
        ('Jugadores', 'jugador')
    ]
    
    # Filtrar métricas que existen en ambos conjuntos
    metricas_filtradas = []
    for nombre, col in metricas_comparar:
        if col in equipo_data and col in metricas_cluster:
            metricas_filtradas.append((nombre, col))
    
    # Preparar datos para el gráfico
    nombres = [m[0] for m in metricas_filtradas]
    valores_equipo = [equipo_data[m[1]] for m in metricas_filtradas]
    valores_comparacion = [metricas_cluster[m[1]] for m in metricas_filtradas]
    
    # Crear figura
    fig = go.Figure()
    
    # Añadir barras para el equipo seleccionado
    fig.add_trace(go.Bar(
        x=nombres,
        y=valores_equipo,
        name=f'{equipo_data["equipo_limpio"]}',
        marker_color=PENYA_PRIMARY_COLOR,
        text=valores_equipo,  # Mostrar valores en las barras
        textposition='auto'   # Posición automática del texto
    ))
    
    # Añadir barras para la comparación
    fig.add_trace(go.Bar(
        x=nombres,
        y=valores_comparacion,
        name='Penya Independent',  # Nombre fijo en lugar de variable
        marker_color=PENYA_SECONDARY_COLOR,
        text=valores_comparacion,  # Mostrar valores en las barras
        textposition='auto'        # Posición automática del texto
    ))
    
    # Personalizar diseño para hacerlo más compacto
    fig.update_layout(
        # Eliminamos completamente el título o lo establecemos explícitamente a ""
        title="",  # Título vacío en lugar de None o título pasado como parámetro
        barmode='group',
        height=300,  # Reducir altura
        margin=dict(l=20, r=20, t=40, b=20),  
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        # Eliminar títulos de ejes para evitar undefined
        xaxis_title="",
        yaxis_title=""
    )
    
    return fig

def graficar_comparativa(equipo_data, metricas_cluster, titulo=None):
    """
    Gráfico de barras comparando un equipo con la media de su cluster
    """
    # Seleccionar métricas relevantes para comparar
    metricas_comparar = [
        ('Goles a favor', 'goles'),
        ('Goles en contra', 'goles_contra'),
        ('Tarj. Amarillas', 'Tarjetas Amarillas'),
        ('Tarj. Rojas', 'Tarjetas Rojas'),
        ('Jugadores', 'jugador')
    ]
    
    # Filtrar métricas que existen en ambos conjuntos
    metricas_filtradas = []
    for nombre, col in metricas_comparar:
        if col in equipo_data and col in metricas_cluster:
            metricas_filtradas.append((nombre, col))
    
    # Preparar datos para el gráfico
    nombres = [m[0] for m in metricas_filtradas]
    valores_equipo = [equipo_data[m[1]] for m in metricas_filtradas]
    valores_comparacion = [metricas_cluster[m[1]] for m in metricas_filtradas]
    
    # Crear figura
    fig = go.Figure()
    
    # Añadir barras para el equipo seleccionado
    fig.add_trace(go.Bar(
        x=nombres,
        y=valores_equipo,
        name=f'{equipo_data["equipo_limpio"]}',
        marker_color=PENYA_PRIMARY_COLOR,
        text=valores_equipo,  # Mostrar valores en las barras
        textposition='auto'   # Posición automática del texto
    ))
    
    # Añadir barras para la comparación
    fig.add_trace(go.Bar(
        x=nombres,
        y=valores_comparacion,
        name='Penya Independent',  # Nombre fijo en lugar de variable
        marker_color=PENYA_SECONDARY_COLOR,
        text=valores_comparacion,  # Mostrar valores en las barras
        textposition='auto'        # Posición automática del texto
    ))
    
    # Personalizar diseño para hacerlo más compacto
    fig.update_layout(
        # Título vacío explícito en lugar de None o título pasado como parámetro
        title="",
        barmode='group',
        height=300,  # Reducir altura
        margin=dict(l=20, r=20, t=40, b=20),  # Reducir márgenes
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        # Eliminar títulos de ejes para evitar undefined
        xaxis_title="",
        yaxis_title=""
    )
    
    return fig

def main():
    """
    Función principal para análisis táctico de equipos
    """
    # Preparar datos
    with st.spinner('Procesando datos de equipos...'):
        try:
            datos_equipos = preparar_datos_clustering()
            
            if datos_equipos.empty or len(datos_equipos) < 2:
                st.warning("No hay suficientes datos para realizar el análisis. Se necesitan al menos 2 equipos diferentes.")
                return
            
        except Exception as e:
            st.error(f"Error al preparar datos: {str(e)}")
            return
    
    # Realizar clustering
    with st.spinner('Realizando análisis de patrones tácticos...'):
        try:
            datos_clustered = realizar_clustering(datos_equipos, n_clusters=4)
        except Exception as e:
            st.error(f"Error en el análisis: {str(e)}")
            return
    
    # Generar características de clusters
    caracteristicas_clusters = generar_caracteristicas_cluster(datos_clustered)
    
    # SECCIÓN 1: Mapa de equipos con botón de descarga a la derecha
    col1, col2 = st.columns([4, 1])
    
    # Título en la columna izquierda
    with col1:
        st.subheader("Análisis de similitud de equipos")
    
    # Selector de equipo y botón en columna derecha
    with col2:
        # Crear un contenedor para datos PDF 
        pdf_data = {
            'datos_clustered': datos_clustered,
            'caracteristicas_clusters': caracteristicas_clusters,
            'mapa_fig': None,  
            'comparativa_fig': None  
        }
        
        # Estilo para el botón alineado a la derecha
        st.markdown("""
        <style>
        div.stButton > button {
            float: right;
        }
        /* Eliminar etiquetas "undefined" */
        .js-plotly-plot .plotly .gtitle {
            display: none !important;
        }
        /* Ocultar títulos de ejes que puedan mostrar undefined */
        .js-plotly-plot .plotly .xtitle, 
        .js-plotly-plot .plotly .ytitle {
            display: none !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Mostrar botón de descarga sin equipo seleccionado aún
        # (El equipo se seleccionará más adelante)
        st.text("")  
    
    # Mostrar el gráfico de dispersión
    fig_mapa, colores_cluster = crear_mapa_equipos(datos_clustered)
    st.plotly_chart(fig_mapa, use_container_width=True)
    
    # SECCIÓN 2: Selector de equipo y análisis
    st.markdown("---")
    
    # Lista de todos los equipos
    todos_equipos = sorted(datos_clustered['equipo_limpio'].unique())
    
    # Poner Penya Independent al principio de la lista
    penya_independents = [e for e in todos_equipos if 'PENYA INDEPENDENT' in e]
    otros_equipos = [e for e in todos_equipos if 'PENYA INDEPENDENT' not in e]
    equipos_ordenados = penya_independents + otros_equipos
    
    # Selector de equipo
    equipo_seleccionado = st.selectbox(
        "Seleccione un equipo para analizar:",
        equipos_ordenados
    )
    
    # Obtener datos del equipo seleccionado
    equipo_data = datos_clustered[datos_clustered['equipo_limpio'] == equipo_seleccionado].iloc[0]
    cluster_id = int(equipo_data['cluster'])
    
    # Datos del cluster al que pertenece el equipo
    cluster_info = caracteristicas_clusters[cluster_id]
    
    # Encontrar Penya Independent para comparación
    penya_data = datos_clustered[datos_clustered['equipo_limpio'].str.contains('PENYA INDEPENDENT', case=False)]
    
    if penya_data.empty:
        st.warning("No se encontraron datos de Penya Independent para comparación")
        return
    
    penya_row = penya_data.iloc[0]
    penya_nombre = penya_row['equipo_limpio']
    penya_cluster = int(penya_row['cluster'])
    
    # SECCIÓN 3: Análisis del equipo seleccionado
    st.subheader(f"Análisis de {equipo_seleccionado}")
    
    # Dividir en dos columnas para organizar mejor la información
    col_info, col_comparativa = st.columns([1, 1])
    
    with col_info:
        # Información básica del equipo
        st.markdown(f"**{equipo_seleccionado}** pertenece al **Grupo {cluster_id}**")
        
        # Mostrar características del cluster
        st.markdown("#### Características del grupo:")
        if cluster_info['descripcion']:
            for desc in cluster_info['descripcion']:
                st.markdown(f"- {desc}")
        else:
            st.markdown("*No se identificaron características distintivas*")
        
        # Mostrar equipos similares
        st.markdown("#### Equipos similares:")
        equipos_similares = [e for e in cluster_info['equipos'] 
                           if e != equipo_seleccionado][:5]  # Mostrar solo 5
        
        if equipos_similares:
            for equipo in equipos_similares:
                st.markdown(f"- {equipo}")
        else:
            st.markdown("*No se encontraron otros equipos en el mismo grupo*")
    
    # Sección de comparación con Penya Independent
    with col_comparativa:
        # Solo mostrar la comparativa si no es Penya Independent
        if 'PENYA INDEPENDENT' not in equipo_seleccionado.upper():
            st.markdown("#### Comparativa con Penya Independent:")
            
            # Indicar si están en el mismo grupo o no
            if penya_cluster == cluster_id:
                st.markdown(f"**{equipo_seleccionado}** y **{penya_nombre}** pertenecen al **mismo grupo táctico** (Grupo {cluster_id})")
            else:
                st.markdown(f"**{equipo_seleccionado}** (Grupo {cluster_id}) y **{penya_nombre}** (Grupo {penya_cluster}) pertenecen a **diferentes grupos tácticos**")
            
            # Diferencias clave en formato compacto
            st.markdown("**Diferencias clave:**")
            
            diferencias = []
            for metrica, col in [('Goles a favor', 'goles'), ('Goles en contra', 'goles_contra'), ('Tarjetas', 'Tarjetas Amarillas'),
                                ('Jugadores', 'jugador'), ('Sustituciones', 'total_sustituciones')]:
                if col in equipo_data and col in penya_row:
                    valor1 = equipo_data[col]
                    valor2 = penya_row[col]
                    
                    if valor2 != 0:
                        diff_pct = ((valor1 - valor2) / valor2) * 100
                    else:
                        diff_pct = 0 if valor1 == 0 else 100
                    
                    if abs(diff_pct) > 15:  # Solo mostrar diferencias significativas
                        if diff_pct > 0:
                            if col == 'goles_contra':
                                # Para goles en contra, más es peor
                                diferencias.append(f"**{metrica}**: {abs(diff_pct):.1f}% más")
                            else:
                                diferencias.append(f"**{metrica}**: {abs(diff_pct):.1f}% más")
                        else:
                            if col == 'goles_contra':
                                # Para goles en contra, menos es mejor
                                diferencias.append(f"**{metrica}**: {abs(diff_pct):.1f}% menos")
                            else:
                                diferencias.append(f"**{metrica}**: {abs(diff_pct):.1f}% menos")
            
            if diferencias:
                for diff in diferencias:
                    st.markdown(f"- {diff}")
            else:
                st.markdown("*No se encontraron diferencias significativas*")
            
            # Gráfico comparativo sin título (quitamos el parámetro del título)
            comparativa_fig = graficar_comparativa(
                equipo_data, 
                {k: penya_row[k] for k in equipo_data.index if k in penya_row},
                titulo=""  # Título vacío explícito
            )
            st.plotly_chart(comparativa_fig, use_container_width=True)
        else:
            st.markdown("#### Información:")
            st.markdown("Este es el análisis de Penya Independent, por lo que no se realiza comparación consigo mismo.")
            comparativa_fig = None  # No hay gráfico comparativo cuando es Penya Independent
    
    # Actualizar los datos del PDF para incluir el equipo seleccionado y las figuras
    pdf_data['mapa_fig'] = fig_mapa
    pdf_data['comparativa_fig'] = comparativa_fig if 'PENYA INDEPENDENT' not in equipo_seleccionado.upper() else None
    pdf_data['cluster_colors'] = colores_cluster  # Añadir los colores de los clusters

    # Actualizar el botón de descarga en la columna superior derecha
    with col2:
        show_download_button(pdf_data, 'ml', equipo_seleccionado=equipo_seleccionado)

if __name__ == "__main__":
    # Configurar la página
    page_config()
    
    # Ejecutar la función principal
    main()