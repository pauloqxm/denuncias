import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from streamlit_javascript import st_javascript
import altair as alt
import os
import numpy as np

st.set_page_config(page_title="Mapeador de Denúncias", layout="centered")

# Initialize session state for complaints
if "denuncias" not in st.session_state:
    if os.path.exists("denuncias.csv"):
        st.session_state.denuncias = pd.read_csv("denuncias.csv")
    else:
        st.session_state.denuncias = pd.DataFrame(columns=["tipo", "bairro", "descricao", "latitude", "longitude", "imagem"])

# Sidebar menu
aba = st.sidebar.radio("Escolha uma aba:", ["📨 Enviar Denúncia", "📊 Painel de Visualização"])

# Clear form fields if needed
if st.session_state.get("limpar"):
    st.session_state["bairro"] = ""
    st.session_state["descricao"] = ""
    st.session_state["latitude"] = ""
    st.session_state["longitude"] = ""
    del st.session_state["limpar"]

if aba == "📨 Enviar Denúncia":
    st.title("📝 Enviar Nova Denúncia")

    # Form fields
    tipo = st.selectbox("Tipo:", ["Denúncia", "Obra"])
    bairro = st.text_input("Bairro:", key="bairro")
    descricao = st.text_area("Descrição:", key="descricao")
    imagem = st.file_uploader("Foto (opcional):", type=["png", "jpg", "jpeg"])

    # Get current location
    st.markdown("### 📍 Capturar Localização Atual")
    coords = st_javascript("await new Promise((resolve) => navigator.geolocation.getCurrentPosition((pos) => resolve({lat: pos.coords.latitude, lon: pos.coords.longitude})))")
    gps_lat = coords.get("lat") if coords else None
    gps_lon = coords.get("lon") if coords else None

    # Coordinates input
    st.markdown("### Coordenadas")
    col1, col2 = st.columns(2)
    with col1:
        final_lat = st.text_input("Latitude", value=str(gps_lat) if gps_lat else "", key="latitude")
    with col2:
        final_lon = st.text_input("Longitude", value=str(gps_lon) if gps_lon else "", key="longitude")

    # Interactive map
    map_center = [float(final_lat), float(final_lon)] if final_lat and final_lon else [-5.2, -39.29]
    mapa = folium.Map(location=map_center, zoom_start=15 if gps_lat else 13)

    if final_lat and final_lon:
        folium.Marker([float(final_lat), float(final_lon)],
                      tooltip="Localização definida",
                      icon=folium.Icon(color="blue")).add_to(mapa)

    map_data = st_folium(mapa, width=700, height=400)
    click_coords = map_data.get("last_clicked")
    if click_coords:
        st.session_state.latitude = str(click_coords["lat"])
        st.session_state.longitude = str(click_coords["lng"])
        final_lat = click_coords["lat"]
        final_lon = click_coords["lng"]

    # Submit button logic
    if st.button("Enviar Denúncia"):
        if not final_lat or not final_lon or not bairro or not descricao:
            st.warning("Preencha todos os campos obrigatórios e defina a localização.")
        else:
            imagem_path = ""
            if imagem is not None:
                try:
                    pasta = "imagens"
                    os.makedirs(pasta, exist_ok=True)
                    # Create unique filename to avoid overwrites
                    timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"{timestamp}_{imagem.name}"
                    caminho_arquivo = os.path.join(pasta, filename)
                    
                    with open(caminho_arquivo, "wb") as f:
                        f.write(imagem.getbuffer())
                    imagem_path = filename
                    st.success(f"Imagem salva como: {filename}")
                except Exception as e:
                    st.error(f"Erro ao salvar imagem: {str(e)}")
                    imagem_path = ""
            
            # Create new complaint record
            nova = {
                "tipo": tipo,
                "bairro": bairro,
                "descricao": descricao,
                "latitude": float(final_lat),
                "longitude": float(final_lon),
                "imagem": imagem_path
            }
            
            # Update data and save to CSV
            st.session_state.denuncias = pd.concat(
                [st.session_state.denuncias, pd.DataFrame([nova])],
                ignore_index=True
            )
            st.session_state.denuncias.to_csv("denuncias.csv", index=False)
            
            # Show success and clear form
            st.success("Denúncia enviada com sucesso!")
            st.balloons()
            st.session_state["limpar"] = True

elif aba == "📊 Painel de Visualização":
    st.title("📊 Painel de Denúncias")

    df = st.session_state.denuncias.copy()

    if df.empty:
        st.info("Nenhuma denúncia cadastrada ainda.")
    else:
        # Map visualization
        st.subheader("📍 Mapa das Denúncias")
        mapa = folium.Map(location=[-5.2, -39.29], zoom_start=13)
        for _, row in df.iterrows():
            imagem_html = ""
            # Verificação mais segura do caminho da imagem
            if pd.notna(row["imagem"]) and isinstance(row["imagem"], str) and row["imagem"].strip():
                try:
                    image_path = os.path.join("imagens", row["imagem"].strip())
                    if os.path.exists(image_path):
                        imagem_html = f'<img src="{image_path}" width="200">'
                    else:
                        st.warning(f"Arquivo de imagem não encontrado: {image_path}")
                except (TypeError, AttributeError) as e:
                    st.warning(f"Erro ao processar caminho da imagem: {e}")
            
            popup_html = f"""
                <b>{row['tipo']} em {row['bairro']}</b><br>
                {row['descricao']}<br>
                {imagem_html}
            """
            folium.Marker(
                location=[row['latitude'], row['longitude']],
                popup=folium.Popup(popup_html, max_width=300),
                icon=folium.Icon(color='green' if row['tipo'] == 'Obra' else 'red')
            ).add_to(mapa)
        st_folium(mapa, width=700, height=400)

        # Charts
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

        # Data table
        st.subheader("📄 Lista de Denúncias")
        st.dataframe(df.reset_index(drop=True))
