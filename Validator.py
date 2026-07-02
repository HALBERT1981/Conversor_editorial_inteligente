# -*- coding: utf-8 -*-
"""
validator.py
Valida o EPUB gerado usando o EPUBCheck oficial (via pacote Python
'epubcheck', que já embute o .jar — só precisa de Java instalado no sistema).
"""
from dataclasses import dataclass, field
from typing import List


@dataclass
class ValidationMessage:
    id: str
    level: str
    location: str
    message: str
    suggestion: str = ""


@dataclass
class ValidationResult:
    available: bool
    valid: bool = False
    messages: List[ValidationMessage] = field(default_factory=list)
    error: str = ""
    n_fatal: int = 0
    n_error: int = 0
    n_warning: int = 0


def validate_epub(epub_path: str) -> ValidationResult:
    try:
        from epubcheck import EpubCheck
    except ImportError:
        return ValidationResult(
            available=False,
            error=(
                "Pacote 'epubcheck' não instalado. Rode: pip install epubcheck "
                "(requer Java instalado no sistema — ex: 'sudo apt install default-jre' "
                "ou 'brew install openjdk')."
            ),
        )

    try:
        result = EpubCheck(epub_path, lang="pt")
    except Exception as e:
        return ValidationResult(
            available=False,
            error=f"Falha ao executar o EPUBCheck (verifique se o Java está instalado): {e}",
        )

    messages = [
        ValidationMessage(
            id=m.id, level=m.level, location=m.location, message=m.message, suggestion=m.suggestion or ""
        )
        for m in (result.messages or [])
    ]

    checker = result.checker
    return ValidationResult(
        available=True,
        valid=bool(result.valid),
        messages=messages,
        n_fatal=getattr(checker, "nFatal", 0) if checker else 0,
        n_error=getattr(checker, "nError", 0) if checker else 0,
        n_warning=getattr(checker, "nWarning", 0) if checker else 0,
    )
