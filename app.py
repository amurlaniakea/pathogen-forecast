#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Pedro Sordo Martínez <amurlaniakea@gmail.com>
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Interfaz visual interactiva para pathogen-forecast (streamlit + folium)."""

from pathlib import Path

import folium
import numpy as np
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

from data_loader import DataLoader
from epimodels import ModeloSEIR
from optimizer import OptimizadorSIR

st.set_page_config(page_title="Pathogen Forecast", layout="wide")
st.title("🦠 Pathogen Forecast — Predicción Epidemiológica Institucional")
st.markdown("**Autor:** Pedro Sordo Martínez <amurlaniakea@gmail.com> | **Licencia:** AGPL-3.0-or-later")

# --- 1. CONTROLES INTERACTIVOS ---
col1, col2 = st.columns(2)
with col1:
    r_objetivo = st.slider("R0 de contagiosidad (Escenario What-If)", 0.5, 10.0, 3.0, 0.1)
    dias = st.slider("Días de simulación", 30, 730, 365, 30)
with col2:
    pais_inicial = st.selectbox("País de origen del brote", ["Spain", "Afghanistan", "United States", "China", "Brazil", "South Africa", "Global"])
    poblacion = st.number_input("Población base (millones)", 1.0, 8000.0, 8.0, 1.0) * 1_000_000

COORDENADAS_PAISES = {
    "Spain": [40.4637, -3.7492],
    "Afghanistan": [33.9391, 67.7099],
    "United States": [37.0902, -95.7129],
    "China": [35.8617, 104.1954],
    "Brazil": [-14.2350, -51.9253],
    "South Africa": [-30.5595, 22.9375],
}

# --- 2. CARGA DE DATOS ---
import os

ruta_env = os.getenv("COVID_DATASET_PATH", "")
ruta_relativa = Path(__file__).resolve().parent / "tests" / "fixtures" / "synthetic_covid.csv"
ruta_dataset = Path(ruta_env) if ruta_env else ruta_relativa

if ruta_dataset.exists():
    loader = DataLoader(ruta_dataset)
    datos = loader.cargar_datos()
else:
    datos = pd.DataFrame({
        "location": ["Spain", "Afghanistan", "United States"],
        "total_cases": [10000, 5000, 50000],
        "reproduction_rate": [2.5, 3.0, 2.8],
        "new_cases": [10, 15, 25],
        "icu_patients": [5, 4, 7],
        "lat": [40.4637, 33.9391, 37.0902],
        "lon": [-3.7492, 67.7099, -95.7129],
    })

# --- 3. CALIBRACIÓN Y SIMULACIÓN ---
if datos is not None and not datos.empty:
    optimizador = OptimizadorSIR(datos)
    try:
        beta_cal, gamma_cal = optimizador.calibrar(N=poblacion)
        st.success(f"✅ Calibración exitosa: β={beta_cal:.3f}, γ={gamma_cal:.3f}, R0 base={beta_cal/gamma_cal:.2f}")
    except (ValueError, RuntimeError) as e:
        beta_cal, gamma_cal = 0.3, 0.1
        st.warning(f"⚠️ Usando parámetros de respaldo (Error en calibración: {e})")
else:
    beta_cal, gamma_cal = 0.3, 0.1

# Ajuste dinámico: el slider modifica beta para coincidir con el R0 deseado por el usuario
beta_ajustado = r_objetivo * gamma_cal

modelo = ModeloSEIR(beta=beta_ajustado, gamma=gamma_cal, sigma=0.2, N=poblacion)
t, y = modelo.simular(S0=poblacion - 100, E0=50, I0=100, R0=0, dias=dias)

# Validación de robustez matemática
if t is None or len(t) == 0:
    st.error("❌ Error crítico: La integración matemática (solve_ivp) falló. Revisa los parámetros.")
    st.stop()

# Métricas SEIR y cálculo del pico
S_final, E_final, I_final, R_final = y[:, -1]
dia_pico = int(t[np.argmax(y[2])])

col3, col4, col5, col6 = st.columns(4)
col3.metric("Susceptibles finales", f"{S_final:,.0f}")
col4.metric("Expuestos finales", f"{E_final:,.0f}")
col5.metric("Infectados activos (Pico)", f"{np.max(y[2]):,.0f}", delta=f"Día {dia_pico}")
col6.metric("Recuperados finales", f"{R_final:,.0f}")

# --- 4. MAPA INTERACTIVO PROFESIONAL ---
m = folium.Map(location=[20.0, 0.0], zoom_start=2, tiles="OpenStreetMap")

# Marcador del país de origen
if pais_inicial in COORDENADAS_PAISES:
    folium.CircleMarker(
        location=COORDENADAS_PAISES[pais_inicial],
        radius=18,
        popup=f"<b>📍 Origen: {pais_inicial}</b><br>Simulación a {dias} días<br>R0 objetivo: {r_objetivo}",
        color="blue", fill=True, fill_color="blue", fill_opacity=0.8, weight=2
    ).add_to(m)

# Visualización de expansión por país (AGREGADA: un solo marcador por país)
if {"lat", "lon", "location"}.issubset(datos.columns):
    datos_unicos = datos.drop_duplicates(subset=["location"], keep="last")
    for _, row in datos_unicos.iterrows():
        pais_nombre = str(row.get("location", "Desconocido"))
        lat, lon = float(row["lat"]), float(row["lon"])
        casos = float(row.get("total_cases", 1000))
        radio = min(50, max(5, int(casos / 10000)))
        if casos < 10000:
            color, severidad = "green", "Baja"
        elif casos < 100000:
            color, severidad = "orange", "Media"
        else:
            color, severidad = "red", "Alta"
        folium.CircleMarker(
            location=[lat, lon],
            radius=radio,
            popup=f"<b>{pais_nombre}</b><br>📊 Casos: {casos:,.0f}<br>⚠️ Severidad: {severidad}<br>🔄 R0 simulado: {r_objetivo}",
            color=color, fill=True, fill_color=color, fill_opacity=0.6
        ).add_to(m)
else:
    # Fallback: puntos aleatorios alrededor del mundo (como antes)
    import random
    random.seed(42)
    for _ in range(20):
        lat = random.uniform(-60, 60)
        lon = random.uniform(-180, 180)
        folium.CircleMarker(
            location=[lat, lon],
            radius=3,
            color="orange", fill=True, fill_opacity=0.6,
        ).add_to(m)

st.subheader("🌍 Mapa mundial interactivo de expansión simulada")
st_folium(m, width=1200, height=600)

st.info(
    "💡 **Nota técnica**: El radio y color de cada marcador reflejan la magnitud real de los casos. "
    "El slider 'R0 de contagiosidad' ajusta dinámicamente la tasa de transmisión (β) para proyectar escenarios 'what-if' en tiempo real."
)
