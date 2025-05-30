import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns
import urllib
import plotly.express as px
import streamlit as st
import folium
from folium.features import GeoJsonTooltip
from streamlit_folium import st_folium
from babel.numbers import format_currency
from pathlib import Path
import plotly.graph_objects as go
from pandas.api.types import CategoricalDtype
import locale

st.set_page_config(page_title='Global Carbon Emissions Analysis', layout='wide')

#load data

#digunakan untuk menampung dataset emisi dan negara
path_data = Path(os.getcwd()).joinpath("all_data_imputed.csv")
if path_data.exists():
    alldata_df = pd.read_csv(str(path_data))
    #ambil data ke dataframe
    # Filter data untuk tahun 2023
    year_selected=2022
    # Negara yang ingin dikecualikan dari visualisasi
    excluded_countries = [
        'World', 'Asia', 'Upper-middle-income countries', 'High-income countries',
        'European Union (28)', 'European Union (27)', 'Europe (excl. EU-27)', 'Europe (excl. EU-28)',
        'North America', 'South America', 'North America (excl. USA)', 'Africa', 'Asia (excl. China and India)', 'Europe',
        'Low-income countries', 'Lower-middle-income countries'
    ]

    
    
else:
    st.error("File all_data_imputed.csv tidak ditemukan. Please ensure the file is in the correct directory.")
    st.error(path_data)
    st.stop()

path_country = Path(os.getcwd()).joinpath("list_country2.csv")
if path_country.exists():
    country_df = pd.read_csv(str(path_country), sep=';')
    #country_df.sort_values(by="country", inplace=True)
    country_df.reset_index(inplace=True)
else:
    st.error("File list_country.csv tidak ditemukan. Please ensure the file is in the correct directory.")
    st.error(path_country)
    st.stop()


alldata_df_filtered = alldata_df[alldata_df['country'].isin(country_df['Country'])]
df_filtered = alldata_df_filtered[alldata_df_filtered['year']==year_selected]
top_10_countries = df_filtered.sort_values('total_ghg', ascending=False).head(10)
top_10_countries_emissions = alldata_df_filtered.sort_values('total_ghg', ascending=False)

