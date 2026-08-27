# kid-gun-1412

Minecraft 1.20.1 / Forge 47.3.0 / TaCZ 1.1.7向けのJava MODです。
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
bash run.sh offline
```

`run.sh`はこのプロジェクト自身のForge `runClient`を起動します。ForgeGradleが
オフラインでもアセット取得タスクを実行しないよう、`downloadAssets`を除外します。

通常のMinecraftでは、生成したJARとTaCZ本体を`mods`フォルダへ入れてください。

## ガンパック資産

編集元はリポジトリ直下の`assets/`、`data/`、`gunpack.meta.json`です。
Gradleの`buildGunPack`タスクがこれらをZIP化し、Java MODのJARへ自動内蔵します。
