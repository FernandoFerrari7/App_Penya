#####################################################################################
### - Importacion de librerias
#####################################################################################

import requests  # Libreria para realizar solicitudes HTTP a paginas web
from bs4 import BeautifulSoup  # Librería para analizar documentos HTML y extraer datos
import os  # Librería para interactuar con el sistema operativo, por ejemplo, para crear carpetas
import pandas as pd  # Librería para manipular datos y trabajar con estructuras como DataFrames
import time  # Librería para manejar tiempos y pausas
import random  # Librería para generar valores aleatorios
import re  # Librería para trabajar con expresiones regulares
from urllib.parse import parse_qsl, urljoin, urlparse
import glob
#from lectura_actas_utils import *
import glob
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import sys



#####################################################################################
### - Definicion de las funciones
#####################################################################################

# Datos generales del partido
def get_match_data(soup):

    # Extraer los nombres de los equipos local y visitante
    equipo_local = soup.find('div', class_='font_widgetL').text.strip()
    equipo_visitante = soup.find('div', class_='font_widgetV').text.strip()

    # Extraer el número de jornada
    jornada_text = soup.find('h5', class_='font-grey-cascade').text.strip()
    jornada_numero = jornada_text.split('Jornada')[1].split()[0]

    # Función para extraer los nombres y números de los jugadores de una tabla
    def extract_players(table, team, status, location):
        players = []
        rows = table.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            if len(cols) > 1:
                number = cols[0].text.strip()
                name = cols[1].text.strip()
                players.append((number, name, team, status, location))
        return players

    # Extraer los jugadores para ambos equipos
    tables = soup.find_all('table', class_='table table-striped table-hover' , width= '100%')

    # Local team
    local_titulares_table = tables[0]
    local_suplentes_table = tables[1]

    # Visitor team
    visitor_titulares_table = tables[3]
    visitor_suplentes_table = tables[4]

    local_titulares_players = extract_players(local_titulares_table, equipo_local, "Titular", "Local")
    local_suplentes_players = extract_players(local_suplentes_table, equipo_local, "Suplente", "Local")
    visitor_titulares_players = extract_players(visitor_titulares_table, equipo_visitante, "Titular", "Visitante")
    visitor_suplentes_players = extract_players(visitor_suplentes_table, equipo_visitante, "Suplente", "Visitante")

    # Crear dataframes para ambos equipos
    df_local_titulares = pd.DataFrame(local_titulares_players, columns=['numero', 'jugador', 'equipo', 'status', 'localizacion'])
    df_local_suplentes = pd.DataFrame(local_suplentes_players, columns=['numero', 'jugador', 'equipo', 'status', 'localizacion'])
    df_visitor_titulares = pd.DataFrame(visitor_titulares_players, columns=['numero', 'jugador', 'equipo', 'status', 'localizacion'])
    df_visitor_suplentes = pd.DataFrame(visitor_suplentes_players, columns=['numero', 'jugador', 'equipo', 'status', 'localizacion'])

    # Unir todos los jugadores en un solo dataframe
    df_all_players = pd.concat([df_local_titulares, df_local_suplentes, df_visitor_titulares, df_visitor_suplentes], ignore_index=True)

    # Añadir la columna de rival y jornada
    df_all_players['rival'] = df_all_players['equipo'].apply(lambda x: equipo_visitante if x == equipo_local else equipo_local)
    df_all_players['jornada'] = jornada_numero



    return df_all_players


# Extraemos una tabla con los goles del partido
def extract_goals_from_soup(soup):

    # Extraer los nombres de los equipos local y visitante
    equipo_local = soup.find('div', class_='font_widgetL').text.strip()
    equipo_visitante = soup.find('div', class_='font_widgetV').text.strip()

    # Extract match details
    match_details = soup.find('h5', class_='font-grey-cascade').text.strip()
    jornada = match_details.split('Jornada')[1].split()[0]

    # Extract goal information
    goals = []
    goal_rows = soup.find_all('tr')

    for row in goal_rows:
        if 'Gol normal' in str(row) or 'Gol de penalti' in str(row):
            cells = row.find_all('td')
            if len(cells) > 1:
                goal_type = 'Normal' if 'Gol normal' in str(row) else 'Penalti'
                minute = cells[1].find('span', class_='font-blue').text.strip("()'")
                scorer = cells[1].text.split(')')[1].strip()
                goals.append([jornada, minute, scorer, goal_type])

    # Create a DataFrame
    df_goals = pd.DataFrame(goals, columns=['Jornada', 'Minuto', 'jugador', 'Tipo de Gol'])

    return df_goals




