import streamlit as st
import re
import zipfile
import io
from pathlib import Path

st.set_page_config(page_title="Renomeador de Relatórios", page_icon="📂", layout="centered")

st.markdown("""
<style>
    .stApp { background-color: #f5f7f7; }
    [data-testid="stSidebar"] { background-color: #1b5d5d; }

    h1 {
        color: #1b5d5d !important;
        border-bottom: 3px solid #ff5400;
        padding-bottom: 0.3rem;
    }
    h2, h3 { color: #1b5d5d !important; }

    .stButton > button[kind="primary"] {
        background-color: #ff5400 !important;
        border: none !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        border-radius: 6px !important;
        transition: opacity 0.2s;
    }
    .stButton > button[kind="primary"]:hover { opacity: 0.88 !important; }

    [data-testid="stFileUploader"] {
        border: 2px dashed #3ca4a6 !important;
        border-radius: 8px !important;
        background: #eaf4f4 !important;
    }

    .stInfo { border-left: 4px solid #3ca4a6 !important; }

    [data-testid="stDataFrame"] th {
        background-color: #1b5d5d !important;
        color: #ffffff !important;
    }

    hr { border-color: #bfbfbf !important; }

    .streamlit-expanderHeader {
        color: #1b5d5d !important;
        font-weight: 600 !important;
    }

    [data-testid="stDownloadButton"] > button {
        background-color: #1b5d5d !important;
        color: #ffffff !important;
        border: none !important;
        font-weight: 600 !important;
        border-radius: 6px !important;
        width: 100%;
        padding: 0.6rem 1rem !important;
        font-size: 1rem !important;
    }
    [data-testid="stDownloadButton"] > button:hover { background-color: #154848 !important; }
</style>
""", unsafe_allow_html=True)

# ── Mapeamento fixo DE → PARA ─────────────────────────────────────────────────
DEPARA = {
    "rel15min-sat1":  "SAT1 km29+730 SP075",
    "rel15min-sat2":  "SAT2 km31+280 SP075",
    "rel15min-sat3":  "SAT3 km38+200 SP075",
    "rel15min-sat4":  "SAT4 km42+100 SP075",
    "rel15min-sat5":  "SAT5 km52+290 SP075",
    "rel15min-sat6":  "SAT6 km60+010 SP075",
    "rel15min-sat7":  "SAT7 km67+590 SP075",
    "rel15min-sat8":  "SAT8 km76+110 SP075",
    "rel15min-sat9":  "SAT9 km18+200 SP127",
    "rel15min-sat10": "SAT10 km43+360 SP127",
    "rel15min-sat11": "SAT11 km70+800 SP127",
    "rel15min-sat12": "SAT12 km83+650 SP127",
    "rel15min-sat13": "SAT13 km93+350 SP127",
    "rel15min-sat14": "SAT14 km89+760 SP280",
    "rel15min-sat15": "SAT15 km109+550 SP280",
    "rel15min-sat16": "SAT16 km114+780 SP280",
    "rel15min-sat17": "SAT17 km121+970 SP280",
    "rel15min-sat18": "SAT18 km65+680 SP300",
    "rel15min-sat19": "SAT19 km83+990 SP300",
    "rel15min-sat20": "SAT20 km112+520 SP300",
    "rel15min-sat21": "SAT21 km128+500 SP300",
    "rel15min-sat22": "SAT22 km139+310 SP300",
    "rel15min-sat23": "SAT23 km1+170 SPI102300",
}

def resolver_nome(nome_arquivo: str) -> str | None:
    """Retorna o novo nome (sem extensão) ou None se não encontrado."""
    stem = Path(nome_arquivo).stem
    # Remove o trecho do mês/ano: -Abril-26, -Janeiro-25, etc.
    chave = re.sub(r"-[^-]+-\d{2}$", "", stem, flags=re.IGNORECASE).lower()
    return DEPARA.get(chave)


# ── Interface ─────────────────────────────────────────────────────────────────
st.title("📂 Renomeador de Relatórios")
st.markdown("Faça upload dos 23 relatórios extraídos do sistema e baixe o `.zip` com os nomes corretos.")

arquivos_upload = st.file_uploader(
    "Selecione os arquivos",
    accept_multiple_files=True,
    key="relatorios",
)

if arquivos_upload:
    st.header("Prévia das renomeações")

    import pandas as pd
    preview_rows = []
    for arq in sorted(arquivos_upload, key=lambda f: f.name):
        suffix = Path(arq.name).suffix
        novo_nome = resolver_nome(arq.name)
        if novo_nome:
            preview_rows.append({
                "Arquivo original": arq.name,
                "Novo nome": novo_nome + suffix,
                "Status": "✅ Renomeado",
            })
        else:
            preview_rows.append({
                "Arquivo original": arq.name,
                "Novo nome": "—",
                "Status": "⚠️ Não reconhecido",
            })

    df_prev = pd.DataFrame(preview_rows)
    st.dataframe(df_prev, use_container_width=True)

    total_ok = sum(1 for r in preview_rows if "Renomeado" in r["Status"])
    st.info(f"**{total_ok}** de **{len(arquivos_upload)}** arquivo(s) reconhecidos e renomeados.")

    if total_ok > 0:
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            for arq in arquivos_upload:
                suffix = Path(arq.name).suffix
                novo_nome = resolver_nome(arq.name)
                nome_final = (novo_nome + suffix) if novo_nome else arq.name
                zf.writestr(nome_final, arq.read())
        zip_buffer.seek(0)

        st.download_button(
            label="⬇️ Baixar arquivos renomeados (.zip)",
            data=zip_buffer,
            file_name="relatorios_renomeados.zip",
            mime="application/zip",
            type="primary",
        )