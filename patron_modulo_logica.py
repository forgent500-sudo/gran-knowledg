#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Patrón Maestro: Módulo de Lógica y Pruebas Unitarias Integradas
==============================================================
Estándar para lógica pura y validación automática de F.O.R.J.A.
- Separación estricta de lógica de negocio y presentación
- Inclusión de suite de pruebas unitarias auto-ejecutables
- 100% biblioteca estándar de Python (consumo < 15 MB RAM)
"""

import sys
import argparse
import unittest
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass


@dataclass(frozen=True)
class ReglaMemoria:
    """Modelo inmutable para reglas de hardware y sistema."""
    clave: str
    limite_mb: int
    permite_pesadas: bool

    def es_valida(self, consumo_proyectado_mb: int) -> bool:
        """Verifica si el consumo proyectado cabe en el límite."""
        return consumo_proyectado_mb <= self.limite_mb


class ValidadorEntorno:
    """Lógica de validación para scripts que correrán en la laptop escolar."""

    def __init__(self, limite_ram_mb: int = 2048):
        self.regla = ReglaMemoria(
            clave="laptop_escolar_q4os",
            limite_mb=limite_ram_mb,
            permite_pesadas=False
        )
        self.librerias_prohibidas = {
            "pandas", "numpy", "tensorflow", "torch", "scipy", "matplotlib", "seaborn"
        }

    def analizar_imports(self, imports_detectados: List[str]) -> Tuple[bool, List[str]]:
        """Determina si una lista de dependencias es segura para 2 GB de RAM."""
        infracciones = [lib for lib in imports_detectados if lib.lower() in self.librerias_prohibidas]
        es_seguro = len(infracciones) == 0
        return es_seguro, infracciones

    def calcular_margen_seguro(self, consumo_estimado_mb: int) -> int:
        """Calcula el margen libre restante tras la ejecución."""
        if not self.regla.es_valida(consumo_estimado_mb):
            raise ValueError(f"Consumo de {consumo_estimado_mb} MB excede el límite de {self.regla.limite_mb} MB.")
        return self.regla.limite_mb - consumo_estimado_mb


# ==============================================================================
# SUITE DE PRUEBAS UNITARIAS AUTO-EJECUTABLES
# ==============================================================================
class TestValidadorEntorno(unittest.TestCase):
    def setUp(self):
        self.validador = ValidadorEntorno(limite_ram_mb=2048)

    def test_librerias_permitidas(self):
        seguro, infracciones = self.validador.analizar_imports(["sys", "os", "rich", "psutil"])
        self.assertTrue(seguro)
        self.assertEqual(len(infracciones), 0)

    def test_librerias_prohibidas(self):
        seguro, infracciones = self.validador.analizar_imports(["os", "pandas", "tensorflow"])
        self.assertFalse(seguro)
        self.assertIn("pandas", infracciones)
        self.assertIn("tensorflow", infracciones)

    def test_margen_seguro(self):
        margen = self.validador.calcular_margen_seguro(500)
        self.assertEqual(margen, 1548)

    def test_exceso_memoria(self):
        with self.assertRaises(ValueError):
            self.validador.calcular_margen_seguro(3000)


def main() -> int:
    parser = argparse.ArgumentParser(description="Módulo de lógica y pruebas para G.R.A.N.")
    parser.add_argument("--test", action="store_true", help="Ejecuta la suite de pruebas unitarias.")
    args = parser.parse_args()

    if args.test:
        suite = unittest.TestLoader().loadTestsFromTestCase(TestValidadorEntorno)
        runner = unittest.TextTestRunner(verbosity=2)
        resultado = runner.run(suite)
        return 0 if resultado.wasSuccessful() else 1

    print("Módulo de lógica cargado. Ejecuta con --test para validar el comportamiento.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
