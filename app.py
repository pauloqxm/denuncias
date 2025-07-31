import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from streamlit_javascript import st_javascript

st.set_page_config(page_title="Mapeador de Denúncias", layout="centered")

if "denuncias" not in st.session_state:
    st.session_state.denuncias = pd.DataFrame(columns=["tipo", "bairro", "descricao", "latitude", "longitude", "imagem"])

st.title("📝 Enviar Nova Denúncia")

tipo = st.selectbox("Tipo:", ["Denúncia", "Obra"])
bairro = st.text_input("Bairro:")
descricao = st.text_area("Descrição:")
imagem = st.file_uploader("Foto (opcional):", type=["png", "jpg", "jpeg"])

st.markdown("### 📍 Capturar Localização Atual")

# Captura do GPS com retorno para Python
coords = st_javascript("await new Promise((resolve) => navigator.geolocation.getCurrentPosition((pos) => resolve({lat: pos.coords.latitude, lon: pos.coords.longitude})))")

gps_lat = coords.get("lat") if coords else None
gps_lon = coords.get("lon") if coords else None

# Define ponto inicial do mapa
map_center = [gps_lat, gps_lon] if gps_lat and gps_lon else [-5.2, -39.29]
mapa = folium.Map(location=map_center, zoom_start=15 if gps_lat else 13)

# Mostra ponto do GPS, se houver
if gps_lat and gps_lon:
    folium.Marker([gps_lat, gps_lon], tooltip="Localização atual (GPS)", icon=folium.Icon(color="blue")).add_to(mapa)

# Mapa clicável
map_data = st_folium(mapa, width=700, height=400)

# Substituir por clique
click_coords = map_data.get("last_clicked")
default_lat = click_coords["lat"] if click_coords else gps_lat
default_lon = click_coords["lng"] if click_coords else gps_lon

# Campos de coordenadas editáveis lado a lado
st.markdown("### Coordenadas")
col1, col2 = st.columns(2)
with col1:
    final_lat = st.text_input("Latitude", value=str(default_lat) if default_lat else "")
with col2:
    final_lon = st.text_input("Longitude", value=str(default_lon) if default_lon else "")

if final_lat and final_lon:
    st.success(f"Localização definida: {final_lat}, {final_lon}")
else:
    st.warning("Localização não definida. Habilite o GPS, clique no mapa ou preencha manualmente.")

if st.button("Enviar Denúncia"):
    if not final_lat or not final_lon or not bairro or not descricao:
        st.warning("Preencha todos os campos obrigatórios e defina a localização.")
    else:
        nova = {
            "tipo": tipo,
            "bairro": bairro,
            "descricao": descricao,
            "latitude": float(final_lat),
            "longitude": float(final_lon),
            "imagem": imagem.name if imagem else ""
        }
        st.session_state.denuncias = pd.concat([st.session_state.denuncias, pd.DataFrame([nova])], ignore_index=True)
        st.success("Denúncia enviada com sucesso!")
        st.balloons()
