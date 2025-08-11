
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
from datetime import datetime, timedelta, timezone
import streamlit.components.v1 as components

st.set_page_config(page_title="Denúncias Recebidas", layout="wide")

# Define o fuso horário de Brasília (UTC-3)
fuso_brasilia = timezone(timedelta(hours=-3))
agora = datetime.now(fuso_brasilia)

dias_semana = {
    'Monday': 'Segunda-feira',
    'Tuesday': 'Terça-feira',
    'Wednesday': 'Quarta-feira',
    'Thursday': 'Quinta-feira',
    'Friday': 'Sexta-feira',
    'Saturday': 'Sábado',
    'Sunday': 'Domingo'
}

meses = {
    'January': 'janeiro',
    'February': 'fevereiro',
    'March': 'março',
    'April': 'abril',
    'May': 'maio',
    'June': 'junho',
    'July': 'julho',
    'August': 'agosto',
    'September': 'setembro',
    'October': 'outubro',
    'November': 'novembro',
    'December': 'dezembro'
}

# Formatar data em português
dia_semana = dias_semana[agora.strftime('%A')]
mes = meses[agora.strftime('%B')]
data_hoje = f"{dia_semana}, {agora.day:02d} de {mes} de {agora.year}"

# Cabeçalho customizado com colunas
st.markdown(f"""
    <style>
    [data-testid="stHeader"] {{
        visibility: hidden;
    }}

    .custom-header {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        background-color: #04a5c9;
        color: white;
        padding: 10px 32px;
        font-family: Tahoma, sans-serif;
        border-bottom: 3px solid #fad905;
        z-index: 9999;
    }}

    .header-top {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-weight: bold;
    }}

    .header-title {{
        font-size: 14px;
        
    }}

    .header-location {{
        font-size: 12px;
    }}

    .header-date {{
        margin-top: 4px;
        font-size: 12px;
    }}

    .main .block-container {{
        padding-top: 70px;
        
    }}
    </style>

    <div class="custom-header">
        <div class="header-top">
            <div class="header-title">🔎 Você Fiscaliza | Quixeramobim - Ceará</div>            
        </div>
        <div class="header-date">📅 {data_hoje}</div>
    </div>
""", unsafe_allow_html=True)

#Menu Inicial

st.markdown(f"""
    <style>
    .social-menu-container {{
        position: relative;
        left: 50%;
        right: 50%;
        margin-left: -50vw;
        margin-right: -50vw;
        width: 100vw;
        background-color: #04a5c9;
        color: white;
        padding: 6px 32px;
        font-family: Tahoma, sans-serif;
        font-size: 13px;
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 30px;
        flex-wrap: wrap;
        margin-top: -40px;  /* Espaço para aparecer abaixo da barra fixa */
        border-bottom: 3px solid #b6b8ba;
        z-index: 1;  /* Mais baixo que o header fixo */
    }}

    .social-menu-container a {{
        color: white;
        text-decoration: none;
        transition: color 0.3s ease;
    }}

    .social-menu-container a:hover {{
        color: #fad905;
    }}
    </style>

    <div class="social-menu-container">
        <a href="https://www.instagram.com/seuusuario" target="_blank">📸 Instagran</a>
        <a href="https://www.facebook.com/seuusuario" target="_blank">📘 Facebook</a>
        <a href="https://wa.me/5588999999999" target="_blank">💬 WhatsApp</a>       
    </div>
""", unsafe_allow_html=True)

st.markdown("""
    <div style='
        font-family: Tahoma, sans-serif;
        font-size: 26px;
        font-weight: bold;
        color: #003366;
        padding-bottom: 8px;
        margin-bottom: 20px;
        border-bottom: 3px solid #fad905;
        display: inline-block;
    '>
        📋 Denúncias Recebidas
    </div>
""", unsafe_allow_html=True)

