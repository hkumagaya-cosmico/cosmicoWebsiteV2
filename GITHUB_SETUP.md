# GitHubリポジトリ作成手順

## 1. GitHubでリポジトリを作成

以下の手順でリポジトリを作成してください：

1. https://github.com/new にアクセス
2. リポジトリ名: `cosmicoWebsiteV2`
3. 説明: `Cosmico Website V2 - Static HTML Site`
4. 公開設定: Public または Private（お好みで）
5. **重要**: "Initialize this repository with" のチェックはすべて外す
6. "Create repository" をクリック

## 2. リモートURLを確認

リポジトリ作成後、以下のコマンドでプッシュできます：

```bash
cd /Users/bera/Project/COSMICO/cosmicoWebsiteV2
git remote set-url origin https://github.com/hkumagaya-cosmico/cosmicoWebsiteV2.git
git push -u origin main
```

## 3. Vercelにデプロイ

GitHubリポジトリが作成されたら、Vercelで以下の手順でデプロイ：

1. https://vercel.com/new にアクセス
2. "Import Git Repository" をクリック
3. `hkumagaya-cosmico/cosmicoWebsiteV2` を選択
4. Framework Preset: "Other" を選択
5. "Deploy" をクリック

または、Vercel CLIを使用：

```bash
npm i -g vercel
cd /Users/bera/Project/COSMICO/cosmicoWebsiteV2
vercel
```
