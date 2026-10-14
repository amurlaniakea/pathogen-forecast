# Metodología — pathogen-forecast

Autor: Pedro Sordo Martínez <amurlaniakea@gmail.com>

## Modelo epidemiológico
Modelo SEIR (Susceptibles, Expuestos, Infectados, Recuperados) con parámetros calibrados a partir del dataset de Kaggle (`covid19_complete_20260829.csv`).

- `beta` (tasa de transmisión): calibrada con `scipy.optimize.minimize` usando la columna `reproduction_rate` del dataset como referencia inicial.
- `gamma` (tasa de recuperación): derivada del período infeccioso observado (aproximado por `case_fatality_rate` y `new_cases` en fases tempranas).
- `sigma` (tasa de incubación): estimada a partir de datos de `icu_patients` vs `new_cases` con retardo temporal.

## Visualización interactiva
Interfaz basada en `streamlit` + `folium` que permite:
1. Seleccionar país/región inicial (`location` del CSV).
2. Ajustar `R` de contagiosidad (`reproduction_rate` observado o simulado).
3. Observar la expansión global en un mapa mundial en tiempo real (simulación diaria).