#Funcion que extrae las tarjetas amarillas
def extract_cards_from_soup(soup):

    # Extraer los nombres de los equipos local y visitante
    equipo_local = soup.find('div', class_='font_widgetL').text.strip()
    equipo_visitante = soup.find('div', class_='font_widgetV').text.strip()

    # Extract match details
    match_details = soup.find('h5', class_='font-grey-cascade').text.strip()
    jornada = match_details.split('Jornada')[1].split()[0]

    # Extract card information
    cards = []
    card_rows = soup.find_all('tr')

    for row in card_rows:
        if 'tarj_amar.gif' in str(row) or 'tarj_roja.gif' in str(row):
            cells = row.find_all('td')
            if len(cells) > 1:
                card_type = 'Amarilla' if 'tarj_amar.gif' in str(row) else 'Roja'
                minute = cells[1].find('span', class_='font-blue').text.strip("()'")
                player = cells[1].text.split(')')[1].strip()
                cards.append([jornada, minute, player, card_type])

    # Create a DataFrame
    df_cards = pd.DataFrame(cards, columns=['Jornada', 'Minuto', 'jugador', 'Tipo de Tarjeta'])

    return df_cards



# Obtener los cambios realizados
def extraer_sustituciones(soup):

    # Extraer información de sustituciones
    substitutions = []
    f = 2

    # Extraer los nombres de los equipos local y visitante
    equipo_local = soup.find('div', class_='font_widgetL').text.strip()
    equipo_visitante = soup.find('div', class_='font_widgetV').text.strip()
    player_in = 'a'
    player_out = 'b'
    minuto = 0

    # Encontrar todas las filas de sustituciones en el HTML
    for table in soup.find_all("table", class_="table table-striped table-hover"):
        for row in table.find_all("tr"):
            cells = row.find_all("td")
            if len(cells) == 3:
                if f % 2 == 0:
                    player_in = cells[1].text.strip()
                    equipo = equipo_local if f % 4 == 0 else equipo_visitante
                else:
                    player = cells[1].text.strip()
                    # Separar la cadena en partes
                    partes = player.split(") ")
                    # Extraer el minuto y el nombre del jugador
                    minuto = int(partes[0][1:-1])
                    player_out = partes[1]
                substitutions.append({"jugador_entra": player_in, "jugador_sale": player_out, "Minuto": minuto})
                f += 1



    # Crear un DataFrame a partir de la lista de sustituciones
    df_substitutions = pd.DataFrame(substitutions)
    df_substitutions = df_substitutions.iloc[1::2]

    return df_substitutions



#####################################################################################
### - Funcion general que agrupa el resto de las funciones
#####################################################################################

