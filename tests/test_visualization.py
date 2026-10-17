# SPDX-FileCopyrightText: 2026 Pedro Sordo Martínez <amurlaniakea@gmail.com>
"""Test básico de la interfaz visual (verificación sintáctica, no ejecución de UI)."""
# Copyright (C) 2026 Pedro Sordo Martínez <amurlaniakea@gmail.com>
# SPDX-License-Identifier: AGPL-3.0-or-later

from pathlib import Path


def test_app_py_parsea():
    # Solo confirma que el archivo se parsea sin errores de sintaxis
    import importlib.util
    spec = importlib.util.spec_from_file_location("app", Path(__file__).resolve().parent.parent / "app" / "app.py")
    assert spec is not None
