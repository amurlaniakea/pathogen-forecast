---
title: Pathogen Forecast
emoji: 🦠
colorFrom: blue
colorTo: green
sdk: streamlit
app_file: app/app.py
pinned: false
---

# pathogen-forecast

> Modelo epidemiológico institucional (SIR/SEIR) con calibración real de datos COVID-19 (2020-2026), predicción de expansión pandémica y visualización interactiva en mapa mundial.

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0.txt)

Predice el crecimiento pandémico estimando R0 y Rt a partir de datos reales de Kaggle.

---

Por Pedro Sordo Martínez (Sil) — amurlaniakea@gmail.com

## Problema

El dataset "Global COVID-19 Pandemic Full Data 2020-2026" (Ali Ahmad, Kaggle) consolida métricas epidemiológicas globales, pero NO entrega el índice de contagiosidad puro (R0) como variable directa. Es necesario derivarlo matemáticamente para modelar proyecciones de crecimiento.

## Solución

Este repositorio estructura un flujo SDD para calcular R0 y el Rt variable a partir del CSV de Kaggle:
- `src/data_loader.py`: carga y limpieza del dataset.
- `src/epimodels.py`: ecuaciones diferenciales SIR con `scipy.integrate.solve_ivp`.
- `src/optimizer.py`: calibración de parámetros (`beta`, `gamma`) contra datos observados.

## Arquitectura

| Componente | Función | Métrica / Nota |
|------------|---------|----------------|
| `data_loader` | Filtrado y validación del CSV | Variables: casos, recuperados, UCI, ventiladores, vacunación |
| `epimodels` | Resolución de SIR/SEIR | `scipy.integrate.solve_ivp` con parámetros calibrables |
| `optimizer` | Ajuste a datos históricos | Minimización de MSE entre simulación y datos reales |

## Instalación

```bash
pip install -e ".[dev]"
```

## Uso básico (simulación SIR)

```python
from src.epimodels import ModeloSIR

modelo = ModeloSIR(beta=0.3, gamma=0.1, N=1_000_000)
t, y = modelo.simular(S0=999_900, I0=100, R0=0, dias=365)
```

## Uso visual interactivo (mapamundi + calibración real)

```bash
streamlit run app/app.py
```

La interfaz permite:
- Ajustar `R` de contagiosidad (`reproduction_rate` del dataset real).
- Seleccionar país inicial y población.
- Observar la expansión pandémica simulada en un mapa mundial interactivo (`folium`).

## Tests

```bash
python -m pytest tests/ -v
```

## Referencias
- Ahmad, A. (2026). Global COVID-19 Pandemic Full Data 2020-2026. Kaggle. https://www.kaggle.com/datasets/aliahmadmphil/global-covid-19-pandemic-full-data-2020-2026

## Licencia

AGPL-3.0-or-later

Copyright (C) 2026 Pedro Sordo Martínez <amurlaniakea@gmail.com>