def lectura_acta(soup):

    # Extraer los nombres de los equipos local y visitante
    equipo_local = soup.find('div', class_='font_widgetL').text.strip()
    equipo_visitante = soup.find('div', class_='font_widgetV').text.strip()

    # Extract match details
    match_details = soup.find('h5', class_='font-grey-cascade').text.strip()
    jornada = match_details.split('Jornada')[1].split()[0]



    # Obtenemos el listado de jugadores del acta
    df_jugadores = get_match_data(soup)

    # Extraer los goles del contenido HTML
    df_goals = extract_goals_from_soup(soup)

    # Guardar archivo de goles
    file_path = os.path.join('Repositorio', 'Goles', f'Goles_J{jornada}_{equipo_local}_vs_{equipo_visitante}.csv')
    df_goals.to_csv(file_path, index=False)

    # Contar el número de goles por jugador
    goles_por_jugador = df_goals['jugador'].value_counts().reset_index()
    goles_por_jugador.columns = ['jugador', 'goles']

    # Unir la información de goles al DataFrame de jugadores
    df_jugadores = df_jugadores.merge(goles_por_jugador, on='jugador', how='left')
    # Rellenar los valores NaN con 0 (jugadores que no marcaron goles) y asegurar que la columna sea de tipo entero
    df_jugadores['goles'] = df_jugadores['goles'].fillna(0).astype(int)



    # Extraer las tarjetas del contenido HTML
    df_cards = extract_cards_from_soup(soup)


    tarjetas_por_jugador = df_cards.pivot_table(index='jugador', columns='Tipo de Tarjeta', aggfunc='size', fill_value=0)
    # Asegurarse de que las columnas de tarjetas amarillas y rojas existan
    if 'Amarilla' not in tarjetas_por_jugador.columns:
        tarjetas_por_jugador['Amarilla'] = 0
    if 'Roja' not in tarjetas_por_jugador.columns:
        tarjetas_por_jugador['Roja'] = 0

    # Renombrar las columnas para mayor claridad
    tarjetas_por_jugador = tarjetas_por_jugador.rename(columns={'Amarilla': 'Tarjetas Amarillas', 'Roja': 'Tarjetas Rojas'})
    tarjetas_por_jugador

    # Unir la información de tarjetas al DataFrame de jugadores
    df_jugadores = df_jugadores.merge(tarjetas_por_jugador, left_on='jugador', right_index=True, how='left')

    # Rellenar los valores NaN con 0 (jugadores que no recibieron tarjetas)
    df_jugadores['Tarjetas Amarillas'] = df_jugadores['Tarjetas Amarillas'].fillna(0).astype(int)
    df_jugadores['Tarjetas Rojas'] = df_jugadores['Tarjetas Rojas'].fillna(0).astype(int)

    df_substitutions = extraer_sustituciones(soup)

    if not df_substitutions.empty:
        # Añadir la columna 'team' de df_jugadores a df_substitutions
        df_substitutions = df_substitutions.merge(df_jugadores[['jugador', 'equipo']], left_on='jugador_entra', right_on='jugador', how='left')
        df_substitutions.drop(columns=['jugador'], inplace=True)

        # Guardar el CSV de sustituciones
        file_path = os.path.join('Repositorio', 'Sustituciones', f'Sustituciones_J{jornada}_{equipo_local}_vs_{equipo_visitante}.csv')
        df_substitutions.to_csv(file_path, index=False)
    else:
        # Crear un DataFrame vacío con las columnas necesarias para que el cálculo de minutos no falle
        df_substitutions = pd.DataFrame(columns=['jugador_entra', 'jugador_sale', 'Minuto', 'equipo'])



    # Duración del partido
    duracion_partido = 90

    # Calcular los minutos jugados por cada jugador
    minutos_jugados = []

    for index, row in df_jugadores.iterrows():
        nombre = row['jugador']
        if row['status']=='Titular':
            # Si el jugador es titular, jugó desde el minuto 0
            minuto_inicio = 0
            # Buscar el minuto en que fue sustituido (si aplica)
            sustitucion = df_substitutions[df_substitutions['jugador_sale'] == nombre]
            if not sustitucion.empty:
                minuto_fin = sustitucion['Minuto'].values[0]
            else:
                minuto_fin = duracion_partido
        else:
            # Si el jugador es suplente, buscar el minuto en que entró
            sustitucion = df_substitutions[df_substitutions['jugador_entra'] == nombre]
            if not sustitucion.empty:
                minuto_inicio = sustitucion['Minuto'].values[0]
                minuto_fin = duracion_partido
            else:
                # Si no hay registro de sustitución, no jugó
                minuto_inicio = duracion_partido
                minuto_fin = duracion_partido

        minutos_jugados.append({
            'jugador': nombre,
            'equipo': row['equipo'],
            'minutos_jugados': minuto_fin - minuto_inicio
        })

    df_minutos_jugados = pd.DataFrame(minutos_jugados)

    # Añadir la columna minutos_jugados de df_minutos_jugados a df_jugadores por la columna nombre
    df_jugadores = df_jugadores.merge(df_minutos_jugados[['jugador', 'minutos_jugados']], on='jugador', how='left')

    # Especifica la ruta de la carpeta en tu Google Drive
    file_path = os.path.join('Repositorio', 'Actas', f'Acta_J{jornada}_{equipo_local}_vs_{equipo_visitante}.csv')
    df_jugadores.to_csv(file_path, index=False)

    return(df_jugadores)


