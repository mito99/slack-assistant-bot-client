# Slack Assistant Bot Client

Slack Assistant Bot用のメッセージ送信クライアントライブラリです。

## 機能

- Slackチャンネルへのメッセージ送信
- 非同期処理対応
- ログ機能

## インストール

```bash
pip install .
```

## 環境設定

以下の環境変数を設定してください：

```bash
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_APP_TOKEN=xapp-your-app-token
SLACK_SIGNING_SECRET=your-signing-secret
```

## 使用例

```python
from src.services.message_service import MessageService

async def main():
    service = MessageService()
    success = await service.send_message(
        channel="#general",
        message="Hello, World!"
    )
    print(f"Message sent: {success}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

## ライセンス

MIT License
