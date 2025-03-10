# Dashboard Penya Independent

Una aplicación web construida con Streamlit para visualizar estadísticas y análisis del equipo Penya Independent.

## Descripción

Este dashboard proporciona un análisis detallado de las estadísticas del equipo de fútbol Penya Independent, incluyendo:

- Estadísticas generales del equipo
- Análisis de jugadores (goles, tarjetas, minutos)
- Análisis de partidos (local vs visitante, rendimiento por rival)
- Visualización de goles y tarjetas

## Estructura del Proyecto

```
AppPenya/
├── .streamlit/           # Configuración de Streamlit
├── assets/               # Recursos estáticos
├── calculos/             # Módulos de cálculo y procesamiento
├── common/               # Componentes comunes (menú, login)
├── data/                 # Archivos CSV
├── pages/                # Páginas de la aplicación
├── utils/                # Funciones auxiliares
├── visualizaciones/      # Componentes visuales
├── home.py               # Página principal
├── README.md             # Documentación
└── requirements.txt      # Dependencias
```

## Requisitos

- Python 3.8+
- Streamlit
- Pandas
- Plotly
- NumPy
- Matplotlib
- Seaborn

## Instalación

1. Clona este repositorio:
   ```bash
   git clone https://github.com/FernandoFerrari7/App_Penya.git
   cd AppPenya
   ```

2. Crea un entorno virtual y actívalo:
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```

3. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

## Uso

Para ejecutar la aplicación:

```bash
streamlit run home.py
```

Navega entre las diferentes secciones utilizando el menú superior.

## Datos

La aplicación utiliza los siguientes archivos CSV:
- `Actas_unificado.csv`: Estadísticas de jugadores por partido
- `Goles_unificado.csv`: Información sobre goles
- `Jornadas_unificado.csv`: Información sobre partidos
- `Sustituciones_unificado.csv`: Datos de sustituciones