
import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

st.set_page_config(page_title="Dashboard Energético", layout="wide")
st.title("🔋 Dashboard Energético Interactivo")

conn = sqlite3.connect("analisis_energetico.db")

df_time = pd.read_sql_query("""
    SELECT DISTINCT Country, Time
    FROM Monthly_Electricity_Statistics
    WHERE Balance = 'Net Electricity Production'
""", conn)
df_time['Time'] = pd.to_datetime(df_time['Time'], format='%B %Y')
df_time['Year'] = df_time['Time'].dt.year

paises = sorted(df_time['Country'].dropna().unique())
anios = sorted(df_time['Year'].dropna().unique(), reverse=True)

st.sidebar.header("Filtros")
pais = st.sidebar.selectbox("Selecciona el país", paises)
anio = st.sidebar.selectbox("Selecciona el año", anios)

df = pd.read_sql_query("""
    SELECT Product, Country, Time, Value
    FROM Monthly_Electricity_Statistics
    WHERE Balance = 'Net Electricity Production'
""", conn)
df['Time'] = pd.to_datetime(df['Time'], format='%B %Y')
df['Year'] = df['Time'].dt.year
df['Month'] = df['Time'].dt.month
df['Mes'] = df['Time'].dt.strftime('%b')

df_pais = df[df['Country'] == pais]
df_filtrado = df_pais[df_pais['Year'] == anio]
df_grouped = df_filtrado.groupby('Product')['Value'].sum().reset_index(name='Total_GWh')
df_anual = df_pais.groupby('Year')['Value'].sum().reset_index(name='Total_Generation_GWh')
df_mensual = df_filtrado.groupby('Month')['Value'].sum().reset_index()
df_mensual['Mes'] = df_mensual['Month'].apply(lambda x: pd.to_datetime(str(x), format='%m').strftime('%b'))

año_actual = datetime.now().year
df_actual = df[df['Year'] == año_actual]
df_renovables = df_actual[df_actual['Product'].isin(['Solar', 'Wind', 'Hydro'])]
df_ren_grouped = df_renovables.groupby('Product')['Value'].sum().reset_index(name='Generation_GWh')

st.header(f"Análisis de {pais} - {anio}")

tabs = st.tabs(["🥧 Distribución por fuente", "📈 Generación mensual", "📉 Histórico anual", "🌱 Renovables actuales"])

with tabs[0]:
    st.subheader("Distribución por fuente")
    if df_grouped.empty:
        st.warning("No hay datos para esta combinación.")
    else:
        fig, ax = plt.subplots()
        ax.pie(df_grouped['Total_GWh'], labels=df_grouped['Product'], autopct='%1.1f%%', startangle=140)
        ax.axis('equal')
        st.pyplot(fig)

with tabs[1]:
    st.subheader("Generación mensual")
    if df_mensual.empty:
        st.warning("No hay datos mensuales.")
    else:
        fig, ax = plt.subplots()
        ax.plot(df_mensual['Mes'], df_mensual['Value'], marker='o', color='green')
        ax.grid(True)
        st.pyplot(fig)

with tabs[2]:
    st.subheader("Histórico anual")
    if df_anual.empty:
        st.warning("No hay datos históricos.")
    else:
        fig, ax = plt.subplots()
        ax.plot(df_anual['Year'], df_anual['Total_Generation_GWh'], marker='o', color='blue')
        ax.grid(True)
        st.pyplot(fig)

with tabs[3]:
    st.subheader(f"Fuentes renovables ({año_actual})")
    if df_ren_grouped.empty:
        st.warning("No hay datos de renovables en el año actual.")
    else:
        fig, ax = plt.subplots()
        ax.bar(df_ren_grouped['Product'], df_ren_grouped['Generation_GWh'], color='teal')
        st.pyplot(fig)

conn.close()
