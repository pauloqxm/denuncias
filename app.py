import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from datetime import datetime, timedelta, timezone

st.set_page_config(page_title="Denúncias Recebidas", layout="wide", initial_sidebar_state="collapsed")

# ---------------------- DATA E FUSO ----------------------
fuso_brasilia = timezone(timedelta(hours=-3))
agora = datetime.now(fuso_brasilia)

dias_semana = {
    'Monday': 'Segunda-feira', 'Tuesday': 'Terça-feira', 'Wednesday': 'Quarta-feira',
    'Thursday': 'Quinta-feira', 'Friday': 'Sexta-feira', 'Saturday': 'Sábado', 'Sunday': 'Domingo'
}
meses = {
    'January': 'janeiro', 'February': 'fevereiro', 'March': 'março', 'April': 'abril',
    'May': 'maio', 'June': 'junho', 'July': 'julho', 'August': 'agosto',
    'September': 'setembro', 'October': 'outubro', 'November': 'novembro', 'December': 'dezembro'
}
dia_semana = dias_semana[agora.strftime('%A')]
mes = meses[agora.strftime('%B')]
data_hoje = f"{dia_semana}, {agora.day:02d} de {mes} de {agora.year}"

# ---------------------- ESTILOS RESPONSIVOS ----------------------
st.markdown(f"""
    <style>
    /* Esconde header padrão do Streamlit */
    [data-testid="stHeader"] {{ visibility: hidden; }}

    /* Container principal: dá espaço pro header/rodapé fixos */
    .main .block-container {{
        padding-top: 90px;  /* espaço para o header fixo */
        padding-bottom: 70px; /* espaço para o rodapé fixo */
    }}

    /* HEADER FIXO */
    .custom-header {{
        position: fixed; top: 0; left: 0; width: 100%;
        background-color: #04a5c9; color: #fff;
        padding: 10px 20px;
        font-family: Tahoma, sans-serif;
        border-bottom: 3px solid #fad905;
        z-index: 9999;
    }}
    .header-top {{ display: flex; justify-content: space-between; align-items: center; font-weight: bold; }}
    .header-title {{ font-size: 16px; }}
    .header-date {{ margin-top: 4px; font-size: 12px; opacity: .95; }}

    /* MENU FAIXA */
    .social-menu-container {{
        position: relative;
        left: 50%; right: 50%;
        margin-left: -50vw; margin-right: -50vw; width: 100vw;
        background-color: #04a5c9; color: #fff;
        padding: 8px 16px;
        font-family: Tahoma, sans-serif;
        font-size: 13px;
        display: flex; justify-content: center; align-items: center;
        gap: 24px; flex-wrap: wrap;
        margin-top: -32px;  /* aparece logo abaixo do header */
        border-bottom: 3px solid #b6b8ba;
        z-index: 1;
    }}
    .social-menu-container a {{ color: #fff; text-decoration: none; transition: color 0.2s ease; }}
    .social-menu-container a:hover {{ color: #fad905; }}

    /* TÍTULO SEÇÃO */
    .page-title {{
        font-family: Tahoma, sans-serif;
        font-size: 26px; font-weight: bold; color: #003366;
        padding-bottom: 8px; margin-bottom: 16px;
        border-bottom: 3px solid #fad905; display: inline-block;
    }}

    /* SELECTS: pinta fundo */
    div[data-baseweb="select"] > div {{
        background-color: #f7dd68;
        border-radius: 6px; padding: 3px;
    }}

    /* MAPA: garante 100% largura no container */
    .folium-map, .stMarkdown iframe, iframe[title="folium"] {{
        width: 100% !important;
        max-width: 100% !important;
        border: none;
    }}

    /* RODAPÉ FAIXA FIXO */
    .custom-footer {{
        position: fixed; bottom: 0; left: 0; width: 100%;
        background-color: #04a5c9; color: white;
        padding: 10px 16px; font-family: Tahoma, sans-serif;
        font-size: 12px; border-top: 3px solid #fad905;
        text-align: center; z-index: 9999;
    }}

    /* TABELA: deixa mais compacta no mobile */
    @media (max-width: 768px) {{
        .header-title {{ font-size: 14px; }}
        .header-date {{ font-size: 11px; }}
        .social-menu-container {{ gap: 12px; font-size: 12px; padding: 6px 10px; }}
        .page-title {{ font-size: 22px; }}
        .main .block-container {{ padding-top: 78px; padding-bottom: 64px; }}
        /* Força colunas do Streamlit a empilharem */
        .block-container div[data-testid="column"] {{
            width: 100% !important; flex: 1 1 100% !important;
        }}
        /* Altura menor pro mapa em telas estreitas */
        iframe[title="folium"] {{ height: 420px !important; }}
    }}

    /* Desktop / tablets: mapa mais alto */
    @media (min-width: 769px) {{
        iframe[title="folium"] {{ height: 600px !important; }}
    }}
    </style>

    <div class="custom-header">
        <div class="header-top">
            <div class="header-title">🔎 Você Fiscaliza | Quixeramobim - Ceará</div>
        </div>
        <div class="header-date">📅 {data_hoje}</div>
    </div>
""", unsafe_allow_html=True)

