import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

st.set_page_config(page_title="Dashboard Energético", layout="wide")
st.title("Análisis Energético - Colombia y el Mundo")

def load_data(table_name):
    conn = sqlite3.connect("analisis_energetico.db")
    df = pd.read_sql_query(f"SELECT * FROM '{table_name}'", conn)
    conn.close()
    return df

main_menu = st.sidebar.radio("Menú Principal", [
    "Diagnóstico Energético de Colombia",
    "Análisis Sectorial",
    "Comparativos Internacionales",
    "Análisis Climático"
])

def apply_filters(df):
    if 'Country' in df.columns:
        paises = df['Country'].unique().tolist()
    else:
        paises = ["Colombia"]
    years = sorted(df['Year'].unique())
    pais_seleccionado = st.sidebar.selectbox("País", paises)
    anio_seleccionado = st.sidebar.selectbox("Año", years, index=len(years)-1)
    if 'Country' in df.columns:
        return df[(df['Year'] == anio_seleccionado) & (df['Country'] == pais_seleccionado)], pais_seleccionado, anio_seleccionado
    else:
        return df[df['Year'] == anio_seleccionado], pais_seleccionado, anio_seleccionado

if main_menu == "Diagnóstico Energético de Colombia":
    df = load_data("International Energy Agency - electricity final consumption by sector in Colombia")
    df_filtrado, pais, year = apply_filters(df)
    submenu = st.sidebar.radio("Análisis", ["Tendencia Mensual", "Comparativo por Año", "Participación Fuentes 2024", "Evolución Diversificación"])
    if submenu == "Tendencia Mensual":
        st.line_chart(df.groupby('Year')['Value'].sum())
    elif submenu == "Comparativo por Año":
        st.line_chart(df.groupby(['Year', 'Sector'])['Value'].sum().unstack())
    elif submenu == "Participación Fuentes 2024":
        df_2024 = df[df['Year'] == 2024]
        if not df_2024.empty:
            fig = px.pie(df_2024.groupby('Sector')['Value'].sum().reset_index(), names='Sector', values='Value')
            st.plotly_chart(fig)
        else:
            st.warning("No hay datos para 2024.")
    elif submenu == "Evolución Diversificación":
        st.area_chart(df.groupby(['Year', 'Sector'])['Value'].sum().unstack())

elif main_menu == "Análisis Sectorial":
    df = load_data("International Energy Agency - electricity final consumption by sector in Colombia")
    df_filtrado, pais, year = apply_filters(df)
    tabs = st.tabs(["Resumen", "Industrial", "Residencial", "Transporte"])
    with tabs[0]:
        st.bar_chart(df_filtrado.groupby('Sector')['Value'].sum())
    with tabs[1]:
        st.line_chart(df[df['Sector'] == 'Industry'].groupby('Year')['Value'].sum())
    with tabs[2]:
        st.line_chart(df[df['Sector'] == 'Residential'].groupby('Year')['Value'].sum())
    with tabs[3]:
        st.line_chart(df[df['Sector'] == 'Transport'].groupby('Year')['Value'].sum())

elif main_menu == "Comparativos Internacionales":
    df = load_data("International Energy Agency - electricity final consumption by sector in Colombia")
    df_filtrado, pais, year = apply_filters(df)
    if 'Country' in df.columns:
        df_grouped = df_filtrado.groupby(['Country', 'Sector'])['Value'].sum().reset_index()
    else:
        df_grouped = df_filtrado.groupby(['Sector'])['Value'].sum().reset_index()
    st.bar_chart(df_grouped.set_index('Sector')['Value'])

elif main_menu == "Análisis Climático":
    df = load_data("International Energy Agency - CO2 emissions by sector in Colombia")
    df_filtrado, pais, year = apply_filters(df)
    st.bar_chart(df_filtrado.groupby('Sector')['Value'].sum())