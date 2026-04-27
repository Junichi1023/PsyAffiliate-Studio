# PsyAffiliate Studio

PsyAffiliate Studio は、Threads・Instagram向けに「占い × 心理学 × AI × アフィリエイト」投稿を企画、生成、審査、保存するためのデスクトップMVPです。

読者を騙してリンクを踏ませる設計ではなく、読者の悩みに合う情報を提供し、PRを明示したうえで、必要な人だけが納得してクリックできる健全なSNSアフィリエイト運用を支援します。

占いは断定予言として扱いません。金運、恋愛、仕事、人間関係などの不安に寄り添い、自己理解と小さな行動整理につなげるための投稿を作る運用OSです。

## 技術スタック

- Frontend: React, TypeScript, Vite
- Desktop: Electron
- Backend: Python, FastAPI
- Database: SQLite
- AI: OpenAI Responses API, `gpt-5.5`
- Search: Phase 1 は `knowledge_items` の `LIKE` 検索
- SNS: Phase 1.5 は Threads / Instagram 投稿サービスのモック投稿判定

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
        empathy.py
        knowledge/
        social/
        export/
    tests/
  frontend/
    src/
      api/
      components/
      constants/
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
- `GET/POST/PUT/DELETE /api/persona-pains`
- `GET/POST/PUT/DELETE /api/fortune-templates`
- `POST /api/content/generate`
- `POST /api/content/compliance-check`
- `POST /api/content/empathy-check`
- `GET/POST/PUT/DELETE /api/drafts`
- `GET /api/drafts/export.csv`
- `POST /api/publish/drafts/{draft_id}/mock`
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
- 設定画面

## Phase 1.5でできること

- 占い特化ナレッジカテゴリの選択
- 悩み別ペルソナ管理
- 占い投稿テンプレート管理
- 金運・恋愛・仕事運テンプレートの初期seed
- 日本語UIでのダッシュボード、投稿作成、下書き・投稿管理
- 投稿作成時に悩みペルソナ、占いジャンル、占いテンプレート、商品、アフィリエイト導線を一連の流れで選択
- 投稿生成時の `fortune_type`, `persona_pain_id`, `fortune_template_id`, `affiliate_intent` 指定
- 寄り添い品質チェック
- 占い危険表現、断定予言、依存誘導、恐怖訴求の検出強化
- Draftごとの `empathy_score`, `publish_ready`, `publish_block_reason` 管理
- `approved` かつ `compliance_score >= 90` かつ `empathy_score >= 75` のDraftだけmock publish可能
- mock投稿対象は、承認済み、安全性、寄り添い度、投稿準備OKの条件をすべて満たす下書きだけ

## Phase 2でやること

- Threads API 実投稿
- Instagram Graph API 実投稿
- `approved` ステータス必須の予約投稿ワーカー
- mock投稿を実API投稿に差し替えるpublisher実装
- 投稿結果の external id / `posted_at` 保存
- 承認済み・安全性スコア90以上・寄り添いスコア75以上・`publish_ready` の投稿だけをSNS APIへ渡す投稿ゲート
- クリック計測、収益分析
- Instagramカルーセル画像生成
- ChromaDB / LanceDB への検索差し替え
- OpenAI APIキーの OS Keychain 管理

## 注意事項

- 医療的断定は禁止です。「治る」「必ず改善」などは避けてください。
- 占いを「必ず当たる」「運命が変わる」などの断定予言として扱わないでください。
- アフィリエイト投稿では `#PR` または「アフィリエイトリンクを含みます」を明記してください。
- ステルスマーケティング規制に対応するため、広告・PRであることを隠さないでください。
- 自動投稿はPhase 1では行いません。将来実装時も、人間が `approved` にし、安全性・寄り添い条件を満たした投稿だけを対象にしてください。
- アフィリエイト導線は「買えば救われる」「買わないと不幸になる」形にしないでください。
- APIキーやアクセストークンをコードやGitHubにコミットしないでください。