st.header("Global Carbon Emission Analysis")
tab1, tab2, tab3 = st.tabs(["Dashboard Utama", "Profil Negara", "Prediksi Emisi 2024-2030"])
with tab1:
    # SECTION 1: STATISTIK RINGKAS
    st.markdown("<h3 style='color: yellow;'>Statistik Emisi Global Tahun Ini</h3>", unsafe_allow_html=True)



    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Emisi (Mt CO2e)", f"{df_filtered['total_ghg'].sum():,.0f}")
    with col2:
        st.metric("Total Populasi", f"{df_filtered['population'].sum():,.0f}")
    with col3:
        st.metric("Total GDP", f"{df_filtered['gdp'].sum():,.0f}")

    #Peta Dasar Emisi Global
    m = folium.Map(location=[20,0], 
                dragging=False,
                scrollWheelZoom=False,
                doubleClickZoom=False,
                touchZoom=False,
                zoom_start=2)

    # Ambil data GeoJSON
    geojson_url = "https://raw.githubusercontent.com/python-visualization/folium/master/examples/data/world-countries.json"

    value_selected="total_ghg"
    legend_selected = "Total Emisi (MtCO2e)"
   
    # Membuat choropleth
    choropleth = folium.Choropleth(
        geo_data=geojson_url, 
        name="choropleth",
        data=df_filtered,
        columns=["country", value_selected],
        key_on="feature.properties.name",
        fill_color="YlOrRd",
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name=legend_selected,
        highlight=True,  # Ini penting untuk hover
    ).add_to(m)

    # Menambahkan tooltip (on hover)
    folium.GeoJson(
        geojson_url,
        style_function=lambda feature: {
            'fillColor': 'transparent',
            'color': 'transparent',
            'weight': 0,
        },
        tooltip=GeoJsonTooltip(
            fields=["name"],
            aliases=["Negara:"],
            labels=True,
            sticky=False
        ),
    ).add_to(m)

    # Gabungkan tooltip dengan data emisi
    for idx, row in df_filtered.iterrows():
        country_name = row['country']
        total_ghg = row['total_ghg']
        
        # Untuk setiap negara, cari fitur GeoJSON yang sesuai
        folium.Marker(
            location=[0, 0],  # Dummy, karena tooltip nempel ke choropleth
            popup=f"{country_name}: {total_ghg} ton CO2e"
        )



    # Full width
    st_folium(m, width="80%", height=500)


    # --------------- BUAT STACKED AREA CHART ---------------
    st.markdown("<h3 style='color: yellow;'>Timeseries Jumlah Emisi Top 10 Negara</h3>", unsafe_allow_html=True)
    # Hitung total emisi GHG per negara sepanjang waktu
    total_emission_by_country = (
        alldata_df_filtered.groupby('country')['total_ghg']
        .sum()
        .sort_values(ascending=False)
    )

    top10_countries = total_emission_by_country.head(10).index.tolist()

    # Filter hanya 10 negara tersebut
    df_top10 = alldata_df_filtered[alldata_df_filtered['country'].isin(top10_countries)]

    #untuk mengurutkan legend berdasarkan negara emisi tertinggi
    country_order = CategoricalDtype(categories=top10_countries, ordered=True)
    df_top10['country'] = df_top10['country'].astype(country_order)


    fig = px.line(
        df_top10,
        x='year',
        y='total_ghg',
        color='country',
        markers=True,
        labels={
            'year': 'Tahun',
            'total_ghg': 'Total Emisi GHG (Mt CO2e)',
            'country': 'Negara'
        },
        color_discrete_sequence=px.colors.qualitative.Vivid,
        category_orders={"country": top10_countries}
    )

    fig.update_layout(
        height=600,
        xaxis=dict(tickmode='linear'),
        yaxis_title="Total Emisi (Mt CO2e)",
        legend_title="Negara",
        hovermode="x unified"
    )

    st.plotly_chart(fig, use_container_width=True)



    g2,g3 = st.columns(2)
    with g2:
        st.markdown("<h3 style='color: yellow;'>Top 10 Negara Total Penyumbang Emisi</h3>", unsafe_allow_html=True)
        top10 = df_filtered.sort_values("total_ghg", ascending=False).head(10)
        fig_bar = px.bar(top10, x="total_ghg", y="country", orientation='h', color='total_ghg', color_continuous_scale='Reds')
        fig_bar.update_layout(yaxis={'categoryorder':'total ascending'}, height=500)
        st.plotly_chart(fig_bar, use_container_width=True)


    with g3:
        st.markdown("<h3 style='color: yellow;'>Emisi Gas Rumah Kaca Per Kapita</h3>", unsafe_allow_html=True)
        fig_capita = px.scatter(
            df_filtered,
            x='population',
            y='total_ghg',
            size='gdp',
            color='country',
            hover_name='country',
            labels={'country':'Negara','population':'Populasi', 'total_ghg':'Total GHG (Mt CO2e)'}
        )
        fig_capita.update_layout(height=600)
        st.plotly_chart(fig_capita, use_container_width=True)


    g4,g5 = st.columns(2)
    with g4:
        st.markdown("<h3 style='color: yellow;'>Tren Jumlah Emisi Global Tahunan</h3>", unsafe_allow_html=True)
        global_trend = alldata_df_filtered.groupby('year').sum(numeric_only=True).reset_index()
        fig_trend = px.line(global_trend, x='year', y='total_ghg', labels={'total_ghg':'Total GHG (Mt CO2e)', 'year':'Tahun'})
        fig_trend.update_layout(height=500)
        st.plotly_chart(fig_trend, use_container_width=True)
    with g5:      
        # --------------- BUAT STACKED AREA CHART ---------------
        st.markdown("<h3 style='color: yellow;'>Tren Emisi Berdasarkan Jenis Gas</h3>", unsafe_allow_html=True)

        #mengambil data dari semua negara yang telah difilter
        df_trend = alldata_df_filtered.groupby('year')[['co2', 'methane', 'nitrous_oxide']].sum().reset_index()

        # Ubah ke format long
        df_area = df_trend.melt(id_vars="year", var_name="Gas", value_name="Emisi")

        # --------------- PLOT STACKED AREA CHART ---------------
        fig = px.area(
            df_area,
            x="year",
            y="Emisi",
            color="Gas",
            labels={"Emisi": "Emisi (Mt CO2e)", "year": "Tahun", "Gas": "Jenis Gas"},
            color_discrete_sequence=px.colors.qualitative.Set1,
        )

        fig.update_layout(
            height=500,
            xaxis=dict(tickmode="linear"),
            yaxis_title="Total Emisi (Mt CO2e)",
            legend_title="Jenis Gas",
            hovermode="x unified"
        )

        st.plotly_chart(fig, use_container_width=True)


    g6,g7 = st.columns(2)
    with g6:
        # --------------- SECTION 6: PERUBAHAN SUHU GLOBAL ---------------
        st.markdown("<h3 style='color: yellow;'>Perubahan Suhu Global Akibat Emisi Gas Rumah Kaca</h3>", unsafe_allow_html=True)

        # --------------- AGGREGASI DATA GLOBAL PER TAHUN ---------------
        # Kelompokkan berdasarkan tahun, lalu ambil total perubahan suhu
        df_temp = alldata_df_filtered.groupby('year')[['temperature_change_from_ghg']].sum().reset_index()

        df_below = df_temp[df_temp['temperature_change_from_ghg'] < 1.5]
        df_above = df_temp[df_temp['temperature_change_from_ghg'] >= 1.5]

        #buat figure kosong terlebih dahulu
        fig_temp = go.Figure()
        
        # Tambahkan garis untuk suhu < 1.5°C
        fig_temp.add_trace(go.Scatter(
            x=df_below['year'],
            y=df_below['temperature_change_from_ghg'],
            mode='lines+markers',
            name='< 1.5°C',
            line=dict(color='green')
        ))

        # Tambahkan garis untuk suhu >= 1.5°C
        fig_temp.add_trace(go.Scatter(
            x=df_above['year'],
            y=df_above['temperature_change_from_ghg'],
            mode='lines+markers',
            name='≥ 1.5°C',
            line=dict(color='red', dash='solid')
        ))

        # Update layout chart
        fig_temp.update_layout(
            height=500,
            xaxis=dict(tickmode="linear"),
            yaxis_title="Perubahan Suhu (°C)",
            xaxis_title="Tahun",
            legend_title=None,
            hovermode="x unified",
        )

        # Tampilkan ke Streamlit
        st.plotly_chart(fig_temp, use_container_width=True)

    with g7:
        st.markdown("<h3 style='color: yellow;'>Analisis Konsumsi Energi terhadap Emisi</h3>", unsafe_allow_html=True)
        #df_energy_emission = df_filtered[['country', 'primary_energy_consumption', 'total_ghg', 'gdp']].dropna()

        # --------------- PLOT SCATTER PLOT ---------------
        fig_efficiency = px.scatter(
            df_filtered,
            x="primary_energy_consumption",
            y="total_ghg",
            size="gdp",                # Ukuran bubble berdasarkan GDP
            color="country",
            hover_name="country",
            labels={
                "primary_energy_consumption": "Konsumsi Energi (TWh)",
                "total_ghg": "Total Emisi GHG (Mt CO2e)",
                "gdp": "GDP (USD)"
            },

        )

        fig_efficiency.update_layout(
            height=600,
            xaxis_title="Konsumsi Energi (TWh)",
            yaxis_title="Total Emisi GHG (Mt CO2e)",
            legend_title="Negara",
            hovermode="closest"
        )

        st.plotly_chart(fig_efficiency, use_container_width=True)

    #Membuat dataframe 
    locale.setlocale(locale.LC_ALL, '')
    st.markdown("<h3 style='color: yellow;'>Daftar Emisi Negara</h3>", unsafe_allow_html=True)
    df_summary = (
        df_filtered.groupby('country')[['population', 'gdp', 'primary_energy_consumption', 'co2', 'methane', 'nitrous_oxide', 'total_ghg']]
        .sum()
        .reset_index()
        .sort_values(by='total_ghg', ascending=False)
    )

    #tambahkan kolom nomor urut
    df_summary.insert(0, 'No', range(1, len(df_summary) + 1))

    #ganti nama kolom
    df_summary.rename(columns={
        'country':'Negara',
        'population':'Populasi',
        'gdp':'GDP (USD)',
        'primary_energy_consumption':'Konsumsi Energi (TWh)',
        'co2':'CO2',
        'methane': 'Metana',
        'nitrous_oxide': 'Nitrous Oxida',
        'total_ghg':'Total Emisi (MtCO2e)'

    }, inplace=True)

    st.dataframe(df_summary.set_index('No').style.format({
            'Populasi': '{:,.0f}',            
            'GDP (USD)': '${:,.0f}',
            'Konsumsi Energi (TWh)': '{:,.0f}',
            'CO2': '{:,.0f}',                  
            'Metana': '{:,.0f}',  
            'Nitrous Oxida': '{:,.0f}',  
            'Total Emisi (MtCO2e)': '{:,.0f}'          
        }), use_container_width=True)

with tab2:
    st.subheader("Profil Negara")
    country_selected="China"
    country_selected = st.selectbox('Country:', country_df["Country"])
    st.write()

with tab3:
    st.write()
    
# --------------- FOOTER ---------------
st.markdown("---")
st.markdown("<center><h6 style='color: white;'>Sumber Data: <a href='https://ourworldindata.org/'>Our World in Data</a> | Dikembangkan oleh Ghifari Munawar (3323305)</h3></center>", unsafe_allow_html=True)
    

