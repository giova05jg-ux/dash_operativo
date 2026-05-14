import streamlit as st
import pandas as pd
import plotly.express as px

# ══════════════════════════════════════════════════════════════
# CONFIGURACIÓN GENERAL
# ══════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="Dashboard Producción Industrial",
    page_icon="🏭",
    layout="wide"
)

st.title("🏭 Dashboard de Producción Industrial")
st.markdown("### MetalParts Colombia S.A.S.")
st.markdown(
    "Dashboard interactivo para analizar producción, eficiencia, calidad, paros, costos, energía y cumplimiento."
)

# ══════════════════════════════════════════════════════════════
# CARGA DE DATOS
# ══════════════════════════════════════════════════════════════

@st.cache_data
def cargar_datos():
    df = pd.read_csv("caso3_produccion_dataset.csv")
    df["fecha_produccion"] = pd.to_datetime(df["fecha_produccion"])

    # Variables adicionales
    df["unidades_buenas"] = df["unidades_producidas"] - df["unidades_defectuosas"]

    df["cumplimiento_produccion_pct"] = (
        df["unidades_producidas"] / df["unidades_planificadas"]
    ) * 100

    df["costo_por_unidad"] = (
        df["costo_produccion_cop"] / df["unidades_producidas"]
    )

    df["energia_por_unidad"] = (
        df["consumo_energia_kwh"] / df["unidades_producidas"]
    )

    return df

df = cargar_datos()

# ══════════════════════════════════════════════════════════════
# SIDEBAR — FILTROS
# ══════════════════════════════════════════════════════════════

st.sidebar.header("🔎 Filtros del dashboard")

fecha_min = df["fecha_produccion"].min().date()
fecha_max = df["fecha_produccion"].max().date()

# Filtro manual de fechas sin selector tipo rango
st.sidebar.markdown("### 📅 Filtro de fechas")

fecha_inicio = st.sidebar.date_input(
    "Fecha inicial:",
    value=fecha_min,
    min_value=fecha_min,
    max_value=fecha_max
)

fecha_fin = st.sidebar.date_input(
    "Fecha final:",
    value=fecha_max,
    min_value=fecha_min,
    max_value=fecha_max
)

if fecha_inicio > fecha_fin:
    st.sidebar.error("⚠️ La fecha inicial no puede ser mayor que la fecha final.")
    st.stop()

st.sidebar.info(
    f"Rango aplicado: {fecha_inicio} → {fecha_fin}"
)

lineas = st.sidebar.multiselect(
    "Línea de producción:",
    options=sorted(df["linea_produccion"].unique()),
    default=sorted(df["linea_produccion"].unique())
)

turnos = st.sidebar.multiselect(
    "Turno:",
    options=sorted(df["turno"].unique()),
    default=sorted(df["turno"].unique())
)

maquinas = st.sidebar.multiselect(
    "Máquina:",
    options=sorted(df["maquina"].unique()),
    default=sorted(df["maquina"].unique())
)

productos = st.sidebar.multiselect(
    "Producto:",
    options=sorted(df["producto"].unique()),
    default=sorted(df["producto"].unique())
)

semanas = st.sidebar.multiselect(
    "Semana:",
    options=sorted(df["semana"].unique()),
    default=sorted(df["semana"].unique())
)

# ══════════════════════════════════════════════════════════════
# APLICAR FILTROS
# ══════════════════════════════════════════════════════════════

df_filtrado = df[
    (df["fecha_produccion"].dt.date >= fecha_inicio) &
    (df["fecha_produccion"].dt.date <= fecha_fin) &
    (df["linea_produccion"].isin(lineas)) &
    (df["turno"].isin(turnos)) &
    (df["maquina"].isin(maquinas)) &
    (df["producto"].isin(productos)) &
    (df["semana"].isin(semanas))
].copy()

if df_filtrado.empty:
    st.warning("⚠️ No hay datos disponibles con los filtros seleccionados.")
    st.stop()

# ══════════════════════════════════════════════════════════════
# KPIs PRINCIPALES
# ══════════════════════════════════════════════════════════════

