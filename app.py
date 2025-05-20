import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="Dashboard Energético", layout="wide")
st.title("Dashboard Energético Interactivo")

@st.cache_data
def cargar_datos():
    conn = sqlite3.connect("analisis_energetico.db")
    query = """
    SELECT * 
    FROM 'Monthly_Electricity_Statistics'
    WHERE Country NOT LIKE '%OECD%' 
    AND Country NOT LIKE '%Total%'
    ORDER BY Country ASC
    """
    df = pd.read_sql(query, conn)
    conn.close()

    # ✅ Corregida la extracción del año
    df['Year'] = df['Time'].str.extract(r'(\d{4})')
    df['Year'] = pd.to_numeric(df['Year'], errors='coerce').astype('Int64')
    return df

df = cargar_datos()

# -------------------
# ✅ Sidebar global con validaciones
# -------------------
with st.sidebar:
    st.title("🔌 Dashboard Energético")

    # País
    paises = ['Todos'] + sorted(df['Country'].dropna().unique())
    pais = st.selectbox("🌍 Selecciona un país", paises)

    # Años con protección ante lista vacía
    anios = sorted(df['Year'].dropna().unique())
    if anios:
        anio = st.selectbox("📅 Selecciona un año", anios, index=len(anios) - 1)
    else:
        st.warning("⚠️ No hay años disponibles en los datos.")
        st.stop()

    # Secciones del dashboard
    seccion = st.radio("📁 Secciones del Dashboard", [
        "Diagnóstico Nacional",
        "Comparativos Internacionales",
        "Tendencia Mensual"
    ])

# -------------------
# 🔄 Filtro general aplicado a los datos
# -------------------
df_filtrado = df[df['Year'] == anio]
if pais != "Todos":
    df_filtrado = df_filtrado[df_filtrado['Country'] == pais]

# -------------------
# 🧩 Función utilitaria para mostrar gráficos en 2 columnas
# -------------------
def mostrar_graficos(graficos):
    cols = st.columns(2)
    for i, fig in enumerate(graficos):
        with cols[i % 2]:
            st.plotly_chart(fig, use_container_width=True)

# --------------------------
# Diagnóstico Nacional
# --------------------------
if seccion == "Diagnóstico Nacional":
    st.subheader(f"Diagnóstico Energético - {pais} ({anio})")

    graficos = []

    # Gráfico 1: Participación Porcentual Renovables vs No Renovables
    productos_a_excluir = [
        'Electricity', 'Total Combustible Fuels',
        'Total Renewables (Hydro, Geo, Solar, Wind, Other)',
        'Not Specified', 'Data is estimated for this month'
    ]

    productos_renovables = [
        'Hydro', 'Wind', 'Geothermal', 'Combustible Renewables', 'Solar', 'Other Renewables'
    ]

    df_energy_filtered = df.copy()
    df_energy_filtered = df_energy_filtered[~df_energy_filtered['Product'].isin(productos_a_excluir)].copy()
    df_energy_filtered['Energy_Type'] = df_energy_filtered['Product'].apply(
        lambda x: 'Renewable' if x in productos_renovables else 'Non-Renewable'
    )
    if pais != "Todos":
        df_energy_filtered = df_energy_filtered[df_energy_filtered['Country'] == pais]
    df_total_by_year = df_energy_filtered.groupby('Year')['Value'].sum().reset_index(name='Total_Year_Value')
    df_agg = df_energy_filtered.groupby(['Year', 'Energy_Type'])['Value'].sum().reset_index()
    df_agg = df_agg.merge(df_total_by_year, on='Year')
    df_agg['Percentage'] = df_agg['Value'] / df_agg['Total_Year_Value'] * 100
    df_percent_pivot = df_agg.pivot(index='Year', columns='Energy_Type', values='Percentage').fillna(0)
    if 'Renewable' in df_percent_pivot.columns and 'Non-Renewable' in df_percent_pivot.columns:
        df_percent_pivot = df_percent_pivot[['Renewable', 'Non-Renewable']]
    fig1 = px.bar(
        df_percent_pivot,
        x=df_percent_pivot.index,
        y=['Renewable', 'Non-Renewable'],
        title=f"% Participación de Energía Renovable vs No Renovable - {pais if pais != 'Todos' else 'Global'}",
        labels={"value": "Porcentaje (%)", "Year": "Año", "variable": "Tipo de Energía"},
        barmode='stack',
        color_discrete_map={"Renewable": "#2ca02c", "Non-Renewable": "#d62728"}
    )
    fig1.update_layout(yaxis_range=[0, 100], xaxis_title="Año", yaxis_title="Porcentaje (%)", legend_title="Tipo de Energía")
    graficos.append(fig1)
    
    # Gráfico 2: Producción por Fuente
    graficos.append(px.bar(df_filtrado, x="Product", y="Value", title="Producción por Fuente"))

    # Gráfico 3: Distribución por Producto (Torta)
    graficos.append(px.pie(df_filtrado, names="Product", values="Value", title="Distribución de Producción"))

    # Gráfico 4: Balance energético
    graficos.append(px.histogram(df_filtrado, x="Balance", y="Value", title="Balance Energético"))

    # Gráfico 5: Distribución por Producto (Pie)
    fig_pie = px.pie(
    df_filtrado,
    names="Product",
    values="Value",
    title="Distribución por Producto"
)
    graficos.append(fig_pie)

    # Gráfico 6: Tendencia Histórica
    tendencia_df = df[df['Country'] == pais] if pais != 'Todos' else df
    graficos.append(px.line(tendencia_df, x="Year", y="Value", title="Tendencia Histórica"))

    # Mostrar todos los gráficos
    mostrar_graficos(graficos)

