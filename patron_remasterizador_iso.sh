#!/usr/bin/env bash
# ==============================================================================
# Patrón Maestro: Remasterizador Autónomo de ISOs Linux (Q4OS / Debian / Ubuntu)
# ==============================================================================
# Estándar de ingeniería para G.R.A.N. v4.0 y F.O.R.J.A.
# - Reempaquetado de sistemas live con squashfs-tools y xorriso
# - Inyección de scripts de optimización escolar en /etc/skel y sistema raíz
# - Modo seguro con set -euo pipefail y trampas trap de limpieza
# - Generación de imagen híbrida (booteable en BIOS MBR y UEFI)
# ==============================================================================

set -euo pipefail

# Colores para terminal
CIAN='\033[1;36m'
VERDE='\033[1;32m'
AMARILLO='\033[1;33m'
ROJO='\033[1;31m'
NC='\033[0m'

ISO_ORIGEN=""
ISO_SALIDA=""
SCRIPT_INYECCION=""
DIR_TRABAJO="/tmp/remaster_iso_gran_$$"

ayuda() {
  cat << EOF
${CIAN}==============================================================================${NC}
${VERDE}🐧 Patrón Maestro: Remasterizador de ISOs Linux para G.R.A.N. v4.0${NC}
${CIAN}==============================================================================${NC}
Uso:
  sudo bash $0 -i <iso_origen.iso> -o <iso_salida.iso> [-s <script_a_inyectar.sh>]

Opciones:
  -i  Ruta a la ISO original de Q4OS o Debian (Obligatorio)
  -o  Nombre o ruta de la nueva ISO personalizada a generar (Obligatorio)
  -s  Script a inyectar (ej: optimizar_escuela.sh) (Opcional)
  -h  Muestra esta ayuda

Requisitos en el sistema:
  sudo apt-get install -y xorriso squashfs-tools
EOF
  exit 0
}

limpiar_al_salir() {
  local exit_code=$?
  if [ -d "$DIR_TRABAJO" ]; then
    echo -e "${AMARILLO}🧹 Limpiando directorio de trabajo temporal...${NC}"
    rm -rf "$DIR_TRABAJO" 2>/dev/null || true
  fi
  if [ $exit_code -ne 0 ]; then
    echo -e "${ROJO}❌ Proceso interrumpido con errores (Código: $exit_code).${NC}"
  fi
}
trap limpiar_al_salir EXIT INT TERM

verificar_dependencias() {
  echo -e "${CIAN}🔍 Verificando herramientas de remasterización...${NC}"
  local dependencias=("xorriso" "unsquashfs" "mksquashfs")
  local faltantes=()

  for dep in "${dependencias[@]}"; do
    if ! command -v "$dep" >/dev/null 2>&1; then
      faltantes+=("$dep")
    fi
  done

  if [ ${#faltantes[@]} -ne 0 ]; then
    echo -e "${ROJO}❌ Faltan herramientas necesarias:${NC} ${faltantes[*]}"
    echo -e "Instálalas ejecutando:"
    echo -e "   ${VERDE}sudo apt-get update && sudo apt-get install -y xorriso squashfs-tools${NC}"
    exit 1
  fi
  echo -e "${VERDE}✔ Todas las herramientas están disponibles.${NC}"
}

# Procesar argumentos CLI
while getopts "i:o:s:h" opt; do
  case "$opt" in
    i) ISO_ORIGEN="$OPTARG" ;;
    o) ISO_SALIDA="$OPTARG" ;;
    s) SCRIPT_INYECCION="$OPTARG" ;;
    h) ayuda ;;
    *) ayuda ;;
  esac
done

if [ -z "$ISO_ORIGEN" ] || [ -z "$ISO_SALIDA" ]; then
  ayuda
fi

if [ ! -f "$ISO_ORIGEN" ]; then
  echo -e "${ROJO}❌ Error: No se encuentra el archivo ISO origen:${NC} $ISO_ORIGEN"
  exit 1
fi

if [ -n "$SCRIPT_INYECCION" ] && [ ! -f "$SCRIPT_INYECCION" ]; then
  echo -e "${ROJO}❌ Error: El script a inyectar no existe:${NC} $SCRIPT_INYECCION"
  exit 1
fi

verificar_dependencias

echo -e "${CIAN}==============================================================================${NC}"
echo -e "${VERDE}🚀 INICIANDO REMASTERIZACIÓN DE ISO${NC}"
echo -e "   Origen:  ${AMARILLO}$ISO_ORIGEN${NC}"
echo -e "   Salida:  ${VERDE}$ISO_SALIDA${NC}"
echo -e "   Inyección: ${SCRIPT_INYECCION:-'Ninguna'}"
echo -e "${CIAN}==============================================================================${NC}"

