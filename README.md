# Kindle Publisher

> Um aplicativo para converter documentos em eBooks EPUB de alta qualidade,
> otimizados para Kindle.

## Visão Geral

Kindle Publisher é uma ferramenta desenvolvida em Python para transformar
documentos Word, Markdown e outros formatos em arquivos EPUB compatíveis com
o ecossistema Kindle.

O objetivo do projeto é automatizar o processo editorial, preservando a
estrutura do documento, gerando índices navegáveis, identificando capas e
aplicando metadados automaticamente.

---

## Funcionalidades

### Conversão

- DOCX → EPUB
- Markdown → EPUB
- HTML → EPUB
- TXT → EPUB (planejado)

### Estrutura

- Reconhecimento de Heading 1, 2 e 3
- Geração automática de índice
- Organização por capítulos
- Preservação de notas de rodapé

### Capa

- Detectar primeira imagem do documento
- Permitir seleção manual de uma capa
- Redimensionamento automático

### Metadados

- Título
- Autor
- Idioma
- Data
- Descrição
- Palavras-chave

### Compatibilidade

- Kindle
- Kobo (planejado)
- Apple Books (planejado)

---

## Interface

O projeto utiliza Streamlit para fornecer uma interface simples e intuitiva.

Fluxo:

1. Selecionar documento
2. Escolher pasta de saída
3. Definir metadados
4. Escolher capa
5. Converter

---

## Tecnologias

- Python 3.12+
- Streamlit
- Pandoc
- pypandoc
- python-docx
- Pillow
- pathlib

---

## Estrutura do Projeto

```
kindle-publisher/
│
├── app/
│   ├── ui.py
│   └── pages/
│
├── core/
│   ├── converter.py
│   ├── parser.py
│   ├── metadata.py
│   ├── cover.py
│   ├── validator.py
│   └── utils.py
│
├── templates/
│
├── tests/
│
├── docs/
│
├── pyproject.toml
│
└── README.md
```

---

## Roadmap

### v0.1

- Conversão DOCX → EPUB

### v0.2

- Seleção de pasta

### v0.3

- Capa automática

### v0.4

- Metadados

### v0.5

- Templates editoriais

### v0.6

- Preview do EPUB

### v1.0

- Conversor completo para Kindle

---

## Roadmap Futuro

- Exportação PDF
- Exportação MOBI
- Exportação AZW3
- Biblioteca pessoal
- Temas editoriais
- Linha de comando (CLI)
- API REST
- Servidor MCP

---

## Objetivo

Transformar a produção de estudos, homilias, artigos e livros em um processo
editorial automatizado, permitindo que autores foquem no conteúdo enquanto o
software cuida da formatação e publicação.

---

## Licença

MIT