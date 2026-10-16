"""Tests del cargador de datos con fixture sintético (independiente del dataset real)."""
# Copyright (C) 2026 Pedro Sordo Martínez <amurlaniakea@gmail.com>
# SPDX-License-Identifier: AGPL-3.0-or-later

from pathlib import Path

from data_loader import DataLoader


def test_carga_fixture_sintetico():
    ruta = Path(__file__).resolve().parent / "fixtures" / "synthetic_covid.csv"
    loader = DataLoader(ruta)
    filas = loader.cargar_filas()
    assert len(filas) == 2
    assert filas[0]["reproduction_rate"] == "2.5"