eficiencia_promedio = df_filtrado["eficiencia_pct"].mean()
tasa_defectos_promedio = df_filtrado["tasa_defectos_pct"].mean()
total_planificadas = df_filtrado["unidades_planificadas"].sum()
total_producidas = df_filtrado["unidades_producidas"].sum()
total_defectuosas = df_filtrado["unidades_defectuosas"].sum()
total_buenas = df_filtrado["unidades_buenas"].sum()
cumplimiento_promedio = (total_producidas / total_planificadas) * 100
tiempo_paro_total = df_filtrado["tiempo_paro_min"].sum()
tiempo_ciclo_promedio = df_filtrado["tiempo_ciclo_min"].mean()
energia_total = df_filtrado["consumo_energia_kwh"].sum()
costo_total = df_filtrado["costo_produccion_cop"].sum()
costo_unitario_promedio = costo_total / total_producidas
energia_unitaria = energia_total / total_producidas

st.markdown("## 📌 Indicadores generales")

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("Eficiencia promedio", f"{eficiencia_promedio:.2f}%")
col2.metric("Tasa defectos", f"{tasa_defectos_promedio:.2f}%")
col3.metric("Cumplimiento", f"{cumplimiento_promedio:.2f}%")
col4.metric("Unidades producidas", f"{total_producidas:,.0f}")
col5.metric("Unidades defectuosas", f"{total_defectuosas:,.0f}")

col6, col7, col8, col9, col10 = st.columns(5)

col6.metric("Tiempo paro total", f"{tiempo_paro_total:,.1f} min")
col7.metric("Tiempo ciclo prom.", f"{tiempo_ciclo_promedio:.2f} min")
col8.metric("Energía total", f"{energia_total:,.1f} kWh")
col9.metric("Costo total", f"${costo_total:,.0f}")
col10.metric("Costo por unidad", f"${costo_unitario_promedio:,.0f}")

st.markdown("---")

# ══════════════════════════════════════════════════════════════
# AGRUPACIONES PRINCIPALES
# ══════════════════════════════════════════════════════════════

eficiencia_linea = (
    df_filtrado.groupby("linea_produccion")
    .agg(
        eficiencia_promedio=("eficiencia_pct", "mean"),
        unidades_planificadas=("unidades_planificadas", "sum"),
        unidades_producidas=("unidades_producidas", "sum"),
        unidades_defectuosas=("unidades_defectuosas", "sum"),
        tiempo_paro_total=("tiempo_paro_min", "sum"),
        tiempo_ciclo_promedio=("tiempo_ciclo_min", "mean"),
        energia_total=("consumo_energia_kwh", "sum"),
        costo_total=("costo_produccion_cop", "sum")
    )
    .reset_index()
)

eficiencia_linea["cumplimiento_pct"] = (
    eficiencia_linea["unidades_producidas"] / eficiencia_linea["unidades_planificadas"]
) * 100

eficiencia_linea["costo_por_unidad"] = (
    eficiencia_linea["costo_total"] / eficiencia_linea["unidades_producidas"]
)

eficiencia_linea["energia_por_unidad"] = (
    eficiencia_linea["energia_total"] / eficiencia_linea["unidades_producidas"]
)

eficiencia_linea = eficiencia_linea.sort_values(
    by="eficiencia_promedio",
    ascending=False
)

defectos_turno = (
    df_filtrado.groupby("turno")
    .agg(
        defectos_totales=("unidades_defectuosas", "sum"),
        unidades_producidas=("unidades_producidas", "sum"),
        tasa_defectos_promedio=("tasa_defectos_pct", "mean")
    )
    .reset_index()
    .sort_values("defectos_totales", ascending=False)
)

defectos_turno_linea = (
    df_filtrado.groupby(["turno", "linea_produccion"])
    .agg(
        defectos_totales=("unidades_defectuosas", "sum"),
        unidades_producidas=("unidades_producidas", "sum"),
        tasa_defectos_promedio=("tasa_defectos_pct", "mean")
    )
    .reset_index()
)

paro_maquina = (
    df_filtrado.groupby("maquina")
    .agg(
        tiempo_paro_total=("tiempo_paro_min", "sum"),
        tiempo_paro_promedio=("tiempo_paro_min", "mean"),
        defectos_totales=("unidades_defectuosas", "sum"),
        eficiencia_promedio=("eficiencia_pct", "mean"),
        ordenes=("id_orden", "count")
    )
    .reset_index()
    .sort_values("tiempo_paro_total", ascending=False)
)

