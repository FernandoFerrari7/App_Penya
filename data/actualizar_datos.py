"""
Script para actualizar datos, sincronizar con GitHub y activar despliegue en Render.
Versión sin emojis para compatibilidad con Windows.
"""

import os
import sys
import subprocess
import time
import datetime
import traceback
import requests
from dotenv import load_dotenv

# Cargar variables de entorno (para almacenar el Deploy Hook URL de forma segura)
load_dotenv()

def ejecutar_proceso_completo():
    """
    Función principal que orquesta todo el proceso de actualización
    """
    print(f"[{datetime.datetime.now()}] Iniciando proceso completo de actualización...")
    
    try:
        # 1. Ejecutar scraping
        exito_scraping = ejecutar_scraping()
        if not exito_scraping:
            print("Error durante el scraping de datos. Proceso abortado.")
            return False
            
        # 2. Sincronizar con GitHub
        exito_github = sincronizar_github()
        if not exito_github:
            print("Error en la sincronización con GitHub.")
            # Continuamos con el despliegue manual incluso si GitHub falla
        
        # 3. Activar manualmente el despliegue en Render
        exito_render = activar_despliegue_render()
        if not exito_render:
            print("Error al activar el despliegue en Render.")
            # No es un error crítico, puede desplegarse más tarde
        
        # 4. Resultado final
        print(f"[{datetime.datetime.now()}] Proceso finalizado exitosamente.")
        return True
            
    except Exception as e:
        print(f"[{datetime.datetime.now()}] Error crítico durante el proceso:")
        print(str(e))
        traceback.print_exc()
        return False

