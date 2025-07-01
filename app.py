# Paso 1. Instalar librerías (solo necesitas hacer esto una vez):
# pip install streamlit pandas requests plotly prophet scikit-learn seaborn

# Para ejecutar tu app:
# streamlit run app.py

# Librerías para la app y datos
import streamlit as st        #  Crea aplicaciones web interactivas en Python.
import requests               #  Permite hacer peticiones a APIs (enlaces de datos).
import pandas as pd           #  Manipula y analiza datos en forma de tablas.
import numpy as np            #  Realiza operaciones matemáticas y numéricas.
import json                   #  Trabaja con datos en formato JSON (muy usado en APIs).

# Visualización de gráficos
import plotly.express as px   #  Crea gráficos interactivos (líneas, barras, mapas, etc.).
import matplotlib.pyplot as plt  #  Genera gráficos estáticos y personalizables.
       #  Estilo más bonito para los gráficos de matplotlib.

# Manejo de fechas y tiempo
import calendar               #  Permite trabajar con fechas, meses, años, etc.
from datetime import datetime #  Para convertir cadenas de texto en fechas.  
import warnings               #  Sirve para ocultar advertencias del sistema.

# Modelos de predicción
from prophet import Prophet   #  Modelo para hacer predicciones en series de tiempo.
from sklearn.cluster import KMeans                     #  Agrupa datos similares (clustering).
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier  #  Modelos de predicción tipo "bosque aleatorio".
from sklearn.metrics import mean_squared_error, r2_score, accuracy_score, confusion_matrix  #  Evalúan si el modelo es bueno o no.
from sklearn.model_selection import train_test_split   #  Divide los datos en entrenamiento y prueba.

import warnings               # Sirve para ocultar advertencias del sistema.
warnings.filterwarnings('ignore')  # Oculta todas las advertencias





#Pregunta 1.- Detallar cada una de las librerías cual es su funcionalidad.

#Paso 2. Configuración de la página


# Importamos la librería Streamlit para construir la interfaz web
import streamlit as st

# Configuración inicial de la página web de la aplicación
st.set_page_config(
    page_title="Análisis de Compras Públicas Ecuador",  # Título que aparece en la pestaña del navegador
    page_icon="📊",  # Ícono (emoji) en la pestaña del navegador
    layout="wide",  # Ancho completo de la pantalla para mejor visualización
    initial_sidebar_state="expanded"  # La barra lateral se abre automáticamente
)

# Título principal que se muestra en la parte superior de la aplicación
st.title("📊 Análisis de Compras Públicas Ecuador")

# Línea divisoria para separar secciones visualmente
st.markdown("---")

# Título o encabezado dentro de la barra lateral
st.sidebar.header("🔍 Filtros de Consulta")

# Lista de provincias disponibles para selección
provincias = [
    "AZUAY", "BOLIVAR", "CAÑAR", "CARCHI", "CHIMBORAZO", "COTOPAXI", 
    "EL ORO", "ESMERALDAS", "GALAPAGOS", "GUAYAS", "IMBABURA", 
    "LOJA", "LOS RIOS", "MANABI", "MORONA SANTIAGO", "NAPO", 
    "ORELLANA", "PASTAZA", "PICHINCHA", "SANTA ELENA", 
    "SANTO DOMINGO DE LOS TSACHILAS", "SUCUMBIOS", "TUNGURAHUA", 
    "ZAMORA CHINCHIPE"
]

# Lista de tipos de contratación disponibles para selección
tipos_contratacion = [
    "Licitación", "Cotización", "Menor Cuantía", "Ínfima Cuantía",
    "Subasta Inversa", "Régimen Especial", "Contratación Directa",
    "Consultoría", "Obra", "Bien", "Servicio"
]

# Checkbox en la barra lateral para activar el análisis de todos los años
todos_los_anios = st.sidebar.checkbox("📅 Analizar todos los años (2015-2025)")

# Menú desplegable para seleccionar un año específico (por defecto 2020)
year = st.sidebar.selectbox("📅 Año:", options=list(range(2015, 2026)), index=5)

