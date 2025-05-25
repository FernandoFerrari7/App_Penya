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
    script_scraping = os.path.join(ruta_base, 'data', 'lectura_actas_adaptada.py')
    
    try:
        # Crear una carpeta temporal para ejecutar el script
        import tempfile
        import shutil
        
        with tempfile.TemporaryDirectory() as temp_dir:
            print(f"Creando entorno temporal en: {temp_dir}")
            
            # Copiar el script lectura_actas_adaptada.py al directorio temporal
            temp_script = os.path.join(temp_dir, 'lectura_actas_adaptada.py')
            shutil.copy2(script_scraping, temp_script)
            
            # Leer el contenido del script
            with open(temp_script, 'r', encoding='utf-8') as f:
                contenido = f.read()
            
            # Modificar las rutas en el script para usar paths relativos correctos
            # Reemplazar referencias a 'Repositorio/'
            contenido_modificado = contenido.replace(
                "# Ruta al archivo CSV\ncsv_path = 'Repositorio/Listado_Jornadas.csv'", 
                "# Ruta al archivo CSV\nimport os\ncsv_path = os.path.join('data', 'Repositorio', 'Listado_Jornadas.csv')"
            )
            contenido_modificado = contenido_modificado.replace(
                "carpeta='Repositorio/Actas'", 
                "carpeta=os.path.join('data', 'Repositorio', 'Actas')"
            )
            contenido_modificado = contenido_modificado.replace(
                "carpeta='Repositorio/Goles'", 
                "carpeta=os.path.join('data', 'Repositorio', 'Goles')"
            )
            contenido_modificado = contenido_modificado.replace(
                "carpeta = 'Repositorio/Sustituciones'", 
                "carpeta = os.path.join('data', 'Repositorio', 'Sustituciones')"
            )
            contenido_modificado = contenido_modificado.replace(
                "carpeta='Repositorio/Jornadas'", 
                "carpeta=os.path.join('data', 'Repositorio', 'Jornadas')"
            )
            
            # También modificar cómo se guardan los archivos unificados
            contenido_modificado = contenido_modificado.replace(
                "df_unificado.to_csv('Actas_unificado.csv', index=False)", 
                "df_unificado.to_csv(os.path.join('data', 'Actas_unificado.csv'), index=False)"
            )
            contenido_modificado = contenido_modificado.replace(
                "df_unificado.to_csv('Goles_unificado.csv', index=False)", 
                "df_unificado.to_csv(os.path.join('data', 'Goles_unificado.csv'), index=False)"
            )
            contenido_modificado = contenido_modificado.replace(
                "df_unificado.to_csv('Jornadas_unificado.csv', index=False)", 
                "df_unificado.to_csv(os.path.join('data', 'Jornadas_unificado.csv'), index=False)"
            )
            contenido_modificado = contenido_modificado.replace(
                "df_unificado.to_csv('Sustituciones_unificado.csv', index=False)", 
                "df_unificado.to_csv(os.path.join('data', 'Sustituciones_unificado.csv'), index=False)"
            )
            
            # Agregar manejo para carpetas vacías
            contenido_modificado = contenido_modificado.replace(
                "# Obtener todos los archivos CSV en la carpeta\narchivos_csv = glob.glob(os.path.join(carpeta, '*.csv'))\n\n# Leer y concatenar todos los archivos CSV\ndf_unificado = pd.concat([pd.read_csv(f) for f in archivos_csv])",
                "# Obtener todos los archivos CSV en la carpeta\narchivos_csv = glob.glob(os.path.join(carpeta, '*.csv'))\n\n# Leer y concatenar todos los archivos CSV si existen\nif archivos_csv:\n    df_unificado = pd.concat([pd.read_csv(f) for f in archivos_csv])\nelse:\n    print(f\"No se encontraron archivos CSV en {carpeta}\")\n    # Crear un DataFrame vacío con columnas apropiadas\n    df_unificado = pd.DataFrame()"
            )
            
            # Escribir el script modificado
            with open(temp_script, 'w', encoding='utf-8') as f:
                f.write(contenido_modificado)
                
            # Ejecutar el script modificado
            print(f"Ejecutando script modificado: {temp_script}")
            resultado = subprocess.run(
                [sys.executable, temp_script],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=ruta_base  # Ejecutar desde la raíz del proyecto
            )
            
            # Mostrar la salida resumida del script
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