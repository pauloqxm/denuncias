import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd

# Página e estilo
st.set_page_config(page_title="Mapeador de Obras", layout="centered")

# Simula um banco de dados
if "denuncias" not in st.session_state:
    st.session_state.denuncias = pd.DataFrame(columns=["tipo", "bairro", "descricao", "latitude", "longitude", "imagem"])

# Função para criar mapa com marcadores
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

# Aba de navegação
aba = st.sidebar.radio("Escolha a aba:", ["📍 Ver Mapa", "📝 Enviar Denúncia"])

# Aba do Mapa
if aba == "📍 Ver Mapa":
    st.title("🗺️ Mapeador de Obras e Denúncias por Bairro")
    st.markdown("Visualize no mapa as obras e denúncias cadastradas por região.")

    data = st.session_state.denuncias.copy()
    bairros = ['Todos'] + sorted(data['bairro'].unique().tolist())
    bairro_escolhido = st.selectbox("Filtrar por bairro:", bairros)

    dados_filtrados = data if bairro_escolhido == 'Todos' else data[data['bairro'] == bairro_escolhido]
    mapa = gerar_mapa(dados_filtrados)
    st_data = st_folium(mapa, width=700, height=500)

# Aba do formulário
else:
    st.title("📝 Enviar Nova Denúncia")
    st.markdown("Marque o local no mapa, escreva a denúncia e envie uma foto se quiser.")

    tipo = st.selectbox("Tipo:", ["Denúncia", "Obra"])
    bairro = st.text_input("Bairro:")
    descricao = st.text_area("Descrição:")
    imagem = st.file_uploader("Foto (opcional):", type=["png", "jpg", "jpeg"])

    st.markdown("📍 Marque no mapa o local da ocorrência:")
    draw_map = folium.Map(location=[-5.2, -39.29], zoom_start=13)
    draw_data = st_folium(draw_map, width=700, height=400, returned_objects=["last_drawn"])

    if st.button("Enviar Denúncia"):
        if not draw_data["last_drawn"]:
            st.warning("Por favor, marque a localização no mapa.")
        elif not bairro or not descricao:
            st.warning("Preencha todos os campos obrigatórios.")
        else:
            coords = draw_data["last_drawn"]["geometry"]["coordinates"]
            nova = {
                "tipo": tipo,
                "bairro": bairro,
                "descricao": descricao,
                "latitude": coords[1],
                "longitude": coords[0],
                "imagem": imagem.name if imagem else ""
            }
            st.session_state.denuncias = pd.concat([st.session_state.denuncias, pd.DataFrame([nova])], ignore_index=True)
            st.success("Denúncia enviada com sucesso!")