def carregar_dados():
    try:
        url = "https://docs.google.com/spreadsheets/d/1MV2b4e3GNc_rhA32jeMuVNhUQWz6HkP7xrC42VscYIk/export?format=csv"
        df = pd.read_csv(url)
        df = df.dropna(how='all')

        # Limpeza e formatação dos dados
        df.columns = df.columns.str.strip()
        df.rename(columns={"_submission_time": "SubmissionDate"}, inplace=True)
        
        # Converter datas para formato mais legível
        try:
            df["SubmissionDate"] = pd.to_datetime(df["SubmissionDate"]).dt.strftime('%d/%m/%Y %H:%M')
        except:
            pass

        # Tratar coordenadas
        df["Latitude"] = pd.to_numeric(df["Latitude"].astype(str).str.replace(",", "."), errors='coerce')
        df["Longitude"] = pd.to_numeric(df["Longitude"].astype(str).str.replace(",", "."), errors='coerce')

        # Tratar URLs de fotos
        if "Foto_URL" in df.columns:
            df["Foto_URL"] = df["Foto_URL"].astype(str).str.replace(",", ".", regex=False)
            df["Foto_URL"] = df["Foto_URL"].apply(lambda x: x if str(x).startswith(('http://', 'https://')) else None)
            
        return df
    except Exception as e:
        st.error(f"Erro ao carregar os dados: {e}")
        return pd.DataFrame()

# Solução definitiva para o recarregamento
if 'df' not in st.session_state:
    st.session_state.df = carregar_dados()

if st.button("🔄 Recarregar dados"):
    st.session_state.df = carregar_dados()
    st.rerun()  # Usando st.rerun() mais moderno

df = st.session_state.df

if df.empty:
    st.error("❌ Não foi possível carregar os dados ou o arquivo está vazio.")
else:
    # Verificar colunas necessárias
    colunas_necessarias = ["Tipo de Denúncia", "Bairro", "Nome", "Breve relato", "SubmissionDate", "Latitude", "Longitude"]
    colunas_faltantes = [col for col in colunas_necessarias if col not in df.columns]
    
    if colunas_faltantes:
        st.error(f"❌ Colunas faltantes no arquivo: {', '.join(colunas_faltantes)}")
    else:

        # Estilo personalizado dos selectbox
        
        st.markdown("""
            <style>
            div[data-baseweb="select"] > div {
                background-color: #f7dd68;  /* Azul claro */
                border-radius: 6px;
                padding: 3px;
            }
            </style>
        """, unsafe_allow_html=True)            
        
        # Filtros
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

        # Filtra apenas os que devem ser exibidos
        filtered_df = filtered_df[filtered_df["Postar"].astype(str).str.strip().str.lower() == "sim"]

        # Mapa
        st.subheader("🗺️ Mapa das Denúncias")
        valid_coords_df = filtered_df[filtered_df["Latitude"].notna() & filtered_df["Longitude"].notna()]
        
        if not valid_coords_df.empty:
            lat_mean = valid_coords_df["Latitude"].mean()
            lon_mean = valid_coords_df["Longitude"].mean()
            mapa = folium.Map(location=[lat_mean, lon_mean], zoom_start=13)

            folium.TileLayer(
                tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
                attr='Google Satellite',
                name='Google Satélite',
                overlay=False,
                control=True
            ).add_to(mapa)

            folium.TileLayer(
                tiles='https://mt1.google.com/vt/lyrs=r&x={x}&y={y}&z={z}',
                attr='Google Streets',
                name='Google Ruas',
                overlay=False,
                control=True
            ).add_to(mapa)

            folium.TileLayer(
                tiles='https://mt1.google.com/vt/lyrs=p&x={x}&y={y}&z={z}',
                attr='Google Terrain',
                name='Google Terreno',
                overlay=False,
                control=True
            ).add_to(mapa)

            folium.LayerControl().add_to(mapa)

            
            for _, row in valid_coords_df.iterrows():
                if str(row.get("Postar", "")).strip().lower() != "sim":
                  continue  
                lat = row["Latitude"]
                lon = row["Longitude"]
                foto_url = row.get("Foto_URL", "")
                
                # Imagem clicável que abre em nova aba
                imagem_html = ""
                if pd.notna(foto_url) and str(foto_url).startswith(('http://', 'https://')):
                    imagem_html = f'<a href="{foto_url}" target="_blank" rel="noopener noreferrer"><img src="{foto_url}" width="200" style="margin-top:10px;"></a><br>'
                
                popup_info = (
                    "<div style='font-family: Arial, sans-serif; border: 2px solid #2A4D9B; border-radius: 8px; padding: 8px; background-color: #f9f9f9;'>"
                    "<h4 style='margin-top: 0; margin-bottom: 8px; color: #2A4D9B; border-bottom: 1px solid #ccc;'>🚨 Denúncia Registrada</h4>"
                    f"<p style='margin: 4px 0;'><span style='color: #2A4D9B; font-weight: bold;'>📛 Nome:</span> {row.get('Nome', 'Sem nome')}</p>"
                    f"<p style='margin: 4px 0;'><span style='color: #2A4D9B; font-weight: bold;'>📝 Tipo:</span> {row.get('Tipo de Denúncia', 'Não informado')}</p>"
                    f"<p style='margin: 4px 0;'><span style='color: #2A4D9B; font-weight: bold;'>📍 Bairro:</span> {row.get('Bairro', 'Não informado')}</p>"
                    f"<p style='margin: 4px 0;'><span style='color: #2A4D9B; font-weight: bold;'>🧾 Relato:</span> {row.get('Breve relato', 'Não informado')}</p>"
                    f"<p style='margin: 4px 0;'><span style='color: #2A4D9B; font-weight: bold;'>📅 Data:</span> {row.get('SubmissionDate', 'Não informado')}</p>"
                    f"{imagem_html}</div>"
                )
                popup = folium.Popup(popup_info, max_width=300)
                popup = folium.Popup(popup_info, max_width=300)
                folium.Marker(
                    [lat, lon],
                    popup=popup,
                    icon=folium.CustomIcon("https://i.ibb.co/Kp64sjfH/LUPA.png", icon_size=(35, 35))
                ).add_to(mapa)
            
            folium_static(mapa, width=1000)
        else:
            st.warning("⚠️ Nenhuma denúncia com coordenadas válidas para exibir no mapa.")

        # Tabela de denúncias
        st.subheader("📄 Lista de Denúncias Filtradas")
        st.dataframe(
            filtered_df[["Nome", "Bairro", "Tipo de Denúncia", "Breve relato", "SubmissionDate"]],
            use_container_width=True,
            column_config={
                "SubmissionDate": "Data/Hora",
                "Tipo de Denúncia": "Tipo",
                "Breve relato": "Relato"
            }
        )

