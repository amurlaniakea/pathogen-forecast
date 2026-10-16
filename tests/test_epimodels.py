"""Tests básicos del modelo epidemiológico."""
# Copyright (C) 2026 Pedro Sordo Martínez <amurlaniakea@gmail.com>
# SPDX-License-Identifier: AGPL-3.0-or-later



import numpy as np

from epimodels import ModeloSIR


def test_sir_simula():
    modelo = ModeloSIR(beta=0.3, gamma=0.1, N=100_000)
    t, y = modelo.simular(S0=99_900, I0=100, R0=0, dias=30)
    assert len(t) == 31
    assert len(y) == 3


def test_sir_conserva_poblacion():
    modelo = ModeloSIR(beta=0.3, gamma=0.1, N=100_000)
    _, y = modelo.simular(S0=99_900, I0=100, R0=0, dias=30)
    assert np.allclose(np.sum(y, axis=0), modelo.N)
