import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from streamlit_javascript import st_javascript
import altair as alt

st.set_page_config(page_title="Mapeador de Denúncias", layout="centered")

# Inicializa o DataFrame no estado da sessão
if "denuncias" not in st.session_state:
    st.session_state.denuncias = pd.DataFrame(columns=["tipo", "bairro", "descricao", "latitude", "longitude", "imagem"])

# Menu lateral
aba = st.sidebar.radio("Escolha uma aba:", ["📨 Enviar Denúncia", "📊 Painel de Visualização"])

if aba == "📨 Enviar Denúncia":
    st.title("📝 Enviar Nova Denúncia")

    tipo = st.selectbox("Tipo:", ["Denúncia", "Obra"])
    bairro = st.text_input("Bairro:", key="bairro")
    descricao = st.text_area("Descrição:", key="descricao")
    imagem = st.file_uploader("Foto (opcional):", type=["png", "jpg", "jpeg"])

    st.markdown("### 📍 Capturar Localização Atual")
    coords = st_javascript("await new Promise((resolve) => navigator.geolocation.getCurrentPosition((pos) => resolve({lat: pos.coords.latitude, lon: pos.coords.longitude})))")
    gps_lat = coords.get("lat") if coords else None
    gps_lon = coords.get("lon") if coords else None

    # Coordenadas lado a lado acima do mapa
    st.markdown("### Coordenadas")
    col1, col2 = st.columns(2)
    with col1:
        final_lat = st.text_input("Latitude", value=str(gps_lat) if gps_lat else "", key="latitude")
    with col2:
        final_lon = st.text_input("Longitude", value=str(gps_lon) if gps_lon else "", key="longitude")

    # Mapa
    map_center = [float(final_lat), float(final_lon)] if final_lat and final_lon else [-5.2, -39.29]
    mapa = folium.Map(location=map_center, zoom_start=15 if gps_lat else 13)

    if final_lat and final_lon:
        folium.Marker([float(final_lat), float(final_lon)],
                      tooltip="Localização definida",
                      icon=folium.Icon(color="blue")).add_to(mapa)

    map_data = st_folium(mapa, width=700, height=400)
    click_coords = map_data.get("last_clicked")
    if click_coords:
        final_lat = click_coords["lat"]
        final_lon = click_coords["lng"]

    if st.button("Enviar Denúncia"):
    enviado = True
else:
    enviado = False
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
            st.session_state["bairro"] = ""
            st.session_state["descricao"] = ""
            st.session_state["latitude"] = ""
            st.session_state["longitude"] = ""

elif aba == "📊 Painel de Visualização":
    st.title("📊 Painel de Denúncias")

    df = st.session_state.denuncias.copy()

    if df.empty:
        st.info("Nenhuma denúncia cadastrada ainda.")
    else:
        st.subheader("📍 Mapa das Denúncias")
        mapa = folium.Map(location=[-5.2, -39.29], zoom_start=13)
        for _, row in df.iterrows():
            cor = 'green' if row['tipo'] == 'Obra' else 'red'
            folium.Marker(
                location=[row['latitude'], row['longitude']],
                popup=f"{row['tipo']} em {row['bairro']}:<br>{row['descricao']}",
                icon=folium.Icon(color=cor)
            ).add_to(mapa)
        st_folium(mapa, width=700, height=400)

        st.subheader("📈 Gráficos")
        grafico_tipo = alt.Chart(df).mark_bar().encode(
            x='tipo:N',
            y='count():Q',
            color='tipo:N'
        ).properties(title="Total por Tipo")
        st.altair_chart(grafico_tipo, use_container_width=True)

        grafico_bairro = alt.Chart(df).mark_bar().encode(
            x='bairro:N',
            y='count():Q',
            color='tipo:N'
        ).properties(title="Denúncias por Bairro")
        st.altair_chart(grafico_bairro, use_container_width=True)

        st.subheader("📄 Lista de Denúncias")
        st.dataframe(df.reset_index(drop=True))
