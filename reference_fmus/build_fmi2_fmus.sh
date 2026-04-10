#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="${ROOT_DIR:-$SCRIPT_DIR/original_repo}"
BUILD_DIR="${BUILD_DIR:-$SCRIPT_DIR/build/fmi2-export}"
OUTPUT_DIR="${OUTPUT_DIR:-$SCRIPT_DIR/fmus}"
SSP_OUTPUT_DIR="${SSP_OUTPUT_DIR:-$SCRIPT_DIR/ssps}"
UNPACK_OUTPUT_DIR="${UNPACK_OUTPUT_DIR:-$SCRIPT_DIR/unpacked_ssps}"
PACKAGE_SCRIPT="${PACKAGE_SCRIPT:-$SCRIPT_DIR/../scripts/package_fmu_as_ssp.sh}"
UNPACK_SCRIPT="${UNPACK_SCRIPT:-$SCRIPT_DIR/../scripts/unpack_model_archive.sh}"

if command -v getconf >/dev/null 2>&1; then
  DEFAULT_JOBS="$(getconf _NPROCESSORS_ONLN)"
else
  DEFAULT_JOBS=1
fi

JOBS="${CMAKE_BUILD_PARALLEL_LEVEL:-$DEFAULT_JOBS}"

echo "Configuring FMI 2.0 build in: $BUILD_DIR"
cmake -S "$ROOT_DIR" -B "$BUILD_DIR" -DFMI_VERSION=2 -DWITH_FMUSIM=OFF

echo "Building FMUs with $JOBS job(s)"
cmake --build "$BUILD_DIR" -j"$JOBS"

mkdir -p "$OUTPUT_DIR"

echo "Copying FMI 2.0 FMUs to: $OUTPUT_DIR"
find "$BUILD_DIR/fmus" -maxdepth 1 -type f -name '*.fmu' -exec cp -f {} "$OUTPUT_DIR"/ \;

mkdir -p "$SSP_OUTPUT_DIR"
mkdir -p "$UNPACK_OUTPUT_DIR"

echo "Packaging SSPs to: $SSP_OUTPUT_DIR"
find "$OUTPUT_DIR" -maxdepth 1 -type f -name '*.fmu' | sort | while read -r fmu; do
  "$PACKAGE_SCRIPT" "$fmu" -o "$SSP_OUTPUT_DIR/$(basename "${fmu%.fmu}").ssp"
done

echo "Unpacking SSPs to: $UNPACK_OUTPUT_DIR"
find "$SSP_OUTPUT_DIR" -maxdepth 1 -type f -name '*.ssp' | sort | while read -r ssp; do
  unpack_dir="$UNPACK_OUTPUT_DIR/$(basename "${ssp%.ssp}")"
  rm -rf "$unpack_dir"
  "$UNPACK_SCRIPT" "$ssp" -o "$unpack_dir"
done

echo "Done. Copied FMUs:"
find "$OUTPUT_DIR" -maxdepth 1 -type f -name '*.fmu' | sort

echo "Generated SSPs:"
find "$SSP_OUTPUT_DIR" -maxdepth 1 -type f -name '*.ssp' | sort

echo "Unpacked SSP directories:"
find "$UNPACK_OUTPUT_DIR" -mindepth 1 -maxdepth 1 -type d | sort
