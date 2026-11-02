"""Pipeline de datos de la app.

Replica, en el mismo orden, la limpieza de las secciones 1 a 17 del notebook
`notebooks/01_eda_online_retail.ipynb` para que las etiquetas de fila (los
numeros que se usan en `drop`) coincidan. Las funciones auxiliares replican los
calculos de las secciones 18 a 26. No hay ningun valor de resultado fijo en este
modulo: todo se calcula a partir del CSV.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st
from scipy import stats

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "online_retail_II.csv"

# Etiquetas de fila (indice del CSV original) que el notebook elimina como errores humanos.
# Secciones 11 y 17: par compra/devolucion de 80995 unidades y par de 74215 unidades.
FILAS_ATIPICAS_AMBAS = [1065882, 1065883]
FILA_ATIPICA_VENTAS = 587080
FILA_ATIPICA_DEVOLUCIONES = 587085

# Descripciones que no son productos vendidos (secciones 20 y 22).
NO_PRODUCTOS_VENTAS = ["Manual", "POSTAGE"]
NO_PRODUCTOS_DEVOLUCIONES = ["Manual", "POSTAGE", "Discount", "CARRIAGE", "CRUK Commission"]

ALPHA = 0.05  # nivel de significancia de la seccion 25
FRACCION_TOP_CLIENTES = 0.2  # seccion 23
TOP_N = 10  # tamano de los rankings (secciones 20, 21 y 22)


def construir_tablas(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Aplica la limpieza del notebook (secciones 3 a 17) y devuelve (ventas, devoluciones)."""
    df_clean = df.dropna(subset=["Customer ID"]).copy()
    df_clean["Customer ID"] = df_clean["Customer ID"].astype(int)
    df_clean["InvoiceDate"] = pd.to_datetime(df_clean["InvoiceDate"])
    df_clean = df_clean.drop_duplicates()
    df_clean = df_clean.drop(FILAS_ATIPICAS_AMBAS)
    df_clean = df_clean[df_clean["Price"].abs() > 0]

    ventas = df_clean[df_clean["Quantity"] > 0].copy()
    ventas["TotalPrice"] = ventas["Quantity"] * ventas["Price"]
    ventas = ventas.drop(FILA_ATIPICA_VENTAS)

    devoluciones = df_clean[df_clean["Quantity"] < 0].copy()
    devoluciones = devoluciones.drop(FILA_ATIPICA_DEVOLUCIONES)
    devoluciones["TotalPrice"] = devoluciones["Quantity"] * devoluciones["Price"]
    return ventas, devoluciones


@st.cache_data(show_spinner="Cargando y limpiando los datos...")
def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Lee el CSV una sola vez y devuelve (ventas, devoluciones) ya limpias."""
    df = pd.read_csv(DATA_PATH)
    return construir_tablas(df)


def filter_data(
    ventas: pd.DataFrame,
    devoluciones: pd.DataFrame,
    paises: list[str] | None = None,
    fecha_ini=None,
    fecha_fin=None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Filtra ventas y devoluciones por pais (lista vacia = todos) y rango de fechas inclusivo."""

    def _filtrar(d: pd.DataFrame) -> pd.DataFrame:
        mascara = pd.Series(True, index=d.index)
        if fecha_ini is not None:
            mascara &= d["InvoiceDate"] >= pd.Timestamp(fecha_ini)
        if fecha_fin is not None:
            mascara &= d["InvoiceDate"] < pd.Timestamp(fecha_fin) + pd.Timedelta(days=1)
        if paises:
            mascara &= d["Country"].isin(paises)
        return d[mascara]

    return _filtrar(ventas), _filtrar(devoluciones)


def kpis(ventas: pd.DataFrame) -> dict:
    """KPIs generales (seccion 18). Con ventas vacias devuelve ceros y NaN en los cocientes."""
    ingresos = float(ventas["TotalPrice"].sum())
    n_facturas = int(ventas["Invoice"].nunique())
    n_clientes = int(ventas["Customer ID"].nunique())
    n_productos = int(ventas["StockCode"].nunique())
    ticket = ventas.groupby("Invoice")["TotalPrice"].sum()
    return {
        "ingresos": ingresos,
        "facturas": n_facturas,
        "clientes": n_clientes,
        "productos": n_productos,
        "frecuencia": n_facturas / n_clientes if n_clientes else float("nan"),
        "ticket_media": float(ticket.mean()) if len(ticket) else float("nan"),
        "ticket_mediana": float(ticket.median()) if len(ticket) else float("nan"),
    }


def mes_incompleto(ventas_total: pd.DataFrame) -> pd.Period | None:
    """Mes del ultimo dato si no llega a su ultimo dia (seccion 19: diciembre de 2011 termina el 9)."""
    ultimo = ventas_total["InvoiceDate"].max()
    if pd.isna(ultimo):
        return None
    fin_de_mes = ultimo.to_period("M").end_time.normalize()
    return ultimo.to_period("M") if ultimo.normalize() < fin_de_mes else None


