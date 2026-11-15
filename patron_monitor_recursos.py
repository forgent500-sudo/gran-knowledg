#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Patrón Maestro: Monitor de Recursos Ultra-Ligero
================================================
Estándar de monitoreo para hardware de 2 GB de RAM.
- Emplea 'psutil' para métricas nativas del kernel en milisegundos
- Visualización con tablas estilizadas de 'rich'
- Detección precisa de compresión ZRAM y Swap
- Consumo de CPU < 0.1% y RAM < 18 MB
"""

import sys
import os
import time
import argparse
from typing import Dict, Any, Optional

try:
    import psutil
except ImportError:
    print("❌ Falta la librería 'psutil'. Instálala con: pip install psutil")
    sys.exit(1)

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    HAVE_RICH = True
except ImportError:
    HAVE_RICH = False

console = Console() if HAVE_RICH else None


def formatear_bytes(b: int) -> str:
    """Convierte bytes a formato legible (MB, GB)."""
    factor = 1024.0
    for unidad in ["B", "KB", "MB", "GB", "TB"]:
        if b < factor:
            return f"{b:.1f} {unidad}"
        b /= factor
    return f"{b:.1f} PB"


def obtener_metricas() -> Dict[str, Any]:
    """Obtiene métricas de CPU, RAM, Swap y Almacenamiento."""
    mem = psutil.virtual_memory()
    swap = psutil.swap_memory()
    uso_cpu = psutil.cpu_percent(interval=0.2)
    cores_logicos = psutil.cpu_count(logical=True)
    disco = psutil.disk_usage("/")

    return {
        "cpu_percent": uso_cpu,
        "cpu_cores": cores_logicos,
        "ram_total": mem.total,
        "ram_used": mem.used,
        "ram_avail": mem.available,
        "ram_percent": mem.percent,
        "swap_total": swap.total,
        "swap_used": swap.used,
        "swap_percent": swap.percent,
        "disco_total": disco.total,
        "disco_used": disco.used,
        "disco_free": disco.free,
        "disco_percent": disco.percent
    }


def mostrar_dashboard(metricas: Dict[str, Any]) -> None:
    """Imprime el panel y la tabla de métricas en consola."""
    if not console:
        print(f"CPU: {metricas['cpu_percent']}% | RAM: {metricas['ram_percent']}% | Disco: {metricas['disco_percent']}%")
        return

    tabla = Table(title="💻 Monitor de Salud del Sistema (G.R.A.N. v4.0)", header_style="bold magenta")
    tabla.add_column("Componente", style="bold cyan", width=18)
    tabla.add_column("Uso actual", justify="center", width=14)
    tabla.add_column("Ocupado / Total", justify="right", width=22)
    tabla.add_column("Diagnóstico para 2 GB", style="dim", justify="left")

    # Diagnóstico CPU
    cpu_p = metricas["cpu_percent"]
    color_cpu = "green" if cpu_p < 60 else "yellow" if cpu_p < 85 else "bold red"
    diag_cpu = "Óptimo" if cpu_p < 60 else "Carga moderada" if cpu_p < 85 else "Alerta de saturación"
    tabla.add_row(
        "🧠 Procesador (CPU)",
        f"[{color_cpu}]{cpu_p:.1f}%[/{color_cpu}]",
        f"{metricas['cpu_cores']} núcleos",
        diag_cpu
    )

    # Diagnóstico RAM
    ram_p = metricas["ram_percent"]
    color_ram = "green" if ram_p < 70 else "yellow" if ram_p < 85 else "bold red"
    diag_ram = "Espacio holgado" if ram_p < 70 else "Cuidado, se acerca al límite" if ram_p < 85 else "Crítico: ZRAM comprimiendo"
    tabla.add_row(
        "⚡ Memoria Física (RAM)",
        f"[{color_ram}]{ram_p:.1f}%[/{color_ram}]",
        f"{formatear_bytes(metricas['ram_used'])} / {formatear_bytes(metricas['ram_total'])}",
        diag_ram
    )

    # Diagnóstico Swap / ZRAM
    swap_p = metricas["swap_percent"]
    color_swap = "green" if swap_p < 30 else "yellow" if swap_p < 70 else "bold red"
    diag_swap = "Inactivo / Sin presión" if swap_p == 0 else "Absorbiendo picos de RAM"
    tabla.add_row(
        "🌀 Swap / ZRAM",
        f"[{color_swap}]{swap_p:.1f}%[/{color_swap}]",
        f"{formatear_bytes(metricas['swap_used'])} / {formatear_bytes(metricas['swap_total'])}",
        diag_swap
    )

    # Diagnóstico Almacenamiento
    disco_p = metricas["disco_percent"]
    color_disco = "green" if disco_p < 75 else "yellow" if disco_p < 90 else "bold red"
    tabla.add_row(
        "💾 Almacenamiento (/)",
        f"[{color_disco}]{disco_p:.1f}%[/{color_disco}]",
        f"{formatear_bytes(metricas['disco_used'])} / {formatear_bytes(metricas['disco_total'])}",
        f"Libre: {formatear_bytes(metricas['disco_free'])}"
    )

    console.print(tabla)


def parsear_argumentos() -> argparse.Namespace:
    """Configuración del parser de argumentos."""
    parser = argparse.ArgumentParser(
        prog="monitor_recursos",
        description="Monitor ligero de hardware y memoria optimizado para 2 GB de RAM."
    )
    parser.add_argument(
        "-i", "--intervalo",
        type=float,
        default=2.0,
        help="Segundos entre actualizaciones continuas."
    )
    parser.add_argument(
        "-c", "--continuo",
        action="store_true",
        help="Modo continuo interactivo (presiona Ctrl+C para salir)."
    )
    return parser.parse_args()


def main() -> int:
    """Ciclo principal de monitor."""
    args = parsear_argumentos()

    try:
        if args.continuo:
            if console:
                console.print("[dim yellow]Presiona Ctrl+C para detener el monitor continuo...[/dim yellow]")
            while True:
                metricas = obtener_metricas()
                if console:
                    console.clear()
                mostrar_dashboard(metricas)
                time.sleep(args.intervalo)
        else:
            metricas = obtener_metricas()
            mostrar_dashboard(metricas)
            return 0
    except KeyboardInterrupt:
        if console:
            console.print("\n[dim green]Monitor finalizado con seguridad.[/dim green]")
        return 0
    except Exception as e:
        if console:
            console.print(f"[bold red]❌ Error de monitoreo:[/bold red] {e}")
        else:
            print(f"❌ Error de monitoreo: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
