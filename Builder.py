# -*- coding: utf-8 -*-
"""
builder.py
Monta o arquivo .epub a partir do ParsedDocument, aplicando normalização de
texto em cada bloco e usando ebooklib para gerar EPUB3 válido (nav, ncx,
spine, capa).
"""
import uuid
from typing import List, Optional, Dict

from ebooklib import epub

try:
    from Parser import ParsedDocument, Chapter, Block, Run
    from Normalizer import normalize_text
except ImportError:  # permite execução direta do arquivo como script
    from .Parser import ParsedDocument, Chapter, Block, Run
    from .Normalizer import normalize_text

EPUB_CSS = """
body { font-family: serif; line-height: 1.5; margin: 1em; }
h1 { font-size: 1.6em; margin-bottom: 0.6em; text-align: center; page-break-before: always; }
h2 { font-size: 1.3em; margin-top: 1.2em; }
h3 { font-size: 1.1em; margin-top: 1em; }
p { margin: 0 0 0.8em 0; text-indent: 1.2em; text-align: justify; }
.image-block { text-align: center; margin: 1em 0; }
.image-block img { max-width: 100%; height: auto; }
"""


def _escape(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _runs_to_html(runs: List[Run]) -> str:
    parts = []
    for r in runs:
        text = normalize_text(r.text)
        if not text:
            continue
        text = _escape(text)
        if r.bold:
            text = f"<strong>{text}</strong>"
        if r.italic:
            text = f"<em>{text}</em>"
        if r.underline:
            text = f"<u>{text}</u>"
        parts.append(text)
    return "".join(parts)


def _chapter_to_xhtml_body(chapter: Chapter, image_href_map: Dict[str, str]) -> str:
    body = [f"<h1>{_escape(normalize_text(chapter.title))}</h1>"]
    list_buffer: List[str] = []
    list_tag: Optional[str] = None

    def flush_list():
        nonlocal list_buffer, list_tag
        if list_buffer:
            tag = "ol" if list_tag == "number" else "ul"
            items = "".join(f"<li>{item}</li>" for item in list_buffer)
            body.append(f"<{tag}>{items}</{tag}>")
            list_buffer = []
            list_tag = None

    for block in chapter.blocks:
        if block.kind == "list_item":
            if list_tag and list_tag != block.list_type:
                flush_list()
            list_tag = block.list_type
            list_buffer.append(_runs_to_html(block.runs))
            continue
        else:
            flush_list()

        if block.kind == "heading2":
            body.append(f"<h2>{_runs_to_html(block.runs)}</h2>")
        elif block.kind == "heading3":
            body.append(f"<h3>{_runs_to_html(block.runs)}</h3>")
        elif block.kind == "paragraph":
            html = _runs_to_html(block.runs)
            if html:
                body.append(f"<p>{html}</p>")
        elif block.kind == "image":
            image_id = block.image_id or ""
            href = image_href_map.get(image_id)
            if href:
                body.append(f'<div class="image-block"><img src="{href}" alt=""/></div>')

    flush_list()
    return "\n".join(body)


def build_epub(
    parsed: ParsedDocument,
    output_path: str,
    title: str,
    author: str,
    language: str = "pt-BR",
    cover_bytes: Optional[bytes] = None,
    identifier: Optional[str] = None,
) -> str:
    book = epub.EpubBook()
    book.set_identifier(identifier or str(uuid.uuid4()))
    book.set_title(title or "Livro sem título")
    book.set_language(language)
    if author:
        book.add_author(author)

    css_item = epub.EpubItem(
        uid="style_default", file_name="style/style.css", media_type="text/css", content=EPUB_CSS
    )
    book.add_item(css_item)

    spine: list = []

    if cover_bytes:
        book.set_cover("cover.jpg", cover_bytes)
        spine.append("cover")

    image_href_map: Dict[str, str] = {}
    for img in parsed.images:
        href = f"images/{img.filename}"
        item = epub.EpubItem(uid=img.id, file_name=href, media_type=img.media_type, content=img.data)
        book.add_item(item)
        image_href_map[img.id] = href

    epub_chapters = []
    for i, chapter in enumerate(parsed.chapters, start=1):
        xhtml_body = _chapter_to_xhtml_body(chapter, image_href_map)
        c = epub.EpubHtml(
            title=normalize_text(chapter.title) or f"Capítulo {i}",
            file_name=f"chap_{i:02d}.xhtml",
            lang=language,
        )
        c.content = (
            "<html xmlns='http://www.w3.org/1999/xhtml'><head>"
            "<link rel='stylesheet' href='style/style.css'/></head>"
            f"<body>{xhtml_body}</body></html>"
        )
        c.add_item(css_item)
        book.add_item(c)
        epub_chapters.append(c)

    book.toc = list(epub_chapters)
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    spine += ["nav"] + epub_chapters
    book.spine = spine

    epub.write_epub(output_path, book, {})
    return output_path