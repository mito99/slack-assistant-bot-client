#!/usr/bin/env python
"""
Slack メッセージ送信スクリプト
"""
import argparse
import asyncio
import os
from typing import Optional

from dotenv import load_dotenv

from services.message_service import MessageService
from utils.logger import get_logger

logger = get_logger(__name__)


async def send_slack_message(
    channel: str, message: str, bot_token: Optional[str] = None
) -> bool:
    """
    Slackメッセージを送信する

    Args:
        channel (str): 送信先チャンネル（例：#general）
        message (str): 送信するメッセージ
        bot_token (Optional[str]): Slack Bot Token。未指定の場合は環境変数から読み込み

    Returns:
        bool: 送信成功時True、失敗時False
    """
    try:
        service = MessageService()
        return await service.send_message(channel=channel, message=message)
    except Exception as e:
        logger.error(f"メッセージ送信中にエラーが発生しました: {e}")
        return False


def parse_args():
    """コマンドライン引数をパースする"""
    parser = argparse.ArgumentParser(description="Slackメッセージ送信スクリプト")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-c", "--channel", help="送信先チャンネル（例：#general）")
    group.add_argument("-u", "--user", help="送信先ユーザーID（例：U1234567）")
    parser.add_argument("-m", "--message", required=True, help="送信するメッセージ")
    return parser.parse_args()


async def main():
    """メインエントリーポイント"""
    # 環境変数の読み込み
    load_dotenv()

    # コマンドライン引数の解析
    args = parse_args()

    if args.channel:
        success = await send_slack_message(args.channel, args.message)
    elif args.user:
        service = MessageService()
        success = await service.send_direct_message(args.user, args.message)

    if success:
        logger.info("メッセージを送信しました")
    else:
        logger.error("メッセージの送信に失敗しました")
        exit(1)


if __name__ == "__main__":
    asyncio.run(main())