# ---------------------- MENU SUPERIOR ----------------------
st.markdown("""
    <div class="social-menu-container">
        <a href="https://www.instagram.com/seuusuario" target="_blank" rel="noopener">📸 Instagram</a>
        <a href="https://www.facebook.com/seuusuario" target="_blank" rel="noopener">📘 Facebook</a>
        <a href="https://wa.me/5588999999999" target="_blank" rel="noopener">💬 WhatsApp</a>
    </div>
""", unsafe_allow_html=True)

# ---------------------- TÍTULO ----------------------
st.markdown("<div class='page-title'>📋 Denúncias Recebidas</div>", unsafe_allow_html=True)

# ---------------------- DADOS ----------------------
@st.cache_data(ttl=300)
def carregar_dados():
    try:
        url = "https://docs.google.com/spreadsheets/d/1MV2b4e3GNc_rhA32jeMuVNhUQWz6HkP7xrC42VscYIk/export?format=csv"
        df = pd.read_csv(url).dropna(how='all')
        df.columns = df.columns.str.strip()
        df.rename(columns={"_submission_time": "SubmissionDate"}, inplace=True)

        # Datas
        with pd.option_context('mode.chained_assignment', None):
            try:
                df["SubmissionDate"] = pd.to_datetime(df["SubmissionDate"]).dt.strftime('%d/%m/%Y %H:%M')
            except Exception:
                pass

            # Coordenadas
            df["Latitude"]  = pd.to_numeric(df["Latitude"].astype(str).str.replace(",", "."), errors='coerce')
            df["Longitude"] = pd.to_numeric(df["Longitude"].astype(str).str.replace(",", "."), errors='coerce')

            # Foto
            if "Foto_URL" in df.columns:
                df["Foto_URL"] = df["Foto_URL"].astype(str).str.replace(",", ".", regex=False)
                df["Foto_URL"] = df["Foto_URL"].apply(lambda x: x if str(x).startswith(('http://', 'https://')) else None)

        return df
    except Exception as e:
        st.error(f"Erro ao carregar os dados: {e}")
        return pd.DataFrame()

if 'df' not in st.session_state:
    st.session_state.df = carregar_dados()

if st.button("🔄 Recarregar dados"):
    st.session_state.df = carregar_dados()
    st.rerun()

df = st.session_state.df

if df.empty:
    st.error("❌ Não foi possível carregar os dados ou o arquivo está vazio.")
