# SPDX-FileCopyrightText: 2026 Pedro Sordo Martínez <amurlaniakea@gmail.com>
"""Configuración de hiperparámetros del modelo epidemiológico."""
# Copyright (C) 2026 Pedro Sordo Martínez <amurlaniakea@gmail.com>
# SPDX-License-Identifier: AGPL-3.0-or-later

# Hiperparámetros por defecto (calibrables con dataset real)
POPULATION_DEFAULT = 8_000_000  # Ejemplo: población aproximada de referencia
BETA_DEFAULT = 0.3
GAMMA_DEFAULT = 0.1  # Recuperación en ~10 días
SIGMA_DEFAULT = 0.2  # Incubación en ~5 días
R0_DEFAULT = 3.0  # R0 aproximado de COVID-19
DIAS_SIMULACION = 365
