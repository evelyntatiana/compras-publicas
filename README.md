# Análisis de Compras Públicas del Ecuador

Aplicación interactiva desarrollada con **Python y Streamlit** para consultar, limpiar, explorar y visualizar información de compras públicas del Ecuador a partir de datos abiertos.

## Funcionalidades

- Consulta de información mediante API.
- Filtros por año, provincia y tipo de contratación.
- Procesamiento y limpieza de datos con Pandas.
- Análisis de múltiples periodos entre 2015 y 2025.
- Visualizaciones interactivas.
- Preparación de datos para análisis estadístico y modelos predictivos.

## Tecnologías

- Python
- Streamlit
- Pandas
- NumPy
- Requests
- Plotly
- Matplotlib
- Prophet
- Scikit-learn

## Fuente de datos

El proyecto consulta la [plataforma de datos abiertos de compras públicas del Ecuador](https://datosabiertos.compraspublicas.gob.ec/) mediante el endpoint `/PLATAFORMA/api/get_analysis`. Requiere conexión a Internet y depende de la disponibilidad y del formato de respuesta de esa API.

## Ejecución local

Requiere Python y Git instalados. Desde una terminal:

```bash
git clone https://github.com/evelyntatiana/compras-publicas.git
cd compras-publicas
python -m venv .venv
```

Activa el entorno virtual:

- Windows (PowerShell): `.\.venv\Scripts\Activate.ps1`
- macOS / Linux: `source .venv/bin/activate`

Instala las dependencias e inicia la aplicación:

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

La ejecución local abre la aplicación en tu equipo. Este README no incluye una demo pública desplegada.

## Alcance y limitaciones

- La interfaz permite consultar años entre 2015 y 2025; la disponibilidad efectiva depende de la API.
- Incluye ejercicios de regresión, clasificación, agrupamiento y series temporales. Sus resultados son exploratorios y dependen de los datos recuperados.
- Si la respuesta no contiene `month` ni `date`, el procesamiento asigna meses de forma cíclica según la posición de las filas. Esos meses no representan fechas observadas y no deben usarse para concluir tendencias temporales ni validar pronósticos.
- Si falta `contracts`, el procesamiento asigna el valor 1 por fila; ese valor no acredita la cantidad real de contratos.

## Propósito

Proyecto académico enfocado en consumo de APIs, limpieza de datos, análisis exploratorio, visualización y aplicación de técnicas de ciencia de datos sobre información pública.

---

**Autora:** Evelyn Criollo
