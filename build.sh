#!/bin/sh
# Kid Gun 1412 — TaCZガンパック ビルドスクリプト
#
# 使い方:
#   bash build.sh                    対話式ビルド（version / release typeを選択）
#   bash build.sh clean              buildを削除してからビルド
#   bash build.sh offline            オフラインビルド
#   bash build.sh clean offline      クリーン＋オフラインビルド
#   bash build.sh 1.1.0              完成バージョンを直接指定（非対話）
#   bash build.sh 1.1.0-beta offline 完成バージョン指定＋オフライン
#
# 出力先:
#   build/libs/kid_gun_1412-<version>.zip
#
# このビルドは assets / data / gunpack.meta.json をZIP化するだけなので、
# ネットワークやGradleを使わず、常にオフラインで実行できます。
set -eu

PROJECT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
VERSION_FILE="$PROJECT_DIR/VERSION"
DEFAULT_VERSION=$(sed -n '1p' "$VERSION_FILE" 2>/dev/null || true)
DEFAULT_VERSION=${DEFAULT_VERSION:-1.0.0}
VERSION_OVERRIDE=""
CLEAN_BUILD=""

for BUILD_ARG in "$@"; do
    case "$BUILD_ARG" in
        help|-h|--help)
            sed -n '2,16p' "$0" | sed 's/^# \{0,1\}//'
            exit 0
            ;;
        offline|-o|--offline)
            # このビルドは外部依存を取得しないため、常にオフラインです。
            ;;
        clean)
            CLEAN_BUILD=1
            ;;
        *)
            VERSION_OVERRIDE=$BUILD_ARG
            ;;
    esac
done

release_suffix() {
    case "$1" in
        b|beta) echo "-beta" ;;
        a|alpha) echo "-alpha" ;;
        rc) echo "-rc" ;;
        t|test) echo "-test" ;;
        r|release|"") echo "" ;;
        *)
            echo "[error] release typeは b / a / r / rc / t から選択してください。" >&2
            exit 1
            ;;
    esac
}

if [ -n "$VERSION_OVERRIDE" ]; then
    VERSION=$VERSION_OVERRIDE
elif [ -t 0 ]; then
    DEFAULT_BASE=$(printf '%s' "$DEFAULT_VERSION" | sed -E 's/-(alpha|beta|rc|test)(\.[0-9]+)?$//')
    printf '\n[Kid Gun 1412] バージョンを入力してください [%s]:\n  > ' "$DEFAULT_BASE"
    read -r INPUT_VERSION
    BASE_VERSION=${INPUT_VERSION:-$DEFAULT_BASE}

    printf '\nリリース種別を選択してください:\n'
    printf '  [r]  release（接尾辞なし・既定）\n'
    printf '  [b]  beta\n'
    printf '  [a]  alpha\n'
    printf '  [rc] release candidate\n'
    printf '  [t]  test\n'
    printf '  > '
    read -r RELEASE_TYPE
    VERSION="${BASE_VERSION}$(release_suffix "${RELEASE_TYPE:-r}")"
else
    VERSION=$DEFAULT_VERSION
fi

case "$VERSION" in
    ''|[!0-9A-Za-z]*|*[!0-9A-Za-z._-]*)
        echo "[error] 不正なバージョンです: $VERSION" >&2
        exit 1
        ;;
esac

if [ -n "$CLEAN_BUILD" ]; then
    rm -rf "$PROJECT_DIR/build"
fi

printf '%s\n' "$VERSION" > "$VERSION_FILE"

OUTPUT_DIR="$PROJECT_DIR/build/libs"
OUTPUT_FILE="$OUTPUT_DIR/kid_gun_1412-$VERSION.zip"
STAGING_DIR=$(mktemp -d "${TMPDIR:-/tmp}/kid-gun-1412-build.XXXXXX")
trap 'rm -rf "$STAGING_DIR"' EXIT INT TERM

mkdir -p "$OUTPUT_DIR"
rm -f "$OUTPUT_FILE"

cd "$PROJECT_DIR"
cp -R assets data gunpack.meta.json "$STAGING_DIR/"
perl -pi -e 's/"version"\s*:\s*"[^"]+"/"version": "'$VERSION'"/' \
    "$STAGING_DIR/assets/kid1412/gunpack_info.json"

cd "$STAGING_DIR"
zip -qr "$OUTPUT_FILE" assets data gunpack.meta.json -x '*.DS_Store'

echo ""
echo "Build complete"
echo "  version: $VERSION"
echo "  output : $OUTPUT_FILE"
