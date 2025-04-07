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
    
    return metricas_equipo

def realizar_clustering(datos, n_clusters=4):
    """
    Realiza clustering de equipos
    """
    # Características para el clustering
    features = [
        'goles', 'Tarjetas Amarillas', 'Tarjetas Rojas', 
        'minutos_jugados', 'jugador', 'total_sustituciones',
        'goles_primer_cuarto', 'goles_segundo_cuarto', 
        'goles_tercer_cuarto', 'goles_ultimo_cuarto'
    ]
    
    # Preparar datos para clustering
    X = datos.copy()
    
    # Verificar que tenemos suficientes datos
    if len(X) < n_clusters:
        X['cluster'] = 0
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

def crear_mapa_equipos(datos_clustered):
    """
    Crea una visualización 2D de los equipos usando PCA
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
    # Cambiado el color del grupo 1 a un azul más oscuro/intenso
    colores_cluster = [
        '#0052CC',  # Azul oscuro intenso para el Grupo 1
        '#d62728',  # Rojo
        '#2ca02c',  # Verde
        '#9467bd',  # Púrpura
        '#8c564b',  # Marrón
        '#e377c2'   # Rosa
    ]
    
    # Crear gráfico
    fig = px.scatter(
        pca_df, 
        x='PCA1', 
        y='PCA2', 
        color='Cluster',
        size='Goles',
        hover_name='Equipo',
        color_discrete_sequence=colores_cluster
    )
    
    # Personalizar para mostrar solo el nombre del equipo y el cluster en el hover
    fig.update_traces(
        hovertemplate='<b>%{hovertext}</b><br>Grupo: %{marker.color}<extra></extra>'
    )
    
    # Resaltar Penya Independent
    if not penya_data.empty:
        fig.add_trace(
            go.Scatter(
                x=penya_data['PCA1'], 
                y=penya_data['PCA2'], 
                mode='markers',
                name='Penya Independent',
                marker=dict(
                    color=PENYA_PRIMARY_COLOR, 
                    size=20, 
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
            itemsizing='constant',  # Mismo tamaño para todos los ítems
            itemwidth=30,  # Ancho fijo para los ítems
            itemclick=False,  # Desactivar click en la leyenda
            itemdoubleclick=False  # Desactivar doble click en la leyenda
        ),
        # Título del gráfico
        title="Análisis de similitud de equipos"
    )
    
    return fig

def graficar_comparativa(equipo_data, metricas_cluster, titulo="Comparativa de Métricas"):
    """
    Gráfico de barras comparando un equipo con la media de su cluster
    """
    # Seleccionar métricas relevantes para comparar
    metricas_comparar = [
        ('Goles', 'goles'),
        ('Tarj. Amarillas', 'Tarjetas Amarillas'),
        ('Tarj. Rojas', 'Tarjetas Rojas'),
        ('Jugadores', 'jugador'),
        ('Sustituciones', 'total_sustituciones')
    ]
    
    # Filtrar métricas que existen en ambos conjuntos
    metricas_filtradas = []
    for nombre, col in metricas_comparar:
        if col in equipo_data and col in metricas_cluster:
            metricas_filtradas.append((nombre, col))
    
    # Preparar datos para el gráfico
    nombres = [m[0] for m in metricas_filtradas]
    valores_equipo = [equipo_data[m[1]] for m in metricas_filtradas]
    valores_cluster = [metricas_cluster[m[1]] for m in metricas_filtradas]
    
    # Crear figura
    fig = go.Figure()
    
    # Añadir barras para el equipo
    fig.add_trace(go.Bar(
        x=nombres,
        y=valores_equipo,
        name=f'{equipo_data["equipo_limpio"]}',
        marker_color=PENYA_PRIMARY_COLOR
    ))
    
    # Añadir barras para la media del cluster
    fig.add_trace(go.Bar(
        x=nombres,
        y=valores_cluster,
        name=f'Media Grupo {int(equipo_data["cluster"])}',
        marker_color=PENYA_SECONDARY_COLOR
    ))
    
    # Personalizar diseño
    fig.update_layout(
        title=titulo,
        barmode='group',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig

def main():
    """
    Función principal para análisis táctico de equipos
    """
    # Eliminado: st.title("🏆 Análisis Táctico de Equipos")
    
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
    
    # Realizar clustering - cambiado a 4 clusters
    with st.spinner('Realizando análisis de patrones tácticos...'):
        try:
            datos_clustered = realizar_clustering(datos_equipos, n_clusters=4)
        except Exception as e:
            st.error(f"Error en el análisis: {str(e)}")
            return
    
    # Generar características de clusters
    caracteristicas_clusters = generar_caracteristicas_cluster(datos_clustered)
    
    # SECCIÓN 1: Mapa de equipos - Eliminado el título "Mapa de Equipos por Similitud"
    fig_mapa = crear_mapa_equipos(datos_clustered)
    st.plotly_chart(fig_mapa, use_container_width=True)
    
    with st.expander("¿Cómo interpretar este mapa?"):
        st.markdown("""
        Este mapa posiciona a cada equipo según la similitud de características:
        
        - **Equipos cercanos**: Tienen estilos de juego similares
        - **Colores**: Cada grupo representa equipos con patrones similares
        - **Tamaño**: Representa la cantidad de goles marcados
        - **Estrella**: Posición de Penya Independent
        """)
    
    # SECCIÓN 2: Características de clusters
    st.subheader("Características de los Grupos")
    
    # Mostrar características de cada cluster
    for cluster_id in sorted(caracteristicas_clusters.keys()):
        cluster_info = caracteristicas_clusters[cluster_id]
        
        # Crear un estilo visual con colores correspondientes al gráfico
        colores_cluster = [
            '#1f77b4',  # Azul más oscuro
            '#d62728',  # Rojo
            '#2ca02c',  # Verde
            '#9467bd',  # Púrpura
            '#8c564b',  # Marrón
            '#e377c2'   # Rosa
        ]
        
        color_cluster = colores_cluster[(cluster_id - 1) % len(colores_cluster)]
        
        st.markdown(
            f"""
            <div style="
                border-left: 5px solid {color_cluster};
                padding-left: 15px;
                margin-bottom: 20px;
            ">
            <h3>Grupo {cluster_id}</h3>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
        # Mostrar descripciones
        if cluster_info['descripcion']:
            for desc in cluster_info['descripcion']:
                st.markdown(f"- {desc}")
        else:
            st.markdown("*No se identificaron características distintivas*")
        
        # Mostrar equipos
        with st.expander(f"Ver equipos del Grupo {cluster_id} ({len(cluster_info['equipos'])} equipos)"):
            # Ordenar equipos alfabéticamente, con Penya primero si está en el grupo
            equipos_ordenados = sorted(cluster_info['equipos'])
            # Mover Penya al principio si existe
            penya_equipos = [e for e in equipos_ordenados if 'PENYA' in e.upper()]
            otros_equipos = [e for e in equipos_ordenados if 'PENYA' not in e.upper()]
            equipos_mostrar = penya_equipos + otros_equipos
            
            # Mostrar en columnas para aprovechar espacio
            cols = st.columns(3)
            for i, equipo in enumerate(equipos_mostrar):
                with cols[i % 3]:
                    if 'PENYA' in equipo.upper():
                        st.markdown(f"**{equipo}**")
                    else:
                        st.markdown(f"{equipo}")