# Menú desplegable para seleccionar una provincia (opción "Todas" incluida)
provincia = st.sidebar.selectbox("🏢 Provincia:", options=["Todas"] + sorted(provincias), index=0)

# Menú desplegable para seleccionar el tipo de contratación (opción "Todos" incluida)
tipo_contratacion = st.sidebar.selectbox("📋 Tipo de Contratación:", options=["Todos"] + sorted(tipos_contratacion), index=0)

# Verifica si existen ciertas variables en la sesión, si no, las crea
# 'session_state' permite guardar valores entre interacciones del usuario
if 'df_data' not in st.session_state:
    st.session_state.df_data = None  # Aquí se guardará el DataFrame con los datos

if 'last_query' not in st.session_state:
    st.session_state.last_query = None  # Aquí se guardará la última consulta realizada






# Pregunta 3.- Para qué sirven los siguientes métodos dar una descripción de cada uno.


# Construye los parámetros que se enviarán en la consulta a la API
def construir_parametros(year, provincia, tipo):
    params = {"year": str(year)}  # Siempre se incluye el año como parámetro
    if provincia != "Todas":
        params["region"] = provincia.upper()  # Si se selecciona una provincia específica, se agrega
    if tipo != "Todos":
        params["type"] = tipo  # Si se selecciona un tipo de contratación específico, se agrega
    return params  # Retorna el diccionario con los parámetros

# Se conecta a la API del gobierno y obtiene los datos según los filtros aplicados
def obtener_datos(year, provincia, tipo):
    url = "https://datosabiertos.compraspublicas.gob.ec/PLATAFORMA/api/get_analysis"
    params = construir_parametros(year, provincia, tipo)  # Se construyen los parámetros a enviar
    try:
        # Se hace la solicitud GET a la API con tiempo límite de espera
        response = requests.get(url, params=params, timeout=30)
        if response.status_code != 200:
            return None, f"Error HTTP {response.status_code}: {response.reason}"  # Error de servidor

        try:
            data = response.json()  # Intenta convertir la respuesta a formato JSON
        except json.JSONDecodeError:
            return None, "Error: La respuesta no es un JSON válido"  # Error de formato

        if not data:
            return None, "No se encontraron datos para los filtros seleccionados"  # Respuesta vacía

        df = pd.DataFrame(data)  # Se convierte el JSON en un DataFrame
        if df.empty:
            return None, "Los datos obtenidos están vacíos"  # DataFrame sin datos

        return df, None  # Retorna los datos y ningún error
    except requests.exceptions.Timeout:
        return None, "Error: Tiempo de espera agotado."  # Error si la API tarda demasiado
    except requests.exceptions.ConnectionError:
        return None, "Error: No se pudo conectar con la API."  # Problema de conexión
    except Exception as e:
        return None, str(e)  # Cualquier otro error inesperado

# Limpia, transforma y prepara los datos para análisis o visualización
def limpiar_datos(df):
    if df is None or df.empty:
        return None, "No hay datos para procesar"  # Verifica que haya datos

    try:
        df_clean = df.copy()  # Copia los datos originales para no modificarlos directamente

        # Diccionario para cambiar nombres de columnas a nombres estándar
        column_mapping = {
            'monto': 'total', 'amount': 'total', 'valor': 'total',
            'tipo': 'internal_type', 'type': 'internal_type', 'categoria': 'internal_type',
            'contratos': 'contracts', 'cantidad': 'contracts', 'count': 'contracts',
            'mes': 'month', 'fecha': 'date'
        }

        # Renombra columnas si es necesario
        for old_name, new_name in column_mapping.items():
            if old_name in df_clean.columns and new_name not in df_clean.columns:
                df_clean[new_name] = df_clean[old_name]

        # Convierte las columnas numéricas a tipo adecuado
        for col in ['total', 'contracts', 'month']:
            if col in df_clean.columns:
                df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')

        # Extrae el mes desde la fecha si no existe la columna 'month'
        if 'month' not in df_clean.columns:
            if 'date' in df_clean.columns:
                df_clean['date'] = pd.to_datetime(df_clean['date'], errors='coerce')
                df_clean['month'] = df_clean['date'].dt.month
            else:
                df_clean['month'] = (df_clean.index % 12) + 1  # Asigna meses aleatorios si no hay fecha

        # Elimina filas con valores nulos o cero en la columna 'total'
        if 'total' in df_clean.columns:
            df_clean = df_clean.dropna(subset=['total'])
            df_clean = df_clean[df_clean['total'] > 0]

        # Elimina registros con tipo de contratación vacío
        if 'internal_type' in df_clean.columns:
            df_clean = df_clean.dropna(subset=['internal_type'])
            df_clean = df_clean[df_clean['internal_type'].str.strip() != '']

        # Si no hay columna de cantidad de contratos, la crea con valor 1
        if 'contracts' not in df_clean.columns:
            df_clean['contracts'] = 1

        if df_clean.empty:
            return None, "No quedan datos válidos"  # Verifica que haya datos útiles

        return df_clean, None  # Retorna el DataFrame limpio y sin errores
    except Exception as e:
        return None, f"Error limpiando datos: {str(e)}"  # Error inesperado durante la limpieza






