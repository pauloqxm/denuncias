import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static

# Configuração da página
st.set_page_config(page_title="Denúncias Recebidas", layout="wide")
st.title("📋 Denúncias Recebidas")

# URL da planilha Google Sheets (exportação CSV pública)
SHEET_ID = "1zzvR-gS__Jx5w85S65mwpRdnc6YGumH7YIjM6bOXrhc"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

@st.cache_data
def carregar_dados():
    try:
        df = pd.read_csv(CSV_URL)
        # Remove linhas completamente vazias
        df = df.dropna(how='all')
        return df
    except Exception as e:
        st.error(f"Erro ao carregar os dados: {e}")
        return pd.DataFrame()

df = carregar_dados()

# Verifica se o DataFrame não está vazio
if df.empty:
    st.error("❌ Não foi possível carregar os dados ou a planilha está vazia.")
else:
    # Mostra colunas disponíveis (para depuração, se necessário)
    # st.write("Colunas:", df.columns.tolist())

    # Detecta colunas dinamicamente (case insensitive)
    denuncia_col = next((col for col in df.columns if "denúncia" in col.lower() or "denuncia" in col.lower()), None)
    bairro_col = next((col for col in df.columns if "bairro" in col.lower()), None)
    nome_col = next((col for col in df.columns if "nome" in col.lower()), "N/A")

    # Verifica se encontrou as colunas necessárias
    if denuncia_col and bairro_col:
        col1, col2 = st.columns(2)
        with col1:
            tipo = st.selectbox("Filtrar por tipo de denúncia", ["Todos"] + sorted(df[denuncia_col].dropna().unique()))
        with col2:
            bairro = st.selectbox("Filtrar por bairro", ["Todos"] + sorted(df[bairro_col].dropna().unique()))

        # Aplica filtros
        filtered_df = df.copy()
        if tipo != "Todos":
            filtered_df = filtered_df[filtered_df[denuncia_col] == tipo]
        if bairro != "Todos":
            filtered_df = filtered_df[filtered_df[bairro_col] == bairro]

        st.dataframe(filtered_df, use_container_width=True)

        # Mapa
        lat_col = next((col for col in df.columns if "latitude" in col.lower()), None)
        lon_col = next((col for col in df.columns if "longitude" in col.lower()), None)

        if lat_col and lon_col:
            st.subheader("🗺️ Mapa das Denúncias")

            # Calcula o centro do mapa baseado nos dados filtrados
            if not filtered_df.empty:
                avg_lat = filtered_df[lat_col].mean()
                avg_lon = filtered_df[lon_col].mean()
                mapa = folium.Map(location=[avg_lat, avg_lon], zoom_start=12)
            else:
                mapa = folium.Map(location=[-5.2, -39.3], zoom_start=12)

            for _, row in filtered_df.iterrows():
                lat = row[lat_col]
                lon = row[lon_col]
                if pd.notna(lat) and pd.notna(lon):
                    popup = f"""
                    <b>Nome:</b> {row.get(nome_col, 'N/A')}<br>
                    <b>Tipo:</b> {row.get(denuncia_col, 'N/A')}<br>
                    <b>Bairro:</b> {row.get(bairro_col, 'N/A')}
                    """
                    folium.Marker(
                        [lat, lon], 
                        popup=folium.Popup(popup, max_width=300),
                        icon=folium.Icon(color="red", icon="info-sign")
                    ).add_to(mapa)

            folium_static(mapa, width=1000)
        else:
            st.warning("⚠️ Colunas de coordenadas não encontradas no arquivo.")
    else:
        st.error("❌ As colunas 'Denúncia' e 'Bairro' não foram encontradas no arquivo.")
