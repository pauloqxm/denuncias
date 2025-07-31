import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static

# Configuração da página
st.set_page_config(page_title="Denúncias Recebidas", layout="wide")
st.title("📋 Denúncias Recebidas")

# URL pública da planilha Google Sheets (exportação CSV direta)
SHEET_ID = "1zzvR-gS__Jx5w85S65mwpRdnc6YGumH7YIjM6bOXrhc"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

# Carrega os dados
@st.cache_data
def carregar_dados():
    return pd.read_csv(CSV_URL)

df = carregar_dados()

# Filtros
col1, col2 = st.columns(2)
with col1:
    tipo = st.selectbox("Filtrar por tipo de denúncia", ["Todos"] + sorted(df["Tipo de Deúncia"].dropna().unique()))
with col2:
    bairro = st.selectbox("Filtrar por bairro", ["Todos"] + sorted(df["Bairro"].dropna().unique()))

if tipo != "Todos":
    df = df[df["Tipo de Deúncia"] == tipo]
if bairro != "Todos":
    df = df[df["Bairro"] == bairro]

# Tabela de dados
st.dataframe(df, use_container_width=True)

# Mapa com marcadores
if "_Coordenadas_latitude" in df.columns and "_Coordenadas_longitude" in df.columns:
    st.subheader("🗺️ Mapa das Denúncias")

    mapa = folium.Map(location=[-5.2, -39.3], zoom_start=12)

    for _, row in df.iterrows():
        lat = row["_Coordenadas_latitude"]
        lon = row["_Coordenadas_longitude"]
        if pd.notna(lat) and pd.notna(lon):
            popup = f"""
            <b>Nome:</b> {row.get('Nome', 'N/A')}<br>
            <b>Tipo:</b> {row.get('Tipo de Deúncia', 'N/A')}<br>
            <b>Bairro:</b> {row.get('Bairro', 'N/A')}
            """
            folium.Marker([lat, lon], popup=popup).add_to(mapa)

    folium_static(mapa)
else:
    st.warning("Colunas de coordenadas não encontradas para exibir o mapa.")
