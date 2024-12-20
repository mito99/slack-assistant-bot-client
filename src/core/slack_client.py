"""
Core Slack client implementation
"""

from typing import Optional

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from config.settings import slack_settings
from utils.logger import get_logger

logger = get_logger(__name__)


class SlackClient:
    """Slack Client wrapper class"""

    def __init__(self, token: Optional[str] = None):
        """Initialize Slack client

        Args:
            token (Optional[str]): Slack Bot Token. If not provided, uses SLACK_BOT_TOKEN from environment
        """
        self.token = token or slack_settings.bot_token
        if not self.token:
            raise ValueError("Slack token is required")

        self.client = WebClient(token=self.token)

    async def send_message(self, channel: str, text: str) -> bool:
        """Send message to Slack channel

        Args:
            channel (str): Channel ID or name
            text (str): Message text to send

        Returns:
            bool: True if message was sent successfully, False otherwise
        """
        try:
            response = await self.client.chat_postMessage(channel=channel, text=text)
            return response["ok"]
        except SlackApiError as e:
            logger.error(f"Error sending message: {e.response['error']}")
            return False

    async def open_conversation_and_send_message(self, users: str, text: str) -> bool:
        """指定されたユーザーとのDMチャンネルを開き、メッセージを送信する

        Args:
            users (str): ユーザーID（例: 'U1234567'）
            text (str): 送信するメッセージ

        Returns:
            bool: 送信成功時True、失敗時False
        """
        try:
            response = await self.client.conversations_open(users=users)
            channel_id = response["channel"]["id"]
            return await self.send_message(channel=channel_id, text=text)
        except SlackApiError as e:
            logger.error(f"DM送信エラー: {e.response['error']}")
            return False