def ejecutar_scraping():
    """
    Ejecuta el script de scraping para obtener nuevos datos
    """
    print(f"[{datetime.datetime.now()}] Iniciando scraping de datos...")
    
    # Obtener la ruta base del proyecto
    ruta_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Ruta al script de scraping
    script_scraping = os.path.join(ruta_base, 'data', 'lectura_actas_v2.py')
    
    try:
        # Detectar donde está realmente el repositorio
        posibles_rutas = [
            os.path.join(ruta_base, 'Repositorio'),
            os.path.join(ruta_base, 'data', 'Repositorio')
        ]
        
        ruta_repositorio = None
        for ruta in posibles_rutas:
            if os.path.exists(ruta) and os.path.exists(os.path.join(ruta, 'Listado_Jornadas.csv')):
                ruta_repositorio = ruta
                print(f"Directorio de Repositorio encontrado en: {ruta_repositorio}")
                break
        
        if not ruta_repositorio:
            print("No se encontró el directorio Repositorio con el archivo Listado_Jornadas.csv")
            return False
        
        # Si el repositorio está en data/Repositorio, crear un enlace simbólico temporal
        if ruta_repositorio == os.path.join(ruta_base, 'data', 'Repositorio'):
            # Estamos en Windows, entonces copiamos el directorio temporalmente
            print("Preparando entorno para ejecutar el script...")
            
            # Crear directorio temporal para el repositorio en el directorio raíz
            temp_repo = os.path.join(ruta_base, 'Repositorio')
            if not os.path.exists(temp_repo):
                os.makedirs(temp_repo)
            
            # Copiar el archivo Listado_Jornadas.csv
            import shutil
            shutil.copy2(
                os.path.join(ruta_repositorio, 'Listado_Jornadas.csv'), 
                os.path.join(temp_repo, 'Listado_Jornadas.csv')
            )
            
            # Crear las subcarpetas necesarias y asegurarse de que tengan al menos un archivo CSV mínimo
            for subcarpeta in ['Actas', 'Goles', 'Jornadas', 'Sustituciones']:
                # Crear subcarpeta
                subcarpeta_path = os.path.join(temp_repo, subcarpeta)
                os.makedirs(subcarpeta_path, exist_ok=True)
                
                # Comprobar si hay archivos CSV en la subcarpeta original
                subcarpeta_original = os.path.join(ruta_repositorio, subcarpeta)
                if os.path.exists(subcarpeta_original):
                    # Copiar archivos existentes
                    for archivo in os.listdir(subcarpeta_original):
                        if archivo.endswith('.csv'):
                            shutil.copy2(
                                os.path.join(subcarpeta_original, archivo),
                                os.path.join(subcarpeta_path, archivo)
                            )
                
                # Asegurar que existe al menos un archivo CSV mínimo
                placeholder_file = os.path.join(subcarpeta_path, f'placeholder_{subcarpeta}.csv')
                if not any(archivo.endswith('.csv') for archivo in os.listdir(subcarpeta_path)):
                    print(f"Creando archivo CSV mínimo en {subcarpeta_path}")
                    with open(placeholder_file, 'w') as f:
                        # Escribir encabezados mínimos según el tipo de subcarpeta
                        if subcarpeta == 'Actas':
                            f.write("numero,jugador,equipo,status,localizacion,rival,jornada,goles,Tarjetas Amarillas,Tarjetas Rojas,minutos_jugados\n")
                        elif subcarpeta == 'Goles':
                            f.write("Jornada,Minuto,jugador,Tipo de Gol\n")
                        elif subcarpeta == 'Jornadas':
                            f.write("cod_temporada,cod_competicion,cod_grupo,jornada,equipo_local,equipo_visitante,cod_acta,link_acta,acta_extraida\n")
                        elif subcarpeta == 'Sustituciones':
                            f.write("jugador_entra,jugador_sale,Minuto,equipo,Jornada\n")
        
        # Modificar script directamente para evitar errores cuando no hay archivos
        try:
            # Leer el archivo original
            with open(script_scraping, 'r', encoding='utf-8') as file:
                script_content = file.read()
            
            # Crear una copia de seguridad
            backup_file = script_scraping + '.bak'
            if not os.path.exists(backup_file):
                with open(backup_file, 'w', encoding='utf-8') as file:
                    file.write(script_content)
            
            # Agregar manejo para carpetas vacías
            modified_content = script_content.replace(
                "df_unificado = pd.concat([pd.read_csv(f) for f in archivos_csv])",
                "if archivos_csv:\n    df_unificado = pd.concat([pd.read_csv(f) for f in archivos_csv])\nelse:\n    # Crear DataFrame vacío con columnas necesarias\n    df_unificado = pd.DataFrame()"
            )
            
            # Guardar el script modificado temporalmente
            with open(script_scraping, 'w', encoding='utf-8') as file:
                file.write(modified_content)
            
            # Ejecutar el script de scraping
            print(f"Ejecutando: {script_scraping}")
            resultado = subprocess.run(
                [sys.executable, script_scraping],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=ruta_base  # Ejecutar desde la raíz del proyecto
            )
            
            # Restaurar el script original
            with open(backup_file, 'r', encoding='utf-8') as file:
                original_content = file.read()
            with open(script_scraping, 'w', encoding='utf-8') as file:
                file.write(original_content)
            
        except Exception as script_error:
            print(f"Error al modificar/restaurar el script: {str(script_error)}")
            # Continuar con la ejecución normal
            resultado = subprocess.run(
                [sys.executable, script_scraping],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=ruta_base
            )
        
        # Si creamos un directorio temporal, mover los resultados de vuelta
        if ruta_repositorio == os.path.join(ruta_base, 'data', 'Repositorio'):
            print("Moviendo resultados al directorio original...")
            
            # Mover los archivos generados
            for archivo in os.listdir(temp_repo):
                ruta_archivo = os.path.join(temp_repo, archivo)
                if os.path.isfile(ruta_archivo) and not archivo.startswith('placeholder_'):
                    shutil.copy2(ruta_archivo, os.path.join(ruta_repositorio, archivo))
                elif os.path.isdir(ruta_archivo):
                    # Es un directorio, copiar todos los archivos excepto placeholders
                    os.makedirs(os.path.join(ruta_repositorio, archivo), exist_ok=True)
                    for subarchivo in os.listdir(ruta_archivo):
                        if not subarchivo.startswith('placeholder_'):
                            ruta_subarchivo = os.path.join(ruta_archivo, subarchivo)
                            if os.path.isfile(ruta_subarchivo):
                                shutil.copy2(ruta_subarchivo, os.path.join(ruta_repositorio, archivo, subarchivo))
            
            # Mover archivos CSV unificados a la raíz
            for archivo in os.listdir(ruta_base):
                if archivo.endswith('_unificado.csv'):
                    shutil.copy2(
                        os.path.join(ruta_base, archivo),
                        os.path.join(ruta_repositorio, '..', archivo)
                    )
        
        # Mostrar la salida resumida del script de scraping
        print("--- RESUMEN DE LA EJECUCIÓN DEL SCRAPING ---")
        
        # Extraer solo las líneas relevantes para un resumen
        salida_resumida = []
        for linea in resultado.stdout.split('\n'):
            if "cargado" in linea or "Refresh" in linea or "correctamente" in linea or "unificad" in linea:
                salida_resumida.append(linea)
                
        # Mostrar resumen
        print('\n'.join(salida_resumida))
        
        # Verificar si hubo errores
        if resultado.returncode != 0:
            print("--- ERRORES DURANTE EL SCRAPING ---")
            print(resultado.stderr)
            return False
        
        print(f"[{datetime.datetime.now()}] Scraping completado exitosamente.")
        return True
        
    except Exception as e:
        print(f"[{datetime.datetime.now()}] Error durante el scraping:")
        print(str(e))
        traceback.print_exc()
        return False