def extraccion_jornada(cod_competicion, cod_grupo, cod_temporada, jornada):
    url = ('https://www.ffib.es/Fed/NPcd/NFG_CmpJornada?cod_primaria=1000110'
           f'&CodCompeticion={cod_competicion}'
           f'&CodGrupo={cod_grupo}'
           f'&CodTemporada={cod_temporada}'
           f'&cod_agrupacion=1'
           f'&CodJornada={jornada}'
           f'&Sch_Codigo_Delegacion=&Sch_Tipo_Juego=1')

    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--user-data-dir=/tmp/selenium_profile')

    driver = webdriver.Chrome(options=options)
    driver.get(url)
    time.sleep(5)  # espera a que cargue el JS

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()

    # Buscar número de jornada real
    jornada_text = soup.find("div", class_="col-sm-12", style="text-align:center")
    if jornada_text:
        match = re.search(r"Jornada\s+(\d+)", jornada_text.get_text())
        if match:
            jornada = int(match.group(1))

    # Buscar partidos
    partidos_raw = soup.find_all("table", width="100%")
    partidos = []

    for partido in partidos_raw:
        equipos = partido.find_all("div", class_=["font_widgetL", "font_widgetV"])
        enlace_acta = partido.find("a", title="Acta del partido")
        fecha_tag = partido.find_all("span", class_="horario")
        info_extra = partido.find("td", colspan="9")

        if len(equipos) == 2 :
            local = equipos[0].get_text(strip=True)
            visitante = equipos[1].get_text(strip=True)
            link_acta = "https://www.ffib.es" + enlace_acta.get("href") if enlace_acta else ""
            cod_acta_match = re.search(r"CodActa=(\d+)", link_acta)
            cod_acta = cod_acta_match.group(1) if cod_acta_match else ""

            # Fecha y hora
            fecha = fecha_tag[0].get_text(strip=True) if len(fecha_tag) > 0 else ""
            hora = fecha_tag[1].get_text(strip=True) if len(fecha_tag) > 1 else ""

            # Estadio
            estadio_tag = info_extra.find("a")
            estadio = estadio_tag.get_text(strip=True) if estadio_tag else ""

            # Extra info
            raw_text = info_extra.get_text(separator="\n")

            # Superficie
            superficie = next((line.replace("-", "").strip() for line in raw_text.split("\n") if "Hierba" in line or "Tierra" in line), "")

            # Árbitro
            arbitro = next((line.replace("Árbitro:", "").strip() for line in raw_text.split("\n") if "Árbitro:" in line), "")

            partidos.append({
                "cod_temporada": cod_temporada,
                "cod_competicion": cod_competicion,
                "cod_grupo":cod_grupo,
                "jornada": jornada,
                "equipo_local": local,
                "equipo_visitante": visitante,
                "cod_acta": cod_acta,
                "link_acta": link_acta,
                "acta_extraida": "No"
            })

    df = pd.DataFrame(partidos)
    return df



###################################################################################################################################################################
# Extraccion de los datos de cada Acta
###################################################################################################################################################################

print("🔄 Iniciando proceso de scraping...")

# Ruta al archivo CSV
csv_path = os.path.join('Repositorio', 'Listado_Jornadas.csv')

# Verificar si el archivo existe
if not os.path.exists(csv_path):
    print(f"❌ Error: No se encuentra el archivo {csv_path}")
    sys.exit(1)

# Leer el archivo CSV
df = pd.read_csv(csv_path)
print(f"📊 Archivo cargado: {len(df)} registros encontrados")

# Asegurar que la columna 'jornada' es numérica
df['jornada'] = pd.to_numeric(df['jornada'], errors='coerce')

