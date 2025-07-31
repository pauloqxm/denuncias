import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import streamlit.components.v1 as components

st.set_page_config(page_title="Mapeador de Denúncias", layout="centered")

if "denuncias" not in st.session_state:
    st.session_state.denuncias = pd.DataFrame(columns=["tipo", "bairro", "descricao", "latitude", "longitude", "imagem"])

st.title("📝 Enviar Nova Denúncia")

tipo = st.selectbox("Tipo:", ["Denúncia", "Obra"])
bairro = st.text_input("Bairro:")
descricao = st.text_area("Descrição:")
imagem = st.file_uploader("Foto (opcional):", type=["png", "jpg", "jpeg"])

st.markdown("### 📍 Capturar Localização Atual")

# JavaScript para capturar geolocalização
components.html("""
    <script>
    navigator.geolocation.getCurrentPosition(
        (pos) => {
            const lat = pos.coords.latitude;
            const lon = pos.coords.longitude;
            const payload = {'latitude': lat, 'longitude': lon};
            const streamlitEvent = new CustomEvent("streamlit:location", {detail: payload});
            window.dispatchEvent(streamlitEvent);
        },
        (err) => {
            console.error("Erro ao obter localização:", err.message);
        }
    );
    </script>
""", height=0)

# Container para resultado
location = st_folium(folium.Map(location=[-5.2, -39.29], zoom_start=13), width=700, height=400)

# Recebe coordenadas automaticamente via JS se já não estiver setado
if "gps_received" not in st.session_state:
    st.session_state.gps_received = False

coords = location.get("last_clicked")
gps_lat = coords["lat"] if coords else None
gps_lon = coords["lng"] if coords else None

st.write("🔍 Clique no mapa para sobrescrever a localização, ou use a localização automática se disponível.")

if gps_lat and gps_lon:
    st.success(f"Localização definida: {gps_lat}, {gps_lon}")
    st.session_state.gps_lat = gps_lat
    st.session_state.gps_lon = gps_lon

final_lat = st.session_state.get("gps_lat", "")
final_lon = st.session_state.get("gps_lon", "")

if st.button("Enviar Denúncia"):
    if not final_lat or not final_lon or not bairro or not descricao:
        st.warning("Por favor, preencha todos os campos e defina a localização.")
    else:
        nova = {
            "tipo": tipo,
            "bairro": bairro,
            "descricao": descricao,
            "latitude": final_lat,
            "longitude": final_lon,
            "imagem": imagem.name if imagem else ""
        }
        st.session_state.denuncias = pd.concat([st.session_state.denuncias, pd.DataFrame([nova])], ignore_index=True)
        st.success("Denúncia enviada com sucesso!")
        st.balloons()
