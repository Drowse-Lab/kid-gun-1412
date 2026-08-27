#!/bin/bash
# Java MODビルド: bash build.sh [version] [offline] [clean]
set -euo pipefail
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VERSION="$(sed -n '1p' "$PROJECT_DIR/VERSION" 2>/dev/null || true)"; VERSION="${VERSION:-1.2.0-rc}"
OFFLINE=""; CLEAN=""; OVERRIDE=""
for ARG in "$@"; do case "$ARG" in offline|-o|--offline) OFFLINE=1;; clean) CLEAN=1;; *) OVERRIDE="$ARG";; esac; done
if [ -n "$OVERRIDE" ]; then VERSION="$OVERRIDE"
elif [ "$#" -eq 0 ] && [ -t 0 ]; then
  BASE="$(printf '%s' "$VERSION" | sed -E 's/-(alpha|beta|rc|test)(\.[0-9]+)?$//')"
  printf '\n[Kid Gun 1412] バージョン [%s]:\n  > ' "$BASE"; read -r INPUT; BASE="${INPUT:-$BASE}"
  printf '種別 [r]release [b]beta [a]alpha [rc]RC [t]test:\n  > '; read -r TYPE
  case "${TYPE:-r}" in r|release) SUFFIX="";; b|beta) SUFFIX="-beta";; a|alpha) SUFFIX="-alpha";; rc) SUFFIX="-rc";; t|test) SUFFIX="-test";; *) exit 1;; esac
  VERSION="${BASE}${SUFFIX}"
fi
printf '%s\n' "$VERSION" > "$PROJECT_DIR/VERSION"
ARGS=(build --no-daemon -Pmod_version="$VERSION" -Dnet.minecraftforge.gradle.check.certs=false)
[ -n "$CLEAN" ] && ARGS=(clean "${ARGS[@]}")
[ -n "$OFFLINE" ] && ARGS+=(--offline)
cd "$PROJECT_DIR"; ./gradlew "${ARGS[@]}"
echo; echo "Build complete"; echo "  version: $VERSION"; echo "  output : $PROJECT_DIR/build/libs/kid_gun_1412-$VERSION.jar"