# Paso 4. Consultar Datos 
# Cuando el usuario presiona el botón en la barra lateral para consultar datos
if st.sidebar.button("🔄 Consultar Datos", type="primary"):

    # Muestra un mensaje mientras se cargan los datos
    with st.spinner("Consultando datos de la API..."):

        # Si el usuario marcó la opción para consultar todos los años (2015-2025)
        if todos_los_anios:
            dataframes = []  # Lista para almacenar los datos de cada año
            errores = []     # Lista para almacenar errores por cada año si ocurre

            # Bucle que recorre todos los años entre 2015 y 2025
            for y in range(2015, 2026):
                df, error = obtener_datos(y, provincia, tipo_contratacion)  # Consulta la API
                if df is not None:
                    df['anio'] = y  # Se agrega una columna con el año para distinguirlo luego
                    dataframes.append(df)  # Se guarda el dataframe del año
                else:
                    errores.append(f"{y}: {error}")  # Se guarda el mensaje de error para ese año

            # Si al menos se obtuvo un año con datos
            if dataframes:
                df_all = pd.concat(dataframes, ignore_index=True)  # Une todos los años en un solo dataframe

                # Se limpian y preparan los datos
                df_clean, clean_error = limpiar_datos(df_all)

                if clean_error:
                    st.error(f"❌ {clean_error}")  # Muestra error si ocurrió durante limpieza
                else:
                    # Se informa cuántos registros se cargaron correctamente
                    st.success(f"✅ {len(df_clean)} registros cargados.")

                    # Se guardan los datos limpios en la sesión (para visualización posterior)
                    st.session_state.df_data = df_clean
                    st.session_state.last_query = "todos_los_anios"
            else:
                # Si no se obtuvo ningún año con datos válidos
                st.error("❌ No se obtuvieron datos para ningún año.")
                for e in errores:
                    st.warning(e)  # Muestra los errores de cada año

        # Si no se seleccionó "todos los años", solo se consulta un año específico
        else:
            df, error = obtener_datos(year, provincia, tipo_contratacion)
            if error:
                st.error(f"❌ {error}")  # Muestra error si no se pudo obtener datos
            else:
                df_clean, clean_error = limpiar_datos(df)  # Limpia los datos

                if clean_error:
                    st.error(f"❌ {clean_error}")  # Muestra error si los datos están vacíos o mal
                else:
                    st.success(f"✅ {len(df_clean)} registros cargados.")  # Mensaje de éxito

                    # Se guardan los datos en la sesión
                    st.session_state.df_data = df_clean
                    st.session_state.last_query = f"{year}_{provincia}_{tipo_contratacion}"









