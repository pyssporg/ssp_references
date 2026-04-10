#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
ROOT_DIR="${ROOT_DIR:-$REPO_ROOT/3rd_party/reference_fmus}"
BUILD_DIR="${BUILD_DIR:-$REPO_ROOT/build/reference_fmus/fmi2-export}"
MODELS_DIR="${MODELS_DIR:-$REPO_ROOT/models/}"
PACKAGE_SCRIPT="${PACKAGE_SCRIPT:-$REPO_ROOT/scripts/package_fmu_as_ssp.sh}"
UNPACK_SCRIPT="${UNPACK_SCRIPT:-$REPO_ROOT/scripts/unpack_model_archive.sh}"
CACHE_FILE="$BUILD_DIR/CMakeCache.txt"

if command -v getconf >/dev/null 2>&1; then
  DEFAULT_JOBS="$(getconf _NPROCESSORS_ONLN)"
else
  DEFAULT_JOBS=1
fi

JOBS="${CMAKE_BUILD_PARALLEL_LEVEL:-$DEFAULT_JOBS}"

if [[ -f "$CACHE_FILE" ]] && ! grep -Fq "$ROOT_DIR" "$CACHE_FILE"; then
  echo "Removing stale CMake cache from moved layout: $BUILD_DIR"
  rm -rf "$BUILD_DIR"
fi

echo "Configuring FMI 2.0 build in: $BUILD_DIR"
cmake -S "$ROOT_DIR" -B "$BUILD_DIR" -DFMI_VERSION=2 -DWITH_FMUSIM=OFF

echo "Building FMUs with $JOBS job(s)"
cmake --build "$BUILD_DIR" -j"$JOBS"

mkdir -p "$MODELS_DIR"

echo "Organizing model artifacts under: $MODELS_DIR"
find "$BUILD_DIR/fmus" -maxdepth 1 -type f -name '*.fmu' | sort | while read -r built_fmu; do
  model_name="$(basename "${built_fmu%.fmu}")"
  model_dir="$MODELS_DIR/$model_name"
  fmu_dir="$model_dir/fmus"
  ssp_path="$model_dir/$model_name.ssp"
  unpack_dir="$model_dir/ssp"

  mkdir -p "$fmu_dir"
  cp -f "$built_fmu" "$fmu_dir/"

  rm -rf "$unpack_dir"

  "$PACKAGE_SCRIPT" "$fmu_dir/$model_name.fmu" -o "$ssp_path"
  "$UNPACK_SCRIPT" "$ssp_path" -o "$unpack_dir"
done

echo "Done. Generated model folders:"
find "$MODELS_DIR" -mindepth 1 -maxdepth 1 -type d | sort