# Dados de rodapé

st.markdown(
    """
    <style>
    .footer-full-width {
        position: relative;
        left: 50%;
        right: 50%;
        margin-left: -50vw;
        margin-right: -50vw;
        width: 100vw;
        border-top: 2px solid #fad905;
        padding: 16px 0 8px 0;
        font-size: 14px;
        font-family: Tahoma, sans-serif;
        color: #333;
        text-align: center;
        margin-top: 30px;
        margin-bottom: -100px;
        line-height: 1.6;
        background-color: white;
        z-index: 9999;
    }
    .footer-full-width .info-top {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 10px;
        flex-wrap: wrap;
    }
    .footer-full-width .address {
        margin-top: 6px;
        font-size: 13px;
        color: #444;
    }
    </style>

    <div class="footer-full-width">
        <div class="info-top">
            <span>📞 (88) 99999-9999</span>
            <span>|</span>
            <span>📧 vocedenuncia@qvocedenuncia</span>
            <span>|</span>
            <span><b>Plataforma Você Denuncia</b></span>
        </div>
        <div class="address">
            🏢 R. 14 de Agosto, 123 - Centro, Quixeramobim - CE, 63800-000
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


st.markdown(f"""
    <style>
    .custom-footer {{
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background-color: #04a5c9;
        color: white;
        padding: 10px 32px;
        font-family: Tahoma, sans-serif;
        font-size: 12px;
        border-top: 3px solid #fad905;
        text-align: center;
        z-index: 9999;
    }}
    </style>

    <div class="custom-footer">
        🔒 Plataforma Você Fiscaliza | Desenvolvido com transparência e participação popular
    </div>
""", unsafe_allow_html=True)
