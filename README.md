# PsyAffiliate Studio

PsyAffiliate Studio は、Threads・Instagram向けに「心理学 × AI × アフィリエイト」投稿を企画、生成、審査、保存するためのデスクトップMVPです。

読者を騙してリンクを踏ませる設計ではなく、読者の悩みに合う情報を提供し、PRを明示したうえで、必要な人だけが納得してクリックできる健全なSNSアフィリエイト運用を支援します。

## 技術スタック

- Frontend: React, TypeScript, Vite
- Desktop: Electron
- Backend: Python, FastAPI
- Database: SQLite
- AI: OpenAI Responses API, `gpt-5.5`
- Search: Phase 1 は `knowledge_items` の `LIKE` 検索
- SNS: Phase 1 は Threads / Instagram 投稿サービスのモック

## ディレクトリ構成

```text
PsyAffiliate-Studio/
  backend/
    app/
      main.py
      database.py
      models.py
      schemas.py
      config.py
      routers/
      services/
        ai/
        compliance/
        knowledge/
        social/
        export/
    tests/
  frontend/
    src/
      api/
      components/
      pages/
      types/
      styles/
  electron/
    main.js
    package.json
```

## セットアップ

```bash
cd "/Users/user/Documents/New project/PsyAffiliate-Studio"
cp .env.example .env
npm run setup
```

`.env` には本物のAPIキーをコミットしないでください。`OPENAI_API_KEY` が未設定でも、アプリはモック投稿を返して動作します。

```env
OPENAI_API_KEY=
OPENAI_MODEL=gpt-5.5
PSYAFFILIATE_DB_PATH=./data/psyaffiliate.sqlite3
VITE_API_BASE_URL=http://127.0.0.1:8000
```

## Backend起動

```bash
npm run dev:backend
```

API:

- `GET /api/health`
- `GET/POST/PUT/DELETE /api/knowledge`
- `GET/POST/PUT/DELETE /api/affiliate-products`
- `POST /api/content/generate`
- `POST /api/content/compliance-check`
- `GET/POST/PUT/DELETE /api/drafts`
- `GET /api/drafts/export.csv`
- `GET/PUT /api/settings`

## Frontend起動

```bash
npm run dev:frontend
```

## Electron起動

```bash
npm run dev
```

Electron は Vite dev server を開きます。`127.0.0.1:8000` が空いていれば FastAPI も Electron 側から起動します。

デスクトップから起動する場合:

```text
/Users/user/Desktop/PsyAffiliate Studio.app
```

## テスト

```bash
npm run test
```

確認項目:

- `/api/health`
- knowledge CRUD
- affiliate_products CRUD
- dangerous terms 検出
- PR表記なしアフィリエイト投稿の警告
- draft保存
- CSVエクスポート

## Phase 1でできること

- ナレッジ登録・一覧・編集・削除
- アフィリエイト商品登録・一覧・編集・削除
- GPT-5.5 / OpenAI Responses APIを使った投稿生成
- APIキー未設定時のモック投稿生成
- PR / 危険表現 / 医療的断定 / 収益保証 / 禁止訴求チェック
- 投稿下書き保存
- 下書き一覧、ステータス管理、スケジュール日時入力
- CSVエクスポート
- Settings画面

## Phase 2でやること

- Threads API 実投稿
- Instagram Graph API 実投稿
- `approved` ステータス必須の予約投稿ワーカー
- 投稿結果の external id / `posted_at` 保存
- クリック計測、収益分析
- Instagramカルーセル画像生成
- ChromaDB / LanceDB への検索差し替え
- OpenAI API Key の OS Keychain 管理

## 注意事項

- 医療的断定は禁止です。「治る」「必ず改善」などは避けてください。
- アフィリエイト投稿では `#PR` または「アフィリエイトリンクを含みます」を明記してください。
- ステルスマーケティング規制に対応するため、広告・PRであることを隠さないでください。
- 自動投稿はPhase 1では行いません。将来実装時も、人間が `approved` にした投稿だけを対象にしてください。
- APIキーやアクセストークンをコードやGitHubにコミットしないでください。
