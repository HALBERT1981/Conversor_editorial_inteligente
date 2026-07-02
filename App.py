# -*- coding: utf-8 -*-
"""
app.py — Conversor Editorial Inteligente para EPUB (v2.0)
Interface Streamlit: upload -> detecção de capítulos -> capa -> metadados ->
gerar EPUB -> preview -> validação Kindle (EPUBCheck).
"""
import os
import tempfile
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

from Parser import parse_docx
from Cover import prepare_cover
from Builder import build_epub
from Preview import load_preview
from Validator import validate_epub
from Normalizer import ftfy_available

st.set_page_config(page_title="Conversor Editorial Inteligente para EPUB", page_icon="📚", layout="wide")

if "parsed" not in st.session_state:
    st.session_state.parsed = None
if "docx_path" not in st.session_state:
    st.session_state.docx_path = None
if "epub_path" not in st.session_state:
    st.session_state.epub_path = None
if "cover_bytes" not in st.session_state:
    st.session_state.cover_bytes = None
if "cover_warnings" not in st.session_state:
    st.session_state.cover_warnings = []

WORKDIR = Path(tempfile.gettempdir()) / "epub_studio"
WORKDIR.mkdir(exist_ok=True)

st.title("📚 Conversor Editorial Inteligente para EPUB")
st.caption("DOCX → EPUB com detecção automática de capítulos, capa, preview e validação Kindle.")

if not ftfy_available():
    st.info(
        "Dica: instale `ftfy` (`pip install ftfy`) para correção automática de encoding quebrado "
        "(ex: 'nÃ£o' → 'não'). Sem ele, a normalização de acentos/espaços continua funcionando normalmente."
    )

# ---------------------------------------------------------------------------
# 1. Upload
# ---------------------------------------------------------------------------
st.header("1. Selecione o arquivo")
uploaded_docx = st.file_uploader("Documento Word (.docx)", type=["docx"])

if uploaded_docx is not None:
    docx_path = WORKDIR / uploaded_docx.name
    docx_path.write_bytes(uploaded_docx.getvalue())
    if st.session_state.docx_path != str(docx_path):
        st.session_state.docx_path = str(docx_path)
        with st.spinner("Analisando estrutura do documento..."):
            st.session_state.parsed = parse_docx(str(docx_path))
        st.session_state.epub_path = None  # invalida conversão anterior

parsed = st.session_state.parsed

