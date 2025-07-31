
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from geopy.distance import geodesic

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

if 'selecionado' not in st.session_state:
    st.session_state['selecionado'] = None

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

                for i, row in valid_coords_df.iterrows():
                    lat = row["_Coordenadas_latitude"]
                    lon = row["_Coordenadas_longitude"]
                    popup_html = (
                        f"<div style='font-family: Arial, sans-serif; border: 2px solid #2A4D9B; border-radius: 8px; padding: 8px; background-color: #f9f9f9;'>"
                        f"<h4 style='margin-top: 0; margin-bottom: 8px; color: #2A4D9B;'>🚨 Denúncia Registrada</h4>"
                        f"<p><b>📛 Nome:</b> {row['Nome']}</p>"
                        f"<p><b>📝 Tipo:</b> {row['Tipo de Denúncia']}</p>"
                        f"<p><b>📍 Bairro:</b> {row['Bairro']}</p>"
                        f"<p><b>🧾 Relato:</b> {row['Breve relato']}</p>"
                        "</div>"
                    )
                    popup = folium.Popup(folium.IFrame(popup_html, width=250, height=220), max_width=300)
                    folium.Marker([lat, lon], popup=popup, icon=folium.Icon(color="blue", icon="info-sign")).add_to(mapa)

                map_result = st_folium(mapa, width=1000, height=500)

                if map_result and map_result.get("last_clicked"):
                    click_lat = map_result["last_clicked"]["lat"]
                    click_lon = map_result["last_clicked"]["lng"]

                    def get_distance(row):
                        return geodesic((row["_Coordenadas_latitude"], row["_Coordenadas_longitude"]), (click_lat, click_lon)).meters

                    distances = valid_coords_df.apply(get_distance, axis=1)
                    closest_idx = distances.idxmin()
                    st.session_state["selecionado"] = closest_idx

        st.subheader("📄 Lista de Denúncias Filtradas")
        if st.session_state['selecionado'] is not None and st.session_state['selecionado'] in filtered_df.index:
            selected_row = filtered_df.loc[st.session_state['selecionado']]
            st.markdown(f"🔎 Linha selecionada: **{selected_row['Nome']}** — {selected_row['Tipo de Denúncia']}")

        st.dataframe(filtered_df[["Nome", "Bairro", "Tipo de Denúncia", "Breve relato", "_submission_time"]], use_container_width=True)
