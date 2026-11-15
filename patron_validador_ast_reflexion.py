#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Patrón Maestro: Validador AST y Bucle de Auto-Reflexión para Agentes
=====================================================================
Estándar de ingeniería y blindaje de código para G.R.A.N. v4.0 y F.O.R.J.A.
Inspirado en la investigación 'Reflexion' (noahshinn/reflexion) y 'AST analysis'.

Características clave:
- Análisis sintáctico estático profundo con 'ast' estándar de Python (0 MB RAM extra).
- Detección previa de errores antes de guardar o ejecutar código en el sistema.
- Bucle de Reflexión Verbal: diagnostica la causa raíz de un traceback y formula
  una lección concisa lista para registrar en memoria.json.
- Consumo < 15 MB RAM.
"""

import sys
import os
import ast
import json
import argparse
import subprocess
from typing import Dict, Any, List, Optional, Tuple

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    HAVE_RICH = True
except ImportError:
    HAVE_RICH = False

console = Console() if HAVE_RICH else None


def validar_sintaxis_ast(codigo_fuente: str) -> Tuple[bool, Optional[str], Optional[int], Optional[int]]:
    """
    Valida sintácticamente el código fuente utilizando el árbol de sintaxis abstracta (AST).
    Retorna (es_valido, mensaje_error, linea, columna).
    """
    try:
        ast.parse(codigo_fuente)
        return True, None, None, None
    except SyntaxError as e:
        return False, e.msg, e.lineno, e.offset
    except Exception as e:
        return False, str(e), None, None


def inspeccionar_calidad_ast(codigo_fuente: str) -> Dict[str, Any]:
    """
    Inspecciona métricas de calidad y buenas prácticas en el código:
    - Funciones definidas y docstrings
    - Clases declaradas
    - Bucles while (para prevenir bucles infinitos)
    - Importaciones
    """
    try:
        arbol = ast.parse(codigo_fuente)
    except SyntaxError:
        return {"valido": False, "error": "No se pudo generar el AST por error de sintaxis."}

    funciones: List[str] = []
    clases: List[str] = []
    imports: List[str] = []
    tiene_bucles_while: bool = False
    bloques_try: int = 0

    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.FunctionDef):
            funciones.append(nodo.name)
        elif isinstance(nodo, ast.ClassDef):
            clases.append(nodo.name)
        elif isinstance(nodo, (ast.Import, ast.ImportFrom)):
            if isinstance(nodo, ast.Import):
                for alias in nodo.names:
                    imports.append(alias.name)
            else:
                modulo = nodo.module or ""
                for alias in nodo.names:
                    imports.append(f"{modulo}.{alias.name}")
        elif isinstance(nodo, ast.While):
            tiene_bucles_while = True
        elif isinstance(nodo, ast.Try):
            bloques_try += 1

    return {
        "valido": True,
        "total_funciones": len(funciones),
        "funciones": funciones,
        "total_clases": len(clases),
        "clases": clases,
        "imports": imports,
        "tiene_bucles_while": tiene_bucles_while,
        "bloques_try": bloques_try,
    }


def reflexionar_sobre_error(
    archivo: str,
    codigo_fuente: str,
    traceback_error: str
) -> Dict[str, str]:
    """
    Genera un bloque de Reflexión Verbal estructurado:
    1. Diagnóstico de fallo
    2. Causa raíz
    3. Lección aprendida (para memoria.json)
    4. Plan de corrección
    """
    linea_afectada = "Desconocida"
    tipo_error = "Error de Ejecución / Sintaxis"

    # Intentar extraer línea del error
    if "line " in traceback_error:
        partes = traceback_error.split("line ")
        if len(partes) > 1:
            num = ""
            for ch in partes[-1]:
                if ch.isdigit():
                    num += ch
                else:
                    break
            if num:
                linea_afectada = num

    if "SyntaxError" in traceback_error:
        tipo_error = "SyntaxError (Sintaxis rota)"
    elif "ImportError" in traceback_error or "ModuleNotFoundError" in traceback_error:
        tipo_error = "Dependencia Faltante (Módulo no instalado)"
    elif "TypeError" in traceback_error:
        tipo_error = "TypeError (Tipado incompatible)"
    elif "IndexError" in traceback_error or "KeyError" in traceback_error:
        tipo_error = "Acceso a elemento inexistente (Límites de lista o llave de dict)"

    leccion = (
        f"Regla detectada para '{os.path.basename(archivo)}': "
        f"Prevenir {tipo_error} validando entradas y tipos en la línea {linea_afectada} antes de invocar la operación."
    )

    sugerencia = (
        f"1. Revisar la línea {linea_afectada} del archivo {os.path.basename(archivo)}.\n"
        f"2. Envolver la llamada en bloque try/except o verificar existencia previa con 'if'.\n"
        f"3. Validar con 'ast.parse()' antes de escribir la modificación final."
    )

    return {
        "archivo": archivo,
        "tipo_error": tipo_error,
        "linea_afectada": linea_afectada,
        "diagnostico": traceback_error.strip().splitlines()[-1] if traceback_error.strip() else "Error no especificado",
        "leccion_verbal": leccion,
        "sugerencia_parche": sugerencia,
    }


def ejecutar_test_con_reflexion(ruta_script: str) -> Dict[str, Any]:
    """
    Ejecuta un script en subproceso con timeout y, si falla, realiza una auto-reflexión inmediata.
    """
    if not os.path.exists(ruta_script):
        return {"exito": False, "error": f"El archivo '{ruta_script}' no existe."}

    with open(ruta_script, "r", encoding="utf-8", errors="replace") as f:
        codigo = f.read()

    # 1. Validación estática previa
    es_valido, msg_err, lineno, col = validar_sintaxis_ast(codigo)
    if not es_valido:
        err_str = f"SyntaxError en línea {lineno}, columna {col}: {msg_err}"
        reflexion = reflexionar_sobre_error(ruta_script, codigo, err_str)
        return {
            "exito": False,
            "fase": "analisis_ast_estatico",
            "error": err_str,
            "reflexion": reflexion
        }

    # 2. Prueba dinámica de arranque (dry-run o ejecución con timeout)
    try:
        proc = subprocess.run(
            [sys.executable, ruta_script, "--help"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False
        )
        if proc.returncode != 0 and proc.stderr:
            reflexion = reflexionar_sobre_error(ruta_script, codigo, proc.stderr)
            return {
                "exito": False,
                "fase": "ejecucion_dinamica",
                "error": proc.stderr.strip(),
                "reflexion": reflexion
            }
        return {
            "exito": True,
            "fase": "validado_completo",
            "detalles": "El script pasó validación AST estática y prueba de arranque."
        }
    except subprocess.TimeoutExpired:
        err_str = "TimeoutExpired: La ejecución superó los 10 segundos (posible bucle infinito)."
        reflexion = reflexionar_sobre_error(ruta_script, codigo, err_str)
        return {
            "exito": False,
            "fase": "tiempo_limite",
            "error": err_str,
            "reflexion": reflexion
        }
    except Exception as e:
        err_str = str(e)
        reflexion = reflexionar_sobre_error(ruta_script, codigo, err_str)
        return {
            "exito": False,
            "fase": "excepcion_subproceso",
            "error": err_str,
            "reflexion": reflexion
        }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Patrón Maestro: Validador AST y Bucle de Auto-Reflexión para Agentes (G.R.A.N. v4.0)"
    )
    parser.add_argument("archivo", help="Ruta al script Python que se desea auditar o evaluar.")
    parser.add_argument("--test", action="store_true", help="Ejecuta una prueba de arranque y genera reflexión si falla.")
    parser.add_argument("--error", type=str, default="", help="Texto de error o traceback para reflexionar sobre él.")
    parser.add_argument("--json", action="store_true", help="Devuelve la salida en formato JSON puro.")

    args = parser.parse_args()

    if not os.path.exists(args.archivo):
        print(f"❌ Error: El archivo '{args.archivo}' no existe.", file=sys.stderr)
        return 1

    with open(args.archivo, "r", encoding="utf-8", errors="replace") as f:
        codigo = f.read()

    if args.test:
        resultado = ejecutar_test_con_reflexion(args.archivo)
        if args.json:
            print(json.dumps(resultado, indent=2, ensure_ascii=False))
            return 0 if resultado["exito"] else 1

        if HAVE_RICH:
            if resultado["exito"]:
                console.print(Panel(
                    f"[bold green]✔ Script validado con éxito:[/bold green] {args.archivo}\n"
                    f"[white]{resultado['detalles']}[/white]",
                    title="🧠 G.R.A.N. AST Validator",
                    border_style="green"
                ))
            else:
                ref = resultado.get("reflexion", {})
                console.print(Panel(
                    f"[bold red]❌ Fallo detectado en fase:[/bold red] {resultado['fase']}\n\n"
                    f"[bold yellow]Diagnóstico:[/bold yellow] {ref.get('diagnostico')}\n"
                    f"[bold cyan]Línea Afectada:[/bold cyan] {ref.get('linea_afectada')}\n\n"
                    f"[bold magenta]🧠 Reflexión Verbal para Memoria:[/bold magenta]\n"
                    f"{ref.get('leccion_verbal')}\n\n"
                    f"[bold green]🔧 Sugerencia de Corrección:[/bold green]\n"
                    f"{ref.get('sugerencia_parche')}",
                    title="⚡ Bucle de Reflexión y Auto-Corrección",
                    border_style="red"
                ))
        else:
            print(json.dumps(resultado, indent=2, ensure_ascii=False))
        return 0 if resultado["exito"] else 1

    # Validación AST directa
    valido, msg_err, lineno, col = validar_sintaxis_ast(codigo)
    calidad = inspeccionar_calidad_ast(codigo)

    if args.error:
        reflexion = reflexionar_sobre_error(args.archivo, codigo, args.error)
    else:
        reflexion = None

    if args.json:
        res_json = {
            "archivo": args.archivo,
            "sintaxis_valida": valido,
            "error_sintaxis": msg_err,
            "linea": lineno,
            "columna": col,
            "metricas": calidad,
            "reflexion": reflexion
        }
        print(json.dumps(res_json, indent=2, ensure_ascii=False))
        return 0 if valido else 1

    if HAVE_RICH:
        if valido:
            tabla = Table(title="📊 Métricas de Estructura AST (Calidad de Código)")
            tabla.add_column("Métrica", style="cyan")
            tabla.add_column("Valor", style="green")

            tabla.add_row("Funciones declaradas", str(calidad.get("total_funciones", 0)))
            tabla.add_row("Clases declaradas", str(calidad.get("total_clases", 0)))
            tabla.add_row("Bloques Try/Except", str(calidad.get("bloques_try", 0)))
            tabla.add_row("Usa bucles While", "Sí" if calidad.get("tiene_bucles_while") else "No")
            tabla.add_row("Módulos importados", ", ".join(calidad.get("imports", [])[:5]) or "Ninguno")

            console.print(Panel(
                f"[bold green]✔ Sintaxis AST 100% Válida:[/bold green] {args.archivo}",
                title="🧠 G.R.A.N. AST Validator",
                border_style="green"
            ))
            console.print(tabla)
        else:
            console.print(Panel(
                f"[bold red]❌ Error de Sintaxis Detectado:[/bold red]\n"
                f"[yellow]Archivo:[/yellow] {args.archivo}\n"
                f"[yellow]Línea {lineno}, Columna {col}:[/yellow] {msg_err}",
                title="🚨 Error de Sintaxis AST",
                border_style="red"
            ))
    else:
        print(f"Sintaxis válida: {valido}")
        if not valido:
            print(f"Error: {msg_err} en línea {lineno}")

    return 0 if valido else 1


if __name__ == "__main__":
    sys.exit(main())
