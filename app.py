# SPDX-FileCopyrightText: 2026 Pedro Sordo Martínez <amurlaniakea@gmail.com>
#!/usr/bin/env python3
"""Interfaz visual interactiva para pathogen-forecast (streamlit + folium)."""
# Copyright (C) 2026 Pedro Sordo Martínez <amurlaniakea@gmail.com>
# SPDX-License-Identifier: AGPL-3.0-or-later

from pathlib import Path

import folium
import streamlit as st
from streamlit_folium import st_folium

from data_loader import DataLoader
from epimodels import ModeloSEIR
from optimizer import OptimizadorSIR

st.set_page_config(page_title="pathogen-forecast", layout="wide")
st.title("pathogen-forecast — Predicción epidemiológica institucional")
st.markdown("**Autor:** Pedro Sordo Martínez <amurlaniakea@gmail.com> | **Licencia:** AGPL-3.0-or-later")

# Controles interactivos
col1, col2 = st.columns(2)
with col1:
    r_contagiosidad = st.slider("R de contagiosidad (reproduction_rate aproximado)", 0.5, 10.0, 3.0, 0.1)
    dias = st.slider("Días de simulación", 30, 730, 365, 30)
with col2:
    pais = st.selectbox("País inicial (ejemplo del dataset)", ["Spain", "Afghanistan", "United States", "Global"])
    poblacion = st.number_input("Población base (millones)", 1.0, 8000.0, 8.0, 1.0) * 1_000_000

import os

# Datos sintéticos por defecto (o dataset real si existe, vía env var)
ruta_env = os.getenv("COVID_DATASET_PATH", "")
ruta_dataset = Path(ruta_env) if ruta_env else Path(__file__).resolve().parent.parent / "tests" / "fixtures" / "synthetic_covid.csv"
if ruta_dataset.exists():
    loader = DataLoader(ruta_dataset)
    datos = loader.cargar_datos()
else:
    loader = DataLoader(Path(__file__).resolve().parent.parent / "tests" / "fixtures" / "synthetic_covid.csv")
    datos = loader.cargar_datos()

# Calibración (opcional, con datos sintéticos/reales)
if datos:
    optimizador = OptimizadorSIR(datos)
    try:
        beta_cal, gamma_cal = optimizador.calibrar(N=poblacion)
        st.success(f"Calibración real completada: beta={beta_cal:.3f}, gamma={gamma_cal:.3f}, R0={beta_cal/gamma_cal:.2f}")
    except (ValueError, RuntimeError) as e:
        beta_cal, gamma_cal = 0.3, 0.1
        st.warning(f"Calibración con datos sintéticos de respaldo (error con datos reales: {e})")
else:
    beta_cal, gamma_cal = 0.3, 0.1
    st.info("Usando parámetros por defecto (sin datos disponibles).")

# Simulación SEIR (con latencia)
modelo = ModeloSEIR(beta=beta_cal, gamma=gamma_cal, sigma=0.2, N=poblacion)
t, y = modelo.simular(S0=poblacion - 100, E0=50, I0=100, R0=0, dias=dias)

# Métricas SEIR
S_final, E_final, I_final, R_final = y[:, -1]
col3, col4, col5, col6 = st.columns(4)
with col3:
    st.metric("Susceptibles finales", f"{S_final:,.0f}")
with col4:
    st.metric("Expuestos finales", f"{E_final:,.0f}")
with col5:
    st.metric("Infectados finales", f"{I_final:,.0f}")
with col6:
    st.metric("Recuperados finales", f"{R_final:,.0f}")

# Mapa interactivo (mapamundi básico con ubicación inicial)
m = folium.Map(location=[20.0, 0.0], zoom_start=2, tiles="cartodbpositron")
folium.CircleMarker(
    location=[40.4168, -3.7038],  # Ejemplo: Madrid (España)
    radius=10,
    popup=f"País inicial: {pais}\nR aproximado: {r_contagiosidad}\nSimulación: {dias} días",
    color="red",
    fill=True,
).add_to(m)

# Añadir puntos simulados de expansión (simplificado: puntos aleatorios alrededor del mundo)
import random

random.seed(42)
for _ in range(20):
    lat = random.uniform(-60, 60)
    lon = random.uniform(-180, 180)
    folium.CircleMarker(
        location=[lat, lon],
        radius=3,
        color="orange",
        fill=True,
        fill_opacity=0.6,
    ).add_to(m)

st.subheader("Mapa mundial interactivo de expansión simulada")
st_folium(m, width=1200, height=600)

# Nota de verificación
st.info("Nota: esta interfaz usa datos sintéticos por defecto o datos reales del dataset de Kaggle (`reproduction_rate` como referencia) para calibración. La expansión visual es una simulación teórica basada en el modelo SEIR básico.")
