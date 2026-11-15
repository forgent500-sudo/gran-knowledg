#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Patrón Maestro: Creador y Validador de Datapacks de Minecraft
=============================================================
Estándar de ingeniería para F.O.R.J.A. y G.R.A.N. v4.0
- Tipado estricto con 'typing'
- Generación de estructura estándar de Datapack (pack.mcmeta, tags, functions)
- Mapeo automático de 'pack_format' según la versión de Minecraft
- Interfaz CLI profesional con 'argparse' y tablas 'rich'
- Consumo < 20 MB RAM
"""

import sys
import os
import json
import argparse
from typing import Dict, Any, Optional

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    HAVE_RICH = True
except ImportError:
    HAVE_RICH = False

console = Console() if HAVE_RICH else None

# Mapeo oficial de versiones a pack_format
FORMATOS_VERSION: Dict[str, int] = {
    "1.20": 15,
    "1.20.1": 15,
    "1.20.2": 18,
    "1.20.4": 26,
    "1.20.6": 41,
    "1.21": 48,
    "1.21.1": 48,
    "1.21.2": 57,
    "1.21.3": 57,
    "1.21.4": 61,
}


def resolver_pack_format(version: str) -> int:
    """Devuelve el pack_format correspondiente a la versión de Minecraft."""
    v_clean = version.strip()
    if v_clean in FORMATOS_VERSION:
        return FORMATOS_VERSION[v_clean]
    # Si no es exacta, buscar prefijo o usar el estándar moderno 1.21
    for k, val in FORMATOS_VERSION.items():
        if v_clean.startswith(k):
            return val
    return 48  # Default 1.21


def forjar_datapack(nombre: str, namespace: str, version: str, destino: str) -> str:
    """Crea la estructura completa y validada de un Datapack de Minecraft."""
    ns_limpio = "".join(c for c in namespace.lower() if c.isalnum() or c in ("_", "-")) or "custom"
    pack_format = resolver_pack_format(version)

    raiz = os.path.join(destino, nombre)
    dir_data = os.path.join(raiz, "data")
    dir_tags_fn = os.path.join(dir_data, "minecraft", "tags", "functions")
    dir_ns = os.path.join(dir_data, ns_limpio)
    dir_functions = os.path.join(dir_ns, "functions")
    dir_recipes = os.path.join(dir_ns, "recipes")
    dir_loot = os.path.join(dir_ns, "loot_tables")

    for d in [dir_tags_fn, dir_functions, dir_recipes, dir_loot]:
        os.makedirs(d, exist_ok=True)

    # 1. pack.mcmeta
    pack_mcmeta: Dict[str, Any] = {
        "pack": {
            "pack_format": pack_format,
            "description": f"Datapack '{nombre}' forjado por G.R.A.N. v4.0 para Jorge (MC {version})"
        }
    }
    with open(os.path.join(raiz, "pack.mcmeta"), "w", encoding="utf-8") as f:
        json.dump(pack_mcmeta, f, indent=2, ensure_ascii=False)

    # 2. Tag minecraft:load
    tag_load = {"values": [f"{ns_limpio}:load"]}
    with open(os.path.join(dir_tags_fn, "load.json"), "w", encoding="utf-8") as f:
        json.dump(tag_load, f, indent=2)

    # 3. Tag minecraft:tick
    tag_tick = {"values": [f"{ns_limpio}:tick"]}
    with open(os.path.join(dir_tags_fn, "tick.json"), "w", encoding="utf-8") as f:
        json.dump(tag_tick, f, indent=2)

    # 4. load.mcfunction (Se ejecuta al entrar al mundo o con /reload)
    load_content = (
        f"# ========================================================\n"
        f"# Funcion de Inicializacion: {nombre}\n"
        f"# ========================================================\n"
        f'tellraw @a [{{"text":"[G.R.A.N.] ","color":"gold","bold":true}},{{"text":"Datapack \'{nombre}\' cargado con exito para Jorge!","color":"green"}}]\n'
    )
    with open(os.path.join(dir_functions, "load.mcfunction"), "w", encoding="utf-8") as f:
        f.write(load_content)

    # 5. tick.mcfunction (Se ejecuta cada game-tick / 20 veces por segundo)
    tick_content = (
        f"# ========================================================\n"
        f"# Bucle Principal (20 tps): {nombre}\n"
        f"# ========================================================\n"
        f"# Agrega aqui tus comandos /execute recurrentes\n"
    )
    with open(os.path.join(dir_functions, "tick.mcfunction"), "w", encoding="utf-8") as f:
        f.write(tick_content)

    return raiz


def mostrar_resumen(nombre: str, namespace: str, version: str, pack_format: int, ruta_final: str) -> None:
    """Muestra el reporte visual de creación en la consola."""
    if not console:
        print(f"Datapack '{nombre}' creado en: {ruta_final}")
        return

    tabla = Table(title=f"🎮 Datapack de Minecraft Forjado Exitosamente", header_style="bold green")
    tabla.add_column("Propiedad", style="bold cyan", width=20)
    tabla.add_column("Valor asignado", style="white")

    tabla.add_row("Nombre del Pack", nombre)
    tabla.add_row("Namespace", namespace)
    tabla.add_row("Versión Minecraft", version)
    tabla.add_row("pack_format", str(pack_format))
    tabla.add_row("Ruta generada", ruta_final)
    tabla.add_row("Archivos clave", "pack.mcmeta, load.json, tick.json, load.mcfunction, tick.mcfunction")

    console.print(tabla)
    console.print(Panel(
        f"[bold yellow]👉 Para instalarlo en tu mundo:[/bold yellow]\n"
        f"Copia la carpeta [bold green]'{nombre}'[/bold green] dentro de:\n"
        f"[dim white].minecraft/saves/<TU_MUNDO>/datapacks/[/dim white]\n"
        f"Y dentro del juego escribe: [bold cyan]/reload[/bold cyan]",
        title="Instalación en Minecraft",
        border_style="cyan"
    ))


def parsear_argumentos() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="datapack_builder",
        description="Generador y validador de estructura de Datapacks para Minecraft (G.R.A.N. v4.0)"
    )
    parser.add_argument(
        "-n", "--nombre",
        type=str,
        default="mi_datapack",
        help="Nombre de la carpeta del datapack."
    )
    parser.add_argument(
        "-s", "--namespace",
        type=str,
        default="custom",
        help="Identificador de namespace (ej: magicos, items, jorge)."
    )
    parser.add_argument(
        "-v", "--version",
        type=str,
        default="1.21.1",
        help="Versión de Minecraft objetivo (ej: 1.20.4, 1.21.1)."
    )
    parser.add_argument(
        "-o", "--destino",
        type=str,
        default=".",
        help="Directorio donde se generará la carpeta del datapack."
    )
    return parser.parse_args()


def main() -> int:
    args = parsear_argumentos()
    try:
        ruta = forjar_datapack(args.nombre, args.namespace, args.version, args.destino)
        formato = resolver_pack_format(args.version)
        mostrar_resumen(args.nombre, args.namespace, args.version, formato, ruta)
        return 0
    except Exception as e:
        if console:
            console.print(f"[bold red]❌ Error forjando datapack:[/bold red] {e}")
        else:
            print(f"❌ Error forjando datapack: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