# Filtrar jornadas entre 1 y 34
df_filtrado = df[df['jornada'].between(1, 34)]
print(f"📊 Jornadas filtradas (1-34): {len(df_filtrado)} registros")

# Filtrar actas extraídas (acta_extraida == "Si")
df_extraidas = df_filtrado[df_filtrado['acta_extraida'] == "Si"]

# Contar actas extraídas por jornada
conteo_extraidas = df_extraidas['jornada'].value_counts().sort_index()

# Asegurar que todas las jornadas del 1 al 34 están presentes
jornadas_completas = pd.Series(index=range(1, 35), dtype=float)
conteo_completo = jornadas_completas.add(conteo_extraidas, fill_value=0).fillna(0).astype(int)

# Obtener jornadas con menos de 9 actas extraídas
jornadas_incompletas = conteo_completo[conteo_completo < 9].index.tolist()

print(f"📋 Estado de jornadas:")
for jornada in range(1, 35):
    actas_extraidas = conteo_completo.get(jornada, 0)
    estado = "✅ Completa" if actas_extraidas >= 9 else f"❌ Incompleta ({actas_extraidas}/9)"
    print(f"  Jornada {jornada:2d}: {estado}")

if not jornadas_incompletas:
    print("\n🎉 ¡Todas las jornadas están completas! No hay nada que actualizar.")
else:
    print(f"\n🔄 Jornadas a procesar: {jornadas_incompletas}")

# Parámetros fijos
cod_competicion = 7077248
cod_grupo = 7077249
cod_temporada = 20

# Lista para guardar los DataFrames de cada jornada
dfs_jornadas = []

for jornada in jornadas_incompletas:  # de la 1 a la 34 inclusive
    print(f"🔍 Extrayendo jornada {jornada}...")
    try:
        df_jornada = extraccion_jornada(cod_competicion, cod_grupo, cod_temporada, jornada)
        if not df_jornada.empty:
            dfs_jornadas.append(df_jornada)
            print(f"✅ Jornada {jornada} extraída: {len(df_jornada)} partidos")
        else:
            print(f"⚠️  Jornada {jornada}: No se encontraron partidos")
    except Exception as e:
        print(f"❌ Error extrayendo jornada {jornada}: {str(e)}")

# Limpiar cada DataFrame de la lista eliminando filas con cod_acta nulo
dfs_jornadas = [df[df['cod_acta'] != ''] for df in dfs_jornadas if not df.empty]

# Ruta al archivo existente
ruta_csv = os.path.join('Repositorio', 'Listado_Jornadas.csv')

# Verificar si hay nuevas jornadas para procesar
if dfs_jornadas:
    print(f"📝 Procesando {len(dfs_jornadas)} jornadas con datos...")
    
    # Unir todo en un único DataFrame con las nuevas jornadas
    df_nuevas_jornadas = pd.concat(dfs_jornadas, ignore_index=True)
    
    if os.path.exists(ruta_csv):
        # Cargar el CSV existente
        df_existente = pd.read_csv(ruta_csv)
        
        # Concatenar con las nuevas jornadas
        df_combinado = pd.concat([df_existente, df_nuevas_jornadas], ignore_index=True)
        
        # Elimina duplicados usando múltiples columnas como clave
        columnas_clave = ['cod_temporada', 'cod_competicion', 'cod_grupo', 'jornada','equipo_local', 'equipo_visitante', 'cod_acta']
        df_combinado = df_combinado.drop_duplicates(subset=columnas_clave)
    else:
        # Si no existe, simplemente usamos el nuevo
        df_combinado = df_nuevas_jornadas
    
    # Guardar el archivo actualizado
    df_combinado.to_csv(ruta_csv, index=False)
    print(f"💾 Archivo actualizado: {len(df_combinado)} registros totales")
else:
    print("ℹ️  No hay nuevas jornadas para agregar al listado")

# Cargar el archivo CSV actualizado
df = pd.read_csv(os.path.join('Repositorio', 'Listado_Jornadas.csv'))