# SECCIÓN 3: Selector de equipo y análisis comparativo
    st.markdown("---")
    st.subheader("Análisis Comparativo de Equipos")
    
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
    
    st.markdown(f"**{equipo_seleccionado}** pertenece al **Grupo {cluster_id}**")
    
    # Métricas del equipo vs media del cluster
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Goles", 
            f"{equipo_data['goles']:.0f}", 
            f"{(equipo_data['goles'] - caracteristicas_clusters[cluster_id]['metricas']['goles']):.1f}"
        )
    
    with col2:
        st.metric(
            "Tarjetas Amarillas", 
            f"{equipo_data['Tarjetas Amarillas']:.0f}", 
            f"{(equipo_data['Tarjetas Amarillas'] - caracteristicas_clusters[cluster_id]['metricas']['Tarjetas Amarillas']):.1f}"
        )
    
    with col3:
        st.metric(
            "Jugadores", 
            f"{equipo_data['jugador']:.0f}", 
            f"{(equipo_data['jugador'] - caracteristicas_clusters[cluster_id]['metricas']['jugador']):.1f}"
        )
    
    # Gráfico comparativo
    st.plotly_chart(
        graficar_comparativa(
            equipo_data, 
            caracteristicas_clusters[cluster_id]['metricas'], 
            f"Comparativa: {equipo_seleccionado} vs Media del Grupo"
        ), 
        use_container_width=True
    )
    
    # Equipos similares
    st.subheader("Equipos con Estilo Similar")
    
    # Encontrar equipos del mismo cluster
    equipos_similares = [e for e in caracteristicas_clusters[cluster_id]['equipos'] 
                       if e != equipo_seleccionado]
    
    if equipos_similares:
        # Si hay más de 5 equipos, mostrar solo los 5 primeros
        if len(equipos_similares) > 5:
            with st.expander(f"Ver los {len(equipos_similares)} equipos similares"):
                cols = st.columns(3)
                for i, equipo in enumerate(equipos_similares):
                    with cols[i % 3]:
                        st.markdown(f"- {equipo}")
        else:
            cols = st.columns(3)
            for i, equipo in enumerate(equipos_similares):
                with cols[i % 3]:
                    st.markdown(f"- {equipo}")
    else:
        st.markdown("No se encontraron otros equipos en el mismo grupo")
    
    # Comparativa con Penya Independent
    if 'PENYA INDEPENDENT' in equipo_seleccionado.upper():
        st.markdown("*Ya estás viendo el análisis de Penya Independent*")
    else:
        st.markdown("---")
        st.subheader("Comparativa con Penya Independent")
        
        # Buscar Penya Independent
        penya_data = datos_clustered[datos_clustered['equipo_limpio'].str.contains('PENYA INDEPENDENT', case=False)]
        
        if not penya_data.empty:
            penya_row = penya_data.iloc[0]
            penya_nombre = penya_row['equipo_limpio']
            penya_cluster = int(penya_row['cluster'])
            
            # Indicar si están en el mismo grupo o no
            if penya_cluster == cluster_id:
                st.markdown(f"**{equipo_seleccionado}** y **{penya_nombre}** pertenecen al **mismo grupo táctico** (Grupo {cluster_id})")
            else:
                st.markdown(f"**{equipo_seleccionado}** (Grupo {cluster_id}) y **{penya_nombre}** (Grupo {penya_cluster}) pertenecen a **diferentes grupos tácticos**")
            
            # Gráfico comparativo
            st.plotly_chart(
                graficar_comparativa(
                    equipo_data, 
                    {k: penya_row[k] for k in equipo_data.index if k in penya_row}, 
                    f"Comparativa: {equipo_seleccionado} vs {penya_nombre}"
                ), 
                use_container_width=True
            )

            # Análisis textual de diferencias
            st.markdown("#### Diferencias clave:")
            
            diferencias = []
            for metrica, col in [('Goles', 'goles'), ('Tarjetas', 'Tarjetas Amarillas'),
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
                            diferencias.append(f"**{metrica}**: {equipo_seleccionado} tiene un {abs(diff_pct):.1f}% más que {penya_nombre}")
                        else:
                            diferencias.append(f"**{metrica}**: {equipo_seleccionado} tiene un {abs(diff_pct):.1f}% menos que {penya_nombre}")
            
            if diferencias:
                for diff in diferencias:
                    st.markdown(f"- {diff}")
            else:
                st.markdown("No se encontraron diferencias significativas en las métricas principales")
        else:
            st.warning("No se encontraron datos de Penya Independent en el análisis")

if __name__ == "__main__":
    # Configurar la página
    page_config()
    
    # Ejecutar la función principal
    main()