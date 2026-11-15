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

---

## 📚 Catálogo de Patrones Maestros

| Archivo | Tipo | Propósito | Tecnologías Clave |
| :--- | :---: | :--- | :--- |
| `patron_cli_profesional.py` | Python | Interfaces de consola profesionales con validación de entradas. | `argparse`, `rich`, `typing`, `dataclasses` |
| `patron_monitor_recursos.py` | Python | Monitor de rendimiento del sistema y memoria en tiempo real. | `psutil`, `rich`, `time` |
| `patron_modulo_logica.py` | Python | Lógica de negocio desacoplada con suite de pruebas unitarias. | `unittest`, `dataclasses`, `typing` |
| `patron_script_seguro.sh` | Bash | Automatización de tareas de sistema operativo protegidas contra errores. | `set -euo pipefail`, `trap`, `getopts` |
| `patron_datapack_builder.py` | Python | Forjador de Datapacks de Minecraft con mapeo de pack_format. | `json`, `rich`, `typing`, `argparse` |
| `patron_analizador_mod_jar.py` | Python | Inspector de mods (.jar) para Fabric, Quilt, NeoForge y Forge. | `zipfile`, `json`, `rich`, `typing` |
| `patron_optimizador_linux.py` | Python | Auditor de servicios de inicio, ZRAM, earlyoom y preload. | `subprocess`, `rich`, `argparse` |

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
