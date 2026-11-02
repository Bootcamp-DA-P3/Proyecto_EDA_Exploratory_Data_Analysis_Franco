# Análisis Exploratorio de Datos: Online Retail II

Análisis exploratorio (EDA) de las ventas de una tienda online británica de regalos y artículos de decoración, entre diciembre de 2009 y diciembre de 2011.

## Objetivo

Limpiar el dataset y responder preguntas de negocio: cuánto se vende, cuándo, qué productos, en qué países, cuánto se devuelve y qué clientes sostienen los ingresos.

## Dataset

- **Fuente:** [Online Retail II - UCI Machine Learning Repository](https://archive.ics.uci.edu/dataset/502/online+retail+ii)
- **Archivo:** `data/online_retail_II.csv`
- **Tamaño:** 1.067.371 filas y 8 columnas. Cada fila es un producto dentro de una factura.

| Columna | Descripción |
|---|---|
| `Invoice` | Número de factura. Si empieza con "C" es una devolución |
| `StockCode` | Código del producto |
| `Description` | Nombre del producto |
| `Quantity` | Unidades. Negativo en devoluciones |
| `InvoiceDate` | Fecha y hora de la factura |
| `Price` | Precio unitario en libras (£) |
| `Customer ID` | Identificador del cliente |
| `Country` | País del cliente |

## Estructura del proyecto

```
├── .streamlit/
│   └── config.toml                # Tema de la app
├── app/
│   ├── streamlit_app.py           # App interactiva
│   ├── data.py                    # Limpieza y cálculos (mismo pipeline del notebook)
│   ├── charts.py                  # Gráficos Plotly
│   ├── theme.py                   # Tokens de diseño y estilos
│   └── formato.py                 # Formato de números y fechas en español
├── data/                          # Dataset original
├── notebooks/
│   └── 01_eda_online_retail.ipynb # Análisis completo
├── reports/                       # Reportes y gráficos
├── requirements.txt
└── README.md
```

## Proceso

**Limpieza (secciones 1 a 17)**
- Se eliminaron las filas sin `Customer ID`, los duplicados exactos y los productos con precio 0.
- Se convirtió `InvoiceDate` a fecha y `Customer ID` a entero.
- Se separaron las ventas de las devoluciones.
- Se eliminaron dos pares de compra y devolución atípicos, interpretados como errores de carga.
- Resultado: 779.423 líneas de venta.

**Análisis (secciones 18 a 23)**
- KPIs generales y ticket por factura.
- Evolución mensual de ingresos.
- Productos más vendidos por ingresos y por unidades.
- Ingresos por país.
- Análisis de devoluciones.
- Concentración de clientes (Pareto).

**Estadística (secciones 24 a 26)**
- Correlaciones de Pearson entre variables de cliente (mapa de calor) y diagrama de dispersión frecuencia vs gasto.
- Prueba de hipótesis con correlación de Spearman.
- Distribución del gasto por cliente comparada con la campana de Gauss.

## Principales hallazgos

- **Negocio:** £17.129.151 de ingresos, 36.967 facturas y 5.878 clientes. Ticket típico de £303 y 6,3 compras por cliente: perfil mayorista.
- **Estacionalidad:** el pico de ventas es en noviembre de ambos años, porque los clientes compran stock antes de Navidad.
- **Productos:** REGENCY CAKESTAND 3 TIER y WHITE HANGING HEART T-LIGHT HOLDER lideran en ingresos.
- **Mercado:** el Reino Unido concentra el 82,6% de los ingresos. El resto viene sobre todo de Europa.
- **Devoluciones:** representan el 4,9% de los ingresos, y el 43,8% de los clientes devolvió al menos una vez.
- **Clientes:** el 20% de los clientes genera el 76,9% de los ingresos.
- **Frecuencia y gasto:** relación fuerte y significativa (Spearman rho = 0,86, p < 0,001). Fomentar compras recurrentes es clave.
- **Distribución:** el gasto por cliente es log-normal y muy asimétrico (asimetría 25,83; en escala log 0,23), por eso se usaron mediana y Spearman.

## Tecnologías

Python, pandas, NumPy, SciPy, Matplotlib, Seaborn, Plotly, Streamlit y Jupyter Notebook.

## Cómo ejecutarlo

```bash
git clone <url-del-repositorio>
cd Proyecto_EDA_Exploratory_Data_Analysis_Franco
pip install -r requirements.txt
jupyter notebook notebooks/01_eda_online_retail.ipynb
```

## App interactiva

Una página con seis pestañas (ventas, productos, mercado, devoluciones, clientes y estadística) y filtros por país y rango de fechas en la barra lateral. La app repite la limpieza del notebook y calcula todos los valores en vivo: no guarda ningún número fijo. Con los filtros vacíos, los resultados coinciden con los del notebook.

```bash
streamlit run app/streamlit_app.py
```

Se abre en `http://localhost:8501`. El diseño (colores, tipografías y bordes rectos) está definido en `.streamlit/config.toml` y `app/theme.py`.

## Autor

Franco Recabarren, proyecto del bootcamp de Data Analytics de Factoría F5.
