#!/bin/bash
# Kid Gun 1412を埋め込んでgun_and_weapon本体までビルドする。
#
# 使い方:
#   bash build_all.sh                 対話式アドオンビルド＋本体ビルド
#   bash build_all.sh offline         保存済みVERSIONでオフラインビルド
#   bash build_all.sh 1.2.0 offline   バージョン指定＋オフラインビルド
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEFAULT_MOD_PROJECT="$(cd "$PROJECT_DIR/.." && pwd)/gun_and_weapon"
MOD_PROJECT_DIR="${MOD_PROJECT_DIR:-$DEFAULT_MOD_PROJECT}"
OFFLINE=""
VERSION_OVERRIDE=""

for BUILD_ALL_ARG in "$@"; do
    case "$BUILD_ALL_ARG" in
        offline|-o|--offline) OFFLINE=offline ;;
        *) VERSION_OVERRIDE="$BUILD_ALL_ARG" ;;
    esac
done

if [ ! -f "$MOD_PROJECT_DIR/build.sh" ]; then
    echo "[error] gun_and_weaponのbuild.shが見つかりません: $MOD_PROJECT_DIR/build.sh" >&2
    exit 1
fi

if [ -n "$VERSION_OVERRIDE" ]; then
    bash "$PROJECT_DIR/build.sh" "$VERSION_OVERRIDE" ${OFFLINE:+offline}
else
    bash "$PROJECT_DIR/build.sh" ${OFFLINE:+offline}
fi

ADDON_VERSION="$(sed -n '1p' "$PROJECT_DIR/VERSION")"
ADDON_ZIP="$PROJECT_DIR/build/libs/kid_gun_1412-$ADDON_VERSION.zip"
EMBEDDED_ZIP="$MOD_PROJECT_DIR/src/main/resources/assets/gun_and_weapon/custom/kid_gun_1412.zip"

mkdir -p "$(dirname "$EMBEDDED_ZIP")"
cp -f "$ADDON_ZIP" "$EMBEDDED_ZIP"
echo "Embedded gun pack: $EMBEDDED_ZIP"

cd "$MOD_PROJECT_DIR"
if [ -n "$OFFLINE" ]; then
    exec bash ./build.sh offline
else
    exec bash ./build.sh
fi
