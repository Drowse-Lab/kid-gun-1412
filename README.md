# kid-gun-1412

Minecraft 1.20.1 / Forge 47.3.0 / TaCZ 1.1.8-hotfix向けのJava MODです。
怪盗キッド風のトランプ銃とトランプ弾薬を追加します。

MODのJARにはTaCZガンパックが内蔵され、起動時にゲームディレクトリの
`tacz/kid_gun_1412.zip`へ自動配置されます。専用クリエイティブタブには、
`GunId` / `AmmoId`を設定済みのアイテムが表示されるため、モデルが`null`になる
TaCZの未設定汎用アイテムを使う必要はありません。

## ビルド

```bash
# バージョンとリリース種別を対話形式で選ぶ
bash build.sh

# 保存済みVERSIONで完全オフラインビルド
bash build.sh offline

# バージョンを直接指定
bash build.sh 1.2.0-rc offline
```

成果物は `build/libs/kid_gun_1412-<version>.jar` です。

## 開発環境で実行

```bash
bash run.sh
```

`run.sh`はJava 17を確認し、このプロジェクト自身のForge `runClient`を起動します。
依存関係とMinecraftアセットを取得済みなら、`bash run.sh --offline`でも起動できます。
オフライン実行時はForgeGradleの`downloadAssets`タスクを除外します。
バージョンも指定する場合は、`bash run.sh 1.2.0-beta offline`のように実行します。

通常のMinecraftでは、生成したJARとTaCZ本体を`mods`フォルダへ入れてください。

## ガンパック資産

編集元はリポジトリ直下の`assets/`、`data/`、`gunpack.meta.json`です。
Gradleの`buildGunPack`タスクがこれらをZIP化し、Java MODのJARへ自動内蔵します。

### トランプ銃の形を手で直す（推奨ワークフロー）

銃の形の正本は `assets/kid1412/geo_models/gun/card_gun_geo.json` の1ファイルです。
Blockbenchの「Open Model」でそのまま開けます（テクスチャは
`assets/kid1412/textures/gun/uv/card_gun.png` を読み込む）。

```bash
# 編集して保存したら1回実行（リグ修復 + HUDアイコン再生成 + パック反映）
python3 tools/apply_model.py

# 保存のたびに自動で反映
python3 tools/apply_model.py --watch
```

`apply_model.py` は編集ミスを自動修復します:

- 消したり名前を変えたボーンを復元（TaCZのアニメーションが全ボーンを要求するため）
- ボーンのピボット・親子・回転をアニメーション用リグ（`tools/card_gun_rig.json`）に強制復帰
  — **キューブ（形そのもの）は編集どおり残ります**
- サイズ0のキューブを削除、identifier・テクスチャサイズを復元

反映先は `run/tacz/kid_gun_1412.zip` です。起動中の開発クライアントなら
`/tacz reload` で読み直せます（効かない場合は再起動）。`bash run.sh` での
再起動時はGradleが編集済みassetsを自動で再梱包するので、何もしなくても反映されます。

注意: 消したボーンは「空」で復元されます。弾のカード（round1〜6, round7〜12）を
消してしまった場合は、他のroundボーンのキューブをBlockbenchでコピーしてください。

### トランプ銃のモデル生成

トランプ銃はTaCZ標準のRhino .357を改造して作ります。ボーン構成・ピボット・
アニメーション（`tacz:rhino357`）・ステートマシンはTaCZ本体のものをそのまま使うため、
標準銃と同じ挙動（シリンダーのスイングアウト、エジェクター、装填）になります。
差し替えるのは見た目だけで、原作のトランプ銃に合わせた角ばった銀のマガジンボックス、
6室のシリンダー、リブ入りの黒グリップを作り直しています。

モデルファイルが既にある場合、生成スクリプトは**手編集を守るため形を上書きしません**
（テクスチャ・display・アニメーションだけ再生成します）。形をゼロから作り直すときだけ
`--reset` を付けます。

```bash
# テクスチャ / display / アニメーションを再生成（形は保持）
python3 tools/generate_card_gun_model.py

# 形も含めて全部作り直す（手編集は消えます）
python3 tools/generate_card_gun_model.py --reset

# 生成したモデルを3Dレンダリングして弾薬HUD用テクスチャにする
python3 tools/render_gun_icon.py
```

生成元は`run/tacz/tacz_default_gun/`に展開されたTaCZ標準ガンパックなので、
一度クライアントを起動してから実行してください。

### インベントリでの3D表示

TaCZは`ItemDisplayContext.GUI`でdisplay JSONの`slot`テクスチャを描くことが
実装で固定されており、ガンパックだけではインベントリに生モデルを出せません。
このアドオンは独立したForge MODでもあるので、Java側で回避しています。

- `slot`テクスチャは空（透明）にして、TaCZが平面アイコンを描かないようにする
- [CardGunSlotRenderer](src/main/java/kid_gun_1412/client/CardGunSlotRenderer.java)が
  Forgeの`RegisterItemDecorationsEvent`でアイテムデコレータを登録し、同じスタックを
  `ItemDisplayContext.FIXED`で描き直す。FIXEDはTaCZが3Dモデル経路に流す表示コンテキストなので、
  インベントリのスロットに実モデルがそのまま出ます
- TaCZの銃は全て同一アイテムなので、デコレータ側でGunIdを見て`kid1412:card_gun`だけに適用します
