#!/bin/bash
# Java MOD起動: bash run.sh [version] [offline] [install-only]
set -euo pipefail
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OFFLINE=""; INSTALL_ONLY=""; BUILD_ARGS=()
for ARG in "$@"; do case "$ARG" in offline|-o|--offline) OFFLINE=1; BUILD_ARGS+=(offline);; install-only|--install-only) INSTALL_ONLY=1;; *) BUILD_ARGS+=("$ARG");; esac; done
bash "$PROJECT_DIR/build.sh" "${BUILD_ARGS[@]}"
[ -n "$INSTALL_ONLY" ] && exit 0
cd "$PROJECT_DIR"
ARGS=(runClient --no-daemon -Dnet.minecraftforge.gradle.check.certs=false)
[ -n "$OFFLINE" ] && ARGS+=(--offline -x downloadAssets)
exec ./gradlew "${ARGS[@]}"
