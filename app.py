
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="Denúncias Recebidas", layout="wide")
st.title("📋 Denúncias Recebidas")

@st.cache_data
def carregar_dados():
    try:
        df = pd.read_csv("fiscaliza.csv")
        df = df.dropna(how='all')

        if "_Coordenadas_latitude" in df.columns:
            df["_Coordenadas_latitude"] = pd.to_numeric(df["_Coordenadas_latitude"].astype(str).str.replace(",", "."), errors='coerce')
        if "_Coordenadas_longitude" in df.columns:
            df["_Coordenadas_longitude"] = pd.to_numeric(df["_Coordenadas_longitude"].astype(str).str.replace(",", "."), errors='coerce')
        if "Foto_URL" in df.columns:
            df["Foto_URL"] = df["Foto_URL"].astype(str).str.replace(",", ".", regex=False)
        return df
    except Exception as e:
        st.error(f"Erro ao carregar os dados: {e}")
        return pd.DataFrame()

df = carregar_dados()

if df.empty:
    st.error("❌ Não foi possível carregar os dados ou o arquivo está vazio.")
else:
    colunas_necessarias = ["Tipo de Denúncia", "Bairro", "Nome", "Breve relato", "_submission_time"]
    colunas_faltantes = [col for col in colunas_necessarias if col not in df.columns]
    if colunas_faltantes:
        st.error(f"❌ Colunas faltantes: {', '.join(colunas_faltantes)}")
    else:
        col1, col2 = st.columns(2)
        with col1:
            tipo = st.selectbox("Filtrar por tipo de denúncia", ["Todos"] + sorted(df["Tipo de Denúncia"].dropna().unique()))
        with col2:
            bairro = st.selectbox("Filtrar por bairro", ["Todos"] + sorted(df["Bairro"].dropna().unique()))
        filtered_df = df.copy()
        if tipo != "Todos":
            filtered_df = filtered_df[filtered_df["Tipo de Denúncia"] == tipo]
        if bairro != "Todos":
            filtered_df = filtered_df[filtered_df["Bairro"] == bairro]

        st.subheader("🗺️ Mapa das Denúncias")

        if "_Coordenadas_latitude" in filtered_df.columns and "_Coordenadas_longitude" in filtered_df.columns:
            valid_coords_df = filtered_df[filtered_df["_Coordenadas_latitude"].notna() & filtered_df["_Coordenadas_longitude"].notna()]
            if not valid_coords_df.empty:
                lat_mean = valid_coords_df["_Coordenadas_latitude"].mean()
                lon_mean = valid_coords_df["_Coordenadas_longitude"].mean()
                mapa = folium.Map(location=[lat_mean, lon_mean], zoom_start=13)

                for idx, row in valid_coords_df.iterrows():
                    lat = row["_Coordenadas_latitude"]
                    lon = row["_Coordenadas_longitude"]
                    popup_html = f"""
                        <div style='font-family: Arial; font-size: 13px;'>
                            <b>Nome:</b> {row['Nome']}<br>
                            <b>Tipo:</b> {row['Tipo de Denúncia']}<br>
                            <b>Bairro:</b> {row['Bairro']}<br>
                            <b>Relato:</b> {row['Breve relato']}<br>
                            <i>(Clique no marcador e veja abaixo)</i>
                        </div>
                    """
                    folium.Marker(
                        location=[lat, lon],
                        popup=folium.Popup(popup_html, max_width=300),
                        tooltip=row["Nome"],
                        icon=folium.Icon(color="blue", icon="info-sign")
                    ).add_to(mapa)

                map_result = st_folium(mapa, width=1000, height=450)

        st.subheader("📄 Lista de Denúncias Filtradas")
        st.dataframe(
            filtered_df[["Nome", "Bairro", "Tipo de Denúncia", "Breve relato", "_submission_time"]],
            use_container_width=True
        )