produccion_semanal = (
    df_filtrado.groupby("semana")
    .agg(
        unidades_planificadas=("unidades_planificadas", "sum"),
        unidades_producidas=("unidades_producidas", "sum"),
        unidades_defectuosas=("unidades_defectuosas", "sum"),
        eficiencia_promedio=("eficiencia_pct", "mean"),
        tasa_defectos_promedio=("tasa_defectos_pct", "mean"),
        tiempo_paro_total=("tiempo_paro_min", "sum"),
        energia_total=("consumo_energia_kwh", "sum"),
        costo_total=("costo_produccion_cop", "sum")
    )
    .reset_index()
    .sort_values("semana")
)

produccion_semanal["cumplimiento_pct"] = (
    produccion_semanal["unidades_producidas"] / produccion_semanal["unidades_planificadas"]
) * 100

produccion_semanal["brecha_unidades"] = (
    produccion_semanal["unidades_planificadas"] - produccion_semanal["unidades_producidas"]
)

causas_paro = (
    df_filtrado.groupby("causa_paro")
    .agg(
        frecuencia=("id_orden", "count"),
        tiempo_paro_total=("tiempo_paro_min", "sum"),
        tiempo_paro_promedio=("tiempo_paro_min", "mean"),
        defectos_totales=("unidades_defectuosas", "sum")
    )
    .reset_index()
    .sort_values("tiempo_paro_total", ascending=False)
)

producto_resumen = (
    df_filtrado.groupby("producto")
    .agg(
        unidades_planificadas=("unidades_planificadas", "sum"),
        unidades_producidas=("unidades_producidas", "sum"),
        unidades_defectuosas=("unidades_defectuosas", "sum"),
        eficiencia_promedio=("eficiencia_pct", "mean"),
        tasa_defectos_promedio=("tasa_defectos_pct", "mean"),
        tiempo_ciclo_promedio=("tiempo_ciclo_min", "mean"),
        energia_total=("consumo_energia_kwh", "sum"),
        costo_total=("costo_produccion_cop", "sum")
    )
    .reset_index()
)

producto_resumen["cumplimiento_pct"] = (
    producto_resumen["unidades_producidas"] / producto_resumen["unidades_planificadas"]
) * 100

producto_resumen["costo_por_unidad"] = (
    producto_resumen["costo_total"] / producto_resumen["unidades_producidas"]
)

producto_resumen["energia_por_unidad"] = (
    producto_resumen["energia_total"] / producto_resumen["unidades_producidas"]
)

producto_resumen = producto_resumen.sort_values(
    "tasa_defectos_promedio",
    ascending=False
)

maquinas_criticas = (
    df_filtrado.groupby("maquina")
    .agg(
        tiempo_paro_total=("tiempo_paro_min", "sum"),
        defectos_totales=("unidades_defectuosas", "sum"),
        eficiencia_promedio=("eficiencia_pct", "mean"),
        tasa_defectos_promedio=("tasa_defectos_pct", "mean"),
        tiempo_ciclo_promedio=("tiempo_ciclo_min", "mean"),
        energia_total=("consumo_energia_kwh", "sum"),
        costo_total=("costo_produccion_cop", "sum"),
        ordenes=("id_orden", "count")
    )
    .reset_index()
    .sort_values(["tiempo_paro_total", "defectos_totales"], ascending=False)
)

ordenes_criticas = df_filtrado[df_filtrado["tasa_defectos_pct"] > 10].copy()

# ══════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    [
        "📊 Producción",
        "⚠️ Calidad",
        "⏱️ Paros",
        "💰 Costos y energía",
        "📌 Análisis integral",
        "📥 Datos"
    ]
)

# ══════════════════════════════════════════════════════════════
# TAB 1 — PRODUCCIÓN
# ══════════════════════════════════════════════════════════════

