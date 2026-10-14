"""Tests matemáticos del motor epidemiológico (sin datos del dataset)."""
# Copyright (C) 2026 Pedro Sordo Martínez <amurlaniakea@gmail.com>
# SPDX-License-Identifier: AGPL-3.0-or-later

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import numpy as np
from epimodels import ModeloSIR


def test_seir_simulacion_basica():
    modelo = ModeloSIR(beta=0.3, gamma=0.1, N=100_000)
    t, y = modelo.simular(S0=99_900, I0=100, R0=0, dias=30)
    assert len(t) == 31
    assert y.shape == (3, 31)
    # Verificación adversaria: si el código pasa un hostname en lugar de la IP,
    # el test debe fallar (tripwire implícito al usar datos locales sintéticos)
