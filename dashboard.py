import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

st.set_page_config(page_title="Dashboard Energético", layout="wide")
st.title("Análisis Energético - Colombia y el Mundo")

# Función para cargar datos
def load_data(table_name):
    conn = sqlite3.connect("analisis_energetico.db")
    df = pd.read_sql_query(f"SELECT * FROM '{table_name}'", conn)
    conn.close()
    return df

# Menú principal
main_menu = st.sidebar.radio("Menú Principal", [
    "Diagnóstico Energético de Colombia",
    "Análisis Sectorial",
    "Comparativos Internacionales",
    "Análisis Climático"
])

# Diagnóstico Energético
if main_menu == "Diagnóstico Energético de Colombia":
    df = load_data("International Energy Agency - electricity final consumption by sector in Colombia")
    paises = df['Country'].unique().tolist() if 'Country' in df.columns else ["Colombia"]
    years = sorted(df['Year'].unique())
    pais_seleccionado = st.sidebar.selectbox("País", paises)
    anio_seleccionado = st.sidebar.selectbox("Año", years, index=len(years)-1)
    df_filtrado = df[(df['Year'] == anio_seleccionado) & (df['Country'] == pais_seleccionado) if 'Country' in df.columns else True]

    submenu = st.sidebar.radio("Análisis", [
        "Tendencia Mensual",
        "Comparativo por Año",
        "Participación Fuentes 2024",
        "Evolución Diversificación"
    ])

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

# Análisis Sectorial
elif main_menu == "Análisis Sectorial":
    df = load_data("International Energy Agency - electricity final consumption by sector in Colombia")
    paises = df['Country'].unique().tolist() if 'Country' in df.columns else ["Colombia"]
    years = sorted(df['Year'].unique())
    pais_seleccionado = st.sidebar.selectbox("País", paises)
    anio_seleccionado = st.sidebar.selectbox("Año", years, index=len(years)-1)
    df_filtrado = df[(df['Year'] == anio_seleccionado) & (df['Country'] == pais_seleccionado) if 'Country' in df.columns else True]

    tabs = st.tabs(["Resumen", "Industrial", "Residencial", "Transporte"])
    with tabs[0]:
        st.bar_chart(df_filtrado.groupby('Sector')['Value'].sum())
    with tabs[1]:
        st.line_chart(df[df['Sector'] == 'Industry'].groupby('Year')['Value'].sum())
    with tabs[2]:
        st.line_chart(df[df['Sector'] == 'Residential'].groupby('Year')['Value'].sum())
    with tabs[3]:
        st.line_chart(df[df['Sector'] == 'Transport'].groupby('Year')['Value'].sum())

# Comparativos Internacionales
elif main_menu == "Comparativos Internacionales":
    df = load_data("International Energy Agency - electricity final consumption by sector in Colombia")
    years = sorted(df['Year'].unique())
    anio_seleccionado = st.sidebar.selectbox("Año", years, index=len(years)-1)
    df_year = df[df['Year'] == anio_seleccionado]

    if not df_year.empty:
        df_grouped = df_year.groupby(['Country', 'Sector'])['Value'].sum().reset_index()
        df_total = df_grouped.groupby('Country')['Value'].sum().reset_index(name='Total')
        df_merged = pd.merge(df_grouped, df_total, on='Country')
        df_merged['Percentage'] = df_merged['Value'] / df_merged['Total'] * 100
        df_pivot = df_merged.pivot(index='Country', columns='Sector', values='Percentage').fillna(0)

        st.bar_chart(df_pivot)

# Análisis Climático
elif main_menu == "Análisis Climático":
    df = load_data("International Energy Agency - CO2 emissions by sector in Colombia")
    years = sorted(df['Year'].unique())
    anio_seleccionado = st.sidebar.selectbox("Año", years, index=len(years)-1)
    df_year = df[df['Year'] == anio_seleccionado]

    if not df_year.empty:
        st.bar_chart(df_year.groupby('Sector')['Value'].sum())