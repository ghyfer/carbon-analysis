import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns
import urllib
import numpy as np
import plotly.express as px
import streamlit as st
import folium
from folium.features import GeoJsonTooltip
from streamlit_folium import st_folium
from babel.numbers import format_currency
from pathlib import Path
import plotly.graph_objects as go
from pandas.api.types import CategoricalDtype
import matplotlib.colors as mcolors
import locale
import requests
import json


#fungsi
def plot_spider_chart(features, values, color_index=0, title=""):
    features = features.tolist()
    values = values.tolist()

    num_vars = len(features)
    angles = [n / float(num_vars) * 2 * np.pi for n in range(num_vars)]
    angles += angles[:1]
    values += values[:1]

    # Setup figure dengan tema gelap
    fig, ax = plt.subplots(figsize=(5, 5), subplot_kw=dict(polar=True), facecolor='#0e1117')
    ax.set_facecolor('#0e1117')

    # Set teks dan ticks warna putih
    plt.xticks(angles[:-1], features, color='white', size=8)
    ax.set_rlabel_position(0)
    plt.yticks([0.1, 0.2, 0.3], ["0.1", "0.2", "0.3"], color="white", size=7)
    plt.ylim(0, max(values) * 1.2)

    # Gunakan warna dari palet Set1
    color = set1_colors[color_index % len(set1_colors)]

    # Radar chart
    ax.plot(angles, values, linewidth=2, linestyle='solid', color=color)
    ax.fill(angles, values, color=color, alpha=0.3)

    # Tambahkan judul di sini
    plt.title(title, size=12, color='white', y=1.1)

    return fig

#mulai awal halaman
st.set_page_config(page_title='Global Carbon Emissions Analysis', layout='wide')

#load data awal
year_selected = 2022
#digunakan untuk menampung dataset emisi dan negara
path_data = Path(os.getcwd()).joinpath("all_data_imputed.csv")
if path_data.exists():
    alldata_df = pd.read_csv(str(path_data))
    #ambil data ke dataframe
    # Filter data untuk tahun 2023
     # Membuat daftar tahun dari 1970 hingga 2023
    tahun_list = list(range(1970, 2024))[::-1]

   
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

path_country_sum = Path(os.getcwd()).joinpath("df_joined.csv")
if path_country_sum.exists():
    country_df_sum = pd.read_csv(str(path_country_sum), sep=';')
    country_df_sum.reset_index(inplace=True)
else:
    st.errors=("File df_joined.csv tidak ditemukan. Pastikan file tersedia!")
    st.error(path_country_sum)
    st.stop()


alldata_df_filtered = alldata_df[alldata_df['country'].isin(country_df['Country'])]
top_countries = (
    alldata_df_filtered
    .groupby("country", as_index=False)["total_ghg"]
    .sum()
    .sort_values("total_ghg", ascending=False)
)
top_countries.reset_index(inplace=True)

with st.sidebar:
    st.title("🌍 Global Carbon Emissions Analysis")
    st.sidebar.header("🔎 Filter Data")
    # Menampilkan selectbox
    selected_tab = st.radio("Halaman Analisis", ["Dashboard Utama", "Profil Negara", "Prediksi Emisi"])
    if selected_tab == "Dashboard Utama":
        year_selected = st.selectbox("Pilih Tahun:", tahun_list)
    elif selected_tab == "Profil Negara":
        year_selected = st.selectbox("Pilih Tahun:", tahun_list)
        country_selected="China"
        country_selected = st.selectbox('Pilih Negara:', top_countries["country"].tolist())
        bandingkan = st.toggle("Bandingkan Profil Negara")
        if bandingkan: 
            list_country = top_countries[top_countries['country'] != country_selected]
            country_comparison = st.selectbox('Pilih Negara:', list_country["country"].tolist(), key="country_comparison")
    elif selected_tab == "Prediksi Emisi":
        country_selected = st.selectbox('Pilih Negara:', top_countries["country"].tolist())
    # --------------- FOOTER ---------------
    st.markdown("---")
    st.markdown("<center><h5><i style='color: #8DD8FF;'><u>Dikembangkan Oleh:</u></i></h5></center>", unsafe_allow_html=True)
    st.markdown("<center><h5>Ghifari Munawar (3323305)<br/>Data Science dan Teknologi Web</h5></center>", unsafe_allow_html=True)
    st.write()
    st.markdown("<center><h5><i style='color: #8DD8FF;'><u>Sumber Data:</u></i></h5></center>", unsafe_allow_html=True)
    st.markdown("<center><h6>Hannah Ritchie, Pablo Rosado, and Max Roser (2023) - “CO₂ and Greenhouse Gas Emissions” Published online at OurWorldinData.org. Retrieved from: 'https://ourworldindata.org/co2-and-greenhouse-gas-emissions' [Online Resource]</h6></center>", unsafe_allow_html=True)
    


df_filtered = alldata_df_filtered[alldata_df_filtered['year']==year_selected]
top_10_countries = df_filtered.sort_values('total_ghg', ascending=False).head(10)
top_10_countries_emissions = alldata_df_filtered.sort_values('total_ghg', ascending=False)