# Filtrar y extraer los links
lista_links = df[
    (df['acta_extraida'] == 'No') & 
    (df['link_acta'].notna()) & 
    (df['link_acta'] != '')
]['link_acta'].tolist()

print(f"\n🔗 Enlaces pendientes de procesar: {len(lista_links)}")

if not lista_links:
    print("✅ No hay actas pendientes por extraer")
else:
    print("🏃‍♂️ Iniciando extracción de actas...")
    
    # Lista de User-Agents para rotación
    headers= {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "en-US,en;q=0.9",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    "Host": "www.ffib.es",
    "sec-ch-ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    "sec-ch-ua-mobile":"?0",
    "sec-ch-ua-platform": "Windows",
    "sec-fetch-dest":"document",
    "sec-fetch-mode":"navigate",
    "sec-fetch-site":"none",
    "sec-fetch-user":"?1",
    "upgrade-insecure-requests":"1",
    "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    
        }
    
    actas_procesadas = 0
    actas_exitosas = 0
    
    for link in lista_links[:]:  # [:] para evitar errores al modificar la lista mientras la recorremos
        actas_procesadas += 1
        print(f'🔄 [{actas_procesadas}/{len(lista_links)}] Procesando acta...')
        
        intentos = 0
        max_reintentos = 3  # Reducido de 1000 a 3 para evitar bucles infinitos
    
        while intentos < max_reintentos:
            try:
                options = Options()
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')
                options.add_argument('--headless')
                options.add_argument('--disable-gpu')
                options.add_argument('--user-data-dir=/tmp/selenium_profile')
    
                driver = webdriver.Chrome(options=options)
                driver.get(link)
                time.sleep(5)  # espera a que cargue el JS
    
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                driver.quit()
    
                if not soup or soup.find("body") is None:  # Si la respuesta está vacía o mal formada
                    intentos += 1
                    print(f"⚠️  HTML vacío o inválido. Intento {intentos} de {max_reintentos}")
                    if intentos < max_reintentos:
                        time.sleep(60)  # Esperar 1 minuto antes de reintentar
                    continue
                else:
                    df_jugadores = lectura_acta(soup)
                    print(f"✅ Acta procesada exitosamente")
                    actas_exitosas += 1
                    break  # Si va bien, salimos del bucle
                    
            except Exception as e:
                intentos += 1
                print(f"❌ Error procesando acta (intento {intentos}): {str(e)}")
                if intentos < max_reintentos:
                    time.sleep(60)  # Esperar antes de reintentar
    
        if intentos >= max_reintentos:
            print(f"❌ No se pudo procesar el acta después de {max_reintentos} intentos")
        
        lista_links.remove(link)
    
    print(f"\n📊 Resumen: {actas_exitosas}/{actas_procesadas} actas procesadas exitosamente")

    if actas_exitosas > 0:
        print("🎉 Se procesaron algunas actas exitosamente")
    else:
        print("❌ No se pudieron procesar ninguna de las actas pendientes")


###################################################################################################################################################################
# Almacenamiento de los datos extraidos
###################################################################################################################################################################

print('\n📁 Iniciando unificación de archivos...')

# Unificar Actas
carpeta = os.path.join('Repositorio', 'Actas')
if os.path.exists(carpeta):
    archivos_csv = glob.glob(os.path.join(carpeta, '*.csv'))
    
    if archivos_csv:
        print(f"🔄 Unificando {len(archivos_csv)} archivos de actas...")
        df_unificado = pd.concat([pd.read_csv(f) for f in archivos_csv], ignore_index=True)
        df_unificado.to_csv('Actas_unificado.csv', index=False)
        print("✅ Actas unificadas correctamente.")
    else:
        print("⚠️  No se encontraron archivos CSV de actas para unificar.")
else:
    print("❌ No existe la carpeta de Actas")

# Unificar Goles
carpeta = os.path.join('Repositorio', 'Goles')
if os.path.exists(carpeta):
    archivos_csv = glob.glob(os.path.join(carpeta, '*.csv'))
    
    if archivos_csv:
        print(f"🔄 Unificando {len(archivos_csv)} archivos de goles...")
        df_unificado = pd.concat([pd.read_csv(f) for f in archivos_csv], ignore_index=True)
        df_unificado.to_csv('Goles_unificado.csv', index=False)
        print("✅ Goles unificados correctamente.")
    else:
        print("⚠️  No se encontraron archivos CSV de goles para unificar.")
