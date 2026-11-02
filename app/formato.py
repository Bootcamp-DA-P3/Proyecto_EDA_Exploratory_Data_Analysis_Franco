"""Formato de numeros y fechas en español (miles con punto, decimales con coma)."""
from __future__ import annotations

import pandas as pd

MESES = [
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
]


def num(valor: float, decimales: int = 0) -> str:
    texto = f"{valor:,.{decimales}f}"
    return texto.replace(",", "\0").replace(".", ",").replace("\0", ".")


def libras(valor: float, decimales: int = 0) -> str:
    signo = "-" if valor < 0 else ""
    return f"{signo}£{num(abs(valor), decimales)}"


def pct(valor: float, decimales: int = 1) -> str:
    return f"{num(valor, decimales)}%"


def mes(periodo: pd.Period) -> str:
    return f"{MESES[periodo.month - 1]} de {periodo.year}"


def fecha(valor) -> str:
    return pd.Timestamp(valor).strftime("%d/%m/%Y")


def p_valor(p: float, umbral: float = 0.001) -> str:
    return f"p < {num(umbral, 3)}" if p < umbral else f"p = {num(p, 3)}"


def lista(items: list[str]) -> str:
    """Une elementos con comas y una 'y' final."""
    if len(items) <= 1:
        return "".join(items)
    return ", ".join(items[:-1]) + " y " + items[-1]
