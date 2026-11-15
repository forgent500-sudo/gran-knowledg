#!/usr/bin/env bash
# ==============================================================================
# Patrón Maestro: Script Seguro de Automatización en Bash
# ==============================================================================
# Estándar de scripting seguro para F.O.R.J.A. (G.R.A.N. v4.0)
# - Modo estricto: set -euo pipefail
# - Trampas de limpieza automática con trap
# - Verificación de privilegios y argumentos
# - Compatible con Debian / Q4OS Trinity / Ubuntu WSL
# ==============================================================================

set -euo pipefail

# Colores de terminal seguros
VERDE='\033[1;32m'
AZUL='\033[1;34m'
AMARILLO='\033[1;33m'
ROJO='\033[1;31m'
RESET='\033[0m'

ARCHIVO_TEMPORAL=""

# Función de limpieza al salir (éxito o fallo)
limpieza() {
    local exit_code=$?
    if [[ -n "${ARCHIVO_TEMPORAL:-}" && -f "${ARCHIVO_TEMPORAL:-}" ]]; then
        rm -f "$ARCHIVO_TEMPORAL"
    fi
    if [[ $exit_code -ne 0 ]]; then
        echo -e "${ROJO}❌ El script finalizó con código de error: $exit_code${RESET}" >&2
    fi
}
trap limpieza EXIT INT TERM

# Funciones de logging
log_info() {
    echo -e "${AZUL}ℹ️  [INFO]:${RESET} $*"
}

log_ok() {
    echo -e "${VERDE}✅ [ÉXITO]:${RESET} $*"
}

log_warn() {
    echo -e "${AMARILLO}⚠️  [ADVERTENCIA]:${RESET} $*"
}

log_error() {
    echo -e "${ROJO}❌ [ERROR]:${RESET} $*" >&2
}

# Ayuda del script
mostrar_ayuda() {
    cat <<EOF
Uso: $(basename "$0") [OPCIONES] <OBJETIVO>

Script seguro de automatización para G.R.A.N.

Opciones:
  -h, --help       Muestra este mensaje de ayuda.
  -v, --verbose    Modo detallado de depuración.
  -f, --forzar     Ejecuta sin pedir confirmación.

Ejemplo:
  $(basename "$0") --verbose /var/log/app
EOF
}

# Análisis de argumentos
MODO_VERBOSE=false
FORZAR=false
OBJETIVO=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        -h|--help)
            mostrar_ayuda
            exit 0
            ;;
        -v|--verbose)
            MODO_VERBOSE=true
            shift
            ;;
        -f|--forzar)
            FORZAR=true
            shift
            ;;
        -*)
            log_error "Opción desconocida: $1"
            mostrar_ayuda
            exit 2
            ;;
        *)
            if [[ -z "$OBJETIVO" ]]; then
                OBJETIVO="$1"
            else
                log_warn "Argumento adicional ignorado: $1"
            fi
            shift
            ;;
    esac
done

if [[ -z "$OBJETIVO" ]]; then
    OBJETIVO="predeterminado"
    log_info "No se especificó objetivo, utilizando: $OBJETIVO"
fi

# Creación de archivo temporal seguro
ARCHIVO_TEMPORAL=$(mktemp /tmp/gran_seguro.XXXXXX)

if $MODO_VERBOSE; then
    log_info "Archivo temporal asignado: $ARCHIVO_TEMPORAL"
fi

# Tarea simulada protegida
echo "Datos de ejecución para $OBJETIVO a las $(date)" > "$ARCHIVO_TEMPORAL"

log_ok "Operación completada con seguridad sobre el objetivo '$OBJETIVO'."
exit 0