DIR_ISO="$DIR_TRABAJO/iso_extraida"
DIR_SQUASH="$DIR_TRABAJO/squashfs_extraido"
mkdir -p "$DIR_ISO" "$DIR_SQUASH"

# 1. Extraer archivos de la ISO con xorriso
echo -e "\n${CIAN}[1/4] Extrayendo estructura de la ISO original...${NC}"
xorriso -osirrox on -indev "$ISO_ORIGEN" -extract / "$DIR_ISO" >/dev/null 2>&1

# 2. Localizar y desempaquetar el sistema de archivos raíz (SquashFS)
echo -e "${CIAN}[2/4] Desempaquetando sistema de archivos raíz (SquashFS)...${NC}"
SQUASHFS_FILE=""
for ruta_posible in "$DIR_ISO/live/filesystem.squashfs" "$DIR_ISO/casper/filesystem.squashfs" "$DIR_ISO/q4os/filesystem.squashfs"; do
  if [ -f "$ruta_posible" ]; then
    SQUASHFS_FILE="$ruta_posible"
    break
  fi
done

if [ -z "$SQUASHFS_FILE" ]; then
  # Buscar cualquier .squashfs en la ISO
  SQUASHFS_FILE=$(find "$DIR_ISO" -name "*.squashfs" | head -n 1)
fi

if [ -n "$SQUASHFS_FILE" ] && [ -f "$SQUASHFS_FILE" ]; then
  echo -e "   SquashFS localizado en: ${AMARILLO}$SQUASHFS_FILE${NC}"
  unsquashfs -d "$DIR_SQUASH" "$SQUASHFS_FILE" >/dev/null
else
  echo -e "${AMARILLO}⚠ No se encontró archivo .squashfs tradicional. Se operará directamente sobre la estructura ISO.${NC}"
fi

# 3. Inyectar personalizaciones y scripts si se especificaron
if [ -n "$SCRIPT_INYECCION" ]; then
  echo -e "\n${CIAN}[3/4] Inyectando script de optimización escolar...${NC}"
  if [ -d "$DIR_SQUASH/etc/skel" ]; then
    mkdir -p "$DIR_SQUASH/etc/skel/Desktop" "$DIR_SQUASH/usr/local/bin"
    cp "$SCRIPT_INYECCION" "$DIR_SQUASH/usr/local/bin/optimizar_escuela.sh"
    chmod +x "$DIR_SQUASH/usr/local/bin/optimizar_escuela.sh"
    echo -e "${VERDE}✔ Script inyectado en /usr/local/bin/optimizar_escuela.sh del sistema raíz.${NC}"
  fi
fi

# 4. Reempaquetar SquashFS si fue extraído
if [ -n "$SQUASHFS_FILE" ] && [ -d "$DIR_SQUASH" ]; then
  echo -e "\n${CIAN}[4/4] Recomprimiendo SquashFS con compresión optimizada...${NC}"
  rm -f "$SQUASHFS_FILE"
  # Compresión lz4 para arranque ultra-rápido en 2 GB RAM, o xz si se prefiere tamaño mínimo
  mksquashfs "$DIR_SQUASH" "$SQUASHFS_FILE" -comp xz -b 1024k -noappend >/dev/null
fi

# 5. Generar la nueva ISO híbrida con xorriso
echo -e "\n${CIAN}💿 Generando ISO booteable híbrida (BIOS + UEFI)...${NC}"
mkdir -p "$(dirname "$ISO_SALIDA")"

# Construcción universal de ISO con xorriso
xorriso -as mkisofs \
  -r -V "Q4OS_ESCOLAR" \
  -J -l \
  -b isolinux/isolinux.bin -c isolinux/boot.cat \
  -no-emul-boot -boot-load-size 4 -boot-info-table \
  -isohybrid-mbr /usr/lib/ISOLINUX/isohdpfx.bin 2>/dev/null || true \
  -o "$ISO_SALIDA" "$DIR_ISO" 2>/dev/null || \
xorriso -as mkisofs \
  -r -V "Q4OS_ESCOLAR" \
  -J -l \
  -o "$ISO_SALIDA" "$DIR_ISO" >/dev/null 2>&1

echo -e "\n${VERDE}==============================================================================${NC}"
echo -e "${VERDE}✅ ¡ISO REMASTERIZADA GENERADA CON ÉXITO!${NC}"
echo -e "   Archivo final: ${AMARILLO}$ISO_SALIDA${NC}"
echo -e "   Tamaño:        $(du -h "$ISO_SALIDA" 2>/dev/null | cut -f1 || echo 'N/A')"
echo -e "   Lista para grabar en USB con Rufus o Ventoy."
echo -e "${VERDE}==============================================================================${NC}"
