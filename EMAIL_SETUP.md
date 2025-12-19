# メール送信機能のセットアップ

## 概要
お問い合わせフォームから`h.kumagaya@cosmicoai.com`にメールを送信する機能です。

## セットアップ手順

### 1. Resendアカウントの作成
1. [Resend](https://resend.com)にアクセスしてアカウントを作成
2. APIキーを取得

### 2. Vercel環境変数の設定
1. Vercelダッシュボードにログイン
2. プロジェクト（cosmico-website）を選択
3. Settings → Environment Variables に移動
4. 以下の環境変数を追加：
   - 名前: `RESEND_API_KEY`
   - 値: Resendで取得したAPIキー
5. 環境: Production, Preview, Development すべてにチェック
6. Save をクリック

### 3. ドメインの検証（オプション）
Resendで`cosmicoai.com`ドメインを検証すると、`from`アドレスをカスタマイズできます。
検証しない場合は、Resendのデフォルトドメインを使用してください。

## 動作確認
環境変数が設定されていない場合、開発モードとして動作し、コンソールにメール内容が出力されます。
本番環境では、環境変数を設定することで実際にメールが送信されます。







