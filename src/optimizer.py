"""Calibración de parámetros epidemiológicos con datos observados del dataset."""
# Copyright (C) 2026 Pedro Sordo Martínez <amurlaniakea@gmail.com>
# SPDX-License-Identifier: AGPL-3.0-or-later

import numpy as np
from scipy.optimize import minimize

from epimodels import ModeloSEIR

# Soporte para datos modernos (DataFrame) y legado (list[dict])
try:
    import pandas as pd
except ImportError:
    pd = None


class OptimizadorSIR:
    """Ajusta beta y gamma minimizando el error con datos reales (reproduction_rate del CSV)."""

    def __init__(self, datos):
        if pd is not None and isinstance(datos, pd.DataFrame):
            self.datos_df = datos
            self.modo = "dataframe"
        else:
            self.datos = datos
            self.modo = "lista"

    def calibrar(self, N: float = 1_000_000, sigma_fijo: float = 0.2) -> tuple[float, float]:
        """Calibra beta y gamma con ModeloSEIR (sigma fijo por defecto para estabilidad con datos sintéticos)."""
        # Extraer reproduction_rate de los datos (primeros valores no nulos)
        valores_rt = []
        if self.modo == "dataframe":
            col = self.datos_df.get("reproduction_rate")
            if col is not None:
                valores_rt = col.fillna(0).astype(float).tolist()
        else:
            valores_rt = [float(f.get("reproduction_rate", 0) or 0) for f in self.datos]
        valores_rt = [v for v in valores_rt if v > 0]
        rt_promedio = np.mean(valores_rt) if valores_rt else 3.0

        # Función objetivo: minimizar diferencia entre simulación SEIR y datos observados
        def objetivo(params):
            beta, gamma = params
            try:
                if self.modo == "dataframe":
                    casos_obs = self.datos_df["new_cases"].fillna(0).astype(float).values
                else:
                    casos_obs = np.array([float(f.get("new_cases", 0) or 0) for f in self.datos])
                return self.error_beta_gamma(params, casos_obs, sigma_fijo)
            except (ValueError, KeyError):
                r0_sim = beta / gamma if gamma > 0 else 0
                return float((r0_sim - rt_promedio) ** 2)

        # Restricciones: beta > 0, gamma > 0
        bounds = [(0.01, 2.0), (0.01, 1.0)]
        resultado = minimize(objetivo, [0.3, 0.1], bounds=bounds, method="L-BFGS-B")
        beta_cal, gamma_cal = resultado.x
        return float(beta_cal), float(gamma_cal)

    def error_beta_gamma(self, params: np.ndarray, casos_reales: np.ndarray, sigma_fijo: float = 0.2) -> float:
        beta, gamma = params
        modelo = ModeloSEIR(beta=beta, gamma=gamma, sigma=sigma_fijo, N=1_000_000)
        _, y = modelo.simular(S0=999_900, E0=0, I0=100, R0=0, dias=len(casos_reales))
        pred = y[2]  # I (infectados) en SEIR
        return float(np.mean((pred - casos_reales) ** 2))
