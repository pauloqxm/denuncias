import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static

# URL da planilha Google Sheets como CSV
SHEET_ID = "1zzvR-gS__Jx5w85S65mwpRdnc6YGumH7YIjM6bOXrhc"
SHEET_NAME = "Página1"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}"

@st.cache_data
def carregar_dados():
    return pd.read_csv(CSV_URL)

st.set_page_config(page_title="Denúncias", layout="wide")
st.title("📋 Denúncias Recebidas")

df = carregar_dados()

# Filtros
col1, col2 = st.columns(2)
with col1:
    tipo = st.selectbox("Filtrar por tipo de denúncia", ["Todos"] + sorted(df["Tipo de Deúncia"].dropna().unique()))
with col2:
    bairro = st.selectbox("Filtrar por bairro", ["Todos"] + sorted(df["Bairro"].dropna().unique()))

# Aplicar filtros
if tipo != "Todos":
    df = df[df["Tipo de Deúncia"] == tipo]
if bairro != "Todos":
    df = df[df["Bairro"] == bairro]

st.dataframe(df, use_container_width=True)

# Verifica se há colunas de coordenadas
if "_Coordenadas_latitude" in df.columns and "_Coordenadas_longitude" in df.columns:
    st.subheader("🗺️ Mapa das denúncias")

    mapa = folium.Map(location=[-5.2, -39.3], zoom_start=12)

    for _, row in df.iterrows():
        lat = row["_Coordenadas_latitude"]
        lon = row["_Coordenadas_longitude"]
        if pd.notna(lat) and pd.notna(lon):
            popup_text = f"""
            <b>Nome:</b> {row.get('Nome', 'N/A')}<br>
            <b>Tipo:</b> {row.get('Tipo de Deúncia', 'N/A')}<br>
            <b>Bairro:</b> {row.get('Bairro', 'N/A')}
            """
            folium.Marker(location=[lat, lon], popup=popup_text).add_to(mapa)

    folium_static(mapa)
else:
    st.warning("As colunas de coordenadas não foram encontradas.")
