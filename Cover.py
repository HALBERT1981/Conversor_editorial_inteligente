# -*- coding: utf-8 -*-
"""
cover.py
Prepara a imagem de capa (automática ou enviada manualmente) para o EPUB:
converte para JPEG RGB e avisa se a resolução/proporção foge do recomendado
pela Amazon/Kindle para capas.
"""
import io
from typing import List, Tuple

from PIL import Image

# Recomendação Amazon KDP: proporção ~1:1.6, mínimo 1000px no lado menor,
# idealmente 1600x2560px.
RECOMMENDED_MIN_WIDTH = 1000
RECOMMENDED_MIN_HEIGHT = 1600
RECOMMENDED_RATIO_RANGE = (1.4, 1.8)


def prepare_cover(image_bytes: bytes) -> Tuple[bytes, str, List[str]]:
    """Converte a imagem para JPEG e retorna (bytes, media_type, avisos)."""
    warnings: List[str] = []
    img = Image.open(io.BytesIO(image_bytes))
    img = img.convert("RGB")
    width, height = img.size

    if width < RECOMMENDED_MIN_WIDTH or height < RECOMMENDED_MIN_HEIGHT:
        warnings.append(
            f"Resolução baixa para Kindle ({width}x{height}px). "
            f"Recomendado: pelo menos {RECOMMENDED_MIN_WIDTH}x{RECOMMENDED_MIN_HEIGHT}px."
        )

    ratio = (height / width) if width else 0
    if ratio and not (RECOMMENDED_RATIO_RANGE[0] <= ratio <= RECOMMENDED_RATIO_RANGE[1]):
        warnings.append(
            f"Proporção fora do padrão recomendado (~1:1.6). Proporção atual: 1:{ratio:.2f}."
        )

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=92)
    return buf.getvalue(), "image/jpeg", warnings