import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

st.set_page_config(page_title="Dashboard Energético Final", layout="wide")
st.title("Dashboard Energético de Colombia y el Mundo")

# Función para cargar datos
def load_data(table_name):
    conn = sqlite3.connect("analisis_energetico.db")
    df = pd.read_sql_query(f"SELECT * FROM '{table_name}'", conn)
    conn.close()
    return df

# Menú Principal
main_menu = st.sidebar.radio("Menú Principal", [
    "📊 Diagnóstico Energético de Colombia",
    "🏭 Análisis Sectorial",
    "🌎 Comparativos Internacionales",
    "🌱 Análisis Climático"
])

# Diagnóstico Energético de Colombia
if main_menu == "📊 Diagnóstico Energético de Colombia":
    df = load_data("International Energy Agency - electricity final consumption by sector in Colombia")
    years = sorted(df['Year'].unique())
    year_selected = st.sidebar.selectbox("Selecciona el año", years, index=len(years)-1)

    sub_menu = st.sidebar.radio("Seleccione un análisis", [
        "Tendencia Mensual de Energía en Colombia (2014-2025)",
        "Comparativo de Fuentes de Energía por Año en Colombia (2014-2025)",
        "Participación de Fuentes de Energía en Colombia (2024)",
        "Evolución Histórica de la Diversificación Energética en Colombia (2014-2025)"
    ])

    df_filtered = df[df['Year'] == year_selected]

    if sub_menu == "Tendencia Mensual de Energía en Colombia (2014-2025)":
        st.line_chart(df.groupby('Year')['Value'].sum())

    elif sub_menu == "Comparativo de Fuentes de Energía por Año en Colombia (2014-2025)":
        df_pivot = df.pivot_table(index='Year', columns='Sector', values='Value', aggfunc='sum').fillna(0)
        st.line_chart(df_pivot)

    elif sub_menu == "Participación de Fuentes de Energía en Colombia (2024)":
        df_2024 = df[df['Year'] == 2024]
        df_grouped = df_2024.groupby('Sector')['Value'].sum().reset_index()
        fig = px.pie(df_grouped, names='Sector', values='Value', title='Participación de Fuentes de Energía en Colombia (2024)')
        st.plotly_chart(fig)

    elif sub_menu == "Evolución Histórica de la Diversificación Energética en Colombia (2014-2025)":
        st.area_chart(df.groupby(['Year', 'Sector'])['Value'].sum().unstack().fillna(0))

# Análisis Sectorial
elif main_menu == "🏭 Análisis Sectorial":
    df = load_data("International Energy Agency - electricity final consumption by sector in Colombia")
    tabs = st.tabs(["Resumen General", "Industrial", "Residencial", "Transporte"])
    with tabs[0]:
        st.bar_chart(df[df['Year'] == 2022].set_index('Sector')['Value'])
    with tabs[1]:
        st.line_chart(df[df['Sector'] == 'Industry'].groupby('Year')['Value'].sum())
    with tabs[2]:
        st.line_chart(df[df['Sector'] == 'Residential'].groupby('Year')['Value'].sum())
    with tabs[3]:
        st.line_chart(df[df['Sector'] == 'Transport'].groupby('Year')['Value'].sum())

# Comparativos Internacionales
elif main_menu == "🌎 Comparativos Internacionales":
    df = load_data("International Energy Agency - electricity final consumption by sector in Colombia")
    year_selected = st.sidebar.selectbox("Selecciona el año", sorted(df['Year'].unique()), index=len(sorted(df['Year'].unique()))-1)

    sub_menu = st.sidebar.radio("Seleccione un análisis", [
        "Comparativo de Participación Renovable en 2024 (Países)",
        "Evolución Global de la Participación Renovable (2010-2025)",
        "Comparativo Energético Global por Año (2010-2025)"
    ])

    if sub_menu == "Comparativo de Participación Renovable en 2024 (Países)":
        df_2024 = df[df['Year'] == 2024]
        st.bar_chart(df_2024.groupby('Sector')['Value'].sum())

    elif sub_menu == "Evolución Global de la Participación Renovable (2010-2025)":
        st.line_chart(df[df['Sector'] == 'Renewable'].groupby('Year')['Value'].sum())

    elif sub_menu == "Comparativo Energético Global por Año (2010-2025)":
        st.line_chart(df.groupby(['Year', 'Sector'])['Value'].sum().unstack().fillna(0))

# Análisis Climático
elif main_menu == "🌱 Análisis Climático":
    df = load_data("International Energy Agency - CO2 emissions by sector in Colombia")
    sub_menu = st.sidebar.radio("Seleccione un análisis", [
        "Evolución de las Emisiones de CO₂ por Sector en Colombia (2000-2021)",
        "Participación Porcentual de las Emisiones de CO₂ por Sector en Colombia (2000-2022)"
    ])

    if sub_menu == "Evolución de las Emisiones de CO₂ por Sector en Colombia (2000-2021)":
        st.line_chart(df.groupby(['Year', 'Sector'])['Value'].sum().unstack().fillna(0))

    elif sub_menu == "Participación Porcentual de las Emisiones de CO₂ por Sector en Colombia (2000-2022)":
        df_total = df.groupby(['Year'])['Value'].sum().reset_index(name='Total')
        df = df.merge(df_total, on='Year')
        df['Percentage'] = df['Value'] / df['Total'] * 100
        df_grouped = df.pivot_table(index='Year', columns='Sector', values='Percentage').fillna(0)
        st.area_chart(df_grouped)