"""Sistema de diseño "Franco Recabarren": tokens, plantilla Plotly y helpers HTML.

Cyber brutalista: radio 0, sin sombras ni degradados, sin bordes laterales de color.
Violeta como acento, lima solo como fondo con texto ink (una vez por pestaña).
"""
from __future__ import annotations

from html import escape

import plotly.graph_objects as go
import streamlit as st

TOKENS = {
    "paper": "#f2f2ef",
    "surface": "#fafaf8",
    "ink": "#0a0a0a",
    "ink_muted": "#5c5c58",
    "line": "#b9b9b4",
    "violet": "#6b3df5",
    "on_violet": "#ffffff",
    "lime": "#d4ff3a",
    "on_lime": "#0a0a0a",
}
T = TOKENS

FONT_MONO = '"JetBrains Mono", ui-monospace, monospace'
FONT_DISPLAY = "Anton, Impact, 'Arial Narrow', sans-serif"
FONT_SANS = "Inter, system-ui, sans-serif"

# Escala del mapa de calor: gris (negativo) -> papel (0) -> violeta (positivo).
HEATMAP_SCALE = [[0.0, T["ink_muted"]], [0.5, T["paper"]], [1.0, T["violet"]]]


def plotly_template() -> go.layout.Template:
    """Plantilla Plotly con los tokens del sistema (superficie, ink, grilla line, sin sombras)."""
    eje = dict(
        gridcolor=T["line"],
        gridwidth=1,
        linecolor=T["ink"],
        linewidth=1,
        zeroline=False,
        ticks="outside",
        tickcolor=T["ink"],
        title=dict(font=dict(size=11, color=T["ink_muted"])),
        tickfont=dict(size=11, color=T["ink"]),
    )
    return go.layout.Template(
        layout=go.Layout(
            paper_bgcolor=T["surface"],
            plot_bgcolor=T["surface"],
            font=dict(family=FONT_MONO, color=T["ink"], size=12),
            colorway=[T["violet"], T["ink"], T["ink_muted"]],
            xaxis=eje,
            yaxis=eje,
            margin=dict(l=56, r=24, t=16, b=48),
            separators=",.",  # decimal con coma y miles con punto
            hoverlabel=dict(
                bgcolor=T["surface"],
                bordercolor=T["ink"],
                font=dict(family=FONT_MONO, color=T["ink"], size=12),
            ),
            legend=dict(
                bgcolor=T["surface"], bordercolor=T["line"], borderwidth=1, font=dict(size=11)
            ),
        )
    )


TEMPLATE = plotly_template()

