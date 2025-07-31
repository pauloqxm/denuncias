import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd

# Dados simulados
data = pd.DataFrame({
    'tipo': ['Obra', 'Denúncia', 'Obra', 'Denúncia'],
    'bairro': ['Centro', 'Alto Alegre', 'Maravilha', 'Edmilson Correia'],
    'descricao': [
        'Pavimentação em andamento',
        'Iluminação pública sem manutenção',
        'Construção de creche parada',
        'Esgoto a céu aberto'
    ],
    'latitude': [-5.196, -5.202, -5.210, -5.215],
    'longitude': [-39.288, -39.295, -39.300, -39.310]
})

# Função para criar o mapa
def gerar_mapa(dataframe):
    mapa = folium.Map(location=[-5.2, -39.29], zoom_start=13)
    for _, row in dataframe.iterrows():
        cor = 'green' if row['tipo'] == 'Obra' else 'red'
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            popup=f"{row['tipo']} em {row['bairro']}:
{row['descricao']}",
            icon=folium.Icon(color=cor)
        ).add_to(mapa)
    return mapa

# Título do app
st.set_page_config(page_title="Mapeador de Obras", layout="centered")
st.title("🗺️ Mapeador de Obras e Denúncias por Bairro")
st.markdown("Acompanhe as obras em andamento e as principais denúncias por bairro.")

# Filtro de bairro
bairros = ['Todos'] + sorted(data['bairro'].unique().tolist())
bairro_escolhido = st.selectbox("Filtrar por bairro:", bairros)

# Filtra dados
dados_filtrados = data if bairro_escolhido == 'Todos' else data[data['bairro'] == bairro_escolhido]

# Gera e exibe mapa
mapa = gerar_mapa(dados_filtrados)
st_data = st_folium(mapa, width=700, height=500)
