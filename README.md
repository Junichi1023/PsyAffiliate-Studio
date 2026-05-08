# PsyAffiliate Studio

PsyAffiliate Studio は、Threads向けに「Facebookナレッジ × 恋愛占い投稿 × Typefully予約 × note導線 × A8電話占い案件」を一体で運用するためのデスクトップMVPです。

読者を騙してリンクを踏ませる設計ではなく、読者の悩みに合う情報を提供し、PRを明示したうえで、必要な人だけが納得してクリックできる健全なSNSアフィリエイト運用を支援します。

占いは断定予言として扱いません。金運、恋愛、仕事、人間関係などの不安に寄り添い、自己理解と小さな行動整理につなげるための投稿を作る運用OSです。

現在の主導線は次の1本に絞っています。

```text
Facebook過去データ
→ 自分らしさナレッジ化
→ 恋愛・復縁・片思い系Threads投稿
→ Typefully予約
→ Threadsプロフィールのnote URL
→ note記事内でA8.netの電話占い・占いアプリ案件へ誘導
```

Threads本文にA8リンクを直貼りしません。Threadsは悩みに寄り添う入口、noteは比較・注意点・質問例を整理する場所、A8案件はnote記事内で紹介するものとして扱います。

## 技術スタック

- Frontend: React, TypeScript, Vite
- Desktop: Electron
- Backend: Python, FastAPI
- Database: SQLite
- AI: OpenAI Responses API, `gpt-5.5`
- Search: Phase 1 は `knowledge_items` の `LIKE` 検索
- SNS: Phase 1.5 は Threads / Instagram 投稿サービスのモック投稿判定
- Scheduling: Typefully API v2想定。APIキー未設定時はmock予約

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
        importers/
        knowledge/
        typefully/
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
- `POST /api/import/facebook/preview`
- `GET /api/import/sessions`
- `GET/PUT /api/import/candidates/{id}`
- `POST /api/import/sessions/{id}/commit`
- `GET/POST/PUT/DELETE /api/note-funnel-pages`
- `GET/POST/PUT/DELETE /api/fortune-a8-offers`
- `GET/POST/PUT/DELETE /api/threads-post-templates`
- `GET/POST/PUT/DELETE /api/note-cta-templates`
- `GET/PUT /api/threads-30day-plan`
- `POST /api/typefully/drafts/{draft_id}/schedule`
- `GET /api/typefully/jobs`

## 自動化ループCLI

初回の占いアフィリエイト検証ループは、下記でローカル実行できます。

```bash
PYTHONPATH=backend .venv/bin/python scripts/run_affiliate_cycle.py --genre 占い --count 12
```

このCLIは、ぱううAIエージェントのプロフィール、占い案件リサーチ、悩みペルソナ、7項目スコア、投稿下書き、画像生成用プロンプト、日次レポートを作成します。外部SNSへの無断投稿、無差別コメント、DM自動送信は行いません。

案件分析だけ見たい場合:

```bash
PYTHONPATH=backend .venv/bin/python scripts/analyze_affiliate_genre.py 占い
```

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
- mock投稿対象は、承認済み、安全性、寄り添い度、A8直リンクなし、プロフィールnote導線あり、誘導先note記事あり、投稿準備OKの条件をすべて満たす下書きだけ

## 収益化導線でできること

- Facebook ZIPをアップロードし、Messengerを除外してPII削除済みのナレッジ候補を作成
- Facebook JSON/HTMLエクスポートのフォルダ構造揺れ、UTF-8 BOM、壊れたJSON/HTMLのスキップに対応
- メール、電話番号、URL、郵便番号、長いID、@ユーザー名、LINE ID、住所らしき表記を除去・警告
- 生投稿全文ではなく、自分らしい口調、価値観、Threads冒頭フック、CTA、寄り添い表現の要約候補に変換
- 候補をプレビュー、選択、編集してから `knowledge_items` へ登録
- note電話占い紹介記事URLを管理
- A8.netの電話占い・チャット占い・占いアプリ案件を管理
- Threads投稿テンプレートとnote CTAを管理
- Threads投稿本文にA8直リンクが入った場合に検出
- プロフィールnote導線が入っているかを検出
- 承認済み、安全性90以上、寄り添い75以上、A8直リンクなし、note導線あり、note記事設定済みの投稿だけTypefully予約可能
- 30日運用プランと投稿ジャンル配分を確認

## Typefully設定方法

`.env` またはアプリの「Typefully設定」で以下を設定します。

