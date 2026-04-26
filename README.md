# PsyAffiliate Studio

心理学 × AI × アフィリエイト投稿を、企画・生成・審査・保存するためのデスクトップアプリです。

Phase 1 では、人間の承認を前提にした下書き管理までを実装しています。Threads API / Instagram Graph API への投稿はモックの service 層だけを用意しています。

## 実装済み

- Electron で起動できるデスクトップ構成
- FastAPI バックエンド
- React / TypeScript / Vite フロントエンド
- SQLite DB 初期化
- ナレッジ CRUD
- アフィリエイト商品 CRUD
- OpenAI Responses API を使う投稿生成 service
- `OPENAI_API_KEY` 未設定時の安全なテンプレート生成フォールバック
- PR 表記・危険表現・医療的断定・収益保証・禁止訴求チェック
- 投稿下書き保存、一覧、削除
- 投稿ステータス管理
- CSV エクスポート
- Settings 画面
- Phase 2 用 SNS service インターフェース
- 最低限の API テスト

## 未実装

- Threads API への実投稿
- Instagram Graph API への実投稿
- 予約投稿ワーカー
- 投稿後の分析取得
- OS Keychain での API キー保存
- ChromaDB / LanceDB などの本格ベクトル検索

## セットアップ

```bash
cd "/Users/user/Documents/New project/PsyAffiliate-Studio"
cp .env.example .env
npm run setup
```

`.env` の `OPENAI_API_KEY` に本物のキーを設定すると、投稿生成で OpenAI Responses API を使います。キーが空の場合は、開発用のテンプレート生成に切り替わります。

## 起動

```bash
npm run dev
```

このコマンドで Vite と Electron を起動します。Electron はバックエンドの `127.0.0.1:8000` が空いていれば FastAPI も起動します。

デスクトップから起動する場合は、`PsyAffiliate Studio.command` をダブルクリックします。

バックエンドだけを起動する場合:

```bash
npm run dev:backend
```

フロントエンドだけを起動する場合:

```bash
npm run dev:frontend
```

## テスト

```bash
npm run test
```

確認している内容:

- `/api/health`
- knowledge CRUD
- affiliate_products CRUD
- dangerous terms の検出
- PR 表記なしアフィリエイト投稿の警告
- draft 保存
- CSV エクスポート

## API

- `GET /api/health`
- `GET /api/dashboard`
- `GET /api/knowledge`
- `POST /api/knowledge`
- `GET /api/knowledge/{id}`
- `PUT /api/knowledge/{id}`
- `DELETE /api/knowledge/{id}`
- `GET /api/affiliate-products`
- `POST /api/affiliate-products`
- `GET /api/affiliate-products/{id}`
- `PUT /api/affiliate-products/{id}`
- `DELETE /api/affiliate-products/{id}`
- `POST /api/content/generate`
- `POST /api/content/compliance-check`
- `POST /api/drafts`
- `GET /api/drafts`
- `GET /api/drafts/{id}`
- `PUT /api/drafts/{id}`
- `DELETE /api/drafts/{id}`
- `GET /api/drafts/export.csv`
- `GET /api/settings`
- `PUT /api/settings`

## Phase 2 候補

- `services/social/threads.py` に Threads API 投稿実装
- `services/social/instagram.py` に Instagram Graph API 投稿実装
- `approved` 以外は投稿不可にする予約投稿ワーカー
- `scheduled_at` を監視するジョブランナー
- 投稿結果の `posted_at` / external id 保存
- Instagram 画像生成・カルーセル生成
- 商品別クリック・CV・投稿効果の分析テーブル
- ナレッジ検索を ChromaDB または LanceDB へ差し替え
- API キーを OS Keychain 管理へ移行