# -------------------------------
# SECCIÓN: COMPARATIVOS INTERNACIONALES
# -------------------------------
elif seccion == "Comparativos Internacionales":
    st.subheader(f"Comparativos Internacionales - {anio}")
    graficos = []

    df_anio = df[df['Year'] == anio]
    top_paises = df_anio.groupby('Country')['Value'].sum().nlargest(10).reset_index()

    # Gráfico 1 - Treemap con valores
    fig_treemap = px.treemap(
        top_paises,
        path=['Country'],
        values='Value',
        title="Top 10 Países por Producción (Treemap)"
    )
    fig_treemap.update_traces(textinfo='label+value')
    graficos.append(fig_treemap)

    # Gráfico 2
    
    # Agrupar y ordenar
    df_grouped = df_anio.groupby("Country")["Value"].sum().reset_index()
    df_grouped = df_grouped.sort_values(by="Value", ascending=False).head(10)
    
    
    # Graficar con etiquetas visibles
    fig_bar = px.bar(
    df_grouped,
    x="Country",
    y="Value",
    title="Top 10 Países por Producción (Ordenado)",
    labels={"Value": "Producción", "Country": "País"},
    text_auto=True  # ✅ Mostrar valores en las barras
)
    graficos.append(fig_bar)

    # Gráfico 3 - Subgráficos comparativos
    fuentes_renovables = [
        'Wind', 'Solar', 'Other Renewables', 'Hydro', 'Geothermal', 'Combustible Renewables'
    ]
    fuentes_no_renovables = [
        'Coal, Peat and Manufactured Gases', 'Oil and Petroleum Products', 'Natural Gas',
        'Other Combustible Non-Renewables', 'Nuclear'
    ]
    df_net = df[df['Balance'] == 'Net Electricity Production'].copy()
    df_net_anio = df_net[df_net['Year'] == anio]
    df_ren = df_net_anio[df_net_anio['Product'].isin(fuentes_renovables)]
    df_no_ren = df_net_anio[df_net_anio['Product'].isin(fuentes_no_renovables)]
    df_ren_pivot = df_ren.groupby(['Year', 'Product'])['Value'].sum().reset_index().pivot(index='Year', columns='Product', values='Value').fillna(0)
    df_no_ren_pivot = df_no_ren.groupby(['Year', 'Product'])['Value'].sum().reset_index().pivot(index='Year', columns='Product', values='Value').fillna(0)
    fig_sub = make_subplots(rows=1, cols=2, subplot_titles=("Energías Renovables", "Energías No Renovables"))
    for col in df_ren_pivot.columns:
        fig_sub.add_trace(go.Bar(name=col, x=df_ren_pivot.index, y=df_ren_pivot[col]), row=1, col=1)
    for col in df_no_ren_pivot.columns:
        fig_sub.add_trace(go.Bar(name=col, x=df_no_ren_pivot.index, y=df_no_ren_pivot[col]), row=1, col=2)
    fig_sub.update_layout(barmode='stack', height=500, title_text=f"Comparativo Energético por Año - {pais}")
    graficos.append(fig_sub)

    # Gráfico 4
    graficos.append(px.line(df[df['Country'].isin(top_paises['Country'])], x="Year", y="Value", color="Country", title="Evolución por País"))

    # Gráfico 5
    graficos.append(px.bar(df_anio.groupby("Product")["Value"].sum().reset_index(), x="Product", y="Value", title="Producción Global por Fuente"))

    # Gráfico 6
    graficos.append(px.treemap(df_anio, path=["Country", "Product"], values="Value", title="Mapa Jerárquico Internacional"))

    mostrar_graficos(graficos)
    
