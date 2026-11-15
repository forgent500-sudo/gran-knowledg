#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Patrón Maestro: Optimizador y Auditor de Sistema Linux para 2 GB RAM
====================================================================
Estándar de optimización para la laptop escolar (G.R.A.N. v4.0)
- Auditoría de servicios de inicio lentos (systemd-analyze)
- Verificación de compresión ZRAM en tiempo real
- Comprobación de demonios clave: earlyoom y preload
- Asistente de comandos para remasterización con squashfs y chroot
- Consumo < 18 MB RAM
"""

import sys
import os
import subprocess
import argparse
from typing import Dict, Any, List

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    HAVE_RICH = True
except ImportError:
    HAVE_RICH = False

console = Console() if HAVE_RICH else None


def ejecutar_comando_silencioso(cmd: List[str]) -> str:
    """Ejecuta un comando de sistema capturando salida sin fallar."""
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=5, check=False)
        return res.stdout.strip()
    except Exception:
        return ""


def auditar_servicios_inicio() -> List[Dict[str, str]]:
    """Obtiene los 5 servicios que más retrasan el arranque con systemd-analyze blame."""
    salida = ejecutar_comando_silencioso(["systemd-analyze", "blame"])
    servicios: List[Dict[str, str]] = []
    for linea in salida.splitlines()[:5]:
        partes = linea.strip().split(None, 1)
        if len(partes) == 2:
            servicios.append({"tiempo": partes[0], "servicio": partes[1]})
    return servicios


def verificar_zram() -> Dict[str, Any]:
    """Revisa si la compresión ZRAM o Swap está activa en el kernel."""
    salida_swaps = ejecutar_comando_silencioso(["cat", "/proc/swaps"])
    tiene_zram = "zram" in salida_swaps.lower()
    tiene_swap = len(salida_swaps.splitlines()) > 1
    return {
        "zram_activo": tiene_zram,
        "swap_activo": tiene_swap,
        "detalle": salida_swaps if tiene_swap else "Sin swap configurado"
    }


def verificar_demonios_ligeros() -> Dict[str, bool]:
    """Comprueba si earlyoom y preload están instalados."""
    salida_pgrep = ejecutar_comando_silencioso(["ps", "-A"])
    return {
        "earlyoom": "earlyoom" in salida_pgrep,
        "preload": "preload" in salida_pgrep
    }


def mostrar_reporte_optimizacion() -> None:
    """Genera el reporte de estado de salud y optimización para 2 GB de RAM."""
    servicios = auditar_servicios_inicio()
    zram = verificar_zram()
    demonios = verificar_demonios_ligeros()

    if not console:
        print(f"ZRAM activo: {zram['zram_activo']} | Earlyoom: {demonios['earlyoom']} | Preload: {demonios['preload']}")
        return

    tabla = Table(title="🐧 Auditoría de Rendimiento para Laptop 2 GB RAM (Q4OS)", header_style="bold green")
    tabla.add_column("Módulo de Rendimiento", style="bold cyan", width=26)
    tabla.add_column("Estado Actual", justify="center", width=18)
    tabla.add_column("Impacto en 2 GB RAM", style="white")

    # ZRAM
    color_zram = "green" if zram["zram_activo"] else "yellow"
    estado_zram = "✅ Activo (Comprimiendo)" if zram["zram_activo"] else "⚠️ No detectado"
    tabla.add_row("Compresión ZRAM", f"[{color_zram}]{estado_zram}[/{color_zram}]", "Multiplica la RAM virtual evitando congelamientos")

    # EarlyOOM
    color_oom = "green" if demonios["earlyoom"] else "yellow"
    estado_oom = "✅ Protegido" if demonios["earlyoom"] else "⚠️ Inactivo"
    tabla.add_row("Protector EarlyOOM", f"[{color_oom}]{estado_oom}[/{color_oom}]", "Mata pestañas saturadas antes de que la PC se congele")

    # Preload
    color_pre = "green" if demonios["preload"] else "yellow"
    estado_pre = "✅ Activo" if demonios["preload"] else "⚠️ Inactivo"
    tabla.add_row("Acelerador Preload", f"[{color_pre}]{estado_pre}[/{color_pre}]", "Precarga apps escolares en memoria para apertura rápida")

    console.print(tabla)

    if servicios:
        tabla_serv = Table(title="⏱️ Servicios más lentos al arrancar (Candidatos a desactivar)", header_style="bold yellow")
        tabla_serv.add_column("Tiempo", style="bold red", width=12)
        tabla_serv.add_column("Servicio", style="white")
        for s in servicios:
            tabla_serv.add_row(s["tiempo"], s["servicio"])
        console.print(tabla_serv)

    console.print(Panel(
        "[bold cyan]Comandos de Remasterización ISO recomendados:[/bold cyan]\n"
        "• Descomprimir raíz del sistema: [dim]unsquashfs filesystem.squashfs[/dim]\n"
        "• Modificar adentro en jaula: [dim]sudo chroot squashfs-root[/dim]\n"
        "• Recomprimir con compresión alta: [dim]mksquashfs squashfs-root filesystem.squashfs -comp xz -b 1048576[/dim]",
        title="Guía Rápida de Remasterización",
        border_style="green"
    ))


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="optimizador_linux",
        description="Auditor y optimizador de rendimiento Linux para 2 GB de RAM (G.R.A.N. v4.0)"
    )
    parser.parse_args()
    mostrar_reporte_optimizacion()
    return 0


if __name__ == "__main__":
    sys.exit(main())