# Si existen datos consultados y almacenados en session_state, se procede a visualizarlos
if st.session_state.df_data is not None:
    st.markdown("### 📥 Descargar Datos Limpios")
    csv = st.session_state.df_data.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Descargar CSV",
        data=csv,
        file_name="datos_limpios.csv",
        mime='text/csv'
        )

    df_clean = st.session_state.df_data

    # Título de la sección de visualización
    st.markdown("## 📊 Visualización de Datos")

    # Se crean pestañas para mostrar diferentes tipos de gráficos
    tabs_vis = st.tabs([
        "Gráfica de Barras", 
        "Gráfica de Líneas", 
        "Gráfica de Pastel", 
        "Gráfica de Dispersión", 
        "Tipos por Mes"
    ])

    # Pestaña 1: Gráfico de barras del monto total por tipo de contratación
    with tabs_vis[0]:
        st.subheader("Gráfica de Barras: Total por Tipo de Contratación")
        if 'internal_type' in df_clean.columns and 'total' in df_clean.columns:
            df_bar = df_clean.groupby('internal_type')['total'].sum().reset_index()
            fig_bar = px.bar(
                df_bar, 
                x='internal_type', 
                y='total', 
                title="Totales por Tipo de Contratación",
                labels={'internal_type': 'Tipo de Contratación', 'total': 'Monto Total ($)'}
            )
            st.plotly_chart(fig_bar, use_container_width=True)

    # Pestaña 2: Gráfico de líneas que muestra la evolución mensual del monto total
    with tabs_vis[1]:
        st.subheader("Gráfica de Líneas: Evolución Mensual de Montos Totales")
        if 'month' in df_clean.columns and 'total' in df_clean.columns:
            df_line = df_clean.groupby('month')['total'].sum().reset_index()
            df_line['mes'] = df_line['month'].apply(lambda x: calendar.month_name[x])  # Nombre del mes
            fig_line = px.line(
                df_line, 
                x='mes', 
                y='total', 
                title="Evolución Mensual del Monto Total",
                labels={'mes': 'Mes', 'total': 'Monto Total ($)'},
                markers=True
            )
            st.plotly_chart(fig_line, use_container_width=True)

    # Pestaña 3: Gráfico de pastel que representa la proporción de contratos por tipo
    with tabs_vis[2]:
        st.subheader("Gráfica de Pastel: Proporción de Contratos por Tipo")
        if 'internal_type' in df_clean.columns and 'contracts' in df_clean.columns:
            df_pie = df_clean.groupby('internal_type')['contracts'].sum().reset_index()
            fig_pie = px.pie(
                df_pie, 
                values='contracts', 
                names='internal_type',
                title="Proporción de Contratos por Tipo"
            )
            st.plotly_chart(fig_pie, use_container_width=True)

    # Pestaña 4: Gráfico de dispersión entre contratos y monto total
    with tabs_vis[3]:
        st.subheader("Gráfica de Dispersión: Relación Total vs Contratos")
        if 'contracts' in df_clean.columns and 'total' in df_clean.columns:
            fig_disp = px.scatter(
                df_clean, 
                x='contracts', 
                y='total', 
                color='internal_type' if 'internal_type' in df_clean.columns else None,
                title="Relación entre Total y Cantidad de Contratos",
                labels={'contracts': 'Contratos', 'total': 'Monto Total ($)'}
            )
            st.plotly_chart(fig_disp, use_container_width=True)

    # Pestaña 5: Línea por mes y tipo de contratación
    with tabs_vis[4]:
        st.subheader("Gráfica de Línea: Tipos de Contrato por Mes")
        if all(col in df_clean.columns for col in ['month', 'internal_type', 'total']):
            df_tipo_mes = df_clean.groupby(['month', 'internal_type'])['total'].sum().reset_index()
            fig_tipo_mes = px.line(
                df_tipo_mes, 
                x='month', 
                y='total', 
                color='internal_type',
                title="Tipos de Contrato por Mes",
                labels={'month': 'Mes', 'total': 'Monto Total ($)', 'internal_type': 'Tipo'},
                markers=True
            )
            fig_tipo_mes.update_xaxes(tickmode='linear', dtick=1)
            st.plotly_chart(fig_tipo_mes, use_container_width=True)
       



    
import seaborn as sns

