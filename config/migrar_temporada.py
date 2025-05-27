"""
Script para migrar a una nueva temporada
Ubicación: config/migrar_temporada.py
"""
import os
import sys
import shutil
from datetime import datetime

# Agregar el directorio raíz al path para importaciones
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.temporadas import *

def migrar_a_nueva_temporada(nueva_temporada_codigo, cod_competicion, cod_grupo, cod_temporada):
    """
    Migra el sistema a una nueva temporada
    """
    print("🔄 INICIANDO MIGRACIÓN A NUEVA TEMPORADA")
    print("=" * 50)
    
    # 1. Hacer backup de la temporada actual
    print("📦 1. Creando backup de temporada actual...")
    backup_folder = f"backup_temporada_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    try:
        os.makedirs(backup_folder, exist_ok=True)
        
        # Backup de archivos principales
        archivos_backup = [
            'data/Repositorio/Listado_Jornadas.csv',
            'data/Actas_unificado.csv',
            'data/Goles_unificado.csv',
            'data/Sustituciones_unificado.csv'
        ]
        
        for archivo in archivos_backup:
            if os.path.exists(archivo):
                shutil.copy2(archivo, backup_folder)
                print(f"  ✅ Backup: {archivo}")
        
        # Backup de carpetas de datos individuales
        carpetas_backup = [
            'data/Repositorio/Actas',
            'data/Repositorio/Goles',
            'data/Repositorio/Sustituciones'
        ]
        
        for carpeta in carpetas_backup:
            if os.path.exists(carpeta):
                backup_carpeta = os.path.join(backup_folder, os.path.basename(carpeta))
                shutil.copytree(carpeta, backup_carpeta)
                print(f"  ✅ Backup carpeta: {carpeta}")
        
        print(f"✅ Backup completado en: {backup_folder}")
        
    except Exception as e:
        print(f"❌ Error durante backup: {e}")
        return False
    
    # 2. Agregar nueva temporada
    print(f"\n🆕 2. Configurando nueva temporada {nueva_temporada_codigo}...")
    
    try:
        agregar_nueva_temporada(
            codigo=nueva_temporada_codigo,
            cod_competicion=cod_competicion,
            cod_grupo=cod_grupo,
            cod_temporada=cod_temporada,
            activar=True  # La hace activa
        )
        print("✅ Nueva temporada configurada")
        
    except Exception as e:
        print(f"❌ Error configurando nueva temporada: {e}")
        return False
    
    # 3. Limpiar datos de temporada anterior (opcional)
    print(f"\n🧹 3. ¿Limpiar datos de temporada anterior?")
    respuesta = input("¿Quieres limpiar los datos de la temporada anterior? (s/N): ")
    
    if respuesta.lower() in ['s', 'si', 'sí', 'y', 'yes']:
        try:
            # Limpiar archivos unificados
            archivos_limpiar = [
                'data/Actas_unificado.csv',
                'data/Goles_unificado.csv', 
                'data/Sustituciones_unificado.csv'
            ]
            
            for archivo in archivos_limpiar:
                if os.path.exists(archivo):
                    os.remove(archivo)
                    print(f"  🗑️  Eliminado: {archivo}")
            
            # Limpiar Listado_Jornadas.csv
            listado_path = 'data/Repositorio/Listado_Jornadas.csv'
            if os.path.exists(listado_path):
                # Crear un archivo vacío con solo headers
                import pandas as pd
                df_vacio = pd.DataFrame(columns=[
                    'cod_temporada', 'cod_competicion', 'cod_grupo', 'jornada',
                    'equipo_local', 'equipo_visitante', 'cod_acta', 'link_acta', 'acta_extraida'
                ])
                df_vacio.to_csv(listado_path, index=False)
                print(f"  🗑️  Reiniciado: {listado_path}")
            
            # Limpiar carpetas de datos individuales
            carpetas_limpiar = [
                'data/Repositorio/Actas',
                'data/Repositorio/Goles',
                'data/Repositorio/Sustituciones'
            ]
            
            for carpeta in carpetas_limpiar:
                if os.path.exists(carpeta):
                    for archivo in os.listdir(carpeta):
                        if archivo.endswith('.csv'):
                            os.remove(os.path.join(carpeta, archivo))
                    print(f"  🗑️  Limpiada carpeta: {carpeta}")
            
            print("✅ Limpieza completada")
            
        except Exception as e:
            print(f"❌ Error durante limpieza: {e}")
    else:
        print("ℹ️  Datos anteriores conservados")
    
    # 4. Verificar configuración
    print(f"\n✅ 4. Verificando nueva configuración...")
    
    try:
        params = obtener_parametros_scraping()
        print(f"   Nueva competición: {params['cod_competicion']}")
        print(f"   Nuevo grupo: {params['cod_grupo']}")
        print(f"   Nueva temporada: {params['cod_temporada']}")
        print(f"   Jornadas esperadas: {params['jornadas_total']}")
        
    except Exception as e:
        print(f"❌ Error verificando configuración: {e}")
        return False
    
    print(f"\n🎉 MIGRACIÓN COMPLETADA EXITOSAMENTE")
    print("=" * 50)
    print(f"📅 Nueva temporada activa: {nueva_temporada_codigo}")
    print(f"📦 Backup guardado en: {backup_folder}")
    print(f"🔄 Ya puedes ejecutar el scraping para la nueva temporada")
    
    return True