else:
    colunas_necessarias = ["Tipo de Denúncia", "Bairro", "Nome", "Breve relato", "SubmissionDate", "Latitude", "Longitude"]
    faltantes = [c for c in colunas_necessarias if c not in df.columns]
    if faltantes:
        st.error(f"❌ Colunas faltantes no arquivo: {', '.join(faltantes)}")
    else:
        # ---------------------- FILTROS (empilham no mobile via CSS) ----------------------
        st.markdown("### 🔎 Filtros")
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

        # Apenas os que devem ser exibidos
        if "Postar" in filtered_df.columns:
            filtered_df = filtered_df[filtered_df["Postar"].astype(str).str.strip().str.lower() == "sim"]

        # ---------------------- MAPA (100% largura) ----------------------
        st.subheader("🗺️ Mapa das Denúncias")
        valid_coords_df = filtered_df[filtered_df["Latitude"].notna() & filtered_df["Longitude"].notna()]

        if not valid_coords_df.empty:
            lat_mean = valid_coords_df["Latitude"].mean()
            lon_mean = valid_coords_df["Longitude"].mean()

            mapa = folium.Map(location=[lat_mean, lon_mean], zoom_start=13, control_scale=True, width="100%", height="100%")

            folium.TileLayer(
                tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
                attr='Google Satellite', name='Google Satélite', overlay=False, control=True
            ).add_to(mapa)
            folium.TileLayer(
                tiles='https://mt1.google.com/vt/lyrs=r&x={x}&y={y}&z={z}',
                attr='Google Streets', name='Google Ruas', overlay=False, control=True
            ).add_to(mapa)
            folium.TileLayer(
                tiles='https://mt1.google.com/vt/lyrs=p&x={x}&y={y}&z={z}',
                attr='Google Terrain', name='Google Terreno', overlay=False, control=True
            ).add_to(mapa)
            folium.LayerControl().add_to(mapa)

            for _, row in valid_coords_df.iterrows():
                if str(row.get("Postar", "sim")).strip().lower() != "sim":
                    continue
                lat = row["Latitude"]; lon = row["Longitude"]; foto_url = row.get("Foto_URL", "")

                imagem_html = ""
                if pd.notna(foto_url) and str(foto_url).startswith(('http://', 'https://')):
                    imagem_html = f'<a href="{foto_url}" target="_blank" rel="noopener noreferrer"><img src="{foto_url}" width="200" style="margin-top:10px;max-width:100%;height:auto;"></a><br>'

                popup_info = (
                    "<div style='font-family: Arial, sans-serif; border: 2px solid #2A4D9B; border-radius: 8px; padding: 8px; background-color: #f9f9f9; max-width: 260px;'>"
                    "<h4 style='margin: 0 0 8px 0; color: #2A4D9B; border-bottom: 1px solid #ccc; padding-bottom: 6px;'>🚨 Denúncia Registrada</h4>"
                    f"<p style='margin: 4px 0;'><b>📛 Nome:</b> {row.get('Nome', 'Sem nome')}</p>"
                    f"<p style='margin: 4px 0;'><b>📝 Tipo:</b> {row.get('Tipo de Denúncia', 'Não informado')}</p>"
                    f"<p style='margin: 4px 0;'><b>📍 Bairro:</b> {row.get('Bairro', 'Não informado')}</p>"
                    f"<p style='margin: 4px 0;'><b>🧾 Relato:</b> {row.get('Breve relato', 'Não informado')}</p>"
                    f"<p style='margin: 4px 0;'><b>📅 Data:</b> {row.get('SubmissionDate', 'Não informado')}</p>"
                    f"{imagem_html}</div>"
                )
                popup = folium.Popup(popup_info, max_width=300)
                folium.Marker(
                    [lat, lon],
                    popup=popup,
                    icon=folium.CustomIcon("https://i.ibb.co/Kp64sjfH/LUPA.png", icon_size=(35, 35))
                ).add_to(mapa)

            # st_folium respeita nosso CSS para 100% e media query para altura
            st_folium(mapa, returned_objects=[], feature_group_to_add=None)
        else:
            st.warning("⚠️ Nenhuma denúncia com coordenadas válidas para exibir no mapa.")

        # ---------------------- TABELA ----------------------
        st.subheader("📄 Lista de Denúncias Filtradas")
        vis_cols = [c for c in ["Nome", "Bairro", "Tipo de Denúncia", "Breve relato", "SubmissionDate"] if c in filtered_df.columns]
        st.dataframe(
            filtered_df[vis_cols],
            use_container_width=True,
            column_config={
                "SubmissionDate": "Data/Hora",
                "Tipo de Denúncia": "Tipo",
                "Breve relato": "Relato"
            },
            hide_index=True
        )

# ---------------------- RODAPÉ AMPLO (INFORMAÇÕES) ----------------------
st.markdown(
    """
    <style>
    .footer-full-width {
        position: relative;
        left: 50%; right: 50%;
        margin-left: -50vw; margin-right: -50vw; width: 100vw;
        border-top: 2px solid #fad905;
        padding: 14px 0 8px 0; font-size: 14px;
        font-family: Tahoma, sans-serif; color: #333; text-align: center;
        margin-top: 24px; background-color: white; z-index: 1;
        line-height: 1.6;
    }
    .footer-full-width .info-top { display: flex; justify-content: center; align-items: center; gap: 10px; flex-wrap: wrap; }
    .footer-full-width .address { margin-top: 6px; font-size: 13px; color: #444; }
    @media (max-width: 768px) {
        .footer-full-width { font-size: 13px; }
        .footer-full-width .address { font-size: 12px; }
    }
    </style>

    <div class="footer-full-width">
        <div class="info-top">
            <span>📞 (88) 99999-9999</span><span>|</span>
            <span>📧 vocedenuncia@qvocedenuncia</span><span>|</span>
            <span><b>Plataforma Você Denuncia</b></span>
        </div>
        <div class="address">
            🏢 R. 14 de Agosto, 123 - Centro, Quixeramobim - CE, 63800-000
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# ---------------------- RODAPÉ FIXO (SELINHO) ----------------------
st.markdown("""
    <div class="custom-footer">
        🔒 Plataforma Você Fiscaliza | Desenvolvido com transparência e participação popular
    </div>
""", unsafe_allow_html=True)
