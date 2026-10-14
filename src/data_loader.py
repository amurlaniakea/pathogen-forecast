"""Carga y limpieza del dataset COVID-19 de Kaggle."""
# Copyright (C) 2026 Pedro Sordo Martínez <amurlaniakea@gmail.com>
# SPDX-License-Identifier: AGPL-3.0-or-later

import csv
from pathlib import Path


class DataLoader:
    """Carga datos del CSV de Kaggle y aísla variables epidemiológicas básicas."""

    def __init__(self, ruta_csv: Path):
        self.ruta = ruta_csv

    def cargar_filas(self) -> list[dict]:
        filas = []
        if not self.ruta.exists():
            raise FileNotFoundError(f"Dataset no encontrado: {self.ruta}")
        with open(self.ruta, newline="", encoding="utf-8") as f:
            lector = csv.DictReader(f)
            for fila in lector:
                filas.append(fila.copy())
        return filas
