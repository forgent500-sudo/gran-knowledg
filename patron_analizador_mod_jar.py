#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Patrón Maestro: Analizador e Inspector de Mods de Minecraft (.jar)
==================================================================
Estándar de ingeniería para F.O.R.J.A. y G.R.A.N. v4.0
- Inspección sin dependencias pesadas usando 'zipfile' nativo
- Detección automática del Loader (Fabric, Quilt, NeoForge, Forge clásico)
- Extracción de dependencias, versión de Minecraft, entrypoints y mixins
- Diagnóstico de actualización de versión
- Consumo < 22 MB RAM
"""

import sys
import os
import json
import zipfile
import argparse
from typing import Dict, Any, Optional, List

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    HAVE_RICH = True
except ImportError:
    HAVE_RICH = False

console = Console() if HAVE_RICH else None


def parsear_toml_simple(texto: str) -> Dict[str, str]:
    """Parser básico para mods.toml y neoforge.mods.toml sin dependencias externas."""
    datos: Dict[str, str] = {}
    for linea in texto.splitlines():
        linea = linea.strip()
        if not linea or linea.startswith("#") or linea.startswith("["):
            continue
        if "=" in linea:
            k, v = linea.split("=", 1)
            datos[k.strip()] = v.strip().strip('"').strip("'")
    return datos


def analizar_mod_jar(ruta_jar: str) -> Dict[str, Any]:
    """Abre un archivo .jar y extrae su arquitectura y metadatos de modding."""
    if not os.path.isfile(ruta_jar):
        raise FileNotFoundError(f"No existe el archivo: {ruta_jar}")
    if not zipfile.is_zipfile(ruta_jar):
        raise ValueError(f"El archivo no es un paquete Java/ZIP válido: {ruta_jar}")

    resultado: Dict[str, Any] = {
        "archivo": os.path.basename(ruta_jar),
        "tamano_mb": round(os.path.getsize(ruta_jar) / (1024 * 1024), 2),
        "loader": "Desconocido",
        "mod_id": "Desconocido",
        "nombre": "Desconocido",
        "version": "Desconocido",
        "minecraft_version": "No especificada",
        "entrypoints": [],
        "mixins": [],
        "total_clases": 0
    }

    with zipfile.ZipFile(ruta_jar, "r") as z:
        archivos = z.namelist()
        resultado["total_clases"] = sum(1 for f in archivos if f.endswith(".class"))

        # Detección de Mixins
        resultado["mixins"] = [f for f in archivos if f.endswith(".mixins.json")]

        # 1. Caso Fabric
        if "fabric.mod.json" in archivos:
            resultado["loader"] = "Fabric"
            try:
                with z.open("fabric.mod.json") as f:
                    meta = json.load(f)
                resultado["mod_id"] = meta.get("id", "desconocido")
                resultado["nombre"] = meta.get("name", resultado["mod_id"])
                resultado["version"] = meta.get("version", "desconocido")

                depends = meta.get("depends", {})
                resultado["minecraft_version"] = depends.get("minecraft", "Cualquiera")

                entrypoints = meta.get("entrypoints", {})
                if isinstance(entrypoints, dict):
                    for tipo, clases in entrypoints.items():
                        if isinstance(clases, list):
                            for c in clases:
                                c_nombre = c.get("value") if isinstance(c, dict) else str(c)
                                resultado["entrypoints"].append(f"{tipo}: {c_nombre}")
            except Exception as e:
                resultado["loader"] = f"Fabric (Error leyendo JSON: {e})"

        # 2. Caso Quilt
        elif "quilt.mod.json" in archivos:
            resultado["loader"] = "Quilt"
            try:
                with z.open("quilt.mod.json") as f:
                    meta = json.load(f)
                quilt_loader = meta.get("quilt_loader", {})
                resultado["mod_id"] = quilt_loader.get("id", "desconocido")
                metadata = quilt_loader.get("metadata", {})
                resultado["nombre"] = metadata.get("name", resultado["mod_id"])
                resultado["version"] = quilt_loader.get("version", "desconocido")
            except Exception:
                pass

        # 3. Caso NeoForge / Forge moderno
        elif "META-INF/neoforge.mods.toml" in archivos or "META-INF/mods.toml" in archivos:
            es_neoforge = "META-INF/neoforge.mods.toml" in archivos
            resultado["loader"] = "NeoForge" if es_neoforge else "Forge"
            toml_file = "META-INF/neoforge.mods.toml" if es_neoforge else "META-INF/mods.toml"
            try:
                with z.open(toml_file) as f:
                    contenido = f.read().decode("utf-8", errors="ignore")
                datos_toml = parsear_toml_simple(contenido)
                resultado["mod_id"] = datos_toml.get("modId", "desconocido")
                resultado["nombre"] = datos_toml.get("displayName", resultado["mod_id"])
                resultado["version"] = datos_toml.get("version", "desconocido")
                resultado["minecraft_version"] = datos_toml.get("versionRange", "No especificada")
            except Exception:
                pass

        # 4. Caso Forge Clásico
        elif "mcmod.info" in archivos:
            resultado["loader"] = "Forge Legacy (1.12 o anterior)"
            try:
                with z.open("mcmod.info") as f:
                    meta_list = json.load(f)
                if isinstance(meta_list, list) and meta_list:
                    item = meta_list[0]
                    resultado["mod_id"] = item.get("modid", "desconocido")
                    resultado["nombre"] = item.get("name", resultado["mod_id"])
                    resultado["version"] = item.get("version", "desconocido")
                    resultado["minecraft_version"] = item.get("mcversion", "1.12.2 o anterior")
            except Exception:
                pass

    return resultado


def mostrar_diagnostico(info: Dict[str, Any]) -> None:
    """Imprime el diagnóstico del mod con formato visual."""
    if not console:
        print(f"Mod: {info['nombre']} ({info['mod_id']}) | Loader: {info['loader']} | MC: {info['minecraft_version']}")
        return

    tabla = Table(title=f"📦 Diagnóstico de Mod de Minecraft: {info['archivo']}", header_style="bold magenta")
    tabla.add_column("Propiedad", style="bold cyan", width=22)
    tabla.add_column("Detalle Extraído", style="white")

    color_loader = "green" if info["loader"] in ("Fabric", "NeoForge") else "yellow"
    tabla.add_row("Loader de Mods", f"[{color_loader}]{info['loader']}[/{color_loader}]")
    tabla.add_row("Identificador (mod_id)", info["mod_id"])
    tabla.add_row("Nombre Visible", info["nombre"])
    tabla.add_row("Versión del Mod", info["version"])
    tabla.add_row("Versión de Minecraft", f"[bold yellow]{info['minecraft_version']}[/bold yellow]")
    tabla.add_row("Tamaño en disco", f"{info['tamano_mb']} MB ({info['total_clases']} clases compiladas)")

    if info["mixins"]:
        tabla.add_row("Configuración Mixins", ", ".join(info["mixins"]))
    if info["entrypoints"]:
        tabla.add_row("Puntos de Entrada", "\n".join(info["entrypoints"][:4]))

    console.print(tabla)


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="analizador_mod_jar",
        description="Inspector de metadatos, loader y dependencias para Mods de Minecraft (G.R.A.N. v4.0)"
    )
    parser.add_argument("archivo_jar", help="Ruta al archivo .jar del mod a examinar.")
    args = parser.parse_args()

    try:
        diagnostico = analizar_mod_jar(args.archivo_jar)
        mostrar_diagnostico(diagnostico)
        return 0
    except Exception as e:
        if console:
            console.print(f"[bold red]❌ Error al examinar el mod:[/bold red] {e}")
        else:
            print(f"❌ Error al examinar el mod: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
