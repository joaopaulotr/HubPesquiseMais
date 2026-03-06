import streamlit as st
import requests
import io

API_BASE = "http://localhost:8000"

st.set_page_config(
    page_title="Pesquise+ Hub",
    page_icon="🔍",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Dark Mode CSS ──────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    /* Fundo geral */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
        background-color: #0e1117 !important;
        color: #e0e0e0 !important;
    }

    /* Sidebar */
    [data-testid="stSidebar"] { background-color: #161b22 !important; }

    /* Cabeçalho / toolbar */
    header[data-testid="stHeader"] { background-color: #0e1117 !important; }

    /* Cards / containers */
    [data-testid="stVerticalBlock"] > div { color: #e0e0e0; }

    /* Títulos */
    h1, h2, h3, h4, h5, h6 { color: #ffffff !important; }

    /* Inputs e select-boxes */
    input, textarea, select,
    [data-testid="stTextInput"] input,
    [data-testid="stTextArea"] textarea {
        background-color: #1c2333 !important;
        color: #e0e0e0 !important;
        border: 1px solid #30363d !important;
        border-radius: 6px !important;
    }

    /* File uploader */
    [data-testid="stFileUploader"] {
        background-color: #161b22 !important;
        border: 1px dashed #30363d !important;
        border-radius: 8px !important;
    }
    [data-testid="stFileUploader"] span,
    [data-testid="stFileUploader"] button,
    [data-testid="stFileUploader"] label { color: #8b949e !important; }

    /* Botões primários */
    [data-testid="stButton"] > button {
        background-color: #238636 !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 0.5rem 1.2rem !important;
        font-weight: 600 !important;
        transition: background-color 0.2s;
    }
    [data-testid="stButton"] > button:hover {
        background-color: #2ea043 !important;
    }

    /* Download buttons */
    [data-testid="stDownloadButton"] > button {
        background-color: #1f6feb !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 0.4rem 1rem !important;
        font-weight: 600 !important;
    }
    [data-testid="stDownloadButton"] > button:hover {
        background-color: #388bfd !important;
    }

    /* Tabs */
    [data-testid="stTabs"] [role="tab"] {
        color: #8b949e !important;
        border-bottom: 2px solid transparent !important;
    }
    [data-testid="stTabs"] [role="tab"][aria-selected="true"] {
        color: #58a6ff !important;
        border-bottom: 2px solid #58a6ff !important;
    }

    /* Caixas de texto de resultado */
    .result-box {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 1rem 1.2rem;
        white-space: pre-wrap;
        font-size: 0.9rem;
        color: #c9d1d9;
        max-height: 340px;
        overflow-y: auto;
        line-height: 1.6;
    }

    /* Badge de idioma */
    .badge {
        display: inline-block;
        background-color: #1f6feb;
        color: #ffffff;
        border-radius: 12px;
        padding: 2px 10px;
        font-size: 0.78rem;
        font-weight: 600;
    }

    /* Divisor */
    hr { border-color: #21262d !important; }

    /* Mensagens de sucesso/erro */
    [data-testid="stAlert"] {
        border-radius: 6px !important;
    }

    /* Logo area */
    .brand-header {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 0.2rem;
    }
    .brand-title {
        font-size: 2rem;
        font-weight: 800;
        color: #58a6ff;
        letter-spacing: -0.5px;
    }
    .brand-subtitle {
        color: #8b949e;
        font-size: 0.95rem;
        margin-top: -0.4rem;
        margin-bottom: 1.5rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="brand-header">
        <span style="font-size:2rem;">🔍</span>
        <span class="brand-title">Pesquise+ Hub</span>
    </div>
    <p class="brand-subtitle">Transcrição de áudio e análise de vídeo com IA</p>
    <hr/>
    """,
    unsafe_allow_html=True,
)

# ── Tabs ───────────────────────────────────────────────────────────────────────
tab_audio, tab_audio_gpt, tab_video = st.tabs(
    ["🎙️ Transcrição de Áudio", "🤖 Transcrição + GPT", "🎬 Descrição de Vídeo"]
)

# ── Helper ─────────────────────────────────────────────────────────────────────
def _result_box(text: str):
    escaped = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    st.markdown(f'<div class="result-box">{escaped}</div>', unsafe_allow_html=True)


def _language_badge(lang: str):
    st.markdown(
        f'<span class="badge">🌐 Idioma detectado: {lang.upper()}</span>',
        unsafe_allow_html=True,
    )
    st.write("")


# ── Tab 1 – Transcrição de Áudio ───────────────────────────────────────────────
with tab_audio:
    st.subheader("Transcrição de Áudio")
    st.caption("Suporta: MP3, WAV, M4A, OGG, FLAC, AAC — até 100 MB")

    audio_file = st.file_uploader(
        "Selecione o arquivo de áudio",
        type=["mp3", "wav", "m4a", "ogg", "flac", "aac"],
        key="audio_uploader",
    )

    if st.button("Transcrever", key="btn_audio", disabled=audio_file is None):
        with st.spinner("Transcrevendo com Whisper…"):
            try:
                response = requests.post(
                    f"{API_BASE}/audio/transcribe",
                    files={"file": (audio_file.name, audio_file.getvalue(), audio_file.type)},
                    timeout=300,
                )
                if response.status_code == 200:
                    data = response.json()
                    st.success("Transcrição concluída!")
                    _language_badge(data.get("language", "?"))
                    st.markdown("**Texto transcrito:**")
                    _result_box(data["text"])
                    st.caption(f"Segmentos: {data.get('segments_count', '—')}")

                    col1, col2 = st.columns(2)
                    with col1:
                        st.download_button(
                            "⬇️ Baixar TXT",
                            data=data["text"],
                            file_name=data["files"]["txt"].split("/")[-1],
                            mime="text/plain",
                        )
                    with col2:
                        srt_resp = requests.get(f"{API_BASE}{data['files']['srt']}", timeout=30)
                        st.download_button(
                            "⬇️ Baixar SRT",
                            data=srt_resp.text,
                            file_name=data["files"]["srt"].split("/")[-1],
                            mime="text/plain",
                        )
                else:
                    detail = response.json().get("detail", response.text)
                    st.error(f"Erro {response.status_code}: {detail}")
            except requests.exceptions.ConnectionError:
                st.error("Não foi possível conectar à API. Verifique se o servidor está rodando em `localhost:8000`.")
            except Exception as e:
                st.error(f"Erro inesperado: {e}")


# ── Tab 2 – Transcrição + Análise GPT ─────────────────────────────────────────
with tab_audio_gpt:
    st.subheader("Transcrição de Áudio + Análise GPT")
    st.caption("Transcreve com Whisper e gera uma análise inteligente via GPT")

    audio_gpt_file = st.file_uploader(
        "Selecione o arquivo de áudio",
        type=["mp3", "wav", "m4a", "ogg", "flac", "aac"],
        key="audio_gpt_uploader",
    )

    if st.button("Transcrever e Analisar", key="btn_audio_gpt", disabled=audio_gpt_file is None):
        with st.spinner("Transcrevendo e analisando com GPT…"):
            try:
                response = requests.post(
                    f"{API_BASE}/audio/transcribe-with-gpt-analyze",
                    files={"file": (audio_gpt_file.name, audio_gpt_file.getvalue(), audio_gpt_file.type)},
                    timeout=300,
                )
                if response.status_code == 200:
                    data = response.json()
                    st.success("Processamento concluído!")
                    _language_badge(data.get("language", "?"))

                    st.markdown("**Análise GPT:**")
                    _result_box(data.get("analysis", ""))

                    with st.expander("Ver transcrição completa"):
                        _result_box(data["text"])

                    col1, col2 = st.columns(2)
                    with col1:
                        st.download_button(
                            "⬇️ Baixar TXT",
                            data=data["text"],
                            file_name=data["files"]["txt"].split("/")[-1],
                            mime="text/plain",
                        )
                    with col2:
                        srt_resp = requests.get(f"{API_BASE}{data['files']['srt']}", timeout=30)
                        st.download_button(
                            "⬇️ Baixar SRT",
                            data=srt_resp.text,
                            file_name=data["files"]["srt"].split("/")[-1],
                            mime="text/plain",
                        )
                else:
                    detail = response.json().get("detail", response.text)
                    st.error(f"Erro {response.status_code}: {detail}")
            except requests.exceptions.ConnectionError:
                st.error("Não foi possível conectar à API. Verifique se o servidor está rodando em `localhost:8000`.")
            except Exception as e:
                st.error(f"Erro inesperado: {e}")


# ── Tab 3 – Descrição de Vídeo ─────────────────────────────────────────────────
with tab_video:
    st.subheader("Descrição de Vídeo com IA")
    st.caption("Extrai áudio + frames e gera uma descrição completa via GPT-4 Vision")

    video_file = st.file_uploader(
        "Selecione o arquivo de vídeo",
        type=["mp4", "avi", "mov", "mkv", "webm", "flv"],
        key="video_uploader",
    )

    if st.button("Analisar Vídeo", key="btn_video", disabled=video_file is None):
        with st.spinner("Analisando vídeo (pode levar alguns instantes)…"):
            try:
                response = requests.post(
                    f"{API_BASE}/video/description",
                    files={"file": (video_file.name, video_file.getvalue(), video_file.type)},
                    timeout=600,
                )
                if response.status_code == 200:
                    data = response.json()
                    st.success("Análise concluída!")
                    _language_badge(data.get("language", "?"))
                    st.caption(f"Frames analisados: {data.get('frames_analyzed', '—')}")

                    st.markdown("**Descrição do vídeo:**")
                    _result_box(data.get("description", ""))

                    with st.expander("Ver transcrição completa do áudio"):
                        _result_box(data.get("transcription", ""))

                    desc_resp = requests.get(f"{API_BASE}{data['file']}", timeout=30)
                    st.download_button(
                        "⬇️ Baixar descrição completa (TXT)",
                        data=desc_resp.text,
                        file_name=data["file"].split("/")[-1],
                        mime="text/plain",
                    )
                else:
                    detail = response.json().get("detail", response.text)
                    st.error(f"Erro {response.status_code}: {detail}")
            except requests.exceptions.ConnectionError:
                st.error("Não foi possível conectar à API. Verifique se o servidor está rodando em `localhost:8000`.")
            except Exception as e:
                st.error(f"Erro inesperado: {e}")

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("<hr/>", unsafe_allow_html=True)
st.markdown(
    '<p style="text-align:center; color:#484f58; font-size:0.8rem;">Pesquise+ Hub · Powered by Whisper & GPT-4 Vision</p>',
    unsafe_allow_html=True,
)