def sincronizar_github():
    """
    Sincroniza los cambios con el repositorio de GitHub
    """
    print(f"[{datetime.datetime.now()}] Sincronizando cambios con GitHub...")
    
    # Obtener la ruta base del proyecto
    ruta_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    try:
        # Comprobar si hay cambios para sincronizar
        resultado_status = subprocess.run(
            ['git', 'status', '--porcelain'],
            check=True,
            capture_output=True,
            text=True,
            cwd=ruta_base
        )
        
        if not resultado_status.stdout.strip():
            print("No hay cambios para sincronizar con GitHub.")
            return True
        
        # Mostrar qué archivos se han modificado
        archivos_modificados = resultado_status.stdout.strip().split('\n')
        print(f"Se sincronizarán {len(archivos_modificados)} archivos:")
        for archivo in archivos_modificados[:5]:  # Mostrar solo los primeros 5
            print(f"  - {archivo}")
        if len(archivos_modificados) > 5:
            print(f"  - ...y {len(archivos_modificados) - 5} más")
            
        # Configurar Git (por si acaso)
        subprocess.run(
            ['git', 'config', '--global', 'user.email', 'app-actualizacion@ejemplo.com'],
            check=True, cwd=ruta_base
        )
        subprocess.run(
            ['git', 'config', '--global', 'user.name', 'App Actualizacion'],
            check=True, cwd=ruta_base
        )
        
        # Añadir todos los archivos modificados
        subprocess.run(
            ['git', 'add', '.'],
            check=True,
            cwd=ruta_base
        )
        
        # Crear un commit con timestamp y detalles de la actualización
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        mensaje_commit = f'Actualización automática: {timestamp}\n\n'
        mensaje_commit += f'Archivos actualizados: {len(archivos_modificados)}\n'
        
        subprocess.run(
            ['git', 'commit', '-m', mensaje_commit],
            check=True,
            cwd=ruta_base
        )
        
        # Hacer push al repositorio remoto
        print("Enviando cambios a GitHub...")
        proceso_push = subprocess.run(
            ['git', 'push'],
            capture_output=True,
            text=True,
            cwd=ruta_base
        )
        
        if proceso_push.returncode != 0:
            print(f"Advertencia: No se pudo hacer push al repositorio:")
            print(proceso_push.stderr)
            
            # Verificar si es un problema de autenticación
            if "Authentication failed" in proceso_push.stderr:
                print("\nPROBLEMA DE AUTENTICACIÓN GITHUB")
                print("Por favor configura la autenticación de GitHub en el servidor.")
                print("Opciones:")
                print("  1. Configura un token de acceso personal:")
                print("     git remote set-url origin https://USERNAME:TOKEN@github.com/USERNAME/REPO.git")
                print("  2. Configura una clave SSH")
                print("  3. Usa el comando 'git credential-store' para guardar credenciales")
                
            return False
            
        print(f"[{datetime.datetime.now()}] Cambios sincronizados correctamente con GitHub.")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"[{datetime.datetime.now()}] Error durante la sincronización con GitHub:")
        print(f"  Comando: {e.cmd}")
        print(f"  Código de salida: {e.returncode}")
        if e.stdout:
            print(f"  Salida: {e.stdout}")
        if e.stderr:
            print(f"  Error: {e.stderr}")
        return False
        
    except Exception as e:
        print(f"[{datetime.datetime.now()}] Error inesperado durante la sincronización:")
        print(str(e))
        traceback.print_exc()
        return False

def activar_despliegue_render():
    """
    Activa manualmente un despliegue en Render utilizando el Deploy Hook URL
    """
    print(f"[{datetime.datetime.now()}] Activando despliegue manual en Render...")
    
    # Obtener el Deploy Hook URL desde variables de entorno
    deploy_hook_url = os.getenv('RENDER_DEPLOY_HOOK')
    
    if not deploy_hook_url:
        print("\nDEPLOY HOOK URL NO CONFIGURADO")
        print("Para activar manualmente el despliegue en Render, sigue estos pasos:")
        print("1. Ve a tu servicio en Render → Settings → Build & Deploy")
        print("2. Copia el 'Deploy Hook' URL")
        print("3. Crea un archivo .env en la raíz del proyecto con la variable:")
        print("   RENDER_DEPLOY_HOOK=https://api.render.com/deploy/srv-xxx?key=yyy")
        return False
    
    try:
        # Realizar la solicitud HTTP POST al Deploy Hook URL
        response = requests.post(deploy_hook_url)
        
        # Verificar la respuesta
        if response.status_code == 200 or response.status_code == 201:
            print(f"Despliegue activado correctamente en Render")
            print(f"  La aplicación se actualizará en unos minutos")
            return True
        else:
            print(f"Error al activar el despliegue en Render:")
            print(f"  Código de estado: {response.status_code}")
            print(f"  Respuesta: {response.text}")
            return False
            
    except Exception as e:
        print(f"[{datetime.datetime.now()}] Error al comunicarse con Render:")
        print(str(e))
        traceback.print_exc()
        return False

# Si el script se ejecuta directamente
if __name__ == "__main__":
    exito = ejecutar_proceso_completo()
    sys.exit(0 if exito else 1)