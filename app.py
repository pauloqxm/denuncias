
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static

st.set_page_config(page_title="Denúncias Recebidas", layout="wide")
st.title("📋 Denúncias Recebidas")

if st.button("🔄 Recarregar dados"):
    st.experimental_rerun()

def carregar_dados():
    try:
        url = "https://docs.google.com/spreadsheets/d/1MV2b4e3GNc_rhA32jeMuVNhUQWz6HkP7xrC42VscYIk/export?format=csv"
        df = pd.read_csv(url)
        df = df.dropna(how='all')

        df.columns = df.columns.str.strip()
        df.rename(columns={"_submission_time": "SubmissionDate"}, inplace=True)

        df["Latitude"] = pd.to_numeric(df["Latitude"].astype(str).str.replace(",", "."), errors='coerce')
        df["Longitude"] = pd.to_numeric(df["Longitude"].astype(str).str.replace(",", "."), errors='coerce')

        if "Foto_URL" in df.columns:
            df["Foto_URL"] = df["Foto_URL"].astype(str).str.replace(",", ".", regex=False)
        return df
    except Exception as e:
        st.error(f"Erro ao carregar os dados: {e}")
        return pd.DataFrame()

df = carregar_dados()

if st.button("🔄 Recarregar dados"):
    st.experimental_rerun()


if df.empty:
    st.error("❌ Não foi possível carregar os dados ou o arquivo está vazio.")
else:
    colunas_necessarias = ["Tipo de Denúncia", "Bairro", "Nome", "Breve relato", "SubmissionDate"]
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

        if "Latitude" in filtered_df.columns and "Longitude" in filtered_df.columns:
            valid_coords_df = filtered_df[filtered_df["Latitude"].notna() & filtered_df["Longitude"].notna()]
            if not valid_coords_df.empty:
                lat_mean = valid_coords_df["Latitude"].mean()
                lon_mean = valid_coords_df["Longitude"].mean()
                mapa = folium.Map(location=[lat_mean, lon_mean], zoom_start=13)
                for _, row in valid_coords_df.iterrows():
                    lat = row["Latitude"]
                    lon = row["Longitude"]
                    foto_url = row.get("Foto_URL", "")
                    imagem_html = ""
                    if pd.notna(foto_url) and str(foto_url).strip().startswith(('http://', 'https://')):
                        imagem_html = f'<img src="{foto_url}" width="200" style="margin-top:10px;"><br>'
                    popup_info = (
                        "<div style='font-family: Arial, sans-serif; border: 2px solid #2A4D9B; border-radius: 8px; padding: 8px; background-color: #f9f9f9;'>"
                        "<h4 style='margin-top: 0; margin-bottom: 8px; color: #2A4D9B; border-bottom: 1px solid #ccc;'>🚨 Denúncia Registrada</h4>"
                        f"<p style='margin: 4px 0;'><span style='color: #2A4D9B; font-weight: bold;'>📛 Nome:</span> {row.get('Nome', 'Sem nome')}</p>"
                        f"<p style='margin: 4px 0;'><span style='color: #2A4D9B; font-weight: bold;'>📝 Tipo:</span> {row.get('Tipo de Denúncia', 'Não informado')}</p>"
                        f"<p style='margin: 4px 0;'><span style='color: #2A4D9B; font-weight: bold;'>📍 Bairro:</span> {row.get('Bairro', 'Não informado')}</p>"
                        f"<p style='margin: 4px 0;'><span style='color: #2A4D9B; font-weight: bold;'>🧾 Relato:</span> {row.get('Breve relato', 'Não informado')}</p>"
                        f"{imagem_html}</div>"
                    )
                    popup = folium.Popup(popup_info, max_width=300)
                    folium.Marker([lat, lon], popup=popup, icon=folium.Icon(color="blue", icon="info-sign")).add_to(mapa)
                folium_static(mapa, width=1000)
            else:
                st.warning("Nenhuma denúncia com coordenadas válidas para exibir no mapa.")
        else:
            st.warning("⚠️ Colunas de coordenadas não encontradas no arquivo.")

        st.subheader("📄 Lista de Denúncias Filtradas")
        st.dataframe(filtered_df[["Nome", "Bairro", "Tipo de Denúncia", "Breve relato", "SubmissionDate"]], use_container_width=True)