elif seccion == "Tendencia Mensual":
# -------------------
# ✅ Función de Clasificación y Filtro
# -------------------
    def clasificar_y_filtrar_productos(df, pais=None, tipo_energia='ambas'):
        productos_excluir = [
            'Electricity',
            'Total Combustible Fuels',
            'Total Renewables (Hydro, Geo, Solar, Wind, Other)',
            'Not Specified',
            'Data is estimated for this month'
        ]

        productos_renovables = [
            'Hydro', 'Wind', 'Geothermal',
            'Combustible Renewables', 'Solar', 'Other Renewables'
        ]

        df_filtrado = df[~df['Product'].isin(productos_excluir)].copy()
        df_filtrado['Energy_Type'] = df_filtrado['Product'].apply(
            lambda x: 'Renewable' if x in productos_renovables else 'Non-Renewable'
        )

        if pais and pais != 'Todos':
            df_filtrado = df_filtrado[df_filtrado['Country'] == pais]

        if tipo_energia == 'renovables':
            df_filtrado = df_filtrado[df_filtrado['Energy_Type'] == 'Renewable']
        elif tipo_energia == 'no_renovables':
            df_filtrado = df_filtrado[df_filtrado['Energy_Type'] == 'Non-Renewable']

        return df_filtrado

    # -------------------
    # ✅ Cargar y preparar los datos
    # -------------------
    conn = sqlite3.connect("analisis_energetico.db")
    query = """
    SELECT Product, Country, Time, Value, Balance
    FROM Monthly_Electricity_Statistics
    WHERE Balance = 'Net Electricity Production'
    """
    df_energy = pd.read_sql_query(query, conn)
    conn.close()

    df_energy['Time'] = pd.to_datetime(df_energy['Time'], format='%B %Y')
    df_energy['YearMonth'] = df_energy['Time'].dt.strftime('%Y-%m')



    # -------------------
    # ✅ Sección: Tendencia Mensual
    # -------------------
    if st.sidebar.radio("Secciones", ["Tendencia Mensual", "Otro módulo"] if "Tendencia Mensual" not in st.session_state else ["Otro módulo", "Tendencia Mensual"]) == "Tendencia Mensual":
        st.subheader("Tendencia y Generación Mensual por Tipo de Energía")

        tipos_energia = {
            'Renovables y No Renovables': 'ambas',
            'Solo Renovables': 'renovables',
            'Solo No Renovables': 'no_renovables'
        }
        tipo_energia = st.selectbox("Tipo de Energía", list(tipos_energia.keys()))
        modo = tipos_energia[tipo_energia]

        df_filtrado = clasificar_y_filtrar_productos(df_energy, pais=pais, tipo_energia=modo)
        df_monthly = df_filtrado.groupby(['YearMonth', 'Energy_Type'])['Value'].sum().reset_index()

        if df_monthly.empty:
            st.warning(f"No hay datos disponibles para {pais} y tipo {tipo_energia}")
        else:
            df_pivot = df_monthly.pivot(index='YearMonth', columns='Energy_Type', values='Value').fillna(0)
            if 'Renewable' in df_pivot.columns and 'Non-Renewable' in df_pivot.columns:
                df_pivot = df_pivot[['Renewable', 'Non-Renewable']]
            df_pivot = df_pivot.reset_index()

            # 🟢 Gráfico 1: Tendencia en Líneas
            fig_line = px.line(
                df_pivot,
                x='YearMonth',
                y=df_pivot.columns[1:],
                title=f"Tendencia mensual de energía - {pais}",
                labels={"value": "GWh", "YearMonth": "Mes-Año", "variable": "Tipo de Energía"},
                markers=True,
                color_discrete_map={"Renewable": "#2ca02c", "Non-Renewable": "#d62728"}
            )
            fig_line.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig_line, use_container_width=True)

            # 🟢 Gráfico 2: Barras Apiladas
            fig_bar = px.bar(
                df_pivot,
                x='YearMonth',
                y=df_pivot.columns[1:],
                title=f"Generación mensual de energía - {pais}",
                labels={"value": "GWh", "YearMonth": "Mes-Año", "variable": "Tipo de Energía"},
                barmode="stack",
                color_discrete_map={"Renewable": "#2ca02c", "Non-Renewable": "#d62728"}
            )
            fig_bar.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig_bar, use_container_width=True)