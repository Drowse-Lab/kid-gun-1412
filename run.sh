#!/usr/bin/env bash
# 開発用Minecraftクライアント起動: bash run.sh [version] [offline]
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GRADLE_ARGS=(
    runClient
    --no-daemon
    -Dnet.minecraftforge.gradle.check.certs=false
)
VERSION_OVERRIDE=""

for RUN_ARG in "$@"; do
    case "$RUN_ARG" in
        offline|-o|--offline)
            GRADLE_ARGS+=(--offline -x downloadAssets)
            ;;
        -h|--help)
            echo "Usage: bash run.sh [version] [--offline]"
            exit 0
            ;;
        *)
            if [ -n "$VERSION_OVERRIDE" ]; then
                echo "[error] Multiple versions specified: $VERSION_OVERRIDE, $RUN_ARG" >&2
                exit 2
            fi
            VERSION_OVERRIDE="$RUN_ARG"
            ;;
    esac
done

if [ -n "$VERSION_OVERRIDE" ]; then
    GRADLE_ARGS+=("-Pmod_version=$VERSION_OVERRIDE")
fi

if ! command -v java >/dev/null 2>&1; then
    echo "[error] Java 17 is required, but java was not found." >&2
    exit 1
fi

JAVA_MAJOR="$(java -version 2>&1 | sed -nE '1s/.*version "([0-9]+).*/\1/p')"
if [ "$JAVA_MAJOR" != "17" ]; then
    echo "[error] Java 17 is required (current: ${JAVA_MAJOR:-unknown})." >&2
    exit 1
fi

cd "$PROJECT_DIR"
exec ./gradlew "${GRADLE_ARGS[@]}"
