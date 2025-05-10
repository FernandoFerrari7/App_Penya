import os
import subprocess
import datetime
import sys

def ejecutar_comando(comando):
    """Ejecuta un comando y muestra su salida de forma más clara"""
    print(f"Ejecutando: {comando}")
    
    # Configurar entorno para usar codificación UTF-8 en Windows
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    
    # Ejecutar el comando y capturar su salida
    proceso = subprocess.run(
        comando, 
        shell=True, 
        text=True, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE,
        env=env,  # Usar el entorno modificado
        errors="replace"  # Reemplazar caracteres que no se pueden mostrar
    )
    
    # Mostrar la salida estándar
    if proceso.stdout:
        print("Salida del comando:")
        print(proceso.stdout)
    
    # Mostrar mensajes de stderr (que no siempre son errores en Git)
    if proceso.stderr and proceso.returncode == 0:
        print("Mensajes informativos:")
        print(proceso.stderr)
    elif proceso.stderr:
        print("ERROR:")
        print(proceso.stderr)
    
    # Verificar si el comando se ejecutó con éxito
    return proceso.returncode == 0

def crear_script_wrapper():
    """
    Crea un script wrapper temporal que ejecuta lectura_actas_v2.py con mejor manejo de errores
    """
    wrapper_script = """
import sys
import os
import traceback

# Intentar ejecutar el script original con mejor manejo de errores
try:
    # Configurar la salida para usar UTF-8 (evita errores con emojis)
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    
    # Importamos las funciones principales del script original
    # Esto ejecutará el código global al inicio del archivo
    try:
        from lectura_actas_v2 import extraccion_jornada, lectura_acta
        print("Funciones importadas correctamente")
    except Exception as e:
        print(f"Error al importar funciones: {str(e)}")
        traceback.print_exc()
        sys.exit(1)
    
    # Ejecutamos el script principal, capturando específicamente los errores por partido
    try:
        # Nota: Esta parte es un poco compleja y podría necesitar ajustes
        import lectura_actas_v2
    except Exception as e:
        print(f"Error en la ejecución principal: {str(e)}")
        traceback.print_exc()
        # A pesar del error, intentamos continuar con la unificación de datos si es posible
    
    # Intentar ejecutar la parte de almacenamiento de datos
    try:
        import glob
        import pandas as pd
        
        print('')
        print('----------------------------------------------------------------------------------------')
        print("Directorio de trabajo actual:", os.getcwd())
        
        # Unificar Actas
        try:
            carpeta='Repositorio/Actas'
            archivos_csv = glob.glob(os.path.join(carpeta, '*.csv'))
            if archivos_csv:
                df_unificado = pd.concat([pd.read_csv(f) for f in archivos_csv])
                df_unificado.to_csv('Actas_unificado.csv', index=False)
                print("Actas unificadas correctamente.")
            else:
                print("No se encontraron archivos en la carpeta de Actas.")
        except Exception as e:
            print(f"Error al unificar Actas: {str(e)}")
        
        # Unificar Goles
        try:
            carpeta='Repositorio/Goles'
            archivos_csv = glob.glob(os.path.join(carpeta, '*.csv'))
            if archivos_csv:
                df_unificado = pd.concat([pd.read_csv(f) for f in archivos_csv])
                df_unificado.to_csv('Goles_unificado.csv', index=False)
                print("Goles unificados correctamente.")
            else:
                print("No se encontraron archivos en la carpeta de Goles.")
        except Exception as e:
            print(f"Error al unificar Goles: {str(e)}")
        
        # Unificar Sustituciones
        try:
            carpeta = 'Repositorio/Sustituciones'
            archivos_csv = glob.glob(os.path.join(carpeta, '*.csv'))
            dataframes = []
            
            for archivo in archivos_csv:
                try:
                    df = pd.read_csv(archivo)
                    jornada = os.path.basename(archivo).split('_')[1][1:]
                    df['Jornada'] = int(jornada)
                    dataframes.append(df)
                except Exception as e:
                    print(f"Error al procesar {archivo}: {str(e)}")
            
            if dataframes:
                df_unificado = pd.concat(dataframes)
                df_unificado.to_csv('Sustituciones_unificado.csv', index=False)
                print("Sustituciones unificadas correctamente")
            else:
                print("No se encontraron archivos CSV válidos para unificar.")
        except Exception as e:
            print(f"Error al unificar Sustituciones: {str(e)}")
        
        # Unificar Jornadas
        try:
            carpeta='Repositorio/Jornadas'
            archivos_csv = glob.glob(os.path.join(carpeta, '*.csv'))
            if archivos_csv:
                df_unificado = pd.concat([pd.read_csv(f) for f in archivos_csv])
                df_unificado.to_csv('Jornadas_unificado.csv', index=False)
                print("Jornadas unificadas correctamente.")
            else:
                print("No se encontraron archivos en la carpeta de Jornadas.")
        except Exception as e:
            print(f"Error al unificar Jornadas: {str(e)}")
        
        # Actualizar estado de extracción
        try:
            ruta_csv = 'Repositorio/Listado_Jornadas.csv'
            ruta_actas = 'Repositorio/Actas'
            
            if os.path.exists(ruta_csv) and os.path.exists(ruta_actas):
                df = pd.read_csv(ruta_csv)
                nombres_archivos = [f for f in os.listdir(ruta_actas) if os.path.isfile(os.path.join(ruta_actas, f))]
                
                for idx, row in df.iterrows():
                    try:
                        equipo_local = str(row['equipo_local']).replace('"', '')
                        equipo_visitante = str(row['equipo_visitante']).replace('"', '')
                        nombre_esperado = f"Acta_J{row['jornada']}_{equipo_local}_vs_{equipo_visitante}.csv"
                        if nombre_esperado in nombres_archivos:
                            df.at[idx, 'acta_extraida'] = 'Si'
                    except Exception as e:
                        print(f"Error al procesar fila {idx}: {str(e)}")
                
                df.to_csv(ruta_csv, index=False)
                print("Actualización de estado completada.")
            else:
                print("No se encontraron los archivos necesarios para actualizar el estado.")
        except Exception as e:
            print(f"Error al actualizar estado: {str(e)}")
        
    except Exception as e:
        print(f"Error en la unificación de datos: {str(e)}")
        traceback.print_exc()
    
    print('')
    print('----------------------------------------------------------------------------------------')
    print("Proceso completado con algunos errores, pero se han unificado los datos disponibles.")
    
except Exception as e:
    print(f"Error general: {str(e)}")
    traceback.print_exc()
    sys.exit(1)
"""
    
    # Escribir el script a un archivo temporal
    script_path = "temp_wrapper.py"
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(wrapper_script)
    
    return script_path