def ventas_mensuales(ventas: pd.DataFrame, excluir: pd.Period | None = None) -> pd.Series:
    """Ingresos por mes (seccion 19), sin el mes incompleto indicado."""
    mensual = ventas.groupby(ventas["InvoiceDate"].dt.to_period("M"))["TotalPrice"].sum()
    if excluir is not None:
        mensual = mensual[mensual.index != excluir]
    return mensual


def top_productos(ventas: pd.DataFrame, n: int = TOP_N) -> tuple[pd.Series, pd.Series]:
    """Top n productos por ingresos y por unidades (seccion 20), sin Manual ni POSTAGE."""
    productos = ventas[~ventas["Description"].isin(NO_PRODUCTOS_VENTAS)]
    top_ingresos = productos.groupby("Description")["TotalPrice"].sum().nlargest(n)
    top_cantidad = productos.groupby("Description")["Quantity"].sum().nlargest(n)
    return top_ingresos, top_cantidad


def ingresos_pais(ventas: pd.DataFrame) -> pd.Series:
    """Ingresos por pais, de mayor a menor (seccion 21)."""
    return ventas.groupby("Country")["TotalPrice"].sum().sort_values(ascending=False)


def resumen_devoluciones(
    ventas: pd.DataFrame, devoluciones: pd.DataFrame, top_ingresos: pd.Series, n: int = TOP_N
) -> dict:
    """Peso de las devoluciones y top n productos por monto devuelto (seccion 22)."""
    ingresos = float(ventas["TotalPrice"].sum())
    n_clientes = int(ventas["Customer ID"].nunique())
    monto = float(devoluciones["TotalPrice"].sum())
    clientes_dev = int(devoluciones["Customer ID"].nunique())
    productos_dev = devoluciones[~devoluciones["Description"].isin(NO_PRODUCTOS_DEVOLUCIONES)]
    top_dev = productos_dev.groupby("Description")["TotalPrice"].sum().nsmallest(n).abs()
    return {
        "monto": monto,
        "pct_ingresos": abs(monto) / ingresos * 100 if ingresos else float("nan"),
        "facturas": int(devoluciones["Invoice"].nunique()),
        "clientes_dev": clientes_dev,
        "clientes_total": n_clientes,
        "pct_clientes": clientes_dev / n_clientes * 100 if n_clientes else float("nan"),
        "top_dev": top_dev,
        "tambien_en_top_ventas": sorted(set(top_dev.index) & set(top_ingresos.index)),
    }


def tabla_clientes(ventas: pd.DataFrame) -> pd.DataFrame:
    """Tabla a nivel cliente (seccion 24)."""
    clientes = ventas.groupby("Customer ID").agg(
        frecuencia=("Invoice", "nunique"),
        unidades=("Quantity", "sum"),
        gasto_total=("TotalPrice", "sum"),
    )
    clientes["ticket_medio"] = clientes["gasto_total"] / clientes["frecuencia"]
    return clientes


def pareto(ventas: pd.DataFrame) -> dict:
    """Concentracion de ingresos por cliente (seccion 23)."""
    por_cliente = ventas.groupby("Customer ID")["TotalPrice"].sum().sort_values(ascending=False)
    n = len(por_cliente)
    n_top = int(n * FRACCION_TOP_CLIENTES)
    total = por_cliente.sum()
    pct_top = por_cliente.head(n_top).sum() / total * 100 if total else float("nan")
    acumulado = por_cliente.cumsum() / total * 100 if total else por_cliente * float("nan")
    pct_clientes = np.arange(1, n + 1) / n * 100 if n else np.array([])
    return {
        "n_clientes": n,
        "n_top": n_top,
        "pct_top": float(pct_top),
        "acumulado": acumulado.to_numpy(),
        "pct_clientes": pct_clientes,
    }


def spearman(clientes: pd.DataFrame) -> dict | None:
    """Spearman entre frecuencia y gasto total (seccion 25). None si no se puede calcular."""
    if len(clientes) < 3:
        return None
    rho, p_valor = stats.spearmanr(clientes["frecuencia"], clientes["gasto_total"])
    if np.isnan(rho):
        return None
    return {
        "n": len(clientes),
        "rho": float(rho),
        "p_valor": float(p_valor),
        "rechaza_h0": bool(p_valor < ALPHA),
        "alpha": ALPHA,
    }


def distribucion_gasto(clientes: pd.DataFrame) -> dict | None:
    """Media, mediana y asimetria del gasto por cliente, en escala normal y log10 (seccion 26)."""
    if len(clientes) < 3:
        return None
    gasto = clientes["gasto_total"]
    gasto_log = np.log10(gasto)
    return {
        "gasto": gasto,
        "gasto_log": gasto_log,
        "media": float(gasto.mean()),
        "mediana": float(gasto.median()),
        "asimetria": float(gasto.skew()),
        "asimetria_log": float(gasto_log.skew()),
    }
