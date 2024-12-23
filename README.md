# Slack Assistant Bot Client

Slack Assistant Bot用のメッセージ送信クライアントライブラリです。
非同期処理に対応し、Slackチャンネルへのメッセージ送信を簡単に実装できます。

## 特徴

- ✨ 非同期処理による高速なメッセージ送信
- 🔒 セキュアな認証管理
- 📝 詳細なログ機能
- 🚀 シンプルで使いやすいAPI
- ⚡ 軽量で高性能

## 必要要件

- Python 3.10以上
- [uv](https://github.com/astral-sh/uv) パッケージマネージャー

## インストール

```bash
# uvを使用してインストール
uv venv
source .venv/bin/activate  # Linux/macOS
# Windows: .venv\Scripts\activate

# 依存関係のインストール
uv pip install -e .
```

## 環境設定

以下の環境変数を`.env`ファイルまたはシステムの環境変数として設定してください：

```bash
SLACK_BOT_TOKEN=xoxb-your-bot-token        # Slackボットトークン
SLACK_APP_TOKEN=xapp-your-app-token        # Slackアプリトークン
SLACK_SIGNING_SECRET=your-signing-secret    # 署名シークレット
```

## 基本的な使用例

```python
from services.message_service import MessageService

async def main():
    # MessageServiceのインスタンス化
    service = MessageService()
    
    # シンプルなメッセージ送信
    success = await service.send_message(
        channel="#general",
        message="Hello, World!"
    )
    
    print(f"メッセージ送信状態: {success}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

## 高度な使用例

```python
from services.message_service import MessageService

async def main():
    service = MessageService()
    
    # リッチテキストメッセージの送信
    success = await service.send_message(
        channel="#announcements",
        message="*重要なお知らせ*\n今週のミーティングについて",
        blocks=[
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*今週のミーティング*\n• 日時: 金曜日 15:00\n• 場所: 会議室A\n• 議題: Q2計画"
                }
            }
        ]
    )

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

## エラーハンドリング

```python
from services.message_service import MessageService
from services.exceptions import SlackAPIError

async def send_with_retry():
    service = MessageService()
    
    try:
        await service.send_message(
            channel="#general",
            message="テストメッセージ"
        )
    except SlackAPIError as e:
        print(f"エラーが発生しました: {e}")
```

## 開発者向け情報

### テストの実行

```bash
pytest tests/
```

### コードスタイル

このプロジェクトは[black](https://github.com/psf/black)と[isort](https://github.com/PyCQA/isort)を使用してコードフォーマットを行っています。

```bash
# コードフォーマットの実行
black .
isort .
```

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。

## コントリビューション

1. このリポジトリをフォーク
2. 機能ブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m '✨ feat: 素晴らしい機能を追加'`)
4. ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. プルリクエストを作成

## サポート

問題や提案がある場合は、GitHubのIssueを作成してください。