if st.session_state.df_data is not None:
    df_modelos = st.session_state.df_data.copy()
    if 'anio' not in df_modelos.columns and 'date' in df_modelos.columns:
        df_modelos['date'] = pd.to_datetime(df_modelos['date'], errors='coerce')
        df_modelos['anio'] = df_modelos['date'].dt.year
    st.markdown("---")
    st.header("🤖 Modelos Analíticos y Predictivos")

    tabs_modelos = st.tabs(["📈 Regresión", "🔍 Clasificación", "📊 Clustering", "⏳ Series Temporales"])

    # --- REGRESIÓN ---
    with tabs_modelos[0]:
        st.subheader("📈 Predicción del Monto Total")
        if all(col in df_modelos.columns for col in ['contracts', 'total', 'month']):
            df_reg = df_modelos[['contracts', 'month', 'total']].dropna()
            X = df_reg[['contracts', 'month']]
            y = df_reg['total']
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

            model_reg = RandomForestRegressor(n_estimators=100, random_state=42)
            model_reg.fit(X_train, y_train)
            y_pred = model_reg.predict(X_test)

            st.write("**Métricas del Modelo:**")
            st.write(f"RMSE: {np.sqrt(mean_squared_error(y_test, y_pred)):.2f}")
            st.write(f"R² Score: {r2_score(y_test, y_pred):.2f}")

            fig_reg = px.scatter(x=y_test, y=y_pred, labels={'x': 'Valor Real', 'y': 'Predicción'},
                                 title="Predicción vs Valor Real")
            st.plotly_chart(fig_reg, use_container_width=True)
        else:
            st.warning("Faltan columnas necesarias para la regresión")

    # --- CLASIFICACIÓN ---
    with tabs_modelos[1]:
        st.subheader("🔍 Clasificación del Monto Total")
        df_clas = df_modelos[['contracts', 'month', 'total']].dropna().copy()
        df_clas['categoria'] = pd.cut(df_clas['total'], bins=[0, 10000, 100000, np.inf],
                                       labels=['Bajo', 'Medio', 'Alto'])
        X = df_clas[['contracts', 'month']]
        y = df_clas['categoria']
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

        model_clf = RandomForestClassifier(n_estimators=100, random_state=42)
        model_clf.fit(X_train, y_train)
        y_pred = model_clf.predict(X_test)

        st.write(f"Accuracy: {accuracy_score(y_test, y_pred):.2f}")
        cm = confusion_matrix(y_test, y_pred, labels=['Bajo', 'Medio', 'Alto'])
        st.write("Matriz de Confusión:")
        st.dataframe(pd.DataFrame(cm, index=['Bajo', 'Medio', 'Alto'], columns=['Bajo', 'Medio', 'Alto']))

    # --- CLUSTERING ---
    with tabs_modelos[2]:
        st.subheader("📊 Agrupamiento por Comportamiento de Contratación")
        df_clust = df_modelos[['contracts', 'month', 'total']].dropna()
        kmeans = KMeans(n_clusters=3, random_state=42)
        df_clust['cluster'] = kmeans.fit_predict(df_clust)
        fig_cluster = px.scatter(df_clust, x='contracts', y='total', color='cluster',title="Clústeres de Contrataciones")
        st.plotly_chart(fig_cluster, use_container_width=True)

    # --- SERIES TEMPORALES ---
    with tabs_modelos[3]:
        st.subheader("⏳ Predicción de Montos con Prophet")
        if 'anio' in df_modelos.columns and 'month' in df_modelos.columns:
            df_ts = df_modelos.groupby(['anio', 'month'])['total'].sum().reset_index()
            df_ts['fecha'] = pd.to_datetime(df_ts['anio'].astype(str) + '-' + df_ts['month'].astype(str) + '-01')
            df_ts = df_ts[['fecha', 'total']].rename(columns={'fecha': 'ds', 'total': 'y'})
            df_ts = df_ts[df_ts['y'] > 0]

            modelo_prophet = Prophet()
            modelo_prophet.fit(df_ts)

            futuro = modelo_prophet.make_future_dataframe(periods=6, freq='M')
            forecast = modelo_prophet.predict(futuro)

            fig_prophet = px.line(forecast, x='ds', y='yhat', title="Predicción de Montos Futuros")
            st.plotly_chart(fig_prophet, use_container_width=True)
        else:
            st.warning("Se necesitan columnas 'anio' y 'month' para construir la serie temporal")

