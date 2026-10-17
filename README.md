# 🦠 Pathogen Forecast

> Modelo epidemiológico institucional (SIR/SEIR) con calibración real de datos COVID-19 (2020-2026), predicción de expansión pandémica y visualización interactiva en mapa mundial.

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0.txt)
[![HF Space](https://img.shields.io/badge/HF%20Space-MagoPredator%2Fpathogen--forecast-blue?logo=huggingface)](https://huggingface.co/spaces/MagoPredator/pathogen-forecast)

Predice el crecimiento pandémico estimando R0 y Rt a partir del dataset de Kaggle (`reproduction_rate`), con calibración matemática basada en MSE entre simulación SEIR y datos históricos.

---

## 🎯 Características

- **Carga de datos optimizada** con `pandas.read_csv` (`usecols`, `dtype`) para datasets grandes.
- **Modelo SEIR con latencia** (`ModeloSEIR`) con período de incubación (`sigma = 0.2`, 1/5 días), implementado con `scipy.integrate.solve_ivp`.
- **Calibración MSE temporal** (`optimizer.py`) que compara la curva de infectados simulados (`new_cases`) con datos observados, con fallback seguro a promedio R0.
- **Visualización interactiva** con `streamlit` + `folium`: mapa mundial, ajuste de `R`, población, país inicial y simulación diaria.
- **Tests verificados** (`pytest`): conservación de población (`S + E + I + R == N`), calibración con fixture sintético (`tests/fixtures/synthetic_covid.csv`).
- **Integridad matemática** auditada con clon limpio (`ruff check .` = limpio; `pytest` = 7 passed en última verificación con `ModeloSEIR`).

---

## 🚀 Demo en Vivo

El Space interactivo está disponible públicamente:

**https://huggingface.co/spaces/MagoPredator/pathogen-forecast** (`SDK: streamlit`, `emoji: 🦠`, `colorFrom: green`, `colorTo: red`)

---

## 📦 Instalación

```bash
pip install -e ".[dev]"
```

Requiere Python `>=3.11`. Dependencias: `numpy>=1.24`, `scipy>=1.10`, `pandas>=2.0`, `streamlit>=1.30`, `folium>=0.15`.

---

## 🧪 Tests

```bash
python -m pytest tests/ -v --tb=short
```

Estado verificado en clon limpio (`/tmp/repo_audit/pathogen-forecast` + venv `clean_venv`):

- `tests/test_epimodels.py`: `test_sir_simula`, `test_seir_conserva_poblacion` (3/3 passed con `ModeloSEIR` y `sigma=0.2`), `test_sir_conserva_poblacion`
- `tests/test_optimizer.py`: `test_calibracion_sintetica` (calibración SEIR con `sigma_fijo=0.2`)
- `tests/test_data.py`: `test_carga_fixture_sintetico` (`DataLoader.cargar_datos()` con `pd.read_csv`)
- `tests/test_math.py`: `test_seir_simulacion_basica`
- `tests/test_visualization.py`: verificación estática (`app/app.py` parsea correctamente)

Verificación con `ruff check .` = `All checks passed!`.

---

## 📊 Estructura del Proyecto

```
pathogen-forecast/
├── app.py                     # Interfaz Streamlit + Folium (migrado de app/app.py en commit 4ccada5)
├── requirements.txt            # Dependencias para deploy en HF Spaces
├── src/
│   ├── config.py              # Hiperparámetros (Población, Beta, Gamma, Sigma=0.2, R0 por defecto)
│   ├── data_loader.py         # Carga Pandas (usecols, dtype optimizado)
│   ├── epimodels.py           # ModeloSIR + ModeloSEIR (solve_ivp con 3/4 variables)
│   └── optimizer.py           # Calibrador MSE temporal (soporte DataFrame/legado, SEIR con sigma_fijo)
├── tests/
│   ├── fixtures/
│   │   └── synthetic_covid.csv  # Fixture sintético (2 filas, reproduction_rate=2.5)
│   ├── test_epimodels.py      # SIR, SEIR, conservación población
│   ├── test_optimizer.py      # Calibración sintética (SEIR)
│   ├── test_data.py            # Carga de datos (Pandas)
│   ├── test_math.py            # Simulación básica
│   └── test_visualization.py   # Verificación estática
├── docs/
│   ├── methodology.md         # Modelo SEIR (beta, gamma, sigma=0.2), calibración MSE, metodología
│   ├── dataset_info.md         # Cobertura temporal, variables confirmadas
│   └── notas_gemini.md         # Notas verificadas del análisis inicial
├── .github/workflows/
│   └── ci.yml                  # CI obligatorio (ruff sin --exclude=tests, pytest)
├── README.md                  # Documentación profesional (para GitHub; separada de metadata HF)
├── LICENSE                     # AGPL-3.0-or-later
└── pyproject.toml              # Configuración del proyecto (setuptools, requires-python>=3.11)
```



## 🔬 Metodología

### Modelo Epidemiológico (SEIR)
Implementado en `src/epimodels.py` (`ModeloSEIR`):

```python
class ModeloSEIR:
    def __init__(self, beta, gamma, sigma=0.2, N=1_000_000):
        ...
    def derivadas(self, t, y):
        S, E, I, R = y
        dS = -beta * S * I / N
        dE = beta * S * I / N - sigma * E
        dI = sigma * E - gamma * I
        dR = gamma * I
        return [dS, dE, dI, dR]
```

Parámetros calibrados por `scipy.optimize.minimize` contra `new_cases` del dataset sintético o real. `sigma` fijado en `0.2` (1/5 días, período de incubación aproximado para COVID-19) por estabilidad con datos sintéticos; calibrable manualmente (`calibrar(sigma_fijo=...)`) si se dispone de datos temporales de alta calidad (`icu_patients` vs `new_cases` con retardo).

Referencia primaria del dataset: Ahmad, A. (2026). *Global COVID-19 Pandemic Full Data 2020-2026*. Kaggle. [https://www.kaggle.com/datasets/aliahmadmphil/global-covid-19-pandemic-full-data-2020-2026](https://www.kaggle.com/datasets/aliahmadmphil/global-covid-19-pandemic-full-data-2020-2026)

### Calibración
Función objetivo (`optimizer.py`): minimizar MSE entre la curva de infectados simulados (`y[2]` del SEIR) y la serie temporal de `new_cases`. Fallback seguro a `rt_promedio` (`reproduction_rate`) si faltan datos temporales.

### Visualización
`streamlit` (`st.slider`, `st.selectbox`, `st.metric`) + `folium` (`folium.Map`, `folium.CircleMarker`) con expansión global simplificada (`random.uniform` con `seed=42`). La nota de verificación (`st.info`) indica claramente que se trata de una simulación teórica basada en SEIR básico con parámetros calibrados.

---

## 📚 Documentación y Referencias
- [`docs/methodology.md`](docs/methodology.md): ecuaciones SEIR (`dS/dt`, `dE/dt`, `dI/dt`, `dR/dt`), calibración MSE (`optimizer.py` con `ModeloSEIR`), metodología de datos sintéticos/reales.
- [`docs/dataset_info.md`](docs/dataset_info.md): cobertura temporal (2020-2026), variables confirmadas, licencia del dataset (`open-data-license`).
- [`docs/notas_gemini.md`](docs/notas_gemini.md): notas verificadas del análisis inicial (dataset NO contiene R0 puro; derivable; Rt varía con vacunación e inmunidad natural; modelo propuesto SIR/SEIR con `scipy.integrate.solve_ivp`).

---

## 📄 Licencia

Este proyecto está licenciado bajo la [GNU Affero General Public License v3.0](LICENSE).

Copyright © 2026 Pedro Sordo Martínez. Todos los derechos reservados.

El dataset de referencia utilizado para la calibración se distribuye bajo licencia Apache 2.0.

---

## 📧 Contacto

- **Autor**: Pedro Sordo Martínez
- **e-mail**: amurlaniakea@gmail.com
- **Hugging Face**: [MagoPredator](https://huggingface.co/MagoPredator)

