import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt

st.set_page_config(page_title="Dashboard Energético", layout="wide")
st.title("Análisis Energético de Colombia y el Mundo")

# Conectar y cargar datos
db_path = "analisis_energetico.db"
conn = sqlite3.connect(db_path)
query = "SELECT Country, Product, Value, Time FROM Monthly_Electricity_Statistics WHERE Country NOT LIKE '%OECD%' AND Country NOT LIKE '%Total%'"
df = pd.read_sql_query(query, conn)
conn.close()

df['Year'] = df['Time'].str.extract(r'(\d{4})').astype(int)

productos_excluir = ['Electricity', 'Total Combustible Fuels', 'Total Renewables (Hydro, Geo, Solar, Wind, Other)', 'Not Specified', 'Data is estimated for this month']
productos_renovables = ['Hydro', 'Wind', 'Geothermal', 'Combustible Renewables', 'Solar', 'Other Renewables']

df = df[~df['Product'].isin(productos_excluir)].copy()
df['Energy_Type'] = df['Product'].apply(lambda x: 'Renewable' if x in productos_renovables else 'Non-Renewable')

main_menu = st.sidebar.radio("Selecciona una categoría", [
    "Diagnóstico Energético de Colombia",
    "Análisis Sectorial",
    "Comparativos Internacionales",
    "Análisis Climático"
])

def plot_energy_trend(df):
    df_monthly = df.groupby('Year')['Value'].sum()
    st.bar_chart(df_monthly)

def plot_energy_comparison(df):
    df_comparison = df.groupby(['Year', 'Product'])['Value'].sum().unstack().fillna(0)
    st.line_chart(df_comparison)

def plot_renewable_percentage(df, year):
    df_year = df[df['Year'] == year]
    df_grouped = df_year.groupby(['Country', 'Energy_Type'])['Value'].sum().reset_index()
    df_total = df_grouped.groupby('Country')['Value'].sum().reset_index(name='Total_Value')
    df_grouped = df_grouped.merge(df_total, on='Country')
    df_grouped['Percentage'] = df_grouped['Value'] / df_grouped['Total_Value'] * 100
    df_pivot = df_grouped.pivot(index='Country', columns='Energy_Type', values='Percentage').fillna(0)
    fig, ax = plt.subplots()
    df_pivot.plot(kind='bar', stacked=True, ax=ax)
    st.pyplot(fig)

if main_menu == "Diagnóstico Energético de Colombia":
    sub_menu = st.sidebar.radio("Seleccione un análisis", [
        "Tendencia Mensual de Energía en Colombia (2014-2025)",
        "Comparativo de Fuentes de Energía por Año en Colombia (2014-2025)",
        "Participación de Fuentes de Energía en Colombia (2024)",
        "Evolución Histórica de la Diversificación Energética en Colombia (2014-2025)"
    ])
    st.header(sub_menu)
    if sub_menu == "Tendencia Mensual de Energía en Colombia (2014-2025)":
        plot_energy_trend(df)
    elif sub_menu == "Comparativo de Fuentes de Energía por Año en Colombia (2014-2025)":
        plot_energy_comparison(df)
    elif sub_menu == "Participación de Fuentes de Energía en Colombia (2024)":
        plot_renewable_percentage(df, 2024)

elif main_menu == "Análisis Sectorial":
    st.subheader("Ejemplo pendiente por desarrollar en futuras versiones.")

elif main_menu == "Comparativos Internacionales":
    st.subheader("Ejemplo pendiente por desarrollar en futuras versiones.")

elif main_menu == "Análisis Climático":
    st.subheader("Ejemplo pendiente por desarrollar en futuras versiones.")