with tab1:
    st.subheader("📊 Análisis de producción y eficiencia")

    col_g1, col_g2 = st.columns(2)

    fig1 = px.box(
        df_filtrado,
        x="linea_produccion",
        y="eficiencia_pct",
        color="linea_produccion",
        points="all",
        title="Distribución de eficiencia por línea",
        labels={
            "linea_produccion": "Línea de producción",
            "eficiencia_pct": "Eficiencia (%)"
        }
    )
    fig1.update_layout(showlegend=False, yaxis_range=[0, 100])

    fig2 = px.line(
        produccion_semanal,
        x="semana",
        y=["unidades_planificadas", "unidades_producidas"],
        markers=True,
        title="Producción semanal: planificado vs producido",
        labels={
            "semana": "Semana",
            "value": "Unidades",
            "variable": "Indicador"
        }
    )

    with col_g1:
        st.plotly_chart(fig1, use_container_width=True)

    with col_g2:
        st.plotly_chart(fig2, use_container_width=True)

    col_g3, col_g4 = st.columns(2)

    fig3 = px.bar(
        eficiencia_linea,
        x="linea_produccion",
        y="cumplimiento_pct",
        text="cumplimiento_pct",
        title="Cumplimiento de producción por línea",
        labels={
            "linea_produccion": "Línea de producción",
            "cumplimiento_pct": "Cumplimiento (%)"
        }
    )
    fig3.update_traces(texttemplate="%{text:.2f}%", textposition="outside")
    fig3.update_layout(yaxis_range=[0, 110])

    fig4 = px.bar(
        produccion_semanal,
        x="semana",
        y="brecha_unidades",
        text="brecha_unidades",
        title="Brecha semanal entre planificado y producido",
        labels={
            "semana": "Semana",
            "brecha_unidades": "Brecha de unidades"
        }
    )
    fig4.update_traces(texttemplate="%{text:,.0f}", textposition="outside")

    with col_g3:
        st.plotly_chart(fig3, use_container_width=True)

    with col_g4:
        st.plotly_chart(fig4, use_container_width=True)

    st.markdown("### Tabla resumen por línea")
    st.dataframe(eficiencia_linea, use_container_width=True)

# ══════════════════════════════════════════════════════════════
# TAB 2 — CALIDAD
# ══════════════════════════════════════════════════════════════

with tab2:
    st.subheader("⚠️ Análisis de calidad y defectos")

    col_q1, col_q2 = st.columns(2)

    fig5 = px.violin(
        df_filtrado,
        x="turno",
        y="tasa_defectos_pct",
        color="turno",
        box=True,
        points="all",
        title="Distribución de tasa de defectos por turno",
        labels={
            "turno": "Turno",
            "tasa_defectos_pct": "Tasa de defectos (%)"
        }
    )
    fig5.update_layout(showlegend=False)

    fig6 = px.bar(
        defectos_turno_linea,
        x="turno",
        y="defectos_totales",
        color="linea_produccion",
        barmode="group",
        text="defectos_totales",
        title="Defectos por turno y línea",
        labels={
            "turno": "Turno",
            "defectos_totales": "Unidades defectuosas",
            "linea_produccion": "Línea de producción"
        }
    )
    fig6.update_traces(texttemplate="%{text:,.0f}", textposition="outside")

    with col_q1:
        st.plotly_chart(fig5, use_container_width=True)

    with col_q2:
        st.plotly_chart(fig6, use_container_width=True)

    col_q3, col_q4 = st.columns(2)

    fig7 = px.scatter(
        df_filtrado,
        x="temperatura_c",
        y="tasa_defectos_pct",
        color="linea_produccion",
        trendline="ols",
        hover_data=["id_orden", "producto", "turno", "maquina"],
        title="Temperatura vs tasa de defectos",
        labels={
            "temperatura_c": "Temperatura (°C)",
            "tasa_defectos_pct": "Tasa de defectos (%)"
        }
    )

    fig8 = px.bar(
        producto_resumen,
        x="producto",
        y="tasa_defectos_promedio",
        text="tasa_defectos_promedio",
        title="Tasa promedio de defectos por producto",
        labels={
            "producto": "Producto",
            "tasa_defectos_promedio": "Tasa defectos (%)"
        }
    )
    fig8.update_traces(texttemplate="%{text:.2f}%", textposition="outside")
    fig8.update_layout(xaxis_tickangle=-45)

    with col_q3:
        st.plotly_chart(fig7, use_container_width=True)

    with col_q4:
        st.plotly_chart(fig8, use_container_width=True)

    st.markdown("### 🚨 Órdenes críticas con defectos mayores al 10%")

    if ordenes_criticas.empty:
        st.success("✅ No hay órdenes críticas con defectos mayores al 10% en el filtro seleccionado.")
    else:
        st.warning(f"Se encontraron {len(ordenes_criticas)} órdenes críticas.")
        st.dataframe(
            ordenes_criticas[
                [
                    "id_orden",
                    "fecha_produccion",
                    "linea_produccion",
                    "producto",
                    "turno",
                    "maquina",
                    "unidades_producidas",
                    "unidades_defectuosas",
                    "tasa_defectos_pct",
                    "temperatura_c"
                ]
            ].sort_values("tasa_defectos_pct", ascending=False),
            use_container_width=True
        )

