import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns
import urllib
import plotly.express as px
import streamlit as st
from babel.numbers import format_currency
from pathlib import Path

st.set_page_config(page_title='Global Carbon Emissions Analysis', layout='wide')
start_year = "1970"
end_year="2023"
country_selected="Indonesia"
#load data
path_data = Path(os.getcwd()).joinpath("all_emissions.csv")
if path_data.exists():
    alldata_df = pd.read_csv(str(path_data))
    #country_df.sort_values(by="country", inplace=True)
    
else:
    st.error("File all_emissions.csv tidak ditemukan. Please ensure the file is in the correct directory.")
    st.error(path_data)
    st.stop()

path_country = Path(os.getcwd()).joinpath("all_countries.csv")
if path_country.exists():
    country_df = pd.read_csv(str(path_country))
    #country_df.sort_values(by="country", inplace=True)
    country_df.reset_index(inplace=True)
else:
    st.error("File all_countries.csv tidak ditemukan. Please ensure the file is in the correct directory.")
    st.error(path_country)
    st.stop()

# Sidebar
with st.sidebar:
    #title
    st.title("Global Carbon Emissions Analysis")
    #radio button
    country_selected = st.selectbox('Country:', country_df["Country"])
    #year range
    start_year = st.text_input('Start Year:',"1970")  
    end_year = st.text_input('End Year:',"2023")
    if st.button("Process"):
        st.balloons()

# Main
selected_columns=["year", "population", "total_ghg"]
main_df = (
    alldata_df[
        (alldata_df["country"] == str(country_selected)) &
        (alldata_df["year"] >= int(start_year)) &
        (alldata_df["year"] <= int(end_year))
    ][selected_columns]
    .rename(columns={
        "year": "Tahun",
        "population": "Total Populasi",
        "total_ghg": "Emisi GRK"
    })
    .reset_index(drop=True)  # Opsional untuk mereset indeks
)

st.header("Global Carbon Emission Analysis")
# Filter data untuk tahun 2023
df_2023 = alldata_df[alldata_df['year'] == 2023]

# Negara yang ingin dikecualikan dari visualisasi
excluded_countries = [
    'World', 'Asia', 'Upper-middle-income countries', 'High-income countries',
    'European Union (28)', 'European Union (27)', 'Europe (excl. EU-27)', 'Europe (excl. EU-28)',
    'North America', 'South America', 'North America (excl. USA)', 'Africa', 'Asia (excl. China and India)', 'Europe',
    'Low-income countries', 'Lower-middle-income countries'
]

# Filter negara dan urutkan berdasarkan emisi GHG tertinggi
df_filtered = df_2023[~df_2023['country'].isin(excluded_countries)]
top_10_countries = df_filtered.sort_values('total_ghg', ascending=False).head(10)

g1 = st.columns(1)[0]
with g1:
    st.subheader("Peta Emisi Karbon Global Dunia")
    
    fig = px.choropleth(
        df_filtered,
        locations='country',
        locationmode='country names',
        color='total_ghg',
        color_continuous_scale='Reds',
    )
 
    # Tampilkan plot
    st.plotly_chart(fig, use_container_width=True)

g2,g3 = st.columns(2)
with g2:
    st.subheader("Daftar Negara Penghasil Emisi Tertinggi ")
   
    # Reset index and add 'No' column
    top_10_countries = top_10_countries.reset_index(drop=True)
    top_10_countries.insert(0, 'No', range(1, len(top_10_countries) + 1))

    st.write(top_10_countries[['No', 'country', 'total_ghg']].rename(columns={'country': 'Negara', 'total_ghg': 'Total Emisi GRK'}).reset_index(drop=True), use_container_width=True)

with g3:
    st.subheader("Grafik Perbandingan Negara Penghasil Emisi Tertinggi ")
    fig, ax=plt.subplots(figsize=(12,6))

    # Data untuk pie chart
    labels = top_10_countries['country']  # Menggunakan alias 'Negara'
    sizes = top_10_countries['total_ghg']  # Menggunakan alias 'Total Emisi GRK'
    
   
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
    ax.axis('equal')  # Agar pie chart berbentuk lingkaran sempurna
    st.pyplot(fig)


g4, g5 = st.columns(2)

with g4:
    st.subheader("Total Emisi Tahunan " + country_selected )
    fig, ax=plt.subplots(figsize=(12,6))
    total_emisi_df =  alldata_df[
        (alldata_df["country"] == str(country_selected)) &
        (alldata_df["year"] >= int(start_year)) &
        (alldata_df["year"] <= int(end_year))
    ]
    ax.plot(
        total_emisi_df["year"],
        total_emisi_df["total_ghg"],
        marker="o",
        linewidth=2,
        color="#90CAF9"
    )
    ax.tick_params(axis="x", rotation=45)
    ax.tick_params(axis="y", labelsize=15)
    st.pyplot(fig)

with g5:
    st.subheader("Perbandingan GRK " + country_selected )
    fig, ax=plt.subplots(figsize=(12,6))
    total_emisi_df =  alldata_df[
        (alldata_df["country"] == str(country_selected)) &
        (alldata_df["year"] >= int(start_year)) &
        (alldata_df["year"] <= int(end_year))
    ]
    co2 = total_emisi_df["co2"].sum()
    methane = total_emisi_df["methane"].sum()
    nitrous_oxide = total_emisi_df["nitrous_oxide"].sum()

    # Data untuk pie chart
    labels = ['CO2', 'Methane', 'Nitrous Oxide']
    values = [co2, methane, nitrous_oxide]
    colors = ['#66b3ff', '#99ff99', '#ffcc99']
    ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=140, colors=colors)
    ax.axis("equal")
    st.pyplot(fig)

