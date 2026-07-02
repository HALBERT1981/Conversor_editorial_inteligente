# -*- coding: utf-8 -*-
"""
normalizer.py
Normalização de texto extraído do DOCX: corrige encoding quebrado (mojibake),
força forma unicode NFC (acentuação consistente) e limpa espaçamento.
"""
import re
import unicodedata

try:
    import ftfy
    _HAS_FTFY = True
except ImportError:
    _HAS_FTFY = False

_MULTI_SPACE = re.compile(r"[ \t]{2,}")
_MULTI_BREAK = re.compile(r"\n{3,}")
NBSP = "\u00a0"


def fix_mojibake(text: str) -> str:
    """Corrige encoding quebrado, ex: 'nÃ£o' -> 'não', 'â€™' -> '’'."""
    if not text:
        return text
    if _HAS_FTFY:
        return ftfy.fix_text(text)
    return text


def normalize_unicode(text: str) -> str:
    """Normaliza para NFC — garante que acentos fiquem em forma composta
    (evita bugs de renderização em leitores de e-book)."""
    return unicodedata.normalize("NFC", text)


def normalize_whitespace(text: str) -> str:
    """Remove espaços não separáveis soltos, espaços duplicados e
    quebras de linha excessivas herdadas do Word."""
    text = text.replace(NBSP, " ")
    text = _MULTI_SPACE.sub(" ", text)
    text = _MULTI_BREAK.sub("\n\n", text)
    return text.strip()


def normalize_text(text: str) -> str:
    """Pipeline completo aplicado a cada bloco de texto antes de virar XHTML."""
    if not text:
        return text
    text = fix_mojibake(text)
    text = normalize_unicode(text)
    text = normalize_whitespace(text)
    return text


def ftfy_available() -> bool:
    return _HAS_FTFY