# ══════════════════════════════════════════════════════════════
# TAB 3 — PAROS
# ══════════════════════════════════════════════════════════════

with tab3:
    st.subheader("⏱️ Análisis de tiempos de paro")

    col_p1, col_p2 = st.columns(2)

    fig9 = px.bar(
        paro_maquina,
        x="tiempo_paro_total",
        y="maquina",
        orientation="h",
        text="tiempo_paro_total",
        title="Tiempo total de paro por máquina",
        labels={
            "tiempo_paro_total": "Tiempo total de paro (min)",
            "maquina": "Máquina"
        }
    )
    fig9.update_traces(texttemplate="%{text:.1f}", textposition="outside")
    fig9.update_layout(yaxis={"categoryorder": "total ascending"})

    fig10 = px.bar(
        causas_paro,
        x="causa_paro",
        y="tiempo_paro_total",
        text="tiempo_paro_total",
        title="Tiempo total de paro por causa",
        labels={
            "causa_paro": "Causa de paro",
            "tiempo_paro_total": "Tiempo total de paro (min)"
        }
    )
    fig10.update_traces(texttemplate="%{text:.1f}", textposition="outside")
    fig10.update_layout(xaxis_tickangle=-45)

    with col_p1:
        st.plotly_chart(fig9, use_container_width=True)

    with col_p2:
        st.plotly_chart(fig10, use_container_width=True)

    fig11 = px.scatter(
        maquinas_criticas,
        x="tiempo_paro_total",
        y="defectos_totales",
        size="ordenes",
        color="eficiencia_promedio",
        hover_name="maquina",
        title="Máquinas críticas: paros vs defectos",
        labels={
            "tiempo_paro_total": "Tiempo total de paro (min)",
            "defectos_totales": "Unidades defectuosas",
            "eficiencia_promedio": "Eficiencia promedio (%)"
        }
    )

    st.plotly_chart(fig11, use_container_width=True)

    st.markdown("### Ranking de máquinas críticas")
    st.dataframe(maquinas_criticas, use_container_width=True)

# ══════════════════════════════════════════════════════════════
# TAB 4 — COSTOS Y ENERGÍA
# ══════════════════════════════════════════════════════════════

