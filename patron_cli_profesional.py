#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Patrón Maestro: CLI Profesional y Ligero
========================================
Estándar de oro para F.O.R.J.A. (G.R.A.N. v4.0)
- Tipado estricto con 'typing'
- Interfaz CLI completa con 'argparse'
- Estética y feedback visual con 'rich'
- Manejo exhaustivo de excepciones (try/except)
- Consumo ultra-bajo de RAM (<25 MB) optimizado para sistemas de 2 GB
"""

import sys
import os
import argparse
from typing import List, Dict, Optional, Any
from dataclasses import dataclass

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.prompt import Prompt
    HAVE_RICH = True
except ImportError:
    HAVE_RICH = False

console = Console() if HAVE_RICH else None


def notificar(mensaje: str, estilo: str = "white") -> None:
    """Imprime mensajes con formato rich o fallback seguro a stdout."""
    if console:
        console.print(f"[{estilo}]{mensaje}[/{estilo}]")
    else:
        print(mensaje)


def mostrar_error(mensaje: str, detalle: Optional[str] = None) -> None:
    """Reporta un error estructurado."""
    if console:
        console.print(f"[bold red]❌ Error:[/bold red] {mensaje}")
        if detalle:
            console.print(f"[dim red]   Detalle: {detalle}[/dim red]")
    else:
        print(f"❌ Error: {mensaje}")
        if detalle:
            print(f"   Detalle: {detalle}")


@dataclass
class ElementoReporte:
    """Estructura de datos tipada para el procesamiento."""
    identificador: int
    nombre: str
    estado: str
    detalles: str


def procesar_elementos(nombres: List[str], modo_estricto: bool = False) -> List[ElementoReporte]:
    """Procesa una lista de elementos aplicando validación y tipado."""
    resultados: List[ElementoReporte] = []
    for idx, nombre in enumerate(nombres, start=1):
        nombre_limpio = nombre.strip()
        if not nombre_limpio:
            if modo_estricto:
                raise ValueError(f"Elemento en posición {idx} no puede estar vacío.")
            continue
        
        estado = "Activo" if len(nombre_limpio) > 3 else "Advertencia"
        resultados.append(ElementoReporte(
            identificador=idx,
            nombre=nombre_limpio,
            estado=estado,
            detalles=f"Longitud: {len(nombre_limpio)} caracteres"
        ))
    return resultados


def renderizar_tabla(elementos: List[ElementoReporte]) -> None:
    """Muestra los resultados en una tabla rich o en texto tabulado."""
    if console:
        tabla = Table(title="📊 Resultados del Procesamiento", show_header=True, header_style="bold cyan")
        tabla.add_column("ID", style="dim", width=6, justify="center")
        tabla.add_column("Nombre", style="bold green")
        tabla.add_column("Estado", justify="center")
        tabla.add_column("Detalles", style="dim white")

        for el in elementos:
            color_estado = "green" if el.estado == "Activo" else "yellow"
            tabla.add_row(
                str(el.identificador),
                el.nombre,
                f"[{color_estado}]{el.estado}[/{color_estado}]",
                el.detalles
            )
        console.print(tabla)
    else:
        print("\n=== RESULTADOS ===")
        for el in elementos:
            print(f"[{el.identificador}] {el.nombre} | {el.estado} | {el.detalles}")


def construir_parser() -> argparse.ArgumentParser:
    """Configura el analizador de argumentos de línea de comandos."""
    parser = argparse.ArgumentParser(
        prog="cli_profesional",
        description="Plantilla maestra de CLI ligera para G.R.A.N. y laptop escolar de 2 GB RAM.",
        epilog="Diseñado artesanalmente con bajo consumo de memoria y tolerancia a fallos."
    )
    parser.add_argument(
        "entradas",
        nargs="*",
        help="Elementos o rutas a procesar."
    )
    parser.add_argument(
        "-s", "--strict",
        action="store_true",
        help="Activa validación estricta de entradas vacías."
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Muestra detalles técnicos adicionales en pantalla."
    )
    parser.add_argument(
        "-o", "--salida",
        type=str,
        default=None,
        help="Ruta opcional para guardar el resumen en texto plano."
    )
    return parser


def main() -> int:
    """Función principal con captura segura de excepciones."""
    parser = construir_parser()
    args = parser.parse_args()

    try:
        entradas = args.entradas
        if not entradas:
            # Ejemplo por defecto si se ejecuta sin argumentos
            notificar("ℹ️  No se proporcionaron argumentos. Usando datos de prueba...", "yellow")
            entradas = ["servidor_red", "dns_local", "gw", "firewall_seguro"]

        if args.verbose:
            notificar(f"🔧 Modo depuración activo. Procesando {len(entradas)} entradas...", "cyan")

        resultados = procesar_elementos(entradas, modo_estricto=args.strict)
        renderizar_tabla(resultados)

        if args.salida:
            with open(args.salida, "w", encoding="utf-8") as f:
                for r in resultados:
                    f.write(f"{r.identificador}\t{r.nombre}\t{r.estado}\t{r.detalles}\n")
            notificar(f"💾 Resumen guardado en: {args.salida}", "bold green")

        notificar("✨ Proceso completado exitosamente.", "bold green")
        return 0

    except KeyboardInterrupt:
        mostrar_error("Operación interrumpida por el usuario (Ctrl+C).")
        return 130
    except ValueError as ve:
        mostrar_error("Fallo de validación de argumentos.", str(ve))
        return 2
    except Exception as e:
        mostrar_error("Error inesperado durante la ejecución.", str(e))
        return 1


if __name__ == "__main__":
    sys.exit(main())