if parsed:
    n_chapters = len(parsed.chapters)
    n_images = len(parsed.images)
    c1, c2, c3 = st.columns(3)
    c1.metric("Capítulos detectados", n_chapters)
    c2.metric("Imagens encontradas", n_images)
    c3.metric("Heading 1 usado?", "Sim" if parsed.heading1_found else "Não")

    if not parsed.heading1_found:
        st.warning(
            "Nenhum estilo 'Heading 1' (Título 1) foi encontrado no documento. "
            "O livro inteiro foi tratado como um único capítulo. Para dividir em "
            "capítulos, aplique o estilo 'Título 1' aos títulos no Word."
        )

    with st.expander("Ver capítulos detectados"):
        for i, ch in enumerate(parsed.chapters, start=1):
            st.write(f"**{i}. {ch.title}**  —  {len(ch.blocks)} blocos de conteúdo")

    # -----------------------------------------------------------------------
    # 2. Capa
    # -----------------------------------------------------------------------
    st.header("2. Capa")
    cover_mode = st.radio(
        "Origem da capa",
        ["Automática (primeira imagem do DOCX)", "Selecionar arquivo manualmente", "Sem capa"],
        horizontal=True,
    )

    raw_cover_bytes = None
    if cover_mode.startswith("Automática"):
        if parsed.cover_candidate:
            raw_cover_bytes = parsed.cover_candidate.data
            st.image(raw_cover_bytes, width=200, caption="Primeira imagem do documento")
        else:
            st.warning("Nenhuma imagem foi encontrada no DOCX para usar como capa automática.")
    elif cover_mode.startswith("Selecionar"):
        cover_upload = st.file_uploader("Imagem de capa", type=["jpg", "jpeg", "png"], key="cover_upload")
        if cover_upload is not None:
            raw_cover_bytes = cover_upload.getvalue()
            st.image(raw_cover_bytes, width=200, caption="Capa selecionada")

    if raw_cover_bytes:
        processed_bytes, media_type, warnings = prepare_cover(raw_cover_bytes)
        st.session_state.cover_bytes = processed_bytes
        st.session_state.cover_warnings = warnings
        for w in warnings:
            st.warning(w)
    else:
        st.session_state.cover_bytes = None
        st.session_state.cover_warnings = []

    # -----------------------------------------------------------------------
    # 3. Metadados
    # -----------------------------------------------------------------------
    st.header("3. Metadados")
    col1, col2, col3 = st.columns([2, 2, 1])
    docx_path_str = st.session_state.docx_path or "document"
    default_title = parsed.title or Path(docx_path_str).stem
    title = col1.text_input("Título", value=default_title)
    author = col2.text_input("Autor", value=parsed.author)
    language = col3.selectbox("Idioma", ["pt-BR", "pt-PT", "en", "es"], index=0)

    # -----------------------------------------------------------------------
    # 4. Gerar EPUB
    # -----------------------------------------------------------------------
    st.header("4. Gerar EPUB")
    if st.button("⚙️ Converter para EPUB", type="primary"):
        with st.spinner("Normalizando texto e montando o EPUB..."):
            out_path = WORKDIR / f"{Path(st.session_state.docx_path or 'document').stem}.epub"
            build_epub(
                parsed=parsed,
                output_path=str(out_path),
                title=title,
                author=author,
                language=language,
                cover_bytes=st.session_state.cover_bytes,
            )
            st.session_state.epub_path = str(out_path)
        st.success("EPUB gerado com sucesso!")

    epub_path = st.session_state.epub_path
    if epub_path and os.path.exists(epub_path):
        with open(epub_path, "rb") as f:
            st.download_button(
                "⬇️ Baixar EPUB",
                data=f.read(),
                file_name=Path(epub_path).name,
                mime="application/epub+zip",
            )

        tab_preview, tab_validate = st.tabs(["👀 Preview do EPUB", "✅ Validação Kindle (EPUBCheck)"])

        with tab_preview:
            chapters = load_preview(epub_path)
            if chapters:
                titles = [f"{i+1}. {c.title}" for i, c in enumerate(chapters)]
                idx = st.selectbox("Capítulo", range(len(chapters)), format_func=lambda i: titles[i])
                components.html(
                    f"<div style='background:#fdfdfb;padding:2em;border-radius:8px;'>{chapters[idx].html}</div>",
                    height=650,
                    scrolling=True,
                )
            else:
                st.info("Nenhum capítulo encontrado para preview.")

        with tab_validate:
            st.write(
                "Roda o EPUBCheck oficial (via pacote `epubcheck`) para verificar se o arquivo "
                "atende ao padrão EPUB exigido por lojas e leitores como o Kindle."
            )
            if st.button("🔍 Validar EPUB"):
                with st.spinner("Executando EPUBCheck..."):
                    result = validate_epub(epub_path)
                if not result.available:
                    st.error(result.error)
                else:
                    if result.valid:
                        st.success("✅ EPUB válido — nenhum erro fatal encontrado.")
                    else:
                        st.error(
                            f"❌ EPUB com problemas — {result.n_fatal} fatal(is), "
                            f"{result.n_error} erro(s), {result.n_warning} aviso(s)."
                        )
                    if result.messages:
                        st.dataframe(
                            [
                                {
                                    "Nível": m.level,
                                    "ID": m.id,
                                    "Local": m.location,
                                    "Mensagem": m.message,
                                }
                                for m in result.messages
                            ],
                            use_container_width=True,
                        )
else:
    st.info("Envie um arquivo .docx para começar.")