with tab4:
    st.subheader("💰 Análisis de costos y consumo energético")

    col_c1, col_c2 = st.columns(2)

    fig12 = px.bar(
        eficiencia_linea.sort_values("costo_por_unidad", ascending=False),
        x="linea_produccion",
        y="costo_por_unidad",
        text="costo_por_unidad",
        title="Costo promedio por unidad producida por línea",
        labels={
            "linea_produccion": "Línea de producción",
            "costo_por_unidad": "Costo por unidad (COP)"
        }
    )
    fig12.update_traces(
        texttemplate="$%{text:,.0f}",
        textposition="outside"
    )
    fig12.update_layout(
        uniformtext_minsize=8,
        uniformtext_mode="hide"
    )

    fig13 = px.bar(
        eficiencia_linea.sort_values("energia_por_unidad", ascending=False),
        x="linea_produccion",
        y="energia_por_unidad",
        text="energia_por_unidad",
        title="Consumo energético por unidad según línea",
        labels={
            "linea_produccion": "Línea de producción",
            "energia_por_unidad": "kWh por unidad"
        }
    )
    fig13.update_traces(
        texttemplate="%{text:.4f}",
        textposition="outside"
    )
    fig13.update_layout(
        uniformtext_minsize=8,
        uniformtext_mode="hide"
    )

    with col_c1:
        st.plotly_chart(fig12, use_container_width=True)

    with col_c2:
        st.plotly_chart(fig13, use_container_width=True)

    st.markdown("### Tabla de costos y energía por línea")

    tabla_costos_energia = eficiencia_linea[
        [
            "linea_produccion",
            "costo_total",
            "costo_por_unidad",
            "energia_total",
            "energia_por_unidad",
            "unidades_producidas",
            "unidades_defectuosas"
        ]
    ].copy()

    tabla_costos_energia["costo_total"] = tabla_costos_energia["costo_total"].round(0)
    tabla_costos_energia["costo_por_unidad"] = tabla_costos_energia["costo_por_unidad"].round(0)
    tabla_costos_energia["energia_total"] = tabla_costos_energia["energia_total"].round(2)
    tabla_costos_energia["energia_por_unidad"] = tabla_costos_energia["energia_por_unidad"].round(4)

    st.dataframe(tabla_costos_energia, use_container_width=True)

# ══════════════════════════════════════════════════════════════
# TAB 5 — ANÁLISIS INTEGRAL
# ══════════════════════════════════════════════════════════════

with tab5:
    st.subheader("📌 Análisis integral para responder preguntas gerenciales")

    col_i1, col_i2 = st.columns(2)

    fig15 = px.box(
        df_filtrado,
        x="linea_produccion",
        y="tiempo_ciclo_min",
        color="linea_produccion",
        points="all",
        title="Distribución del tiempo ciclo por línea",
        labels={
            "linea_produccion": "Línea de producción",
            "tiempo_ciclo_min": "Tiempo ciclo (min)"
        }
    )
    fig15.update_layout(showlegend=False)

    fig16 = px.line(
        produccion_semanal,
        x="semana",
        y=[
            "eficiencia_promedio",
            "tasa_defectos_promedio",
            "cumplimiento_pct"
        ],
        markers=True,
        title="Evolución semanal de eficiencia, defectos y cumplimiento",
        labels={
            "semana": "Semana",
            "value": "Porcentaje (%)",
            "variable": "Indicador"
        }
    )

    with col_i1:
        st.plotly_chart(fig15, use_container_width=True)

    with col_i2:
        st.plotly_chart(fig16, use_container_width=True)

    matriz_linea_turno = (
        df_filtrado.groupby(["linea_produccion", "turno"])
        .agg(
            tasa_defectos_promedio=("tasa_defectos_pct", "mean"),
            eficiencia_promedio=("eficiencia_pct", "mean"),
            tiempo_paro_total=("tiempo_paro_min", "sum"),
            unidades_producidas=("unidades_producidas", "sum")
        )
        .reset_index()
    )

    fig17 = px.density_heatmap(
        matriz_linea_turno,
        x="turno",
        y="linea_produccion",
        z="tasa_defectos_promedio",
        text_auto=".2f",
        title="Heatmap de tasa de defectos por línea y turno",
        labels={
            "turno": "Turno",
            "linea_produccion": "Línea de producción",
            "tasa_defectos_promedio": "Tasa defectos (%)"
        }
    )

    st.plotly_chart(fig17, use_container_width=True)

    st.markdown("### Tabla gerencial por línea")
    st.dataframe(eficiencia_linea, use_container_width=True)

    st.markdown("### Resumen por producto")
    st.dataframe(producto_resumen, use_container_width=True)

    st.markdown("### Evolución semanal integral")
    st.dataframe(produccion_semanal, use_container_width=True)

# ══════════════════════════════════════════════════════════════
# TAB 6 — DATOS Y DESCARGA
# ══════════════════════════════════════════════════════════════

