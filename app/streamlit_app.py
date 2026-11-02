"""App interactiva del EDA de Online Retail II.

Una pagina con pestañas y filtros de pais y fechas en la barra lateral.
Todos los valores se calculan en vivo con el mismo pipeline del notebook (ver data.py).
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402
import streamlit as st  # noqa: E402

import charts as ch  # noqa: E402
import data as dt  # noqa: E402
import formato as fm  # noqa: E402
import theme as th  # noqa: E402

st.set_page_config(page_title="Online Retail II", layout="wide")
th.inject_css()


NUM_LIDERES = 3  # paises que se nombran en el texto del mercado


def mostrar(fig, alt: str) -> None:
    """Dibuja un grafico Plotly con la plantilla propia (sin tema de Streamlit)."""
    st.plotly_chart(fig, theme=None, width="stretch", alt=alt, config={"displayModeBar": False})


# ---------------------------------------------------------------- datos
ventas_total, devoluciones_total = dt.load_data()
fecha_min = ventas_total["InvoiceDate"].min().date()
fecha_max = ventas_total["InvoiceDate"].max().date()
mes_inc = dt.mes_incompleto(ventas_total)

# ---------------------------------------------------------------- cabecera
th.brand("FRANCO_R")
th.page_title(
    "/00 — INFORME INTERACTIVO",
    "Online Retail II",
    f"Ventas de una tienda online británica · {fm.fecha(fecha_min)} a {fm.fecha(fecha_max)}",
)

# ---------------------------------------------------------------- filtros
with st.sidebar:
    st.html('<div class="fr-label">/F — FILTROS</div>')
    paises = st.multiselect(
        "País",
        sorted(ventas_total["Country"].unique()),
        placeholder="Todos los países",
        help="Sin selección se muestran todos los países.",
    )
    rango = st.date_input(
        "Rango de fechas",
        value=(fecha_min, fecha_max),
        min_value=fecha_min,
        max_value=fecha_max,
        format="DD/MM/YYYY",
    )

if len(rango) != 2:
    st.info("Elige la fecha de inicio y la de fin para aplicar el rango.", title="Rango incompleto")
    st.stop()

fecha_ini, fecha_fin = rango
ventas, devoluciones = dt.filter_data(ventas_total, devoluciones_total, paises, fecha_ini, fecha_fin)

with st.sidebar:
    th.status_bar(
        f"Líneas de venta: {fm.num(len(ventas))} · Líneas de devolución: {fm.num(len(devoluciones))}"
    )

if ventas.empty:
    st.info("No hay ventas con estos filtros. Prueba con otro país o amplía el rango de fechas.", title="Sin datos")
    st.stop()

# ---------------------------------------------------------------- KPIs
k = dt.kpis(ventas)
kpis_fila = [
    ("Ingresos", fm.libras(k["ingresos"])),
    ("Facturas", fm.num(k["facturas"])),
    ("Clientes", fm.num(k["clientes"])),
    ("Productos", fm.num(k["productos"])),
    ("Compras por cliente", fm.num(k["frecuencia"], 1)),
    ("Ticket mediano", fm.libras(k["ticket_mediana"], 2)),
]
for fila in (kpis_fila[:3], kpis_fila[3:]):
    for columna, (etiqueta, valor) in zip(st.columns(len(fila)), fila):
        columna.metric(etiqueta, valor, border=True)

# Productos y pais se usan en varias pestañas.
top_ingresos, top_cantidad = dt.top_productos(ventas)
ingresos_por_pais = dt.ingresos_pais(ventas)

tab_ventas, tab_productos, tab_mercado, tab_devoluciones, tab_clientes, tab_estadistica = st.tabs(
    ["/01 VENTAS", "/02 PRODUCTOS", "/03 MERCADO", "/04 DEVOLUCIONES", "/05 CLIENTES", "/06 ESTADÍSTICA"]
)

# ---------------------------------------------------------------- /01 ventas
with tab_ventas:
    th.section_header("/01", "VENTAS", "Cuándo se vende", "Ingresos mensuales y estacionalidad")
    mensual = dt.ventas_mensuales(ventas, mes_inc)
    if mensual.empty:
        st.info("No hay meses completos en el rango elegido para dibujar la evolución mensual.")
    else:
        mes_pico, mes_valle = mensual.idxmax(), mensual.idxmin()
        mejores = mensual.nlargest(min(3, len(mensual)))
        th.signal_card(fm.libras(mensual.max()), f"Ingresos de {fm.mes(mes_pico)}, el mes de mayor venta")
        with th.card("ventas_mensuales"):
            th.chart_title("Ingresos mensuales (£)")
            mostrar(
                ch.linea_mensual(mensual),
                f"Línea de ingresos mensuales; el máximo es {fm.mes(mes_pico)}.",
            )
        frases = [
            f"El mes de mayor ingreso es {fm.mes(mes_pico)} con {fm.libras(mensual.max())}; "
            f"el más bajo es {fm.mes(mes_valle)} con {fm.libras(mensual.min())}.",
            "Los meses con más ingresos son " + fm.lista([fm.mes(p) for p in mejores.index]) + ".",
            f"El ticket por factura tiene una mediana de {fm.libras(k['ticket_mediana'], 2)} "
            f"y una media de {fm.libras(k['ticket_media'], 2)}.",
        ]
        if k["ticket_media"] > k["ticket_mediana"]:
            frases[-1] += " La media supera a la mediana: unas pocas facturas grandes suben el promedio."
        th.insight(*frases)
        if mes_inc is not None and ventas["InvoiceDate"].max().to_period("M") == mes_inc:
            st.caption(
                f"Se excluye {fm.mes(mes_inc)} del gráfico porque es un mes incompleto "
                f"(los datos terminan el {fm.fecha(fecha_max)})."
            )

# ---------------------------------------------------------------- /02 productos
with tab_productos:
    th.section_header("/02", "PRODUCTOS", "Qué se vende más", f"Top {dt.TOP_N} por ingresos y por unidades")
    if top_ingresos.empty:
        st.info("Con estos filtros no hay productos para mostrar (solo ajustes manuales o costos de envío).")
    else:
        th.signal_card(
            fm.libras(top_ingresos.iloc[0]),
            f"{top_ingresos.index[0]}, el producto que más ingresa",
        )
        col_ingresos, col_unidades = st.columns(2)
        with col_ingresos, th.card("top_ingresos"):
            th.chart_title(f"Top {dt.TOP_N} por ingresos (£)")
            mostrar(
                ch.barras_horizontales(top_ingresos, "Ingresos (£)", prefijo="£"),
                f"Barras horizontales de los productos con más ingresos; lidera {top_ingresos.index[0]}.",
            )
        with col_unidades, th.card("top_unidades"):
            th.chart_title(f"Top {dt.TOP_N} por unidades")
            mostrar(
                ch.barras_horizontales(top_cantidad, "Unidades", color=th.T["ink"]),
                f"Barras horizontales de los productos más vendidos en unidades; lidera {top_cantidad.index[0]}.",
            )
        en_ambos = sorted(set(top_ingresos.index) & set(top_cantidad.index))
        th.insight(
            f"{top_ingresos.index[0]} lidera en ingresos y {top_cantidad.index[0]} lidera en unidades.",
            f"{len(en_ambos)} de {len(top_ingresos)} productos aparecen en los dos rankings"
            + (", así que el ingreso y el volumen no siempre van de la mano." if len(en_ambos) < len(top_ingresos) else "."),
            "Se excluyen Manual (ajustes manuales) y POSTAGE (costo de envío) porque no son productos vendidos.",
        )

# ---------------------------------------------------------------- /03 mercado
with tab_mercado:
    th.section_header("/03", "MERCADO", "Dónde se vende", "Ingresos por país")
    total_ingresos = ingresos_por_pais.sum()
    lider = ingresos_por_pais.index[0]
    pct_lider = ingresos_por_pais.iloc[0] / total_ingresos * 100
    n_paises = len(ingresos_por_pais)
    quitar_uk = "United Kingdom" in ingresos_por_pais.index and n_paises > 1
    top_paises = (ingresos_por_pais.drop("United Kingdom") if quitar_uk else ingresos_por_pais).head(dt.TOP_N)

    th.signal_card(fm.pct(pct_lider), f"de los ingresos viene de {lider}")
    with th.card("top_paises"):
        th.chart_title(f"Top {dt.TOP_N} países por ingresos (£)" + (" · sin United Kingdom" if quitar_uk else ""))
        mostrar(
            ch.barras_horizontales(top_paises, "Ingresos (£)", prefijo="£"),
            f"Barras horizontales de los países con más ingresos; lidera {top_paises.index[0]}.",
        )
    if n_paises == 1:
        frases = [f"Con este filtro solo hay ventas a un país: {lider}."]
    else:
        lideres = [
            f"{pais} ({fm.pct(valor / total_ingresos * 100)})" for pais, valor in top_paises.head(NUM_LIDERES).items()
        ]
        frases = [
            f"Se vende a {n_paises} países. {lider} concentra {fm.libras(ingresos_por_pais.iloc[0])}, "
            f"el {fm.pct(pct_lider)} de los ingresos; el resto de los países suma el {fm.pct(100 - pct_lider)}.",
            ("Fuera de United Kingdom lideran " if quitar_uk else f"Los {len(lideres)} con más ingresos son ")
            + fm.lista(lideres)
            + ".",
        ]
    th.insight(*frases)

# ---------------------------------------------------------------- /04 devoluciones
with tab_devoluciones:
    th.section_header("/04", "DEVOLUCIONES", "Cuánto se devuelve", "Peso en dinero y productos más devueltos")
    if devoluciones.empty:
        st.info("No hay devoluciones con los filtros elegidos.")
    else:
        res = dt.resumen_devoluciones(ventas, devoluciones, top_ingresos)
        pct_filas = len(devoluciones) / (len(devoluciones) + len(ventas)) * 100
        th.signal_card(fm.pct(res["pct_ingresos"]), "de los ingresos se devolvió")
        if res["top_dev"].empty:
            st.info("Las devoluciones de estos filtros no incluyen productos (solo ajustes o descuentos).")
        else:
            with th.card("top_devoluciones"):
                th.chart_title(f"Top {dt.TOP_N} productos por monto devuelto (£)")
                mostrar(
                    ch.barras_horizontales(res["top_dev"], "Monto devuelto (£)", color=th.T["ink"], prefijo="£"),
                    f"Barras horizontales de los productos más devueltos; lidera {res['top_dev'].index[0]}.",
                )
        frases = [
            f"Se devolvieron {fm.libras(abs(res['monto']))}, el {fm.pct(res['pct_ingresos'])} de los ingresos, "
            f"en {fm.num(res['facturas'])} facturas de devolución.",
            f"En líneas, las devoluciones son el {fm.pct(pct_filas)} del total, pero en dinero pesan el "
            f"{fm.pct(res['pct_ingresos'])}.",
            f"{fm.num(res['clientes_dev'])} de {fm.num(res['clientes_total'])} clientes "
            f"({fm.pct(res['pct_clientes'])}) devolvieron al menos una vez.",
        ]
        if not res["top_dev"].empty:
            coincidencias = res["tambien_en_top_ventas"]
            frases.append(
                f"{len(coincidencias)} de los {len(res['top_dev'])} productos más devueltos también están "
                "entre los de mayor ingreso."
            )
        th.insight(*frases)

# ---------------------------------------------------------------- /05 clientes
with tab_clientes:
    th.section_header("/05", "CLIENTES", "Quién sostiene el negocio", "Concentración de ingresos (Pareto)")
    par = dt.pareto(ventas)
    pct_fraccion = dt.FRACCION_TOP_CLIENTES * 100
    minimo_clientes = math.ceil(1 / dt.FRACCION_TOP_CLIENTES)
    if par["n_top"] < 1:
        st.warning(
            f"Con {fm.num(par['n_clientes'])} cliente(s) no se puede calcular el grupo del "
            f"{fm.pct(pct_fraccion, 0)} superior: se necesitan al menos {minimo_clientes}."
        )
    else:
        th.signal_card(
            fm.pct(par["pct_top"]),
            f"de los ingresos lo genera el {fm.pct(pct_fraccion, 0)} de los clientes",
        )
        with th.card("pareto"):
            th.chart_title("Curva de Pareto: ingresos acumulados por cliente")
            mostrar(
                ch.curva_pareto(par["pct_clientes"], par["acumulado"], par["pct_top"], dt.FRACCION_TOP_CLIENTES),
                f"Curva de Pareto: el {fm.pct(pct_fraccion, 0)} de los clientes genera el {fm.pct(par['pct_top'])} "
                "de los ingresos.",
            )
        th.insight(
            f"El {fm.pct(pct_fraccion, 0)} de los clientes ({fm.num(par['n_top'])} de {fm.num(par['n_clientes'])}) "
            f"genera el {fm.pct(par['pct_top'])} de los ingresos.",
            f"Con un reparto parejo, ese grupo aportaría solo el {fm.pct(pct_fraccion, 0)}. "
            "Cuanto más sube la curva al inicio, más depende el negocio de pocos clientes.",
        )

# ---------------------------------------------------------------- /06 estadística
with tab_estadistica:
    th.section_header("/06", "ESTADÍSTICA", "Qué relaciona a los clientes", "Correlaciones, prueba de hipótesis y distribución")
    clientes = dt.tabla_clientes(ventas)
    corr = clientes.corr(method="pearson")
    sp = dt.spearman(clientes)
    dist = dt.distribucion_gasto(clientes)

    if len(clientes) < 3:
        st.warning(
            f"Con {fm.num(len(clientes))} cliente(s) no hay datos suficientes para correlaciones ni "
            "pruebas de hipótesis: se necesitan al menos 3. Amplía el filtro."
        )
    elif corr.isna().any().any() or sp is None or dist is None or dist["gasto_log"].std() == 0:
        st.info("Los clientes de este filtro no varían lo suficiente para calcular correlaciones. Amplía el filtro.")
    else:
        th.signal_card(
            fm.num(sp["rho"], 2),
            "Spearman rho entre frecuencia de compra y gasto total",
        )
        col_mapa, col_dispersion = st.columns(2)
        with col_mapa, th.card("heatmap"):
            th.chart_title("Correlación de Pearson entre variables de cliente")
            mostrar(ch.heatmap_pearson(corr), "Mapa de calor de correlaciones de Pearson entre variables de cliente.")
        with col_dispersion, th.card("dispersion"):
            th.chart_title("Frecuencia vs gasto total (escala log)")
            mostrar(ch.dispersion_log(clientes), "Dispersión de frecuencia contra gasto total por cliente, en escala logarítmica.")

        pares = corr.abs().where(~np.eye(len(corr), dtype=bool)).stack()
        fuerte = pares.idxmax()
        r_pearson_fg = corr.loc["frecuencia", "gasto_total"]
        decision = "se rechaza" if sp["rechaza_h0"] else "no se puede rechazar"
        th.insight(
            f"La relación más fuerte es entre {fuerte[0]} y {fuerte[1]} (r = {fm.num(corr.loc[fuerte[0], fuerte[1]], 2)}).",
            f"Frecuencia y gasto total: Spearman rho = {fm.num(sp['rho'], 2)} frente a Pearson r = "
            f"{fm.num(r_pearson_fg, 2)} sobre {fm.num(sp['n'])} clientes.",
            f"Con {fm.p_valor(sp['p_valor'])} y α = {fm.num(sp['alpha'], 2)}, {decision} H₀ "
            "(no hay correlación entre frecuencia y gasto).",
        )

        with th.card("histograma"):
            th.chart_title("Gasto por cliente (log10) vs curva normal")
            mostrar(ch.histograma_log(dist["gasto_log"]), "Histograma del logaritmo del gasto por cliente con una curva normal superpuesta.")
        frases = [
            f"La media del gasto por cliente ({fm.libras(dist['media'], 2)}) es "
            f"{fm.num(dist['media'] / dist['mediana'], 1)} veces la mediana ({fm.libras(dist['mediana'], 2)}).",
            f"La asimetría es {fm.num(dist['asimetria'], 2)} en escala normal y "
            f"{fm.num(dist['asimetria_log'], 2)} en escala log10.",
        ]
        if abs(dist["asimetria_log"]) < abs(dist["asimetria"]):
            frases[-1] += " El logaritmo acerca la distribución a la campana de Gauss."
        th.insight(*frases)

th.status_bar("Fuente: UCI Machine Learning Repository · Online Retail II")
