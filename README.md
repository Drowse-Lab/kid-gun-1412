# kid-gun-1412

TaCZ用「怪盗キッドのトランプ銃」ガンパックです。パック本体はリポジトリ直下の `assets`、`data`、`gunpack.meta.json` です。

## ビルド

```bash
bash build.sh
```

引数なしで実行すると、バージョン番号とリリース種別を対話形式で選択できます。選択結果は `VERSION` に保存され、ZIP名とパック内情報の両方へ反映されます。

```text
[Kid Gun 1412] バージョンを入力してください [1.0.0]:
  > 1.1.0

リリース種別を選択してください:
  [r]  release
  [b]  beta
  [a]  alpha
  [rc] release candidate
  [t]  test
  > b
```

この例では `build/libs/kid_gun_1412-1.1.0-beta.zip` が生成されます。

完成した `build/libs/kid_gun_1412-1.0.0.zip` を Minecraft の TaCZ ガンパックフォルダへ配置してください。

バージョンを指定する場合:

```bash
bash build.sh 1.1.0
```

外部依存を使わないため、オフラインでも同じようにビルドできます。

```bash
bash build.sh offline
bash build.sh clean offline
```

## 開発環境で実行

隣の `gun_and_weapon` 開発環境へガンパックを配置し、Minecraftクライアントを起動します。

```bash
bash run.sh
bash run.sh offline
```

`run.sh` は、アドオンZIPの生成、`gun_and_weapon` のJAR内への埋め込み、本体MODのビルド、Minecraftクライアントの起動までを一括で行います。

オフライン起動ではForgeGradleの `downloadAssets` を除外し、既存のローカルMinecraftアセットキャッシュを使用します。一度もMinecraft 1.20.1を起動したことがなくキャッシュが存在しない環境では、初回だけ通常起動が必要です。

引数なしの `bash run.sh` では、次の内容を順番に選択できます。

1. バージョン番号
2. release / beta / alpha / rc / test
3. オフライン起動 / 通常起動 / 統合JARのビルドのみ

配置だけ行い、Minecraftを起動しない場合:

```bash
bash run.sh offline install-only
```

別のForge開発環境を使う場合は、その環境に `run_quick.sh` と `run/tacz` が必要です。

```bash
RUN_PROJECT_DIR=/path/to/forge-project bash run.sh offline
```

## gun_and_weaponへ同梱してビルド

完成したガンパックZIPを `gun_and_weapon` のJAR内へ埋め込み、そのまま本体MODをビルドします。本体MODの起動時に、同梱ZIPが自動的に `tacz/kid_gun_1412.zip` へ展開されます。

```bash
bash build_all.sh
bash build_all.sh offline
bash build_all.sh 1.2.0-rc offline
```

別の本体MODプロジェクトを使う場合:

```bash
MOD_PROJECT_DIR=/path/to/gun_and_weapon bash build_all.sh offline
```

## カード展開演出

射撃時は銃口内の丸まったカードを約0.08秒だけ押し出し、直後に開いた投射物モデルへ切り替えます。

## ゲーム内での入手

ガンスミステーブルから「怪盗キッドのトランプ銃」と「トランプカード」を作成してください。クリエイティブインベントリに表示される、名前が `item.tacz.ammo` の紫黒アイテムは弾薬IDが入っていないTaCZの汎用アイテムで、このパックのトランプカードではありません。

## テクスチャ再生成

```bash
python3 tools/generate_kid1412_textures.py
```