with tab6:
    st.subheader("📥 Dataset filtrado")

    st.write(f"Registros disponibles después de aplicar filtros: {len(df_filtrado)}")

    st.dataframe(df_filtrado, use_container_width=True)

    csv = df_filtrado.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="📥 Descargar dataset filtrado en CSV",
        data=csv,
        file_name="dataset_filtrado_caso3_produccion.csv",
        mime="text/csv"
    )

# ══════════════════════════════════════════════════════════════
# INSIGHTS AUTOMÁTICOS
# ══════════════════════════════════════════════════════════════

st.markdown("---")
st.subheader("🧠 Insights automáticos")

linea_mayor_eficiencia = eficiencia_linea.sort_values("eficiencia_promedio", ascending=False).iloc[0]
linea_menor_eficiencia = eficiencia_linea.sort_values("eficiencia_promedio", ascending=True).iloc[0]
linea_mayor_defectos = eficiencia_linea.sort_values("unidades_defectuosas", ascending=False).iloc[0]
linea_mayor_paro = eficiencia_linea.sort_values("tiempo_paro_total", ascending=False).iloc[0]
linea_mayor_costo = eficiencia_linea.sort_values("costo_por_unidad", ascending=False).iloc[0]
linea_mayor_energia = eficiencia_linea.sort_values("energia_por_unidad", ascending=False).iloc[0]

producto_mas_defectuoso = producto_resumen.sort_values("tasa_defectos_promedio", ascending=False).iloc[0]
maquina_critica = maquinas_criticas.sort_values(["tiempo_paro_total", "defectos_totales"], ascending=False).iloc[0]
semana_menor_cumplimiento = produccion_semanal.sort_values("cumplimiento_pct", ascending=True).iloc[0]

correlacion_temp_defectos = df_filtrado["temperatura_c"].corr(df_filtrado["tasa_defectos_pct"])

st.markdown(
    f"""
    - La línea con mayor eficiencia promedio es **{linea_mayor_eficiencia["linea_produccion"]}**, con **{linea_mayor_eficiencia["eficiencia_promedio"]:.2f}%**.

    - La línea con menor eficiencia promedio es **{linea_menor_eficiencia["linea_produccion"]}**, con **{linea_menor_eficiencia["eficiencia_promedio"]:.2f}%**.

    - La línea con mayor cantidad de unidades defectuosas es **{linea_mayor_defectos["linea_produccion"]}**, con **{linea_mayor_defectos["unidades_defectuosas"]:,.0f}** unidades defectuosas.

    - La línea con mayor tiempo total de paro es **{linea_mayor_paro["linea_produccion"]}**, con **{linea_mayor_paro["tiempo_paro_total"]:,.1f} minutos**.

    - La línea con mayor costo por unidad es **{linea_mayor_costo["linea_produccion"]}**, con **${linea_mayor_costo["costo_por_unidad"]:,.0f} COP por unidad**.

    - La línea con mayor consumo energético por unidad es **{linea_mayor_energia["linea_produccion"]}**, con **{linea_mayor_energia["energia_por_unidad"]:.4f} kWh por unidad**.

    - El producto con mayor tasa promedio de defectos es **{producto_mas_defectuoso["producto"]}**, con **{producto_mas_defectuoso["tasa_defectos_promedio"]:.2f}%**.

    - La máquina más crítica es **{maquina_critica["maquina"]}**, porque acumula **{maquina_critica["tiempo_paro_total"]:,.1f} minutos de paro** y **{maquina_critica["defectos_totales"]:,.0f} defectos**.

    - La semana con menor cumplimiento fue la **semana {semana_menor_cumplimiento["semana"]}**, con un cumplimiento de **{semana_menor_cumplimiento["cumplimiento_pct"]:.2f}%**.

    - La correlación entre temperatura y tasa de defectos es **{correlacion_temp_defectos:.3f}**.
    """
)

# ══════════════════════════════════════════════════════════════
# PIE DE PÁGINA
# ══════════════════════════════════════════════════════════════

st.markdown("---")

st.markdown(
    """
    <div style="
        text-align: center;
        color: #6c757d;
        font-size: 14px;
        padding: 18px 0 8px 0;
        margin-top: 20px;
    ">
        Visualización de Datos | Pablo Cendales - Giovanni Jiménez
    </div>
    """,
    unsafe_allow_html=True
)