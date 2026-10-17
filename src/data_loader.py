# SPDX-FileCopyrightText: 2026 Pedro Sordo Martínez <amurlaniakea@gmail.com>
"""Carga y limpieza del dataset COVID-19 de Kaggle."""
# Copyright (C) 2026 Pedro Sordo Martínez <amurlaniakea@gmail.com>
# SPDX-License-Identifier: AGPL-3.0-or-later

from pathlib import Path

import pandas as pd


class DataLoader:
    """Carga datos del CSV de Kaggle y aísla variables epidemiológicas básicas."""

    def __init__(self, ruta_csv: Path):
        self.ruta = ruta_csv

    def cargar_datos(self) -> pd.DataFrame:
        if not self.ruta.exists():
            raise FileNotFoundError(f"Dataset no encontrado: {self.ruta}")
        return pd.read_csv(
            self.ruta,
            dtype={"reproduction_rate": "float32", "new_cases": "float32"},
            usecols=lambda c: c in {"reproduction_rate", "new_cases", "total_cases", "icu_patients"},
        )