if selected_tab == "Dashboard Utama":
    st.header("Dashboard Utama")
    # SECTION 1: STATISTIK RINGKAS
    st.markdown(f"<h3 style='color: yellow;'>Statistik Emisi Global Tahun {year_selected}</h3>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Emisi (Mt CO2e)", f"{df_filtered['total_ghg'].sum():,.0f}", border=True)
    with col2:
        st.metric("Total Populasi", f"{df_filtered['population'].sum():,.0f}", border=True)
    with col3:
        st.metric("Total GDP", f"{df_filtered['gdp'].sum():,.0f}", border=True)

    
    # Buat peta dasar
    m = folium.Map(
        location=[20, 0],
        zoom_start=2,
        control_scale=True,
        scrollWheelZoom=False,
        dragging=False,
        doubleClickZoom=False,
        touchZoom=False,
        tiles="cartodb positron"  # Tema yang lebih bersih
    )

    # Data GeoJSON
    geojson_url = "https://raw.githubusercontent.com/python-visualization/folium/master/examples/data/world-countries.json"

    # Load GeoJSON dari URL
    response = requests.get(geojson_url)
    world_geojson = response.json()

    
    value_selected = "total_ghg"
    legend_selected = "Total Emisi (MtCO2e)"
    rename_country = df_filtered.copy()
    rename_country['country'] = rename_country['country'].replace("United States", "United States of America")
    
    # Buat mapping dari negara ke emisi
    ghg_dict = rename_country.set_index('country')['total_ghg'].to_dict()
    pop_dict = rename_country.set_index('country')['population'].to_dict()
    gdp_dict = rename_country.set_index('country')['gdp'].to_dict()
    # Sisipkan total_ghg ke dalam setiap fitur
    for feature in world_geojson['features']:
        country_name = feature['properties']['name']
        feature['properties']['total_ghg'] = ghg_dict.get(country_name, "N/A")
        feature['properties']['population'] = pop_dict.get(country_name, "N/A")
        feature['properties']['gdp'] = gdp_dict.get(country_name, "N/A")
    # Parameter
    
    # Tambahkan Choropleth Layer
    choropleth = folium.Choropleth(
        geo_data=world_geojson,
        name="GHG Choropleth",
        data=rename_country,
        columns=["country", value_selected],
        key_on="feature.properties.name",
        fill_color="YlOrRd",
        fill_opacity=0.8,
        line_opacity=0.2,
        legend_name=legend_selected,
        highlight=True,
    ).add_to(m)

    # Tambahkan tooltip interaktif
    choropleth.geojson.add_child(
        GeoJsonTooltip(
            fields=["name", "total_ghg", "population", "gdp"],
            aliases=["Negara:", "Emisi (MtCO2e):", "Population:", "GDP ($):"],
            localize=True,
            sticky=True,
            labels=True,
            style="""
                background-color: white;
                border: 1px solid black;
                border-radius: 3px;
                box-shadow: 3px;
            """
        )
    )

    # Optimasi tampilan peta di Streamlit (gunakan 100% width agar tidak membuat space kosong)
    st.markdown(
        """
        <style>
        .block-container {
            padding-bottom: 0rem;
        }
        iframe {
            margin-bottom: 0px !important;
        }
        .main {
            padding-bottom: 0px !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    st_data = st_folium(m, width="95%", height=500, returned_objects=[])


    # --------------- BUAT STACKED AREA CHART ---------------
    st.markdown("<h3 style='color: yellow;'>Timeseries Jumlah Emisi Top 10 Negara</h3>", unsafe_allow_html=True)
    
    time_col1, time_col2=st.columns(2)
    with time_col1:
        timeseries_col1, timeseries_col2 = st.columns([4, 1])
        with timeseries_col1:
            year_range_timeseries = st.slider(
                "Pilih rentang tahun",
                min_value=1970,
                max_value=2023,
                value=(1970, year_selected),
                step=1,
                key="slider_timeseries"
            )

    # Filter data berdasarkan rentang tahun
    filtered_timeseries_df = alldata_df_filtered[
            (alldata_df_filtered['year'] >= year_range_timeseries[0]) &
            (alldata_df_filtered['year'] <= year_range_timeseries[1])
        ]
    
    # Hitung total emisi GHG per negara sepanjang waktu
    total_emission_by_country = (
        filtered_timeseries_df.groupby('country')['total_ghg']
        .sum()
        .sort_values(ascending=False)
    )

    top10_countries = total_emission_by_country.head(10).index.tolist()

    # Filter hanya 10 negara tersebut
    df_top10 = filtered_timeseries_df[filtered_timeseries_df['country'].isin(top10_countries)]

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
        col1, col2=st.columns([4,1])
        with col1:
            year_range_emisi_global = st.slider(
                "Pilih rentang tahun",
                min_value=1970,
                max_value=2023,
                value=(1970, year_selected),
                step=1,
                key="slider_emisi_global"
            )
            filtered_emisi_global_df = alldata_df_filtered[
                (alldata_df_filtered['year'] >= year_range_emisi_global[0]) & 
                (alldata_df_filtered['year'] <= year_range_emisi_global[1])
            ]   
        global_trend = filtered_emisi_global_df.groupby('year').sum(numeric_only=True).reset_index()
        fig_trend = px.line(global_trend, x='year', y='total_ghg', labels={'total_ghg':'Total GHG (Mt CO2e)', 'year':'Tahun'})
        fig_trend.update_layout(height=500)
        st.plotly_chart(fig_trend, use_container_width=True)
    with g5:      
        # --------------- BUAT STACKED AREA CHART ---------------
        st.markdown("<h3 style='color: yellow;'>Tren Emisi Berdasarkan Jenis Gas</h3>", unsafe_allow_html=True)
        col1, col2=st.columns([4,1])
        with col1:
            year_range_gas_global = st.slider(
                "Pilih rentang tahun",
                min_value=1970,
                max_value=2023,
                value=(1970, year_selected),
                step=1,
                key="slider_gas_global"
            )
            filtered_emisi_global_df = alldata_df_filtered[
                (alldata_df_filtered['year'] >= year_range_gas_global[0]) & 
                (alldata_df_filtered['year'] <= year_range_gas_global[1])
            ]   
        #mengambil data dari semua negara yang telah difilter
        df_trend = filtered_emisi_global_df.groupby('year')[['co2', 'methane', 'nitrous_oxide']].sum().reset_index()

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
    st.markdown(f"<h3 style='color: yellow;'>Daftar Emisi Negara Tahun {year_selected}</h3>", unsafe_allow_html=True)
    
    df_now = alldata_df_filtered[alldata_df_filtered['year'] == year_selected]
    df_prev = alldata_df_filtered[alldata_df_filtered['year'] == year_selected - 1]

    #hitung total emisi tahun tersebut
    df_now_sum = df_now.groupby('country')[['total_ghg']].sum().reset_index().rename(columns={'total_ghg':'total_now'})
    df_prev_sum = df_prev.groupby('country')[['total_ghg']].sum().reset_index().rename(columns={'total_ghg':'total_prev'})
    df_trend = pd.merge(df_now_sum, df_prev_sum, on='country', how='left')
    def trend_symbol(row):
            if pd.isna(row['total_prev']):
                return "–"
            elif row['total_now'] > row['total_prev']:
                return "🔴"  # naik
            elif row['total_now'] < row['total_prev']:
                return "🟢"  # turun
            else:
                return "🟢"
            
    df_trend['Trend Emisi'] = df_trend.apply(trend_symbol, axis=1)

   
    df_summary = (
        df_filtered[df_filtered['year'] == year_selected]
        .groupby('country')[['population', 'gdp', 'primary_energy_consumption', 'co2', 'methane', 'nitrous_oxide', 'total_ghg']]
        .sum()
        .reset_index()
        .sort_values(by='total_ghg', ascending=False)
    )

    df_summary = pd.merge(df_summary, df_trend[['country', 'Trend Emisi']], on='country', how='left')

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

    # ----------------- Tambah Radio Button Filter -----------------
    filter_option = st.radio(
        "Pilih tren emisi:",
        ("Semua Tren", "Naik", "Turun"),
        index=0,
        horizontal=True
    )

    # ----------------- Terapkan Filter Berdasarkan Pilihan -----------------
    if filter_option == "Naik":
        df_summary = df_summary[df_summary["Trend Emisi"] == "🔴"]
    elif filter_option == "Turun":
        df_summary = df_summary[df_summary["Trend Emisi"] == "🟢"]

    # ----------------- Tampilkan DataFrame -----------------

    st.dataframe(
        df_summary.set_index('No').style.format({
                'Populasi': '{:,.0f}',            
                'GDP (USD)': '${:,.0f}',
                'Konsumsi Energi (TWh)': '{:,.0f}',
                'CO2': '{:,.0f}',                  
                'Metana': '{:,.0f}',  
                'Nitrous Oxida': '{:,.0f}',  
                'Total Emisi (MtCO2e)': '{:,.0f}'          
            }), use_container_width=True

    )

    st.markdown("""
    **Legenda Trend Emisi**

    🔴 = Emisi naik   
    🟢 = Emisi turun / Tidak ada perubahan  
    
    """)

elif selected_tab == "Profil Negara":
   
    all_df_country = alldata_df_filtered[alldata_df_filtered['country'] == country_selected]
    
    df_filtered_country = df_filtered[df_filtered['country'] == country_selected]
    df_filtered_country_year = df_filtered_country[df_filtered_country['year'] == year_selected]
    df_filtered_country_sum = country_df_sum[country_df_sum['country'] == country_selected]
    rank_county = top_countries[top_countries['country'] == country_selected]
    
    
    
    if bandingkan:
        rank_country2 = top_countries[top_countries['country'] == country_comparison]
        if({country_selected} != {country_comparison}):
            st.header(f"Profil Negara {country_selected} (Rank #{rank_county.index[0]+1}) vs {country_comparison} (Rank #{rank_country2.index[0]+1})")
            st.markdown(f"<h3 style='color: yellow;'>Statistik Negara Tahun {year_selected}</h3>", unsafe_allow_html=True)
            df_filtered_country2 = df_filtered[df_filtered['country'] == country_comparison]
            df_filtered_country_year2 = df_filtered_country2[df_filtered_country2['year'] == year_selected]
            df_filtered_country_sum2 = country_df_sum[country_df_sum['country'] == country_comparison]

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(label="Total Emisi (Mt CO2e)", value=f"{df_filtered_country_year['total_ghg'].sum():,.0f}", delta=f"{(df_filtered_country_year['total_ghg'].sum()-df_filtered_country_year2['total_ghg'].sum()):,.0f}", delta_color="inverse", border=True)
            with col2:
                st.metric(label="Total Populasi", value=f"{df_filtered_country_year['population'].sum():,.0f}", delta=f"{(df_filtered_country_year['population'].sum()-df_filtered_country_year2['population'].sum()):,.0f}", delta_color="inverse", border=True)
            with col3:
                st.metric(label="Total GDP", value=f"{df_filtered_country_year['gdp'].sum():,.0f}", delta=f"{df_filtered_country_year['gdp'].sum()-df_filtered_country_year2['gdp'].sum():,.0f}", border=True)
            
            col4, col5, col6 = st.columns(3)
            with col4:
                st.metric(label="Air Quality", value=f"{df_filtered_country_sum['air quality'].sum():,.0f}", delta=f"{(df_filtered_country_sum['air quality'].sum()-df_filtered_country_sum2['air quality'].sum()):,.0f}", border=True)
            with col5:
                st.metric(label="Carbon Emissions", value=f"{df_filtered_country_sum['carbon emissions'].sum():,.0f}", delta=f"{(df_filtered_country_sum['carbon emissions'].sum()-df_filtered_country_sum2['carbon emissions'].sum()):,.0f}", delta_color="inverse", border=True)
            with col6:
                st.metric(label="Informal Economic", value=f"{df_filtered_country_sum['informal economy'].sum():,.0f}", delta=f"{(df_filtered_country_sum['informal economy'].sum()-df_filtered_country_sum2['informal economy'].sum()):,.0f}",  border=True)
            
            
            col10, col11, col12 = st.columns(3)
            with col10:
                st.metric(label="Land Area", value=f"{df_filtered_country_sum['land area'].sum():,.0f}", delta=f"{(df_filtered_country_sum['land area'].sum()-df_filtered_country_sum2['land area'].sum()):,.0f}", border=True)
            with col11:
                st.metric(label="Density", value=f"{df_filtered_country_sum['density'].sum():,.0f}", delta=f"{(df_filtered_country_sum['density'].sum()-df_filtered_country_sum2['density'].sum()):,.0f}", delta_color="inverse", border=True)
            with col12:
                st.metric(label="Water Access", value=f"{df_filtered_country_sum['water access'].sum():,.0f}", delta=f"{(df_filtered_country_sum['water access'].sum()-df_filtered_country_sum2['water access'].sum()):,.0f}", border=True)

            col7, col8, col9 = st.columns(3)
            with col7:
                st.metric(label="Primary Energy Consumption", value=f"{df_filtered_country_sum['primary_energy_consumption'].sum():,.0f}", delta=f"{(df_filtered_country_sum['primary_energy_consumption'].sum()-df_filtered_country_sum2['primary_energy_consumption'].sum()):,.0f}", delta_color="inverse", border=True)
            with col8:
                st.metric(label="Population in Employment (%)", value=f"{df_filtered_country_sum['population in employment'].sum():,.0f}", delta=f"{(df_filtered_country_sum['population in employment'].sum()-df_filtered_country_sum2['population in employment'].sum()):,.0f}", border=True)
            with col9:
                st.metric(label="Life Expectancy", value=f"{df_filtered_country_sum['life expectancy'].sum():,.0f}", delta=f"{(df_filtered_country_sum['life expectancy'].sum()-df_filtered_country_sum2['life expectancy'].sum()):,.0f}", border=True)
        else:
            st.header(f"Profil Negara {country_selected} (Rank #{rank_county.index[0]+1})")
            st.markdown(f"<h3 style='color: yellow;'>Statistik Negara Tahun {year_selected}</h3>", unsafe_allow_html=True)
           
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Emisi (Mt CO2e)", f"{df_filtered_country_year['total_ghg'].sum():,.0f}", border=True)
            with col2:
                st.metric("Total Populasi", f"{df_filtered_country_year['population'].sum():,.0f}", border=True)
            with col3:
                st.metric("Total GDP", f"{df_filtered_country_year['gdp'].sum():,.0f}", border=True)
            
            col4, col5, col6 = st.columns(3)
            with col4:
                st.metric("Air Quality", f"{df_filtered_country_sum['air quality'].sum():,.0f}", border=True)
            with col5:
                st.metric("Carbon Emissions", f"{df_filtered_country_sum['carbon emissions'].sum():,.0f}", border=True)
            with col6:
                st.metric("Informal Economic", f"{df_filtered_country_sum['informal economy'].sum():,.0f}", border=True)
            
            
            col10, col11, col12 = st.columns(3)
            with col10:
                st.metric("Land Area", f"{df_filtered_country_sum['land area'].sum():,.0f}", border=True)
            with col11:
                st.metric("Density", f"{df_filtered_country_sum['density'].sum():,.0f}", border=True)
            with col12:
                st.metric("Water Access", f"{df_filtered_country_sum['water access'].sum():,.0f}", border=True)

            col7, col8, col9 = st.columns(3)
            with col7:
                st.metric("Primary Energy Consumption", f"{df_filtered_country_sum['primary_energy_consumption'].sum():,.0f}", border=True)
            with col8:
                st.metric("Population in Employment (%)", f"{df_filtered_country_sum['population in employment'].sum():,.0f}", border=True)
            with col9:
                st.metric("Life Expectancy", f"{df_filtered_country_sum['life expectancy'].sum():,.0f}", border=True)
    else:
        st.header(f"Profil Negara {country_selected} (Rank #{rank_county.index[0]+1})")
        st.markdown(f"<h3 style='color: yellow;'>Statistik Negara Tahun {year_selected}</h3>", unsafe_allow_html=True)
       
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Emisi (Mt CO2e)", f"{df_filtered_country_year['total_ghg'].sum():,.0f}", border=True)
        with col2:
            st.metric("Total Populasi", f"{df_filtered_country_year['population'].sum():,.0f}", border=True)
        with col3:
            st.metric("Total GDP", f"{df_filtered_country_year['gdp'].sum():,.0f}", border=True)
        
        col4, col5, col6 = st.columns(3)
        with col4:
            st.metric("Air Quality", f"{df_filtered_country_sum['air quality'].sum():,.0f}", border=True)
        with col5:
            st.metric("Carbon Emissions", f"{df_filtered_country_sum['carbon emissions'].sum():,.0f}", border=True)
        with col6:
            st.metric("Informal Economic", f"{df_filtered_country_sum['informal economy'].sum():,.0f}", border=True)
        
        
        col10, col11, col12 = st.columns(3)
        with col10:
            st.metric("Land Area", f"{df_filtered_country_sum['land area'].sum():,.0f}", border=True)
        with col11:
            st.metric("Density", f"{df_filtered_country_sum['density'].sum():,.0f}", border=True)
        with col12:
            st.metric("Water Access", f"{df_filtered_country_sum['water access'].sum():,.0f}", border=True)

        col7, col8, col9 = st.columns(3)
        with col7:
            st.metric("Primary Energy Consumption", f"{df_filtered_country_sum['primary_energy_consumption'].sum():,.0f}", border=True)
        with col8:
            st.metric("Population in Employment (%)", f"{df_filtered_country_sum['population in employment'].sum():,.0f}", border=True)
        with col9:
            st.metric("Life Expectancy", f"{df_filtered_country_sum['life expectancy'].sum():,.0f}", border=True)

    
   

    g2,g3 = st.columns(2)
    with g2:
        st.markdown("<h3 style='color: yellow;'>Tren Jumlah Populasi Tahunan</h3>", unsafe_allow_html=True)
        pop_col1, pop_col2 = st.columns([4,1])
        bandingkan_country = [country_selected]
        if bandingkan and (country_selected!=country_comparison):
            bandingkan_country = [country_selected, country_comparison]
        with pop_col1:
            year_range_pop = st.slider(
                "Pilih rentang tahun",
                min_value=1970,
                max_value=2023,
                value=(1970, year_selected),
                step=1,
                key="slider_pop"
            )
        filtered_pop_df = alldata_df_filtered[
            (alldata_df_filtered['year'] >= year_range_pop[0]) & 
            (alldata_df_filtered['year'] <= year_range_pop[1]) &
            (alldata_df_filtered['country'].isin(bandingkan_country))
        ]
        # Plot grafik populasi per negara
        fig_pop = px.line(
            filtered_pop_df,
            x='year',
            y='population',
            color='country',
            labels={'population': 'Populasi', 'year': 'Tahun', 'country': 'Negara'},
            color_discrete_sequence=px.colors.qualitative.Vivid,
        )

        # Layout: legend di bawah
        fig_pop.update_layout(
            height=500,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.3,
                xanchor="center",
                x=0.5
            )
        )

        st.plotly_chart(fig_pop, use_container_width=True)
   
    with g3:      
        st.markdown("<h3 style='color: yellow;'>Tren Jumlah GDP Tahunan</h3>", unsafe_allow_html=True)
        gdp_col1, gdp_col2 = st.columns([4,1])
        bandingkan_country = [country_selected]
        if bandingkan and (country_selected!=country_comparison):
            bandingkan_country = [country_selected, country_comparison]
        with gdp_col1:
            year_range_gdp = st.slider(
                "Pilih rentang tahun",
                min_value=1970,
                max_value=2023,
                value=(1970, year_selected),
                step=1,
                key="slider_gdp"
            )
        filtered_gdp_df = alldata_df_filtered[
            (alldata_df_filtered['year'] >= year_range_gdp[0]) & 
            (alldata_df_filtered['year'] <= year_range_gdp[1]) &
            (alldata_df_filtered['country'].isin(bandingkan_country))
        ]

        # Plot grafik populasi per negara
        fig_gdp = px.line(
            filtered_gdp_df,
            x='year',
            y='gdp',
            color='country',
            labels={'gdp': 'GDP', 'year': 'Tahun', 'country': 'Negara'},
            color_discrete_sequence=px.colors.qualitative.Vivid,
        )

        # Layout: legend di bawah
        fig_gdp.update_layout(
            height=500,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.3,
                xanchor="center",
                x=0.5
            )
        )

        st.plotly_chart(fig_gdp, use_container_width=True)

    g4,g5 = st.columns(2)
    with g4:
        st.markdown("<h3 style='color: yellow;'>Tren Jumlah Emisi Tahunan</h3>", unsafe_allow_html=True)
        emisi_col1, emisi_col2 = st.columns([4,1])
        bandingkan_country = [country_selected]
        if bandingkan and (country_selected!=country_comparison):
            bandingkan_country = [country_selected, country_comparison]
        with emisi_col1:
            year_range_emisi = st.slider(
                "Pilih rentang tahun",
                min_value=1970,
                max_value=2023,
                value=(1970, year_selected),
                step=1,
                key="slider_emisi"
            )
        filtered_emisi_df = alldata_df_filtered[
            (alldata_df_filtered['year'] >= year_range_emisi[0]) & 
            (alldata_df_filtered['year'] <= year_range_emisi[1]) &
            (alldata_df_filtered['country'].isin(bandingkan_country))
        ]

        # Plot grafik populasi per negara
        fig_emisi = px.line(
            filtered_emisi_df,
            x='year',
            y='total_ghg',
            color='country',
            labels={'total_ghg': 'Total GHG (Mton CO2e)', 'year': 'Tahun', 'country': 'Negara'},
            color_discrete_sequence=px.colors.qualitative.Vivid,
        )

        # Layout: legend di bawah
        fig_emisi.update_layout(
            height=500,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.3,
                xanchor="center",
                x=0.5
            )
        )

        st.plotly_chart(fig_emisi, use_container_width=True)
    with g5:   
        # --------------- SECTION 6: PERUBAHAN SUHU GLOBAL ---------------
        st.markdown("<h3 style='color: yellow;'>Tren Konsumsi Energi Tahunan</h3>", unsafe_allow_html=True)

        energi_col1, energi_col2 = st.columns([4,1])
        bandingkan_country = [country_selected]
        if bandingkan and (country_selected!=country_comparison):
            bandingkan_country = [country_selected, country_comparison]
        with energi_col1:
            year_range_energi = st.slider(
                "Pilih rentang tahun",
                min_value=1970,
                max_value=2023,
                value=(1970, year_selected),
                step=1,
                key="slider_energi"
            )
        filtered_energi_df = alldata_df_filtered[
            (alldata_df_filtered['year'] >= year_range_energi[0]) & 
            (alldata_df_filtered['year'] <= year_range_energi[1]) &
            (alldata_df_filtered['country'].isin(bandingkan_country))
        ]
        
        # Plot grafik populasi per negara
        fig_energi = px.line(
            filtered_energi_df,
            x='year',
            y='primary_energy_consumption',
            color='country',
            labels={'primary_energy_consumption': 'Total Konsumsi Energi (kWh)', 'year': 'Tahun', 'country': 'Negara'},
            color_discrete_sequence=px.colors.qualitative.Vivid,
        )

        # Layout: legend di bawah
        fig_energi.update_layout(
            height=500,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.3,
                xanchor="center",
                x=0.5
            )
        )

        st.plotly_chart(fig_energi, use_container_width=True)

    if bandingkan:
        all_df_country_comparison = alldata_df_filtered[alldata_df_filtered['country'] == country_comparison]
        # --------------- PIE CHART TOTAL EMISI BERDASARKAN JENIS GAS ---------------
        st.markdown(f"<h3 style='color: yellow;'>Proporsi Emisi Berdasarkan Jenis Gas</h3>", unsafe_allow_html=True)
        gas_col_comp1, gas_col_comp2 = st.columns(2)
        with gas_col_comp1:
            gas_col1, gas_col2 = st.columns([4, 1])
            with gas_col1:
                year_range_gas = st.slider(
                    "Pilih rentang tahun",
                    min_value=1970,
                    max_value=2023,
                    value=(1970, year_selected),
                    step=1,
                    key="slider_gas"
                )
        g10, g11 = st.columns(2)
        # Filter data berdasarkan rentang tahun
        filtered_gas_df = all_df_country[
                (all_df_country['year'] >= year_range_gas[0]) &
                (all_df_country['year'] <= year_range_gas[1])
            ]

        filtered_gas_df_comparison = all_df_country_comparison[
                (all_df_country_comparison['year'] >= year_range_gas[0]) &
                (all_df_country_comparison['year'] <= year_range_gas[1])
            ]

        # Hitung total emisi untuk setiap gas
        total_gas_emissions = filtered_gas_df[['co2', 'methane', 'nitrous_oxide']].sum().reset_index()
        total_gas_emissions.columns = ['Jenis Gas', 'Total Emisi']

        total_gas_emissions_comparison = filtered_gas_df_comparison[['co2', 'methane', 'nitrous_oxide']].sum().reset_index()
        total_gas_emissions_comparison.columns = ['Jenis Gas', 'Total Emisi']
        
        with g10:
            
            # Pie chart
            fig = px.pie(
                total_gas_emissions,
                names='Jenis Gas',
                values='Total Emisi',
                color='Jenis Gas',
                color_discrete_sequence=px.colors.qualitative.Set1,
                hole=0.3,  # Opsional: jadikan pie chart seperti donut
                title=country_selected
            )

            # Layout gelap dan ukuran
            fig.update_layout(
                template='plotly_dark',
                height=500,
                legend_title_text='Jenis Gas'
            )
            st.plotly_chart(fig, use_container_width=True)
        with g11:
            # Pie chart
            fig = px.pie(
                total_gas_emissions_comparison,
                names='Jenis Gas',
                values='Total Emisi',
                color='Jenis Gas',
                color_discrete_sequence=px.colors.qualitative.Set1,
                hole=0.3,  # Opsional: jadikan pie chart seperti donut
                title=country_comparison
            )

            # Layout gelap dan ukuran
            fig.update_layout(
                template='plotly_dark',
                height=500,
                legend_title_text='Jenis Gas'
            )
            st.plotly_chart(fig, use_container_width=True, key=f"chart_gas_{country_comparison}")
        
        
        st.markdown("<h3 style='color: yellow;'>Perbandingan Emisi CO₂ vs CO₂-LUC</h3>", unsafe_allow_html=True)
        luc_col_comp1, luc_col_comp2 = st.columns(2)
        with luc_col_comp1:
            luc_col1, luc_col2 = st.columns([4,1])
            with luc_col1:
                # Pilih rentang tahun
                year_range_co2 = st.slider(
                    "Pilih rentang tahun",
                    min_value=int(all_df_country['year'].min()),
                    max_value=int(all_df_country['year'].max()),
                    value=(1970, year_selected),
                    step=1,
                    key="slider_co2"
                )
        g12,g13 = st.columns(2)
        with g12:
            
            # Filter berdasarkan negara & tahun
            df_filtered = all_df_country[
                (all_df_country['country'] == country_selected) &
                (all_df_country['year'] >= year_range_co2[0]) &
                (all_df_country['year'] <= year_range_co2[1])
            ][['year', 'co2', 'co2_including_luc']].copy()

            # Ubah format long untuk plotly express
            df_long = df_filtered.melt(id_vars='year', 
                                    value_vars=['co2', 'co2_including_luc'], 
                                    var_name='Tipe Emisi', 
                                    value_name='Jumlah Emisi')

            # Buat line chart perbandingan
            fig1 = px.line(
                df_long,
                x='year',
                y='Jumlah Emisi',
                color='Tipe Emisi',
                markers=True,
                title=country_selected,
                labels={
                    'year': 'Tahun',
                    'Jumlah Emisi': 'Emisi (Mt CO₂)',
                    'Tipe Emisi': 'Kategori Emisi'
                },
                color_discrete_map={
                    'co2': '#e41a1c',
                    'co2_including_luc': '#377eb8'
                }
            )

            fig1.update_layout(
                template='plotly_dark',
                height=500,
                hovermode='x unified',
                legend=dict(
                    title='Kategori Emisi',
                    orientation="h",
                    yanchor="bottom",
                    y=-0.3,
                    xanchor="center",
                    x=0.5
                )
            )

            st.plotly_chart(fig1, use_container_width=True, key=f"chart_{country_selected}")
        
        with g13:
            # Filter berdasarkan negara & tahun
            df_filtered_comparison = all_df_country_comparison[
                (all_df_country_comparison['year'] >= year_range_co2[0]) &
                (all_df_country_comparison['year'] <= year_range_co2[1])
            ][['year', 'co2', 'co2_including_luc']].copy()

            # Ubah format long untuk plotly express
            df_long_comparison = df_filtered_comparison.melt(id_vars='year', 
                                    value_vars=['co2', 'co2_including_luc'], 
                                    var_name='Tipe Emisi', 
                                    value_name='Jumlah Emisi')

            # Buat line chart perbandingan
            fig2 = px.line(
                df_long_comparison,
                x='year',
                y='Jumlah Emisi',
                color='Tipe Emisi',
                markers=True,
                title=country_comparison,
                labels={
                    'year': 'Tahun',
                    'Jumlah Emisi': 'Emisi (Mt CO₂)',
                    'Tipe Emisi': 'Kategori Emisi'
                },
                color_discrete_map={
                    'co2': '#e41a1c',
                    'co2_including_luc': '#377eb8'
                }
            )

            fig2.update_layout(
                template='plotly_dark',
                height=500,
                hovermode='x unified',
                legend=dict(
                    title='Kategori Emisi',
                    orientation="h",
                    yanchor="bottom",
                    y=-0.3,
                    xanchor="center",
                    x=0.5
                )
            )

            st.plotly_chart(fig2, use_container_width=True, key=f"chart_{country_comparison}")
            
    else:
        g8, g9 = st.columns(2)
        with g8:
            # --------------- PIE CHART TOTAL EMISI BERDASARKAN JENIS GAS ---------------
            st.markdown("<h3 style='color: yellow;'>Proporsi Emisi Berdasarkan Jenis Gas</h3>", unsafe_allow_html=True)

            gas_col1, gas_col2 = st.columns([4, 1])
            with gas_col1:
                year_range_gas = st.slider(
                    "Pilih rentang tahun",
                    min_value=1970,
                    max_value=2023,
                    value=(1970, year_selected),
                    step=1,
                    key="slider_gas"
                )
            # Filter data berdasarkan rentang tahun
            filtered_gas_df = all_df_country[
                (all_df_country['year'] >= year_range_gas[0]) &
                (all_df_country['year'] <= year_range_gas[1])
            ]

            # Hitung total emisi untuk setiap gas
            total_gas_emissions = filtered_gas_df[['co2', 'methane', 'nitrous_oxide']].sum().reset_index()
            total_gas_emissions.columns = ['Jenis Gas', 'Total Emisi']

            # Pie chart
            fig = px.pie(
                total_gas_emissions,
                names='Jenis Gas',
                values='Total Emisi',
                color='Jenis Gas',
                color_discrete_sequence=px.colors.qualitative.Set1,
                hole=0.3  # Opsional: jadikan pie chart seperti donut
            )

            # Layout gelap dan ukuran
            fig.update_layout(
                template='plotly_dark',
                height=500,
                legend_title_text='Jenis Gas'
            )
            st.plotly_chart(fig, use_container_width=True)
        with g9:
            st.markdown("<h3 style='color: yellow;'>Perbandingan Emisi CO₂ vs CO₂-LUC</h3>", unsafe_allow_html=True)
            luc_col1, luc_col2 = st.columns([4,1])
            with luc_col1:
                # Pilih rentang tahun
                year_range_co2 = st.slider(
                    "Pilih rentang tahun",
                    min_value=int(all_df_country['year'].min()),
                    max_value=int(all_df_country['year'].max()),
                    value=(1970, year_selected),
                    step=1,
                    key="slider_co2"
                )

            # Filter berdasarkan negara & tahun
            df_filtered = all_df_country[
                (all_df_country['country'] == country_selected) &
                (all_df_country['year'] >= year_range_co2[0]) &
                (all_df_country['year'] <= year_range_co2[1])
            ][['year', 'co2', 'co2_including_luc']].copy()

            # Ubah format long untuk plotly express
            df_long = df_filtered.melt(id_vars='year', 
                                    value_vars=['co2', 'co2_including_luc'], 
                                    var_name='Tipe Emisi', 
                                    value_name='Jumlah Emisi')

            # Buat line chart perbandingan
            fig = px.line(
                df_long,
                x='year',
                y='Jumlah Emisi',
                color='Tipe Emisi',
                markers=True,
                labels={
                    'year': 'Tahun',
                    'Jumlah Emisi': 'Emisi (Mt CO₂)',
                    'Tipe Emisi': 'Kategori Emisi'
                },
                color_discrete_map={
                    'co2': '#e41a1c',
                    'co2_including_luc': '#377eb8'
                }
            )

            fig.update_layout(
                template='plotly_dark',
                height=500,
                hovermode='x unified',
                legend=dict(title='Kategori Emisi'),
            )

            st.plotly_chart(fig, use_container_width=True)

    if bandingkan:
        st.markdown(f"<h3 style='color: yellow;'>Grafik Top 15 Faktor Penting Negara {country_selected} vs {country_comparison}</h3>", unsafe_allow_html=True)
        from model_utils import train_model_by_country
        df_country_selected = all_df_country[all_df_country['country'] == country_selected]
        importance_df = train_model_by_country(df_country_selected, country_selected)
        importance_df.reset_index(drop=True, inplace=True)
        importance_df.insert(0, 'No', range(1, len(importance_df) + 1))

        df_country_comparison = all_df_country_comparison[all_df_country_comparison['country'] == country_comparison]
        importance_df_comparison = train_model_by_country(df_country_comparison, country_comparison)
        importance_df_comparison.reset_index(drop=True, inplace=True)
        importance_df_comparison.insert(0, 'No', range(1, len(importance_df_comparison) + 1))

        
        set1_colors = [
                '#E41A1C',  # Merah
                '#377EB8',  # Biru
                '#4DAF4A',  # Hijau
                '#984EA3',  # Ungu
                '#FF7F00',  # Oranye
                '#A65628',  # Coklat
                '#F781BF',  # Pink
                '#999999'   # Abu-abu
        ]
        col_radar1, col_radar2 = st.columns(2)

        with col_radar1:
            top_features = importance_df.head(15)
            fig = plot_spider_chart(top_features['Feature'], top_features['Importance'], color_index=1, title=country_selected)  # pilih warna dari Set1
            st.pyplot(fig)
        with col_radar2:
            top_features2 = importance_df_comparison.head(15)
            fig = plot_spider_chart(top_features2['Feature'], top_features2['Importance'], color_index=1, title=country_comparison)  # pilih warna dari Set1
            st.pyplot(fig)

    else:
        g6,g7 = st.columns(2)
        # Jalankan training dan ambil hasil hanya sekali
        from model_utils import train_model_by_country
        df_country_selected = all_df_country[all_df_country['country'] == country_selected]
        importance_df = train_model_by_country(df_country_selected, country_selected)
        importance_df.reset_index(drop=True, inplace=True)
        importance_df.insert(0, 'No', range(1, len(importance_df) + 1))
        # Visualisasi di kolom kiri (bar chart dan tabel)
        with g6:
            st.markdown(f"<h3 style='color: yellow;'>Top 15 Faktor Penting Negara {country_selected}</h3>", unsafe_allow_html=True)
            st.dataframe(
                importance_df.head(15)[['No', 'Feature', 'Importance']], 
                use_container_width=True,
                hide_index=True,
                height=500)  # ✅ langsung DataFrame, tanpa list
            #st.bar_chart(importance_df.set_index("Feature").head(10))

        # Visualisasi di kolom kanan (radar chart)
        with g7:
            

            # Daftar warna Set1 dari Plotly
            set1_colors = [
                '#E41A1C',  # Merah
                '#377EB8',  # Biru
                '#4DAF4A',  # Hijau
                '#984EA3',  # Ungu
                '#FF7F00',  # Oranye
                '#A65628',  # Coklat
                '#F781BF',  # Pink
                '#999999'   # Abu-abu
            ]

            def plot_spider_chart(features, values, color_index=0):
                features = features.tolist()
                values = values.tolist()

                num_vars = len(features)
                angles = [n / float(num_vars) * 2 * np.pi for n in range(num_vars)]
                angles += angles[:1]
                values += values[:1]

                # Setup figure dengan tema gelap
                fig, ax = plt.subplots(figsize=(5, 5), subplot_kw=dict(polar=True), facecolor='#0e1117')
                ax.set_facecolor('#0e1117')

                # Set teks dan ticks warna putih
                plt.xticks(angles[:-1], features, color='white', size=8)
                ax.set_rlabel_position(0)
                plt.yticks([0.1, 0.2, 0.3], ["0.1", "0.2", "0.3"], color="white", size=7)
                plt.ylim(0, max(values) * 1.2)

                # Gunakan warna dari palet Set1
                color = set1_colors[color_index % len(set1_colors)]

                # Radar chart
                ax.plot(angles, values, linewidth=2, linestyle='solid', color=color)
                ax.fill(angles, values, color=color, alpha=0.3)

                return fig

            st.markdown(f"<h3 style='color: yellow;'>Grafik Top 15 Faktor Penting Negara {country_selected}</h3>", unsafe_allow_html=True)
            top_features = importance_df.head(15)
            fig = plot_spider_chart(top_features['Feature'], top_features['Importance'], color_index=1)  # pilih warna dari Set1
            st.pyplot(fig)
    
    if bandingkan:
        st.markdown(f"<h3 style='color: yellow;'>Diagram Irisan Faktor Penting Negara {country_selected} vs {country_comparison}</h3>", unsafe_allow_html=True)
        from model_utils import train_model_by_country
        df_country_selected = all_df_country[all_df_country['country'] == country_selected]
        importance_df = train_model_by_country(df_country_selected, country_selected)
        importance_df.reset_index(drop=True, inplace=True)
        importance_df.insert(0, 'No', range(1, len(importance_df) + 1))
        top_features = importance_df.head(15)['Feature'].dropna().astype(str).unique()
        
        df_country_comparison = all_df_country_comparison[all_df_country_comparison['country'] == country_comparison]
        importance_df_comparison = train_model_by_country(df_country_comparison, country_comparison)
        importance_df_comparison.reset_index(drop=True, inplace=True)
        importance_df_comparison.insert(0, 'No', range(1, len(importance_df_comparison) + 1))
        top_features2 = importance_df_comparison.head(15)['Feature'].dropna().astype(str).unique()
        
        from matplotlib_venn import venn2
        # Konversi ke himpunan
        set1 = set(top_features)
        set2 = set(top_features2)
        intersection = set1.intersection(set2)

        # Buat kolom layout
        col1, col2 = st.columns(2)

        with col1:
            # Visualisasi diagram Venn dengan background hitam dan warna mencolok
            st.write("Bagan Irisan Fitur:")
            fig, ax = plt.subplots(figsize=(6, 6))
            fig.patch.set_facecolor('#0e1117')
            ax.set_facecolor('#0e1117')

            v = venn2([set1, set2], set_labels=(country_selected, country_comparison), ax=ax)

            # Warna mencolok ala px.colors.qualitative.Vivid
            vivid_colors = ['#E45756', '#4C78A8', '#F58518']  # Warna untuk A, B, dan A∩B
            if v.get_patch_by_id('10'):
                v.get_patch_by_id('10').set_color(vivid_colors[0])
            if v.get_patch_by_id('01'):
                v.get_patch_by_id('01').set_color(vivid_colors[1])
            if v.get_patch_by_id('11'):
                v.get_patch_by_id('11').set_color(vivid_colors[2])

            # Ubah warna teks label agar terlihat di background hitam
            for text in v.set_labels:
                if text:
                    text.set_color('white')
            for text in v.subset_labels:
                if text:
                    text.set_color('white')

            # Tambahkan nama fitur irisan secara manual jika diperlukan
            if intersection:
                ax.text(0, 0, "\n".join(intersection), fontsize=8, color='white', ha='center', va='center')

            st.pyplot(fig)

        with col2:
            st.write("Tabel Irisan Fitur:")
            if intersection:
                df_intersection = pd.DataFrame(sorted(intersection), columns=['Feature'])
                df_intersection.index = df_intersection.index + 1
                st.dataframe(df_intersection)
            else:
                st.info("Tidak ada fitur yang sama dalam top 15 kedua negara.")


elif selected_tab == "Prediksi Emisi":
    from sklearn.ensemble import RandomForestRegressor
    rank_county = top_countries[top_countries['country'] == country_selected]
    st.header(f"Proyeksi Emisi Total GHG {country_selected} (Rank #{rank_county.index[0]+1})")
    # === Sidebar parameter ===
    
    data_country = alldata_df.copy()
    data_country = data_country[data_country['country'] == country_selected]
    st.markdown("⚙️ Atur Parameter Tahunan (%) untuk Setiap Skenario")
    
    # Hitung rata-rata pertumbuhan tahunan (%) --  menggunakan CAGR
    def compute_avg_growth(df, col):
        df = df.sort_values('year')
        growth_rates = df[col].pct_change().dropna()
        return round(growth_rates.mean() * 100, 2)

    def compute_cagr(df, col):
        df = df.sort_values('year')
        start_val = df[col].iloc[0]
        end_val = df[col].iloc[-1]
        n_years = df['year'].iloc[-1] - df['year'].iloc[0]
        if start_val <= 0 or end_val <= 0 or n_years <= 0:
            return 0.0
        cagr = (end_val / start_val) ** (1 / n_years) - 1
        return round(cagr * 100, 2)

    bau_defaults = {
        'population': compute_cagr(data_country, 'population'),
        'gdp': compute_cagr(data_country, 'gdp'),
        'energy_per_capita': compute_cagr(data_country, 'energy_per_capita'),
        'co2_per_capita': compute_cagr(data_country, 'co2_per_capita'),
        'coal_co2': compute_cagr(data_country, 'coal_co2'),
        'oil_co2': compute_cagr(data_country, 'oil_co2'),
        'gas_co2': compute_cagr(data_country, 'gas_co2'),
    }

    bau_col, moderate_col, strong_col = st.columns(3)
    with bau_col:
        st.markdown(f"<h3 style='color: yellow;'>🔴 Business as Usual (BAU)</h3>", unsafe_allow_html=True)
        bau = {
                'population': st.number_input("Pertumbuhan Populasi (BAU)", value=bau_defaults['population'], key='bau_pop'),
                'gdp': st.number_input("Pertumbuhan GDP (BAU)", value=bau_defaults['gdp'], key='bau_gdp'),
                'energy_per_capita': st.number_input("Perubahan Energy/capita (BAU)", value=bau_defaults['energy_per_capita'], key='bau_energy'),
                'co2_per_capita': st.number_input("Perubahan CO2/capita (BAU)", value=bau_defaults['co2_per_capita'], key='bau_co2'),
                'coal_co2': st.number_input("Perubahan Coal CO2 (BAU)", value=bau_defaults['coal_co2'], key='bau_coal'),
                'oil_co2': st.number_input("Perubahan Oil CO2 (BAU)", value=bau_defaults['oil_co2'], key='bau_oil'),
                'gas_co2': st.number_input("Perubahan Gas CO2 (BAU)", value=bau_defaults['gas_co2'], key='bau_gas'),
            }
    with moderate_col:
        st.markdown(f"<h3 style='color: yellow;'>🟡 Mitigasi Sedang</h3>", unsafe_allow_html=True)
       
        moderate = {
                'population': st.number_input("Pertumbuhan Populasi (Sedang)", value=1.0, key='mod_pop'),
                'gdp': st.number_input("Pertumbuhan GDP (Sedang)", value=2.0, key='mod_gdp'),
                'energy_per_capita': st.number_input("Penurunan Energy/capita (Sedang)", value=-1.5, key='mod_energy'),
                'co2_per_capita': st.number_input("Penurunan CO2/capita (Sedang)", value=-1.5, key='mod_co2'),
                'coal_co2': st.number_input("Penurunan Coal CO2 (Sedang)", value=-3.0, key='mod_coal'),
                'oil_co2': st.number_input("Penurunan Oil CO2 (Sedang)", value=-2.5, key='mod_oil'),
                'gas_co2': st.number_input("Penurunan Gas CO2 (Sedang)", value=-2.0, key='mod_gas'),
            }
    with strong_col:
        st.markdown(f"<h3 style='color: yellow;'>🟢 Mitigasi Kuat</h3>", unsafe_allow_html=True)
        strong = {
                'population': st.number_input("Pertumbuhan Populasi (Kuat)", value=1.0, key='str_pop'),
                'gdp': st.number_input("Pertumbuhan GDP (Kuat)", value=2.0, key='str_gdp'),
                'energy_per_capita': st.number_input("Penurunan Energy/capita (Kuat)", value=-3.0, key='str_energy'),
                'co2_per_capita': st.number_input("Penurunan CO2/capita (Kuat)", value=-3.0, key='str_co2'),
                'coal_co2': st.number_input("Penurunan Coal CO2 (Kuat)", value=-5.0, key='str_coal'),
                'oil_co2': st.number_input("Penurunan Oil CO2 (Kuat)", value=-4.0, key='str_oil'),
                'gas_co2': st.number_input("Penurunan Gas CO2 (Kuat)", value=-3.5, key='str_gas'),
            }

    pred_year_end = st.slider("📆 Proyeksi Hingga Tahun", 2024, 2060, 2040)

    # === Model Training ===
    features = ['population', 'gdp', 'energy_per_capita', 'co2_per_capita', 'coal_co2', 'oil_co2', 'gas_co2']
    target = 'total_ghg'

    X_train = data_country[features]
    y_train = data_country[target]
    model = RandomForestRegressor(n_estimators=200, random_state=42)
    model.fit(X_train, y_train)

    # === Fungsi Proyeksi ===
    def generate_projection(initial_df, year_end, annual_change):
        row = initial_df.copy()
        base_year = int(row['year'].values[0])
        projections = []
        for year in range(base_year + 1, year_end + 1):
            row['year'] = year
            for col, pct in annual_change.items():
                row[col] *= (1 + pct / 100)
            projections.append(row.copy())
        return pd.concat(projections, ignore_index=True)

    # Data terakhir
    last_row = data_country[data_country['year'] == data_country['year'].max()]

    # Proyeksi tiap skenario
    bau_df = generate_projection(last_row, pred_year_end, bau)
    mod_df = generate_projection(last_row, pred_year_end, moderate)
    str_df = generate_projection(last_row, pred_year_end, strong)

    bau_df = pd.concat([last_row, bau_df], ignore_index=True)
    mod_df = pd.concat([last_row, mod_df], ignore_index=True)
    str_df = pd.concat([last_row, str_df], ignore_index=True)

    bau_df['scenario'] = 'BAU'
    mod_df['scenario'] = 'Moderate'
    str_df['scenario'] = 'Strong'

    # Prediksi total_ghg untuk tiap skenario
    bau_df['predicted_total_ghg'] = model.predict(bau_df[features])
    mod_df['predicted_total_ghg'] = model.predict(mod_df[features])
    str_df['predicted_total_ghg'] = model.predict(str_df[features])

    # === Gabungkan semua skenario ===
    result_df = pd.concat([bau_df, mod_df, str_df])

    result_col1, result_col2 = st.columns([3,2])
    with result_col1:
        st.markdown(f"<h3 style='color: yellow;'>Grafik Proyeksi Total Emisi GHG - {country_selected}</h3>", unsafe_allow_html=True)
        # === Plot ===
        fig, ax = plt.subplots(figsize=(10, 6))

        # Data historis
        ax.plot(data_country['year'], data_country['total_ghg'], label='Historis', color='grey', linewidth=2)

        # Plot skenario
        ax.plot(bau_df['year'], bau_df['predicted_total_ghg'], label='BAU', linestyle='--', color='red')
        ax.plot(mod_df['year'], mod_df['predicted_total_ghg'], label='Mitigasi Sedang', linestyle='--', color='gold')
        ax.plot(str_df['year'], str_df['predicted_total_ghg'], label='Mitigasi Kuat', linestyle='--', color='green')

        ax.set_title(f"Proyeksi Emisi Total GHG {country_selected} (2024–{pred_year_end}) - Random Forest".format(pred_year_end), fontweight='bold')
        ax.set_xlabel("Tahun")
        ax.set_ylabel("Total GHG")
        ax.grid(True)
        ax.legend()

        st.pyplot(fig)
    with result_col2:
        st.markdown(f"<h3 style='color: yellow;'>Data Nilai Proyeksi Emisi  - {country_selected}</h3>", unsafe_allow_html=True)
        st.dataframe(result_df[['year', 'scenario', 'predicted_total_ghg']].rename(columns={
                        'year': 'Tahun',
                        'scenario': 'Skenario',
                        'predicted_total_ghg': 'Prediksi Total Emisi GHG'
                    }),
                    use_container_width=True,
                    hide_index=True,
                    height=500)
    