CSS = f"""
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
:root {{
  --paper: {T["paper"]}; --surface: {T["surface"]}; --ink: {T["ink"]}; --ink-muted: {T["ink_muted"]};
  --line: {T["line"]}; --violet: {T["violet"]}; --on-violet: {T["on_violet"]};
  --lime: {T["lime"]}; --on-lime: {T["on_lime"]};
}}
.fr-brand {{ font-family: {FONT_MONO}; font-weight: 700; font-size: 0.85rem; letter-spacing: 0.08em; color: var(--ink); }}
.fr-label {{ font-family: {FONT_MONO}; font-weight: 500; font-size: 0.75rem; letter-spacing: 0.08em;
  text-transform: uppercase; color: var(--violet); }}
.fr-display {{ font-family: {FONT_DISPLAY}; font-weight: 400; text-transform: uppercase; color: var(--ink);
  line-height: 1; margin: 0.25rem 0 0; }}
.fr-title {{ font-size: clamp(2.6rem, 6vw, 4.5rem); }}
.fr-h2 {{ font-size: clamp(1.9rem, 3.5vw, 2.6rem); }}
.fr-kicker {{ font-family: {FONT_MONO}; font-weight: 500; font-size: 0.85rem; letter-spacing: 0.04em;
  text-transform: uppercase; color: var(--violet); margin: 0.5rem 0 1rem; }}
.fr-rule {{ border-top: 1px solid var(--line); margin: 1.5rem 0 1rem; }}
.fr-chart-title {{ font-family: {FONT_MONO}; font-weight: 500; font-size: 0.75rem; letter-spacing: 0.08em;
  text-transform: uppercase; color: var(--ink-muted); margin: 0 0 0.25rem; }}
.fr-insight {{ font-family: {FONT_SANS}; font-size: 1rem; line-height: 1.6; color: var(--ink);
  max-width: 72ch; margin: 0 0 0.5rem; }}
.fr-status {{ font-family: {FONT_MONO}; font-size: 0.75rem; letter-spacing: 0.08em; text-transform: uppercase;
  color: var(--ink-muted); border-top: 1px solid var(--line); padding-top: 0.5rem; margin-top: 1rem; }}
.fr-status a {{ color: var(--violet); text-decoration: none; border-bottom: 1px solid var(--violet); }}
.fr-status a:hover {{ color: var(--ink); border-color: var(--ink); }}
.fr-signal {{ background: var(--lime); color: var(--on-lime); padding: 1rem; display: flex;
  align-items: baseline; gap: 1rem; flex-wrap: wrap; margin: 0.5rem 0 1rem; }}
.fr-signal b {{ font-family: {FONT_DISPLAY}; font-weight: 400; font-size: clamp(2rem, 4vw, 3rem); line-height: 1; }}
.fr-signal span {{ font-family: {FONT_MONO}; font-weight: 500; font-size: 0.8rem; text-transform: uppercase;
  letter-spacing: 0.04em; }}
[data-testid="stMetricLabel"] {{ font-family: {FONT_MONO}; text-transform: uppercase; letter-spacing: 0.04em;
  font-size: 0.68rem; color: var(--ink-muted); }}
[data-testid="stMetricValue"] {{ font-family: {FONT_DISPLAY}; }}
"""


def inject_css() -> None:
    """Inyecta el CSS minimo del sistema (los colores base vienen de .streamlit/config.toml)."""
    st.html(f"<style>{CSS}</style>")


def brand(texto: str = "FRANCO_R") -> None:
    st.html(f'<div class="fr-brand">{escape(texto)}</div>')


def page_title(etiqueta: str, titulo: str, kicker: str) -> None:
    """Cabecera principal: etiqueta numerada, titulo display y kicker violeta."""
    st.html(
        f'<div class="fr-label">{escape(etiqueta)}</div>'
        f'<h1 class="fr-display fr-title">{escape(titulo)}</h1>'
        f'<div class="fr-kicker">{escape(kicker)}</div>'
    )


def section_header(numero: str, seccion: str, titulo: str, kicker: str) -> None:
    """Cabecera de pestaña: etiqueta "/01 — VENTAS", titulo display y kicker mono violeta."""
    st.html(
        f'<div class="fr-label">{escape(numero)} — {escape(seccion)}</div>'
        f'<h2 class="fr-display fr-h2">{escape(titulo)}</h2>'
        f'<div class="fr-kicker">{escape(kicker)}</div>'
    )


def chart_title(texto: str) -> None:
    st.html(f'<div class="fr-chart-title">{escape(texto)}</div>')


def signal_card(valor: str, texto: str) -> None:
    """Dato destacado: unico uso de lima por pestaña, solo como fondo con texto ink."""
    st.html(f'<div class="fr-signal"><b>{escape(valor)}</b><span>{escape(texto)}</span></div>')


def insight(*frases: str) -> None:
    """Texto de lectura (Inter). Cada frase ya viene armada con valores calculados."""
    st.html("".join(f'<p class="fr-insight">{escape(f)}</p>' for f in frases))


def status_bar(texto: str, link_texto: str | None = None, link_url: str | None = None) -> None:
    """Barra de estado mono: "● ...". Si se pasa link, agrega un enlace al final."""
    enlace = ""
    if link_texto and link_url:
        enlace = f' · <a href="{escape(link_url)}" target="_blank" rel="noopener">{escape(link_texto)}</a>'
    st.html(f'<div class="fr-status">● {escape(texto)}{enlace}</div>')


def card(nombre: str):
    """Contenedor con borde (line) para un grafico. Streamlit pinta el papel del grafico con el fondo de la app."""
    return st.container(border=True, key=f"card_{nombre}")
