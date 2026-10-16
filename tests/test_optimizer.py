"""Tests del calibrador con datos sintéticos (independiente del dataset real)."""
# Copyright (C) 2026 Pedro Sordo Martínez <amurlaniakea@gmail.com>
# SPDX-License-Identifier: AGPL-3.0-or-later

from pathlib import Path

from data_loader import DataLoader
from optimizer import OptimizadorSIR


def test_calibracion_sintetica():
    ruta = Path(__file__).resolve().parent / "fixtures" / "synthetic_covid.csv"
    loader = DataLoader(ruta)
    datos = loader.cargar_datos()
    optimizador = OptimizadorSIR(datos)
    beta, gamma = optimizador.calibrar()
    assert beta > 0
    assert gamma > 0
    r0_sim = beta / gamma
    # El fixture sintético tiene reproduction_rate=2.5; la calibración debe aproximarse
    assert 1.5 < r0_sim < 4.0
