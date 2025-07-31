import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import streamlit.components.v1 as components

st.set_page_config(page_title="Mapeador de Obras", layout="centered")

if "denuncias" not in st.session_state:
    st.session_state.denuncias = pd.DataFrame(columns=["tipo", "bairro", "descricao", "latitude", "longitude", "imagem"])

if "gps_lat" not in st.session_state:
    st.session_state.gps_lat = None
    st.session_state.gps_lon = None

def gerar_mapa(dataframe):
    mapa = folium.Map(location=[-5.2, -39.29], zoom_start=13)
    for _, row in dataframe.iterrows():
        cor = 'green' if row['tipo'] == 'Obra' else 'red'
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            popup=f"{row['tipo']} em {row['bairro']}:<br>{row['descricao']}",
            icon=folium.Icon(color=cor)
        ).add_to(mapa)
    return mapa

aba = st.sidebar.radio("Escolha a aba:", ["📍 Ver Mapa", "📝 Enviar Denúncia"])

if aba == "📍 Ver Mapa":
    st.title("🗺️ Mapeador de Obras e Denúncias por Bairro")
    st.markdown("Visualize no mapa as obras e denúncias cadastradas por região.")

    data = st.session_state.denuncias.copy()
    bairros = ['Todos'] + sorted(data['bairro'].unique().tolist())
    bairro_escolhido = st.selectbox("Filtrar por bairro:", bairros)

    dados_filtrados = data if bairro_escolhido == 'Todos' else data[data['bairro'] == bairro_escolhido]
    mapa = gerar_mapa(dados_filtrados)
    st_data = st_folium(mapa, width=700, height=500)

else:
    st.title("📝 Enviar Nova Denúncia")
    st.markdown("Marque no mapa ou use sua localização para facilitar o envio.")

    tipo = st.selectbox("Tipo:", ["Denúncia", "Obra"])
    bairro = st.text_input("Bairro:")
    descricao = st.text_area("Descrição:")
    imagem = st.file_uploader("Foto (opcional):", type=["png", "jpg", "jpeg"])

    st.markdown("### 📍 Capturar Localização Atual")
    components.html("""
        <script>
        navigator.geolocation.getCurrentPosition(
            (position) => {
                const lat = position.coords.latitude;
                const lon = position.coords.longitude;
                const streamlitDoc = window.parent.document;
                const inputLat = streamlitDoc.querySelector('input[data-testid="stTextInput"][aria-label="latitude"]');
                const inputLon = streamlitDoc.querySelector('input[data-testid="stTextInput"][aria-label="longitude"]');
                if (inputLat && inputLon) {
                    inputLat.value = lat;
                    inputLat.dispatchEvent(new Event('input', { bubbles: true }));
                    inputLon.value = lon;
                    inputLon.dispatchEvent(new Event('input', { bubbles: true }));
                }
            },
            (error) => {
                console.log("Erro ao acessar localização:", error.message);
            }
        );
        </script>
    """, height=0)

    lat = st.text_input("Latitude (preenchida automaticamente se autorizado):", key="latitude")
    lon = st.text_input("Longitude:", key="longitude")

    st.markdown("Ou marque no mapa abaixo:")
    draw_map = folium.Map(location=[-5.2, -39.29], zoom_start=13)
    draw_data = st_folium(draw_map, width=700, height=400, returned_objects=["last_drawn"])

    if st.button("Enviar Denúncia"):
        final_lat = lat
        final_lon = lon

        if draw_data["last_drawn"]:
            coords = draw_data["last_drawn"]["geometry"]["coordinates"]
            final_lon = coords[0]
            final_lat = coords[1]

        if not final_lat or not final_lon or not bairro or not descricao:
            st.warning("Preencha todos os campos obrigatórios e forneça a localização.")
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
