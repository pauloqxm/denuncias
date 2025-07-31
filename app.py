import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static

# Configuração da página
st.set_page_config(page_title="Denúncias Recebidas", layout="wide")
st.title("📋 Denúncias Recebidas")

@st.cache_data
def carregar_dados():
    try:
        df = pd.read_csv("fiscaliza.csv")
        # Remove linhas completamente vazias
        df = df.dropna(how='all')
        
        # Verifica e converte coordenadas para numérico
        if "_Coordenadas_latitude" in df.columns:
            df["_Coordenadas_latitude"] = pd.to_numeric(df["_Coordenadas_latitude"], errors='coerce')
        if "_Coordenadas_longitude" in df.columns:
            df["_Coordenadas_longitude"] = pd.to_numeric(df["_Coordenadas_longitude"], errors='coerce')
            
        return df
    except Exception as e:
        st.error(f"Erro ao carregar os dados: {e}")
        return pd.DataFrame()

df = carregar_dados()

# Verifica se o DataFrame não está vazio
if df.empty:
    st.error("❌ Não foi possível carregar os dados ou o arquivo está vazio.")
else:
    # Verifica se as colunas necessárias existem
    colunas_necessarias = ["Tipo de Denúncia", "Bairro", "Nome", "Breve relato", "_submission_time"]
    colunas_faltantes = [col for col in colunas_necessarias if col not in df.columns]
    
    if colunas_faltantes:
        st.error(f"❌ Colunas faltantes no arquivo: {', '.join(colunas_faltantes)}")
    else:
        # Filtros
        col1, col2 = st.columns(2)
        with col1:
            tipo = st.selectbox("Filtrar por tipo de denúncia", ["Todos"] + sorted(df["Tipo de Denúncia"].dropna().unique()))
        with col2:
            bairro = st.selectbox("Filtrar por bairro", ["Todos"] + sorted(df["Bairro"].dropna().unique()))

        # Aplica filtros sem modificar o DataFrame original
        filtered_df = df.copy()
        if tipo != "Todos":
            filtered_df = filtered_df[filtered_df["Tipo de Denúncia"] == tipo]
        if bairro != "Todos":
            filtered_df = filtered_df[filtered_df["Bairro"] == bairro]

        # Exibir tabela
        st.dataframe(filtered_df[["Nome", "Bairro", "Tipo de Denúncia", "Breve relato", "_submission_time"]], 
                    use_container_width=True)

        # Mapa com imagem no popup
        if "_Coordenadas_latitude" in filtered_df.columns and "_Coordenadas_longitude" in filtered_df.columns:
            st.subheader("🗺️ Mapa das Denúncias")

            # Filtra apenas linhas com coordenadas válidas
            valid_coords_df = filtered_df[
                (filtered_df["_Coordenadas_latitude"].notna()) & 
                (filtered_df["_Coordenadas_longitude"].notna())
            ]
            
            # Calcula o centro do mapa baseado nos dados filtrados
            if not valid_coords_df.empty:
                try:
                    lat_mean = valid_coords_df["_Coordenadas_latitude"].mean()
                    lon_mean = valid_coords_df["_Coordenadas_longitude"].mean()
                    mapa = folium.Map(location=[lat_mean, lon_mean], zoom_start=12)
                except:
                    mapa = folium.Map(location=[-5.2, -39.3], zoom_start=12)
            else:
                mapa = folium.Map(location=[-5.2, -39.3], zoom_start=12)
                st.warning("Nenhuma denúncia com coordenadas válidas para exibir no mapa.")

            for _, row in valid_coords_df.iterrows():
                try:
                    lat = float(row["_Coordenadas_latitude"])
                    lon = float(row["_Coordenadas_longitude"])
                    
                    foto_url = row.get("Foto_URL", "")
                    # Verifica se a URL da foto é válida
                    imagem_html = ""
                    if pd.notna(foto_url) and str(foto_url).strip() and str(foto_url).startswith(('http://', 'https://')):
                        imagem_html = f'<img src="{foto_url}" width="200" style="margin-top:10px;"><br>'
                    
                    popup = folium.Popup(f"""
                        <div style="font-family: Arial, sans-serif;">
                            <b>Nome:</b> {row.get('Nome', 'N/A')}<br>
                            <b>Tipo:</b> {row.get('Tipo de Denúncia', 'N/A')}<br>
                            <b>Bairro:</b> {row.get('Bairro', 'N/A')}<br>
                            <b>Relato:</b> {row.get('Breve relato', 'N/A')}<br>
                            {imagem_html}
                        </div>
                    """, max_width=300)
                    
                    folium.Marker(
                        [lat, lon], 
                        popup=popup,
                        icon=folium.Icon(color="red", icon="info-sign")
                    ).add_to(mapa)
                except ValueError:
                    continue  # Pula linhas com coordenadas inválidas

            folium_static(mapa, width=1000)
        else:
            st.warning("⚠️ Colunas de coordenadas não encontradas no arquivo.")
