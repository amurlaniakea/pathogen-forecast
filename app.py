#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Pedro Sordo Martínez <amurlaniakea@gmail.com>
# SPDX-License-Identifier: AGPL-3.0-or-later
"""
Simulador SEIR de Población Única con Calibración Histórica.
Nota de honestidad: Este modelo asume una población homogénea y mezclada.
No modela movilidad ni transmisión entre diferentes países.
"""

import os
import sys
from pathlib import Path

# Asegurar que Streamlit encuentre los módulos dentro de la carpeta src/
sys.path.append(str(Path(__file__).resolve().parent / "src"))

import folium
import numpy as np
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

from data_loader import DataLoader
from epimodels import ModeloSEIR
from optimizer import OptimizadorSIR

st.set_page_config(page_title="Pathogen Forecast (SEIR)", layout="wide")
st.title("🦠 Pathogen Forecast — Simulador SEIR de Población Única")
st.markdown("**Autor:** Pedro Sordo Martínez <amurlaniakea@gmail.com> | **Licencia:** AGPL-3.0-or-later")

st.info("⚠️ **Nota metodológica**: Este simulador utiliza un modelo SEIR de compartimentos únicos. Asume una población homogénea y mezclada. **No modela movilidad ni transmisión entre países**. La calibración se realiza exclusivamente con los datos históricos del país seleccionado.")

# --- 1. CONTROLES INTERACTIVOS ---
col1, col2 = st.columns(2)
with col1:
    pais_inicial = st.selectbox(
        "País a simular y calibrar",
        ["Spain", "Afghanistan", "United States", "China", "Brazil", "South Africa"]
    )
    poblacion = st.number_input("Población base (millones)", 1.0, 8000.0, 8.0, 1.0) * 1_000_000

with col2:
    r_objetivo = st.slider("R0 de contagiosidad (Escenario What-If)", 0.5, 10.0, 3.0, 0.1)
    dias = st.slider("Días de proyección", 30, 730, 365, 30)

COORDENADAS_PAISES = {
    "Spain": [40.4637, -3.7492],
    "Afghanistan": [33.9391, 67.7099],
    "United States": [37.0902, -95.7129],
    "China": [35.8617, 104.1954],
    "Brazil": [-14.2350, -51.9253],
    "South Africa": [-30.5595, 22.9375],
}

# --- 2. CARGA Y FILTRADO DE DATOS ---
ruta_env = os.getenv("COVID_DATASET_PATH", "")
ruta_dataset = Path(ruta_env) if ruta_env else Path(__file__).resolve().parent / "tests" / "fixtures" / "synthetic_covid.csv"

datos_completos = pd.DataFrame()
if ruta_dataset.exists():
    loader = DataLoader(ruta_dataset)
    datos_completos = loader.cargar_datos()

# Filtrar estrictamente por el país seleccionado para la calibración
datos_pais = datos_completos[datos_completos["location"] == pais_inicial].sort_values("date").reset_index(drop=True)

# --- 3. CALIBRACIÓN Y SIMULACIÓN ---
if not datos_pais.empty:
    optimizador = OptimizadorSIR(datos_pais)
    try:
        beta_cal, gamma_cal = optimizador.calibrar(N=poblacion)
        r0_calibrado = beta_cal / gamma_cal if gamma_cal > 0 else 0
        st.success(f"✅ Calibrado con datos históricos de {pais_inicial}: β={beta_cal:.3f}, γ={gamma_cal:.3f}, R0 histórico ≈ {r0_calibrado:.2f}")
    except (ValueError, RuntimeError) as e:
        beta_cal, gamma_cal = 0.3, 0.1
        st.warning(f"⚠️ Fallo en calibración, usando parámetros por defecto: {e}")
else:
    beta_cal, gamma_cal = 0.3, 0.1
    st.info(f"ℹ️ Sin datos históricos para {pais_inicial}. Usando parámetros base (β=0.3, γ=0.1).")

# Ajuste dinámico: el slider modifica beta para forzar el R0 deseado por el usuario
gamma_estimado = gamma_cal if gamma_cal > 0 else 0.1
beta_ajustado = r_objetivo * gamma_estimado

modelo = ModeloSEIR(beta=beta_ajustado, gamma=gamma_estimado, sigma=0.2, N=poblacion)
t, y = modelo.simular(S0=poblacion - 100, E0=50, I0=100, R0=0, dias=dias)

# Validación de robustez matemática
if t is None or len(t) == 0:
    st.error("❌ Error crítico: La integración matemática (solve_ivp) falló.")
    st.stop()

# --- 4. VISUALIZACIÓN HONESTA (Curvas Temporales) ---
st.subheader(f"📈 Proyección temporal para {pais_inicial}")

df_chart = pd.DataFrame({
    "Día": t,
    "Susceptibles": y[0],
    "Expuestos": y[1],
    "Infectados Activos": y[2],
    "Recuperados": y[3]
}).set_index("Día")

# Métricas clave
dia_pico = int(t[np.argmax(y[2])])
pico_infeccion = int(np.max(y[2]))

col3, col4, col5 = st.columns(3)
col3.metric("Pico de Infectados", f"{pico_infeccion:,}", delta=f"Día {dia_pico}")
col4.metric("Infectados al final", f"{int(y[2][-1]):,}")
col5.metric("Recuperados al final", f"{int(y[3][-1]):,}")

# Gráfico de curvas SEIR (la salida real y honesta del modelo matemático)
st.line_chart(df_chart, use_container_width=True)

# --- 5. MAPA MINIMALISTA Y HONESTO ---
st.subheader("📍 Ubicación del foco de simulación")
col_map1, col_map2 = st.columns([3, 1])

with col_map1:
    coords = COORDENADAS_PAISES.get(pais_inicial, [20.0, 0.0])
    m = folium.Map(location=coords, zoom_start=4, tiles="OpenStreetMap")

    folium.CircleMarker(
        location=coords,
        radius=15,
        popup=f"<b>{pais_inicial}</b><br>Población: {poblacion:,.0f}<br>R0 simulado: {r_objetivo}",
        color="red", fill=True, fill_color="red", fill_opacity=0.6, weight=2
    ).add_to(m)

    st_folium(m, width=700, height=400)

with col_map2:
    st.markdown("""
    **Leyenda del Modelo:**
    - 🔴 **Punto rojo**: Foco único de la simulación.
    - **Sin flechas ni expansión**: El modelo SEIR estándar no calcula propagación geográfica entre nodos, solo la evolución temporal de una población cerrada.
    """)

st.caption("Desarrollado con fines educativos y de modelado teórico. No debe usarse para toma de decisiones sanitarias reales sin validación epidemiológica profesional.")
