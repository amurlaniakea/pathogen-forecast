# Verificación del dataset descargado

Fecha de descarga: 2026-10-14
Token utilizado: archivo `/home/sil/.kaggle/access_token` (no expuesto en output)
Ruta de descarga: `/tmp/covid_dataset/COVID19_Complete_Dataset/`

## Archivos confirmados (evidencia real)
```
COVID19_Complete_Dataset/
├── covid19_complete_20260829.csv
├── covid19_country_summary_20260829.csv
├── covid19_top10_countries_20260829.csv
├── covid19_latest_20260829.csv
├── data_dictionary_20260829.csv
├── data_verification_report.csv
├── sample_submission_format.csv
└── README.md
```

## Licencia del dataset
Según `kaggle datasets download`: `License(s): apache-2.0`.
Apache-2.0 es compatible con AGPL-3.0-or-later para uso derivado (no restringe distribución). Se documenta, no se perpetúa como licencia del repositorio.

## Variables confirmadas (archivo `covid19_complete_20260829.csv`)
Se verificará con `head` + `python` antes de cualquier calibración. No se asume esquema.

## Regla operativa
- El CSV NO se commitea al repo (`.gitignore` cubre `.csv`).
- El script `src/data_loader.py` apunta a la ruta por defecto (`data/covid19_complete.csv`) o recibe la ruta como argumento (`sys.argv`).
- Si el archivo no está en `data/`, el usuario debe copiarlo desde `/tmp/covid_dataset/COVID19_Complete_Dataset/` antes de correr tests que lo usen.
