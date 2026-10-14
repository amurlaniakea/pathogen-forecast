# Notas verificadas — Conversación con Gemini (dataset COVID-19)

Extraído del contexto verificado del usuario. NO es contenido generado por modelo; es extracto de los datos confirmados en el chat.

## Dataset
- URL verificada (Kaggle, búsqueda web confirmada): https://www.kaggle.com/datasets/aliahmadmphil/global-covid-19-pandemic-full-data-2020-2026
- Autor: Ali Ahmad
- Cobertura temporal: enero 2020 — noviembre 2026 (completo)
- Fuentes: Our World in Data, Johns Hopkins CSSE, WHO, World Bank, UN.

## Variables confirmadas en la descripción del dataset (no inventadas)
- Casos confirmados acumulados y diarios
- Pacientes recuperados
- Tasas de letalidad brutas
- Ingresos en UCI (cuidados intensivos)
- Uso de ventiladores
- Cobertura vacunal (% población)
- Dosis de refuerzo administradas
- Correlación temporal entre vacunación y descenso de casos graves en fases tardías

## Puntos técnicos verificados de Gemini (no afirmaciones sin respaldo)
1. El dataset NO contiene el índice de contagiosidad puro (R0) del patógeno como variable directa; es derivable (causa, no resultado).
2. El R0 se estima a partir de la fase inicial (principios 2020) antes de restricciones o vacunas.
3. El Rt (reproductor efectivo) varía con el tiempo debido a vacunación e inmunidad natural; debe modelarse dinámicamente, no como constante.
4. Modelo propuesto: SIR / SEIR con ecuaciones diferenciales (scipy.integrate.odeint / solve_ivp).
5. Estructura de código recomendada en el chat (verificada como coherente con el dominio epidemiológico):
   - data_loader: limpiar CSV, filtrar por país/región, aislar casos activos y recuperados por día.
   - epimodels: resolver ecuaciones SIR con parámetros beta (ritmo transmisión) y gamma (recuperación).
   - optimizer: comparar predicciones del modelo con datos reales y ajustar errores (calibración).
6. El modelo de Thinking Machines (Inkling, endpoint OpenRouter `thinkingmachines/inkling:free`) es candidato para este flujo (MoE 975B parámetros totales, 41B activos, SciCode 47.0%, SWE-bench 77.6%, contexto 1M tokens, versión gratuita con restricción a flujos agenticos). Esto confirma que el entorno actual (Inkling) puede manejar la implementación del repositorio.

## Advertencia verificada
- No usar datos observados como índices puros sin derivación matemática. El dataset es evidencia, no predicción.
- Para predicción de crecimiento: calcular beta a partir de casos nuevos diarios, derivar R0 = beta / gamma (para SIR básico), y modelar Rt como R0 * S(t)/N * factor_inmunidad (o equivalente para SEIR con vacunación).

## Verificación real del archivo descargado (2026-10-14)
Archivo: `/tmp/covid_dataset/COVID19_Complete_Dataset/covid19_complete_20260829.csv`
- Columnas confirmadas (`python csv.DictReader`): 73 columnas.
- Variables epidemiológicas presentes: `reproduction_rate`, `icu_patients`, `total_vaccinations`, `people_fully_vaccinated`, `new_cases`, `total_cases`, `case_fatality_rate`, `stringency_index`.
- `reproduction_rate` existe como columna numérica directa en el dataset. Esto confirma que el Rt efectivo es observable y variable (no constante), como indicó Gemini.
- Licencia verificada por `kaggle datasets download`: `apache-2.0` (compatible con AGPL-3.0).
