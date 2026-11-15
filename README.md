# 🧠 G.R.A.N. Knowledge & Pattern Repository
### Repositorio de Conocimiento y Patrones Maestros para G.R.A.N. v4.0

Este repositorio almacena los estándares de oro de ingeniería, patrones de diseño ligeros y plantillas de desarrollo artesanal para el asistente personal **G.R.A.N.** y su subagente desarrollador **F.O.R.J.A.**.

---

## 🎯 Propósito del Repositorio

1. **Aprendizaje por Demostración (Few-Shot Learning):**
   Los modelos locales como `qwen2.5-coder:7b` razonan con mayor precisión cuando disponen de ejemplos concretos de código de producción en lugar de solo directrices teóricas.
2. **Blindaje para Hardware Escolar (2 GB RAM):**
   Todo patrón en este repositorio está certificado para ejecutarse con menos de **25 MB de memoria RAM**, excluyendo terminantemente dependencias hipertróficas como `pandas` o `tensorflow`.
3. **Pensamiento Técnico y Razonamiento Previo:**
   F.O.R.J.A. estructura un bloque de análisis técnico (`<pensamiento>`) antes de escribir código basándose en estas plantillas.
4. **Auto-Mejora y Soberanía Local:**
   Herramientas independientes de filtros externos para validar sintaxis AST, auto-reflexionar sobre errores, forjar mods y remasterizar sistemas operativos.

---

## 📚 Catálogo de los 10 Patrones Maestros

| # | Archivo | Tipo | Propósito | Tecnologías Clave |
| :-: | :--- | :---: | :--- | :--- |
| **1** | `patron_cli_profesional.py` | Python | Interfaces de consola profesionales con validación de entradas. | `argparse`, `rich`, `typing`, `dataclasses` |
| **2** | `patron_monitor_recursos.py` | Python | Monitor de rendimiento del sistema y memoria en tiempo real. | `psutil`, `rich`, `time` |
| **3** | `patron_modulo_logica.py` | Python | Lógica de negocio desacoplada con suite de pruebas unitarias. | `unittest`, `dataclasses`, `typing` |
| **4** | `patron_script_seguro.sh` | Bash | Automatización de tareas de sistema operativo protegidas contra errores. | `set -euo pipefail`, `trap`, `getopts` |
| **5** | `patron_datapack_builder.py` | Python | Forjador de Datapacks de Minecraft con mapeo de pack_format. | `json`, `rich`, `typing`, `argparse` |
| **6** | `patron_analizador_mod_jar.py` | Python | Inspector de mods (.jar) para Fabric, Quilt, NeoForge y Forge. | `zipfile`, `json`, `rich`, `typing` |
| **7** | `patron_optimizador_linux.py` | Python | Auditor de servicios de inicio, ZRAM, earlyoom y preload. | `subprocess`, `rich`, `argparse` |
| **8** | `patron_validador_ast_reflexion.py` | Python | Validador sintáctico AST y bucle de auto-reflexión verbal para corregir errores. | `ast`, `subprocess`, `rich`, `typing` |
| **9** | `patron_fabric_mod_scaffolder.py` | Python | Generador de mods Fabric en Java/Gradle con mixins y configuración oficial. | `json`, `rich`, `typing`, `argparse` |
| **10** | `patron_remasterizador_iso.sh` | Bash | Remasterizador de ISOs de Linux con compresión SquashFS y arranque híbrido. | `xorriso`, `squashfs-tools`, `set -euo pipefail` |

---

## 🔗 Repositorio Oficial en GitHub

Repositorio respaldado en la nube:
👉 **[https://github.com/forgent500-sudo/gran-knowledg](https://github.com/forgent500-sudo/gran-knowledg)**

Para sincronizar o subir nuevos cambios:
```bash
cd D:\WSL\Proyecto_WSL_Linux_IA\patrones  # o en WSL: cd /home/forge/lab_gran/patrones
git push -u origin main
```

---

*Desarrollado para el proyecto G.R.A.N. v4.0 (Jorge).*
