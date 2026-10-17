# SPDX-FileCopyrightText: 2026 Pedro Sordo Martínez <amurlaniakea@gmail.com>
"""Modelo epidemiológico SIR básico para predicción de crecimiento pandémico."""
# Copyright (C) 2026 Pedro Sordo Martínez <amurlaniakea@gmail.com>
# SPDX-License-Identifier: AGPL-3.0-or-later

import numpy as np
from scipy.integrate import solve_ivp


class ModeloSIR:
    """Modelo SIR con parámetros derivables del dataset COVID-19."""

    def __init__(self, beta: float, gamma: float, N: float = 1_000_000):
        self.beta = beta  # ritmo de transmisión
        self.gamma = gamma  # ritmo de recuperación
        self.N = N  # población base (simulada)

    def derivadas(self, t, y):
        S, I, _R = y
        dS = -self.beta * S * I / self.N
        dI = self.beta * S * I / self.N - self.gamma * I
        dR = self.gamma * I
        return [dS, dI, dR]

    def simular(self, S0: float, I0: float, R0: float, dias: int = 365):
        y0 = [S0, I0, R0]
        t_span = (0, dias)
        t_eval = np.linspace(0, dias, dias + 1)
        sol = solve_ivp(self.derivadas, t_span, y0, t_eval=t_eval, method="RK45")
        return sol.t, sol.y  # t, [S, I, R]


class ModeloSEIR:
    """Modelo SEIR con período de latencia (sigma) para COVID-19."""

    def __init__(self, beta: float, gamma: float, sigma: float = 0.2, N: float = 1_000_000):
        self.beta = beta  # ritmo de transmisión
        self.gamma = gamma  # ritmo de recuperación
        self.sigma = sigma  # ritmo de progresión de E a I (1/periodo_incubacion)
        self.N = N  # población base (simulada)

    def derivadas(self, t, y):
        S, E, I, _R = y
        dS = -self.beta * S * I / self.N
        dE = self.beta * S * I / self.N - self.sigma * E
        dI = self.sigma * E - self.gamma * I
        dR = self.gamma * I
        return [dS, dE, dI, dR]

    def simular(self, S0: float, E0: float, I0: float, R0: float, dias: int = 365):
        y0 = [S0, E0, I0, R0]
        t_span = (0, dias)
        t_eval = np.linspace(0, dias, dias + 1)
        sol = solve_ivp(self.derivadas, t_span, y0, t_eval=t_eval, method="RK45")
        return sol.t, sol.y  # t, [S, E, I, R]
