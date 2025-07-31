
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static

st.set_page_config(page_title="Denúncias Recebidas", layout="wide")
st.title("📋 Denúncias Recebidas")

@st.cache_data
def carregar_dados():
    try:
        df = pd.read_csv("fiscaliza.csv")
        df = df.dropna(how='all')

        # Corrigir vírgulas nas coordenadas
        if "_Coordenadas_latitude" in df.columns:
            df["_Coordenadas_latitude"] = pd.to_numeric(
                df["_Coordenadas_latitude"].astype(str).str.replace(",", "."), errors='coerce'
            )
        if "_Coordenadas_longitude" in df.columns:
            df["_Coordenadas_longitude"] = pd.to_numeric(
                df["_Coordenadas_longitude"].astype(str).str.replace(",", "."), errors='coerce'
            )

        # Corrigir vírgulas em URLs de imagem
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
        st.dataframe(filtered_df[["Nome", "Bairro", "Tipo de Denúncia", "Breve relato", "_submission_time"]], use_container_width=True)

        if "_Coordenadas_latitude" in filtered_df.columns and "_Coordenadas_longitude" in filtered_df.columns:
            st.subheader("🗺️ Mapa das Denúncias")
            valid_coords_df = filtered_df[filtered_df["_Coordenadas_latitude"].notna() & filtered_df["_Coordenadas_longitude"].notna()]
            if not valid_coords_df.empty:
                lat_mean = valid_coords_df["_Coordenadas_latitude"].mean()
                lon_mean = valid_coords_df["_Coordenadas_longitude"].mean()
                mapa = folium.Map(location=[lat_mean, lon_mean], zoom_start=12)
                for _, row in valid_coords_df.iterrows():
                    lat = row["_Coordenadas_latitude"]
                    lon = row["_Coordenadas_longitude"]
                    foto_url = row.get("Foto_URL", "")
                    imagem_html = ""
                    if pd.notna(foto_url) and str(foto_url).strip().startswith(('http://', 'https://')):
                        imagem_html = f'<img src="{foto_url}" width="200" style="margin-top:10px;"><br>'
                    popup = folium.Popup(f"""
                        <div style="font-family: Arial; font-size: 13px;">
                            <b>Nome:</b> {row.get('Nome', 'N/A')}<br>
                            <b>Tipo:</b> {row.get('Tipo de Denúncia', 'N/A')}<br>
                            <b>Bairro:</b> {row.get('Bairro', 'N/A')}<br>
                            <b>Relato:</b> {row.get('Breve relato', 'N/A')}<br>
                            {imagem_html}
                        </div>
                    """, max_width=300)
                    folium.Marker([lat, lon], popup=popup, icon=folium.Icon(color="red", icon="info-sign")).add_to(mapa)
                folium_static(mapa, width=1000)
            else:
                st.warning("Nenhuma denúncia com coordenadas válidas para exibir no mapa.")
        else:
            st.warning("⚠️ Colunas de coordenadas não encontradas no arquivo.")
