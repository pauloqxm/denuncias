import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static

# Configuração da página
st.set_page_config(page_title="Denúncias Recebidas", layout="wide")
st.title("📋 Denúncias Recebidas")

@st.cache_data
def carregar_dados():
    return pd.read_csv("fiscaliza.csv")

df = carregar_dados()

# Filtros
col1, col2 = st.columns(2)
with col1:
    tipo = st.selectbox("Filtrar por tipo de denúncia", ["Todos"] + sorted(df["Tipo de Denúncia"].dropna().unique()))
with col2:
    bairro = st.selectbox("Filtrar por bairro", ["Todos"] + sorted(df["Bairro"].dropna().unique()))

if tipo != "Todos":
    df = df[df["Tipo de Denúncia"] == tipo]
if bairro != "Todos":
    df = df[df["Bairro"] == bairro]

# Exibir tabela
st.dataframe(df[["Nome", "Bairro", "Tipo de Denúncia", "Breve relato", "_submission_time"]], use_container_width=True)

# Mapa com imagem no popup
if "_Coordenadas_latitude" in df.columns and "_Coordenadas_longitude" in df.columns:
    st.subheader("🗺️ Mapa das Denúncias")

    mapa = folium.Map(location=[df["_Coordenadas_latitude"].mean(), df["_Coordenadas_longitude"].mean()], zoom_start=12)

    for _, row in df.iterrows():
        lat = row["_Coordenadas_latitude"]
        lon = row["_Coordenadas_longitude"]
        if pd.notna(lat) and pd.notna(lon):
            foto_url = row.get("Foto_URL", "")
            imagem_html = f'<img src="{foto_url}" width="200">' if pd.notna(foto_url) and foto_url.strip() else 'Sem imagem'

            popup = folium.Popup(f"""
                <b>Nome:</b> {row.get('Nome', 'N/A')}<br>
                <b>Tipo:</b> {row.get('Tipo de Denúncia', 'N/A')}<br>
                <b>Bairro:</b> {row.get('Bairro', 'N/A')}<br>
                <b>Relato:</b> {row.get('Breve relato', 'N/A')}<br>
                {imagem_html}
            """, max_width=300)
            folium.Marker([lat, lon], popup=popup).add_to(mapa)

    folium_static(mapa)
else:
    st.warning("⚠️ Colunas de coordenadas não encontradas no arquivo.")
