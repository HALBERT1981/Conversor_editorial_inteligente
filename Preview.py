# -*- coding: utf-8 -*-
"""
preview.py
Carrega o conteúdo de capítulos de um EPUB para exibição de preview.
"""
from ebooklib import epub


def load_preview(epub_path: str):
    try:
        book = epub.read_epub(epub_path)
    except Exception:
        return []

    chapters = []
    for item in book.get_items_of_type(epub.EpubHtml):
        title = item.title or item.file_name
        chapters.append(type("PreviewChapter", (), {"title": title, "html": item.content.decode("utf-8", errors="ignore")}))
    return chapters
