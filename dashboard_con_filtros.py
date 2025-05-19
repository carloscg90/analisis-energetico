import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt

st.set_page_config(page_title="Dashboard Energético con Filtros", layout="wide")
st.title("Análisis Energético de Colombia y el Mundo - Con Filtros Interactivos")

# Función para cargar datos desde una tabla específica
def load_data(table_name):
    conn = sqlite3.connect("analisis_energetico.db")
    df = pd.read_sql_query(f"SELECT * FROM '{table_name}'", conn)
    conn.close()
    return df

# Menú principal
main_menu = st.sidebar.radio("Selecciona una categoría", [
    "Análisis Sectorial",
    "Comparativos Internacionales",
    "Análisis Climático"
])

if main_menu == "Análisis Sectorial":
    df_sectorial = load_data("International Energy Agency - electricity final consumption by sector in Colombia")
    paises = ["Colombia"]  # Solo Colombia en esta tabla
    anios = sorted(df_sectorial['Year'].unique())

    pais_seleccionado = st.sidebar.selectbox("Selecciona un país", paises)
    anio_seleccionado = st.sidebar.selectbox("Selecciona el año", anios)

    df_filtrado = df_sectorial[df_sectorial['Year'] == anio_seleccionado]

    st.subheader(f"Consumo por Sector en {pais_seleccionado} - {anio_seleccionado}")
    st.bar_chart(df_filtrado.set_index('Sector')['Value'])

elif main_menu == "Comparativos Internacionales":
    df_comparativo = load_data("International Energy Agency - electricity final consumption by sector in Colombia")
    paises = ["Colombia"]  # Solo Colombia en esta tabla
    anios = sorted(df_comparativo['Year'].unique())

    pais_seleccionado = st.sidebar.selectbox("Selecciona un país", paises)
    anio_seleccionado = st.sidebar.selectbox("Selecciona el año", anios)

    df_filtrado = df_comparativo[df_comparativo['Year'] == anio_seleccionado]

    st.subheader(f"Comparativo Energético en {pais_seleccionado} - {anio_seleccionado}")
    st.bar_chart(df_filtrado.set_index('Sector')['Value'])

elif main_menu == "Análisis Climático":
    df_climatico = load_data("International Energy Agency - CO2 emissions by sector in Colombia")
    paises = ["Colombia"]  # Solo Colombia en esta tabla
    anios = sorted(df_climatico['Year'].unique())

    pais_seleccionado = st.sidebar.selectbox("Selecciona un país", paises)
    anio_seleccionado = st.sidebar.selectbox("Selecciona el año", anios)

    df_filtrado = df_climatico[df_climatico['Year'] == anio_seleccionado]

    st.subheader(f"Emisiones de CO2 por Sector en {pais_seleccionado} - {anio_seleccionado}")
    st.bar_chart(df_filtrado.set_index('Sector')['Value'])