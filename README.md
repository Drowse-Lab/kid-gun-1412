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

### トランプ銃のモデル生成

トランプ銃はTaCZ標準のRhino .357を改造して作ります。ボーン構成・ピボット・
アニメーション（`tacz:rhino357`）・ステートマシンはTaCZ本体のものをそのまま使うため、
標準銃と同じ挙動（シリンダーのスイングアウト、エジェクター、装填）になります。
差し替えるのは見た目だけで、原作のトランプ銃に合わせた角ばった銀のマガジンボックス、
6室のシリンダー、リブ入りの黒グリップを作り直しています。

```bash
# モデル / UVテクスチャ / LOD / display JSON を生成
python3 tools/generate_card_gun_model.py

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