```env
TYPEFULLY_API_KEY=
TYPEFULLY_SOCIAL_SET_ID=
TYPEFULLY_DEFAULT_SCHEDULE_MODE=draft_only
PROFILE_NOTE_URL=https://note.com/your-note-page
```

APIキー未設定時はmockレスポンスで予約ジョブを作成します。`draft_only` は下書き作成、`next_free_slot` はTypefullyの次の空き枠、`scheduled_time` は指定日時で予約する想定です。

## note URL設定方法

「note導線管理」で、Threadsプロフィールに置くnote記事URLを登録します。記事タイプは `first_time_guide`、`question_examples`、`avoid_mistakes`、`dependency_prevention`、`comparison` などを使います。

## A8占い案件登録方法

「A8占い案件」で、案件名、サービス種別、A8広告URL、報酬額、成果条件、否認条件、禁止訴求を登録します。`affiliate_url` はnote記事内だけで使い、Threads本文には入れません。

## Facebook取り込み方法

「Facebook取り込み」からFacebook ZIPをアップロードします。JSON形式だけでなく、HTML形式のエクスポートZIPにも対応しています。Messenger、Inbox、Chat系ファイルはデフォルト除外します。メール、電話番号、URL、郵便番号、長いID、@ユーザー名、LINE ID、住所らしき表記を削除・警告し、候補だけをプレビューします。

画面では次の手順で操作します。

1. ZIPファイルを選択する
2. Messenger取り込みのON/OFF、最大解析件数を選ぶ
3. 解析結果、処理したJSON/HTML数、スキップされたファイル、個人情報除去サマリーを確認する
4. 候補のタイトル、カテゴリ、内容、登録対象ON/OFFを編集する
5. 個人情報が残っていないことを確認して、選択候補だけナレッジ登録する

Facebookの生投稿全文は保存しません。複数投稿から、自分らしい口調、価値観、Threads冒頭フック、自然なCTA、恋愛・人間関係への寄り添い表現に要約して登録します。

### Facebook ZIPが取り込めない場合

- Facebookのダウンロード形式はJSON推奨ですが、HTML形式のZIPも取り込めます
- ZIPを解凍せず、そのままアップロードする
- Messengerは最初はOFFにする
- ファイルサイズが大きい場合は最大解析件数を500にする
- `posts` や `comments_and_reactions` が含まれているか確認する
- 壊れたJSON/HTMLが一部あっても処理は継続しますが、すべて壊れている場合は再ダウンロードしてください

### DraftがTypefully予約不可になる理由

- 承認済みではありません
- 安全性スコアが90未満です
- 寄り添いスコアが75未満です
- A8直リンクらしきURLが含まれています
- プロフィールnoteへの導線がありません
- 誘導先note記事が設定されていません
- 「必ず復縁」「100%当たる」「彼の本音が全部わかる」などの禁止表現が含まれています

## 30日運用プラン

- 1〜3日目: A8案件10〜20件リスト化
- 4〜7日目: 電話占い・占いアプリ比較note作成
- 8〜14日目: Threads投稿1日3本
- 15〜21日目: 反応が良いテーマでnote記事2本追加
- 22〜30日目: A8クリック数、note閲覧数、Threads反応を見て案件・CTA・投稿文を修正

投稿配分は、恋愛・復縁の共感投稿40%、占いの使い方・注意点25%、質問例・チェックリスト20%、記事誘導10%、自分の考え・体験談5%を目安にしています。

## Phase 2でやること

- Typefully API本番レスポンスの詳細マッピング
- Typefully予約キャンセルの実API連携
- `approved` ステータス必須の予約投稿ワーカー
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
- Threads投稿ではA8リンクを直貼りしないでください。プロフィールのnote記事へ誘導し、note記事内でA8案件を紹介してください。
- ステルスマーケティング規制に対応するため、広告・PRであることを隠さないでください。
- 自動投稿はPhase 1では行いません。将来実装時も、人間が `approved` にし、安全性・寄り添い条件を満たした投稿だけを対象にしてください。
- アフィリエイト導線は「買えば救われる」「買わないと不幸になる」形にしないでください。
- 占い依存を避けるため、電話占いは答えをもらう場所ではなく、相談前に気持ちや質問を整理する補助として説明してください。
- 収益保証、復縁保証、的中保証はしません。最終投稿前に人間レビューが必要です。
- APIキーやアクセストークンをコードやGitHubにコミットしないでください。
