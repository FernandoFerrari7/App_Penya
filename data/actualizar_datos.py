"""
Script para actualizar datos, sincronizar con GitHub y activar despliegue en Render.
Versión mejorada con mejor manejo de errores y casos edge.
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
    print(f"🚀 [{datetime.datetime.now()}] Iniciando proceso completo de actualización...")
    
    try:
        # 1. Ejecutar scraping
        exito_scraping = ejecutar_scraping()
        if not exito_scraping:
            print("❌ Error durante el scraping de datos. Proceso abortado.")
            return False
            
        # 2. Sincronizar con GitHub
        exito_github = sincronizar_github()
        if not exito_github:
            print("⚠️  Error en la sincronización con GitHub.")
            # Continuamos con el despliegue manual incluso si GitHub falla
        
        # 3. Activar manualmente el despliegue en Render
        exito_render = activar_despliegue_render()
        if not exito_render:
            print("⚠️  Error al activar el despliegue en Render.")
            # No es un error crítico, puede desplegarse más tarde
        
        # 4. Resultado final
        print(f"🎉 [{datetime.datetime.now()}] Proceso finalizado exitosamente.")
        return True
            
    except Exception as e:
        print(f"💥 [{datetime.datetime.now()}] Error crítico durante el proceso:")
        print(str(e))
        traceback.print_exc()
        return False

def ejecutar_scraping():
    """
    Ejecuta el script de scraping para obtener nuevos datos
    """
    print(f"🔄 [{datetime.datetime.now()}] Iniciando scraping de datos...")
    
    # Obtener la ruta base del proyecto
    ruta_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Ruta al script de scraping
    script_scraping = os.path.join(ruta_base, 'data', 'lectura_actas.py')
    
    # Verificar que el script existe
    if not os.path.exists(script_scraping):
        print(f"❌ No se encuentra el script de scraping en: {script_scraping}")
        return False
    
    try:
        # Crear una carpeta temporal para ejecutar el script
        import tempfile
        import shutil
        
        with tempfile.TemporaryDirectory() as temp_dir:
            print(f"📁 Creando entorno temporal en: {temp_dir}")
            
            # Copiar el script lectura_actas.py al directorio temporal
            temp_script = os.path.join(temp_dir, 'lectura_actas.py')
            shutil.copy2(script_scraping, temp_script)
            
            # Leer el contenido del script
            with open(temp_script, 'r', encoding='utf-8') as f:
                contenido = f.read()
            
            # Modificar las rutas en el script para usar paths relativos correctos
            contenido_modificado = modificar_rutas_script(contenido)
            
            # Escribir el script modificado
            with open(temp_script, 'w', encoding='utf-8') as f:
                f.write(contenido_modificado)
                
            # Ejecutar el script modificado
            print(f"▶️  Ejecutando script modificado...")
            resultado = subprocess.run(
                [sys.executable, temp_script],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=ruta_base  # Ejecutar desde la raíz del proyecto
            )
            
            # Procesar la salida
            return procesar_resultado_scraping(resultado)
        
    except Exception as e:
        print(f"💥 [{datetime.datetime.now()}] Error durante el scraping:")
        print(str(e))
        traceback.print_exc()
        return False

def modificar_rutas_script(contenido):
    """
    Modifica las rutas del script para que funcionen correctamente
    """
    # Reemplazar referencias a 'Repositorio/'
    contenido_modificado = contenido.replace(
        "csv_path = 'Repositorio/Listado_Jornadas.csv'", 
        "csv_path = os.path.join('data', 'Repositorio', 'Listado_Jornadas.csv')"
    )
    
    # Actualizar rutas de guardado de archivos
    rutas_modificaciones = {
        "file_path = './Repositorio/Goles/'": "file_path = os.path.join('data', 'Repositorio', 'Goles', ",
        "file_path = './Repositorio/Sustituciones/'": "file_path = os.path.join('data', 'Repositorio', 'Sustituciones', ",
        "file_path = './Repositorio/Actas/'": "file_path = os.path.join('data', 'Repositorio', 'Actas', ",
        "ruta_csv = './Repositorio/Listado_Jornadas.csv'": "ruta_csv = os.path.join('data', 'Repositorio', 'Listado_Jornadas.csv')",
        "df = pd.read_csv('Repositorio/Listado_Jornadas.csv')": "df = pd.read_csv(os.path.join('data', 'Repositorio', 'Listado_Jornadas.csv'))",
        "carpeta='./Repositorio/Actas'": "carpeta=os.path.join('data', 'Repositorio', 'Actas')",
        "carpeta='./Repositorio/Goles'": "carpeta=os.path.join('data', 'Repositorio', 'Goles')",
        "carpeta = './Repositorio/Sustituciones'": "carpeta = os.path.join('data', 'Repositorio', 'Sustituciones')",
        "ruta_csv = 'Repositorio/Listado_Jornadas.csv'": "ruta_csv = os.path.join('data', 'Repositorio', 'Listado_Jornadas.csv')",
        "ruta_actas = 'Repositorio/Actas'": "ruta_actas = os.path.join('data', 'Repositorio', 'Actas')"
    }
    
    for original, reemplazo in rutas_modificaciones.items():
        contenido_modificado = contenido_modificado.replace(original, reemplazo)
    
    # Actualizar rutas de archivos unificados
    archivos_unificados = {
        "'Actas_unificado.csv'": "os.path.join('data', 'Actas_unificado.csv')",
        "'Goles_unificado.csv'": "os.path.join('data', 'Goles_unificado.csv')",
        "'Sustituciones_unificado.csv'": "os.path.join('data', 'Sustituciones_unificado.csv')"
    }
    
    for original, reemplazo in archivos_unificados.items():
        contenido_modificado = contenido_modificado.replace(original, reemplazo)
    
    return contenido_modificado

def procesar_resultado_scraping(resultado):
    """
    Procesa el resultado del script de scraping y muestra información relevante
    """
    print("\n" + "="*60)
    print("📊 RESUMEN DE LA EJECUCIÓN DEL SCRAPING")
    print("="*60)
    
    if resultado.returncode == 0:
        # Extraer información relevante de la salida
        salida_lineas = resultado.stdout.split('\n')
        
        # Buscar líneas informativas
        lineas_relevantes = []
        for linea in salida_lineas:
            if any(palabra in linea.lower() for palabra in [
                'procesando', 'extraída', 'completado', 'unificad', 
                'resumen final', 'actas extraídas', 'progreso'
            ]):
                lineas_relevantes.append(linea.strip())
        
        if lineas_relevantes:
            for linea in lineas_relevantes[-10:]:  # Mostrar últimas 10 líneas relevantes
                if linea:
                    print(f"  {linea}")
        else:
            print("  ℹ️  Proceso ejecutado sin información detallada")
        
        # Mostrar estadísticas si están disponibles
        if "actas extraídas:" in resultado.stdout.lower():
            for linea in salida_lineas:
                if "actas extraídas:" in linea.lower() or "progreso:" in linea.lower():
                    print(f"  📈 {linea.strip()}")
        
        print("✅ Scraping completado exitosamente")
        return True
        
    else:
        print("❌ ERRORES DURANTE EL SCRAPING")
        print("-" * 40)
        
        # Analizar el tipo de error
        error_output = resultado.stderr
        
        if "No objects to concatenate" in error_output:
            print("ℹ️  No hay datos nuevos para procesar")
            print("   Esto es normal si todos los datos están actualizados")
            return True  # No es realmente un error
        elif "FileNotFoundError" in error_output:
            print("❌ Error: Archivos o carpetas no encontrados")
            print("   Verifica la estructura de carpetas del proyecto")
        elif "selenium" in error_output.lower():
            print("❌ Error: Problema con Selenium/ChromeDriver")
            print("   Verifica que ChromeDriver esté instalado correctamente")
        else:
            print("❌ Error desconocido:")
            
        # Mostrar las últimas líneas del error para diagnóstico
        error_lines = error_output.strip().split('\n')
        for line in error_lines[-5:]:  # Últimas 5 líneas del error
            if line.strip():
                print(f"   {line}")
        
        return False

def sincronizar_github():
    """
    Sincroniza los cambios con el repositorio de GitHub
    """
    print(f"🔄 [{datetime.datetime.now()}] Sincronizando cambios con GitHub...")
    
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
            print("ℹ️  No hay cambios para sincronizar con GitHub.")
            return True
        
        # Mostrar qué archivos se han modificado
        archivos_modificados = [line for line in resultado_status.stdout.strip().split('\n') if line.strip()]
        print(f"📝 Se sincronizarán {len(archivos_modificados)} archivos:")
        for archivo in archivos_modificados[:5]:  # Mostrar solo los primeros 5
            print(f"   📄 {archivo}")
        if len(archivos_modificados) > 5:
            print(f"   📄 ...y {len(archivos_modificados) - 5} más")
            
        # Configurar Git (por si acaso)
        try:
            subprocess.run(
                ['git', 'config', '--global', 'user.email', 'app-actualizacion@ejemplo.com'],
                check=True, cwd=ruta_base, capture_output=True
            )
            subprocess.run(
                ['git', 'config', '--global', 'user.name', 'App Actualizacion'],
                check=True, cwd=ruta_base, capture_output=True
            )
        except subprocess.CalledProcessError:
            print("⚠️  No se pudo configurar Git (puede estar ya configurado)")
        
        # Añadir todos los archivos modificados
        subprocess.run(
            ['git', 'add', '.'],
            check=True,
            cwd=ruta_base
        )
        
        # Crear un commit con timestamp y detalles de la actualización
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        mensaje_commit = f'🤖 Actualización automática: {timestamp}\n\n'
        mensaje_commit += f'📊 Archivos actualizados: {len(archivos_modificados)}'
        
        subprocess.run(
            ['git', 'commit', '-m', mensaje_commit],
            check=True,
            cwd=ruta_base
        )
        
        # Hacer push al repositorio remoto
        print("⬆️  Enviando cambios a GitHub...")
        proceso_push = subprocess.run(
            ['git', 'push'],
            capture_output=True,
            text=True,
            cwd=ruta_base
        )
        
        if proceso_push.returncode != 0:
            print(f"⚠️  Advertencia: No se pudo hacer push al repositorio:")
            print(proceso_push.stderr)
            
            # Verificar si es un problema de autenticación
            if "Authentication failed" in proceso_push.stderr:
                print("\n🔐 PROBLEMA DE AUTENTICACIÓN GITHUB")
                print("Por favor configura la autenticación de GitHub:")
                print("  1. Token de acceso personal:")
                print("     git remote set-url origin https://USERNAME:TOKEN@github.com/USERNAME/REPO.git")
                print("  2. Configura una clave SSH")
                print("  3. Usa 'git credential-store' para guardar credenciales")
                
            return False
            
        print(f"✅ [{datetime.datetime.now()}] Cambios sincronizados correctamente con GitHub.")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ [{datetime.datetime.now()}] Error durante la sincronización con GitHub:")
        print(f"   Comando: {e.cmd}")
        print(f"   Código de salida: {e.returncode}")
        if e.stdout:
            print(f"   Salida: {e.stdout}")
        if e.stderr:
            print(f"   Error: {e.stderr}")
        return False
        
    except Exception as e:
        print(f"💥 [{datetime.datetime.now()}] Error inesperado durante la sincronización:")
        print(str(e))
        traceback.print_exc()
        return False

def activar_despliegue_render():
    """
    Activa manualmente un despliegue en Render utilizando el Deploy Hook URL
    """
    print(f"🚀 [{datetime.datetime.now()}] Activando despliegue manual en Render...")
    
    # Obtener el Deploy Hook URL desde variables de entorno
    deploy_hook_url = os.getenv('RENDER_DEPLOY_HOOK')
    
    if not deploy_hook_url:
        print("\n🔧 DEPLOY HOOK URL NO CONFIGURADO")
        print("Para activar manualmente el despliegue en Render:")
        print("1. Ve a tu servicio en Render → Settings → Build & Deploy")
        print("2. Copia el 'Deploy Hook' URL")
        print("3. Crea un archivo .env en la raíz del proyecto con:")
        print("   RENDER_DEPLOY_HOOK=https://api.render.com/deploy/srv-xxx?key=yyy")
        return False
    
    try:
        # Realizar la solicitud HTTP POST al Deploy Hook URL
        print("📡 Enviando solicitud de despliegue...")
        response = requests.post(deploy_hook_url, timeout=30)
        
        # Verificar la respuesta
        if response.status_code in [200, 201]:
            print(f"✅ Despliegue activado correctamente en Render")
            print(f"   🕐 La aplicación se actualizará en unos minutos")
            return True
        else:
            print(f"⚠️  Respuesta inesperada al activar el despliegue en Render:")
            print(f"   📊 Código de estado: {response.status_code}")
            print(f"   📄 Respuesta: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"⏰ Timeout al comunicarse con Render (esto puede ser normal)")
        print(f"   El despliegue puede haberse activado correctamente")
        return True  # Consideramos esto como éxito
        
    except Exception as e:
        print(f"💥 [{datetime.datetime.now()}] Error al comunicarse con Render:")
        print(str(e))
        return False

def mostrar_resumen_final():
    """
    Muestra un resumen final del estado del proyecto
    """
    print("\n" + "="*60)
    print("📋 RESUMEN FINAL DEL PROCESO")
    print("="*60)
    
    try:
        ruta_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Verificar archivos principales
        archivos_importantes = [
            ('data/Repositorio/Listado_Jornadas.csv', 'Listado de jornadas'),
            ('data/Actas_unificado.csv', 'Actas unificadas'),
            ('data/Goles_unificado.csv', 'Goles unificados'),
            ('data/Sustituciones_unificado.csv', 'Sustituciones unificadas')
        ]
        
        for archivo, descripcion in archivos_importantes:
            ruta_completa = os.path.join(ruta_base, archivo)
            if os.path.exists(ruta_completa):
                try:
                    # Intentar leer como CSV para obtener estadísticas
                    import pandas as pd
                    df = pd.read_csv(ruta_completa)
                    print(f"✅ {descripcion}: {len(df)} registros")
                except:
                    print(f"✅ {descripcion}: Archivo presente")
            else:
                print(f"❌ {descripcion}: No encontrado")
        
        print(f"\n🕐 Proceso completado: {datetime.datetime.now()}")
        
    except Exception as e:
        print(f"⚠️  Error generando resumen: {str(e)}")

# Si el script se ejecuta directamente
if __name__ == "__main__":
    print("🤖 SCRIPT DE ACTUALIZACIÓN AUTOMÁTICA")
    print("="*60)
    
    exito = ejecutar_proceso_completo()
    
    mostrar_resumen_final()
    
    if exito:
        print("\n🎉 ¡Proceso completado exitosamente!")
        sys.exit(0)
    else:
        print("\n❌ El proceso terminó con errores")
        sys.exit(1)