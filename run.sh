#!/bin/bash
# Kid Gun 1412 — アドオン＋gun_and_weapon統合ビルド・起動スクリプト
#
# 使い方:
#   bash run.sh                       対話式（version / release type / 起動方法）
#   bash run.sh offline               保存済みVERSIONでオフライン起動
#   bash run.sh install-only          統合JARをビルドして起動しない
#   bash run.sh offline install-only  オフライン統合ビルドのみ
#   bash run.sh 1.2.0-beta offline    完成バージョンを直接指定して起動
#
# 既定の実行環境:
#   ../gun_and_weapon
# 環境を変更する場合:
#   RUN_PROJECT_DIR=/path/to/forge-project bash run.sh offline
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEFAULT_RUN_PROJECT="$(cd "$PROJECT_DIR/.." && pwd)/gun_and_weapon"
RUN_PROJECT_DIR="${RUN_PROJECT_DIR:-$DEFAULT_RUN_PROJECT}"
OFFLINE=""
INSTALL_ONLY=""
VERSION="$(sed -n '1p' "$PROJECT_DIR/VERSION" 2>/dev/null || true)"
VERSION="${VERSION:-1.0.0}"
VERSION_OVERRIDE=""
INTERACTIVE=""

if [ "$#" -eq 0 ] && [ -t 0 ]; then
    INTERACTIVE=1
fi

for RUN_ARG in "$@"; do
    case "$RUN_ARG" in
        help|-h|--help)
            sed -n '2,14p' "$0" | sed 's/^# \{0,1\}//'
            exit 0
            ;;
        offline|-o|--offline) OFFLINE="offline" ;;
        install-only|--install-only) INSTALL_ONLY=1 ;;
        *) VERSION_OVERRIDE="$RUN_ARG" ;;
    esac
done

if [ -n "$VERSION_OVERRIDE" ]; then
    VERSION="$VERSION_OVERRIDE"
fi

if [ ! -d "$RUN_PROJECT_DIR" ]; then
    echo "[error] Forge開発環境が見つかりません: $RUN_PROJECT_DIR" >&2
    echo "        RUN_PROJECT_DIR=/path/to/forge-project bash run.sh offline" >&2
    exit 1
fi

if [ ! -f "$RUN_PROJECT_DIR/run_quick.sh" ]; then
    echo "[error] run_quick.sh がありません: $RUN_PROJECT_DIR/run_quick.sh" >&2
    exit 1
fi

if [ -n "$INTERACTIVE" ]; then
    bash "$PROJECT_DIR/build.sh"
    VERSION="$(sed -n '1p' "$PROJECT_DIR/VERSION")"

    printf '\n起動方法を選択してください:\n'
    printf '  [o] オフライン起動（既定）\n'
    printf '  [n] 通常起動\n'
    printf '  [i] ガンパックの配置のみ\n'
    printf '  > '
    read -r RUN_MODE
    case "${RUN_MODE:-o}" in
        o|offline) OFFLINE="offline" ;;
        n|normal) OFFLINE="" ;;
        i|install) OFFLINE="offline"; INSTALL_ONLY=1 ;;
        *)
            echo "[error] o / n / i から選択してください。" >&2
            exit 1
            ;;
    esac
else
    BUILD_ARGS=("$VERSION")
    if [ -n "$OFFLINE" ]; then
        BUILD_ARGS+=("offline")
    fi
    bash "$PROJECT_DIR/build.sh" "${BUILD_ARGS[@]}"
fi

PACK_FILE="$PROJECT_DIR/build/libs/kid_gun_1412-$VERSION.zip"
TAcz_DIR="$RUN_PROJECT_DIR/run/tacz"
INSTALLED_PACK="$TAcz_DIR/kid_gun_1412.zip"
EMBEDDED_PACK="$RUN_PROJECT_DIR/src/main/resources/assets/gun_and_weapon/custom/kid_gun_1412.zip"

mkdir -p "$TAcz_DIR"
cp -f "$PACK_FILE" "$INSTALLED_PACK"
echo "Installed gun pack: $INSTALLED_PACK"
mkdir -p "$(dirname "$EMBEDDED_PACK")"
cp -f "$PACK_FILE" "$EMBEDDED_PACK"
echo "Embedded gun pack : $EMBEDDED_PACK"

echo ""
echo "==> Building gun_and_weapon with Kid Gun 1412"
if [ -n "$OFFLINE" ]; then
    (cd "$RUN_PROJECT_DIR" && bash ./build.sh offline </dev/null)
else
    (cd "$RUN_PROJECT_DIR" && bash ./build.sh </dev/null)
fi

LATEST_MOD_JAR="$(find "$RUN_PROJECT_DIR/build/libs" -maxdepth 1 -type f -name 'gun_and_weapon-*.jar' \
    ! -name '*-sources.jar' ! -name '*-dev.jar' ! -name '*-javadoc.jar' -print0 \
    | xargs -0 ls -t | head -n 1)"
if [ -z "$LATEST_MOD_JAR" ] || [ ! -f "$LATEST_MOD_JAR" ]; then
    echo "[error] gun_and_weaponのJARが生成されませんでした。" >&2
    exit 1
fi
if ! jar tf "$LATEST_MOD_JAR" | grep -q '^assets/gun_and_weapon/custom/kid_gun_1412.zip$'; then
    echo "[error] 生成JARにKid Gun 1412が埋め込まれていません: $LATEST_MOD_JAR" >&2
    exit 1
fi
echo "Integrated mod JAR: $LATEST_MOD_JAR"

if [ -n "$INSTALL_ONLY" ]; then
    exit 0
fi

cd "$RUN_PROJECT_DIR"
if [ -n "$OFFLINE" ]; then
    # ForgeGradleのdownloadAssetsは --offline でもMojangへ再接続する場合がある。
    # 既存のローカルアセットキャッシュを使い、再ダウンロードだけを除外する。
    exec bash ./run_quick.sh offline -x downloadAssets
else
    exec bash ./run_quick.sh
fi
