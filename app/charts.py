"""Constructores de graficos Plotly con el sistema de diseño (ver theme.py)."""
from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from scipy import stats

from theme import HEATMAP_SCALE, T, TEMPLATE

N_BINS_HISTOGRAMA = 50  # igual que la seccion 26 del notebook


def _figura(altura: int = 380) -> go.Figure:
    fig = go.Figure()
    fig.update_layout(template=TEMPLATE, height=altura)
    return fig


def _corto(texto: str, maximo: int = 28) -> str:
    return texto if len(texto) <= maximo else texto[: maximo - 1] + "…"


def linea_mensual(mensual: pd.Series) -> go.Figure:
    """Ingresos por mes (seccion 19). El indice es un PeriodIndex mensual."""
    fig = _figura()
    fig.add_trace(
        go.Scatter(
            x=mensual.index.to_timestamp(),
            y=mensual.to_numpy(),
            mode="lines+markers",
            line=dict(color=T["violet"], width=2),
            marker=dict(symbol="square", size=7, color=T["violet"], line=dict(color=T["ink"], width=1)),
            hovertemplate="%{x|%m/%Y}<br>£%{y:,.0f}<extra></extra>",
            showlegend=False,
        )
    )
    fig.update_xaxes(tickformat="%m/%Y", title_text="Mes")
    fig.update_yaxes(tickprefix="£", title_text="Ingresos (£)", rangemode="tozero")
    return fig


def barras_horizontales(serie: pd.Series, eje: str, color: str = T["violet"], prefijo: str = "") -> go.Figure:
    """Top n como barras horizontales, la mayor arriba (secciones 20, 21 y 22)."""
    orden = serie.sort_values()
    fig = _figura()
    fig.add_trace(
        go.Bar(
            x=orden.to_numpy(),
            y=[_corto(str(i)) for i in orden.index],
            orientation="h",
            marker=dict(color=color, line=dict(color=T["ink"], width=1)),
            customdata=[str(i) for i in orden.index],
            hovertemplate="%{customdata}<br>" + prefijo + "%{x:,.0f}<extra></extra>",
            showlegend=False,
        )
    )
    fig.update_xaxes(title_text=eje, tickprefix=prefijo)
    fig.update_yaxes(automargin=True, showgrid=False)
    return fig


def curva_pareto(pct_clientes: np.ndarray, acumulado: np.ndarray, pct_top: float, fraccion: float) -> go.Figure:
    """Curva de Pareto con guias en la fraccion de clientes elegida (seccion 23)."""
    fig = _figura()
    fig.add_trace(
        go.Scatter(
            x=pct_clientes,
            y=acumulado,
            mode="lines",
            line=dict(color=T["violet"], width=2),
            hovertemplate="%{x:.1f}% de los clientes<br>%{y:.1f}% de los ingresos<extra></extra>",
            showlegend=False,
        )
    )
    guia = dict(color=T["ink_muted"], width=1, dash="dash")
    fig.add_vline(x=fraccion * 100, line=guia)
    fig.add_hline(y=pct_top, line=guia)
    fig.add_annotation(
        x=fraccion * 100,
        y=pct_top,
        text=f"{pct_top:.1f}%".replace(".", ","),
        showarrow=False,
        xanchor="left",
        yanchor="top",
        xshift=8,
        yshift=-8,
        font=dict(family=TEMPLATE.layout.font.family, size=12, color=T["ink"]),
        bgcolor=T["surface"],
    )
    fig.update_xaxes(title_text="% de clientes (de mayor a menor gasto)", ticksuffix="%", range=[0, 100])
    fig.update_yaxes(title_text="% acumulado de ingresos", ticksuffix="%", range=[0, 100])
    return fig


def heatmap_pearson(corr: pd.DataFrame) -> go.Figure:
    """Mapa de calor de correlaciones con el valor en cada celda (seccion 24)."""
    etiquetas = list(corr.columns)
    fig = _figura(altura=420)
    fig.add_trace(
        go.Heatmap(
            z=corr.to_numpy(),
            x=etiquetas,
            y=etiquetas,
            colorscale=HEATMAP_SCALE,
            zmin=-1,
            zmax=1,
            xgap=1,
            ygap=1,
            colorbar=dict(thickness=12, outlinewidth=1, outlinecolor=T["ink"], tickfont=dict(size=11)),
            hovertemplate="%{y} vs %{x}: %{z:.2f}<extra></extra>",
        )
    )
    for i, fila in enumerate(etiquetas):
        for j, col in enumerate(etiquetas):
            valor = float(corr.iloc[i, j])
            fig.add_annotation(
                x=col,
                y=fila,
                text=f"{valor:.2f}".replace(".", ","),
                showarrow=False,
                font=dict(
                    family=TEMPLATE.layout.font.family,
                    size=13,
                    color=T["on_violet"] if abs(valor) > 0.55 else T["ink"],
                ),
            )
    fig.update_xaxes(showgrid=False, side="bottom")
    fig.update_yaxes(showgrid=False, autorange="reversed", automargin=True)
    return fig


def dispersion_log(clientes: pd.DataFrame) -> go.Figure:
    """Frecuencia vs gasto total por cliente en escala logaritmica (seccion 24)."""
    fig = _figura(altura=420)
    fig.add_trace(
        go.Scatter(
            x=clientes["frecuencia"],
            y=clientes["gasto_total"],
            mode="markers",
            marker=dict(size=6, color=T["violet"], opacity=0.4, line=dict(width=0)),
            customdata=clientes.index,
            hovertemplate="Cliente %{customdata}<br>%{x} facturas<br>£%{y:,.0f}<extra></extra>",
            showlegend=False,
        )
    )
    fig.update_xaxes(type="log", title_text="Facturas por cliente (log)")
    fig.update_yaxes(type="log", title_text="Gasto total £ (log)")
    return fig


def histograma_log(gasto_log: pd.Series) -> go.Figure:
    """Histograma del log10 del gasto por cliente y curva normal ajustada (seccion 26)."""
    minimo, maximo = float(gasto_log.min()), float(gasto_log.max())
    ancho = (maximo - minimo) / N_BINS_HISTOGRAMA
    fig = _figura(altura=420)
    fig.add_trace(
        go.Histogram(
            x=gasto_log,
            histnorm="probability density",
            xbins=dict(start=minimo, end=maximo, size=ancho) if ancho > 0 else None,
            marker=dict(color=T["violet"], opacity=0.7, line=dict(color=T["surface"], width=1)),
            name="Clientes",
            hovertemplate="log10 %{x:.2f}<br>densidad %{y:.3f}<extra></extra>",
        )
    )
    x = np.linspace(minimo, maximo, 500)
    fig.add_trace(
        go.Scatter(
            x=x,
            y=stats.norm.pdf(x, gasto_log.mean(), gasto_log.std()),
            mode="lines",
            line=dict(color=T["ink"], width=2),
            name="Curva normal",
            hoverinfo="skip",
        )
    )
    fig.update_xaxes(title_text="log10(Gasto total £)")
    fig.update_yaxes(title_text="Densidad")
    fig.update_layout(legend=dict(x=0.98, xanchor="right", y=0.98, yanchor="top"), bargap=0)
    return fig