def limpiar_archivos_temporales():
    """Elimina los archivos temporales creados"""
    if os.path.exists("temp_wrapper.py"):
        os.remove("temp_wrapper.py")
    if os.path.exists("temp_wrapper.pyc"):
        os.remove("temp_wrapper.pyc")

def main():
    print("=== INICIANDO PROCESO DE ACTUALIZACIÓN ===")
    print(f"Fecha y hora: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Crear script wrapper para mejor manejo de errores
    wrapper_script = crear_script_wrapper()
    
    # Paso 1: Ejecutar el script de extracción de datos con el wrapper
    print("\n--- Paso 1: Ejecutando script de extracción de datos ---")
    extraccion_exitosa = ejecutar_comando(f"python {wrapper_script}")
    
    # Limpiar archivos temporales
    limpiar_archivos_temporales()
    
    if not extraccion_exitosa:
        print("⚠️ La extracción de datos tuvo algunos errores, pero continuaremos con la actualización de GitHub")
    else:
        print("✓ Script de extracción ejecutado con éxito")
    
    # Paso 2: Añadir los cambios a Git
    print("\n--- Paso 2: Añadiendo cambios a Git ---")
    if not ejecutar_comando("git add ."):
        print("❌ Error al añadir cambios a Git. Abortando.")
        return
    
    print("✓ Cambios añadidos a Git")
    
    # Paso 3: Hacer commit con mensaje automático
    print("\n--- Paso 3: Creando commit ---")
    fecha_actual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    mensaje_commit = f"Actualización automática de datos: {fecha_actual}"
    
    if not ejecutar_comando(f'git commit -m "{mensaje_commit}"'):
        print("⚠️ No se creó ningún commit. Puede que no haya cambios para commitear.")
        # No abortamos aquí, ya que podría ser que simplemente no haya cambios
    else:
        print("✓ Commit creado correctamente")
    
    # Paso 4: Subir cambios a GitHub
    print("\n--- Paso 4: Subiendo cambios a GitHub ---")
    # Intentar detectar la rama actual
    try:
        result = subprocess.run(
            "git branch --show-current", 
            shell=True, 
            text=True,
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE
        )
        rama = result.stdout.strip() if result.returncode == 0 and result.stdout.strip() else "master"
    except:
        rama = "master"  # Valor por defecto
    
    if not ejecutar_comando(f"git push origin {rama}"):
        print(f"❌ Error al subir cambios a GitHub en la rama {rama}.")
        return
    
    print("✓ Cambios subidos a GitHub correctamente")
    print("\n=== PROCESO COMPLETADO CON ÉXITO ===")

if __name__ == "__main__":
    main()