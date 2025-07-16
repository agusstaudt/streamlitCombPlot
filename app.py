import streamlit as st
import pandas as pd
import pymysql
import plotly.express as px

# ------------------------
# Configuración de conexión
# ------------------------
@st.cache_data(ttl=3600)
def obtener_datos():
    cnx = pymysql.connect(
        host='45.228.176.80',
        user='dev',
        password='rtk099%!ZmY&101',
        port=43306,
        database='datos_combustibles'
    )
    query = "SELECT * FROM base_misiones"
    df = pd.read_sql(query, cnx)
    cnx.close()
    return df

# ------------------------
# Diccionario de meses español → inglés
# ------------------------
meses_es_en = {
    "Enero": "January",
    "Febrero": "February",
    "Marzo": "March",
    "Abril": "April",
    "Mayo": "May",
    "Junio": "June",
    "Julio": "July",
    "Agosto": "August",
    "Septiembre": "September",
    "Octubre": "October",
    "Noviembre": "November",
    "Diciembre": "December"
}
meses_en_es = {v: k for k, v in meses_es_en.items()}

# ------------------------
# Función para traducir 'Abril de 2025' → 'April 2025'
# ------------------------
def traducir_mes(mes_str):
    try:
        partes = mes_str.split(' de ')
        mes_en = meses_es_en.get(partes[0], partes[0])
        return f"{mes_en} {partes[1]}"
    except:
        return None

# ------------------------
# Streamlit App
# ------------------------
st.set_page_config(page_title="Dashboard de Volumen", layout="wide")
st.title("📊 Dashboard de Volumen informado (m3)")

# Cargar datos
if st.button("🔄 Actualizar datos desde la base"):
    obtener_datos.clear()
df = obtener_datos()

# Preprocesamiento
df['Mes_str'] = df['Mes'].apply(traducir_mes)
df['fecha'] = pd.to_datetime(df['Mes_str'], format='%B %Y', errors='coerce')
df = df.dropna(subset=['fecha'])

# Columnas auxiliares
df['Año'] = df['fecha'].dt.year
df['Mes_num'] = df['fecha'].dt.month
df['Mes_nombre'] = df['fecha'].dt.strftime('%B').map(meses_en_es)
df['Mes_display'] = df['Mes_nombre'] + ' ' + df['Año'].astype(str)

# Crear DataFrame de períodos únicos ordenados por fecha real
periodos = df[['fecha', 'Mes_display']].drop_duplicates().sort_values('fecha', ascending=False)

# Selector ordenado cronológicamente
mes_opcion = st.selectbox("Seleccionar período (mes/año)", periodos['Mes_display'].tolist())

# Extraer año y mes
mes_nombre, año = mes_opcion.split(' ')
año = int(año)
mes_num = list(meses_es_en.keys()).index(mes_nombre) + 1

# Filtro
df_filtrado = df[(df['Año'] == año) & (df['Mes_num'] == mes_num)]

# Gráfico
if not df_filtrado.empty:
    fig = px.bar(
        df_filtrado,
        x='Localidad',
        y='Volumen informado (m3)',
        title=f'Volumen informado en {mes_nombre} {año}',
        labels={'Volumen informado (m3)': 'Volumen (m3)'},
        color='Localidad',
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("⚠ No hay datos disponibles para ese mes/año.")