import os
import subprocess
import datetime

# Este script debe guardarse en la misma carpeta que lectura_actas_v2.py

def ejecutar_comando(comando):
    """Ejecuta un comando y muestra su salida"""
    print(f"Ejecutando: {comando}")
    
    # Ejecutar el comando y capturar su salida
    proceso = subprocess.run(comando, shell=True, text=True, 
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Mostrar la salida
    if proceso.stdout:
        print(f"Salida: {proceso.stdout}")
    
    # Mostrar errores si los hay
    if proceso.stderr:
        print(f"Error: {proceso.stderr}")
    
    # Verificar si el comando se ejecutó con éxito
    return proceso.returncode == 0

def main():
    print("=== INICIANDO PROCESO DE ACTUALIZACIÓN ===")
    print(f"Fecha y hora: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Paso 1: Ejecutar el script de extracción de datos
    print("\n--- Paso 1: Ejecutando script de extracción de datos ---")
    if not ejecutar_comando("python lectura_actas_v2.py"):
        print("❌ Error al ejecutar el script de extracción. Abortando.")
        return
    
    print("✅ Script de extracción ejecutado con éxito")
    
    # Paso 2: Añadir los cambios a Git
    print("\n--- Paso 2: Añadiendo cambios a Git ---")
    if not ejecutar_comando("git add ."):
        print("❌ Error al añadir cambios a Git. Abortando.")
        return
    
    print("✅ Cambios añadidos a Git")
    
    # Paso 3: Hacer commit con mensaje automático
    print("\n--- Paso 3: Creando commit ---")
    fecha_actual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    mensaje_commit = f"Actualización automática de datos: {fecha_actual}"
    
    if not ejecutar_comando(f'git commit -m "{mensaje_commit}"'):
        print("❌ Error al crear commit. Puede que no haya cambios para commitear.")
        # No abortamos aquí, ya que podría ser que simplemente no haya cambios
    else:
        print("✅ Commit creado correctamente")
    
    # Paso 4: Subir cambios a GitHub
    print("\n--- Paso 4: Subiendo cambios a GitHub ---")
    if not ejecutar_comando("git push origin master"):
        print("❌ Error al subir cambios a GitHub.")
        return
    
    print("✅ Cambios subidos a GitHub correctamente")
    print("\n=== PROCESO COMPLETADO CON ÉXITO ===")

if __name__ == "__main__":
    main()