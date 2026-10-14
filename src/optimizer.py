"""Calibración de parámetros epidemiológicos con datos observados."""
# Copyright (C) 2026 Pedro Sordo Martínez <amurlaniakea@gmail.com>
# SPDX-License-Identifier: AGPL-3.0-or-later

import numpy as np
from scipy.optimize import minimize

from src.epimodels import ModeloSIR


class OptimizadorSIR:
    """Ajusta beta y gamma para minimizar el error con datos reales."""

    def __init__(self, datos: list[dict]):
        self.datos = datos

    def error_beta_gamma(self, params: np.ndarray, casos_reales: np.ndarray) -> float:
        beta, gamma = params
        modelo = ModeloSIR(beta=beta, gamma=gamma, N=1_000_000)
        # Simulación simplificada para calibración inicial
        _, y = modelo.simular(S0=999_900, I0=100, R0=0, dias=len(casos_reales))
        pred = y[1]  # casos infectados simulados
        return float(np.mean((pred - casos_reales) ** 2))
