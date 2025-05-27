"""
Configuración para diferentes temporadas y competiciones
"""
import os
from datetime import datetime

# Configuración de temporadas
TEMPORADAS = {
    # Temporada 2024-2025 (actual)
    "2024-25": {
        "cod_competicion": 7077248,
        "cod_grupo": 7077249,
        "cod_temporada": 20,
        "nombre": "Temporada 2024-2025",
        "fecha_inicio": "2024-08-01",
        "fecha_fin": "2025-05-31",
        "jornadas_total": 34,
        "activa": True
    },
    
    # Plantilla para próxima temporada (a actualizar cuando esté disponible)
    "2025-26": {
        "cod_competicion": None,  # A determinar
        "cod_grupo": None,        # A determinar
        "cod_temporada": None,    # A determinar
        "nombre": "Temporada 2025-2026",
        "fecha_inicio": "2025-08-01",
        "fecha_fin": "2026-05-31",
        "jornadas_total": 34,
        "activa": False
    }
}

def obtener_temporada_activa():
    """
    Obtiene la configuración de la temporada activa
    """
    # Buscar la temporada marcada como activa
    for codigo, config in TEMPORADAS.items():
        if config.get('activa', False):
            return codigo, config
    
    # Si no hay ninguna activa, usar la más reciente
    temporada_mas_reciente = max(TEMPORADAS.keys())
    return temporada_mas_reciente, TEMPORADAS[temporada_mas_reciente]

def obtener_configuracion_temporada(codigo_temporada=None):
    """
    Obtiene la configuración de una temporada específica o la activa
    """
    if codigo_temporada and codigo_temporada in TEMPORADAS:
        return TEMPORADAS[codigo_temporada]
    else:
        _, config = obtener_temporada_activa()
        return config

def cambiar_temporada_activa(nuevo_codigo):
    """
    Cambia la temporada activa
    """
    if nuevo_codigo not in TEMPORADAS:
        raise ValueError(f"Temporada {nuevo_codigo} no encontrada")
    
    # Desactivar todas las temporadas
    for codigo in TEMPORADAS:
        TEMPORADAS[codigo]['activa'] = False
    
    # Activar la nueva temporada
    TEMPORADAS[nuevo_codigo]['activa'] = True
    
    print(f"✅ Temporada activa cambiada a: {TEMPORADAS[nuevo_codigo]['nombre']}")

def agregar_nueva_temporada(codigo, cod_competicion, cod_grupo, cod_temporada, 
                           nombre=None, fecha_inicio=None, fecha_fin=None, 
                           jornadas_total=34, activar=True):
    """
    Agrega una nueva temporada al sistema
    """
    if nombre is None:
        nombre = f"Temporada {codigo}"
    
    nueva_temporada = {
        "cod_competicion": cod_competicion,
        "cod_grupo": cod_grupo,
        "cod_temporada": cod_temporada,
        "nombre": nombre,
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin,
        "jornadas_total": jornadas_total,
        "activa": activar
    }
    
    # Si se va a activar esta temporada, desactivar las demás
    if activar:
        for codigo_temp in TEMPORADAS:
            TEMPORADAS[codigo_temp]['activa'] = False
    
    TEMPORADAS[codigo] = nueva_temporada
    
    print(f"✅ Nueva temporada agregada: {nombre}")
    if activar:
        print(f"✅ Temporada {codigo} establecida como activa")

def listar_temporadas():
    """
    Lista todas las temporadas configuradas
    """
    print("📅 TEMPORADAS CONFIGURADAS:")
    print("-" * 50)
    
    for codigo, config in TEMPORADAS.items():
        estado = "🟢 ACTIVA" if config.get('activa') else "⚪ Inactiva"
        print(f"  {codigo}: {config['nombre']} {estado}")
        print(f"    Competición: {config['cod_competicion']}")
        print(f"    Grupo: {config['cod_grupo']}")
        print(f"    Temporada: {config['cod_temporada']}")
        print(f"    Jornadas: {config['jornadas_total']}")
        print()

def detectar_nueva_temporada():
    """
    Detecta automáticamente si es necesario cambiar de temporada
    basándose en las fechas
    """
    fecha_actual = datetime.now()
    
    for codigo, config in TEMPORADAS.items():
        if config['fecha_fin']:
            fecha_fin = datetime.strptime(config['fecha_fin'], "%Y-%m-%d")
            
            # Si la temporada activa ya terminó
            if config.get('activa') and fecha_actual > fecha_fin:
                print(f"⚠️  La temporada activa ({config['nombre']}) ya terminó")
                print(f"   Fecha fin: {config['fecha_fin']}")
                print(f"   Fecha actual: {fecha_actual.strftime('%Y-%m-%d')}")
                return True
    
    return False

def obtener_parametros_scraping():
    """
    Obtiene los parámetros necesarios para el scraping de la temporada activa
    """
    config = obtener_configuracion_temporada()
    
    # Verificar que los parámetros estén configurados
    if not all([config['cod_competicion'], config['cod_grupo'], config['cod_temporada']]):
        raise ValueError("La temporada activa no tiene todos los parámetros configurados")
    
    return {
        'cod_competicion': config['cod_competicion'],
        'cod_grupo': config['cod_grupo'],
        'cod_temporada': config['cod_temporada'],
        'jornadas_total': config['jornadas_total']
    }

# Función para uso directo en scripts existentes
def obtener_parametros_actuales():
    """
    Función de compatibilidad con scripts existentes
    Retorna: cod_competicion, cod_grupo, cod_temporada
    """
    params = obtener_parametros_scraping()
    return params['cod_competicion'], params['cod_grupo'], params['cod_temporada']

if __name__ == "__main__":
    # Ejemplos de uso
    print("🔧 CONFIGURACIÓN DE TEMPORADAS")
    print("=" * 50)
    
    # Listar temporadas
    listar_temporadas()
    
    # Mostrar temporada activa
    codigo_activa, config_activa = obtener_temporada_activa()
    print(f"📅 Temporada activa: {config_activa['nombre']}")
    
    # Detectar si necesita cambio
    if detectar_nueva_temporada():
        print("🚨 Se recomienda actualizar la temporada activa")
    
    # Mostrar parámetros para scraping
    try:
        params = obtener_parametros_scraping()
        print(f"\n🕷️  PARÁMETROS PARA SCRAPING:")
        print(f"   Competición: {params['cod_competicion']}")
        print(f"   Grupo: {params['cod_grupo']}")
        print(f"   Temporada: {params['cod_temporada']}")
        print(f"   Jornadas: {params['jornadas_total']}")
    except ValueError as e:
        print(f"❌ Error: {e}")