def detectar_codigos_nueva_temporada():
    """
    Ayuda a detectar los códigos de una nueva temporada
    """
    print("🔍 DETECTANDO CÓDIGOS DE NUEVA TEMPORADA")
    print("=" * 50)
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from bs4 import BeautifulSoup
        import time
    except ImportError:
        print("❌ Error: Necesitas instalar selenium y beautifulsoup4")
        print("   pip install selenium beautifulsoup4")
        return
    
    # Probar diferentes códigos de temporada
    cod_competicion_base = 7077248
    cod_grupo_base = 7077249
    
    print("🕷️  Probando diferentes códigos de temporada...")
    
    for cod_temp in range(20, 26):  # Probar temporadas 20-25
        try:
            url = (f'https://www.ffib.es/Fed/NPcd/NFG_CmpJornada?cod_primaria=1000110'
                   f'&CodCompeticion={cod_competicion_base}'
                   f'&CodGrupo={cod_grupo_base}'
                   f'&CodTemporada={cod_temp}'
                   f'&cod_agrupacion=1'
                   f'&CodJornada=1')
            
            options = Options()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            
            driver = webdriver.Chrome(options=options)
            driver.get(url)
            time.sleep(3)
            
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            driver.quit()
            
            # Verificar si la página tiene contenido válido
            jornada_text = soup.find("div", class_="col-sm-12", style="text-align:center")
            partidos = soup.find_all("table", width="100%")
            
            if jornada_text and partidos:
                print(f"  ✅ Temporada {cod_temp}: ACTIVA - {len(partidos)} partidos encontrados")
                
                # Extraer información adicional
                if "Jornada" in jornada_text.text:
                    print(f"      📅 {jornada_text.text.strip()}")
                    
            else:
                print(f"  ❌ Temporada {cod_temp}: Sin datos")
                
        except Exception as e:
            print(f"  ⚠️  Temporada {cod_temp}: Error - {e}")
    
    print("\n💡 Usa el código de temporada que muestre 'ACTIVA' para la migración")

if __name__ == "__main__":
    print("🔧 HERRAMIENTA DE MIGRACIÓN DE TEMPORADA")
    print("=" * 50)
    
    print("1. Detectar códigos de nueva temporada")
    print("2. Migrar a nueva temporada")
    print("3. Listar temporadas configuradas")
    
    opcion = input("\nSelecciona una opción (1-3): ")
    
    if opcion == "1":
        detectar_codigos_nueva_temporada()
    elif opcion == "2":
        print("\n📝 Configuración de nueva temporada:")
        codigo = input("Código de temporada (ej: 2025-26): ")
        cod_comp = int(input("Código de competición (ej: 7077248): "))
        cod_grupo = int(input("Código de grupo (ej: 7077249): "))
        cod_temp = int(input("Código de temporada numérico (ej: 21): "))
        
        migrar_a_nueva_temporada(codigo, cod_comp, cod_grupo, cod_temp)
    elif opcion == "3":
        listar_temporadas()
    else:
        print("❌ Opción no válida")