else:
    print("❌ No existe la carpeta de Goles")

# Unificar Sustituciones
carpeta = os.path.join('Repositorio', 'Sustituciones')
if os.path.exists(carpeta):
    archivos_csv = glob.glob(os.path.join(carpeta, '*.csv'))
    
    if archivos_csv:
        print(f"🔄 Unificando {len(archivos_csv)} archivos de sustituciones...")
        dataframes = []
        
        for archivo in archivos_csv:
            df = pd.read_csv(archivo)
            # Extraer el número de jornada del nombre del archivo
            nombre_archivo = os.path.basename(archivo)
            jornada_match = re.search(r'_J(\d+)_', nombre_archivo)
            if jornada_match:
                jornada = int(jornada_match.group(1))
                df['Jornada'] = jornada
            dataframes.append(df)
        
        if dataframes:
            df_unificado = pd.concat(dataframes, ignore_index=True)
            df_unificado.to_csv('Sustituciones_unificado.csv', index=False)
            print("✅ Sustituciones unificadas correctamente.")
        else:
            print("⚠️  No se pudieron procesar los archivos de sustituciones.")
    else:
        print("⚠️  No se encontraron archivos CSV de sustituciones para unificar.")
else:
    print("❌ No existe la carpeta de Sustituciones")

# Actualizar el estado de las actas extraídas
print("\n🔄 Actualizando estado de actas extraídas...")

ruta_csv = os.path.join('Repositorio', 'Listado_Jornadas.csv')
ruta_actas = os.path.join('Repositorio', 'Actas')

if os.path.exists(ruta_csv) and os.path.exists(ruta_actas):
    df = pd.read_csv(ruta_csv)
    nombres_archivos = [f for f in os.listdir(ruta_actas) if os.path.isfile(os.path.join(ruta_actas, f))]
    
    actas_actualizadas = 0
    for idx, row in df.iterrows():
        equipo_local = str(row['equipo_local']).replace('"', '')
        equipo_visitante = str(row['equipo_visitante']).replace('"', '')
        nombre_esperado = f"Acta_J{row['jornada']}_{equipo_local}_vs_{equipo_visitante}.csv"
        
        if nombre_esperado in nombres_archivos and row['acta_extraida'] != 'Si':
            df.at[idx, 'acta_extraida'] = 'Si'
            actas_actualizadas += 1
    
    if actas_actualizadas > 0:
        df.to_csv(ruta_csv, index=False)
        print(f"✅ Estado actualizado: {actas_actualizadas} actas marcadas como extraídas")
    else:
        print("ℹ️  No hay cambios en el estado de las actas")
else:
    print("❌ No se pudo actualizar el estado (archivos no encontrados)")

print("\n🎯 Proceso completado")
print("=" * 50)

# Resumen final
try:
    df_final = pd.read_csv(os.path.join('Repositorio', 'Listado_Jornadas.csv'))
    total_actas = len(df_final)
    actas_extraidas = len(df_final[df_final['acta_extraida'] == 'Si'])
    
    print(f"📊 RESUMEN FINAL:")
    print(f"   Total de actas: {total_actas}")
    print(f"   Actas extraídas: {actas_extraidas}")
    print(f"   Pendientes: {total_actas - actas_extraidas}")
    print(f"   Progreso: {(actas_extraidas/total_actas)*100:.1f}%")
    
    # Verificar archivos unificados
    archivos_unificados = ['Actas_unificado.csv', 'Goles_unificado.csv', 'Sustituciones_unificado.csv']
    for archivo in archivos_unificados:
        if os.path.exists(archivo):
            df_check = pd.read_csv(archivo)
            print(f"   {archivo}: {len(df_check)} registros")
        else:
            print(f"   {archivo}: ❌ No encontrado")
            
except Exception as e:
    print(f"⚠️  Error generando resumen final: {str(e)}")

print("=" * 50)