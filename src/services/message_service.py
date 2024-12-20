"""
Message service implementation for handling Slack messages
"""

from typing import Optional

from core.slack_client import SlackClient
from utils.logger import get_logger

logger = get_logger(__name__)


class MessageService:
    """Service for handling Slack messages"""

    def __init__(self, slack_client: Optional[SlackClient] = None):
        """Initialize MessageService

        Args:
            slack_client (Optional[SlackClient]): SlackClient instance
        """
        self.slack_client = slack_client or SlackClient()

    async def send_message(self, channel: str, message: str) -> bool:
        """Send message to Slack channel

        Args:
            channel (str): Channel ID or name
            message (str): Message to send

        Returns:
            bool: True if message was sent successfully, False otherwise
        """
        logger.info(f"Sending message to channel {channel}")
        return await self.slack_client.send_message(channel=channel, text=message)

    async def send_direct_message(self, user_id: str, message: str) -> bool:
        """特定のユーザーにダイレクトメッセージを送信する

        Args:
            user_id (str): 受信者のユーザーID
            message (str): 送信するメッセージ

        Returns:
            bool: 送信成功時True、失敗時False
        """
        logger.info(f"Sending direct message to user {user_id}")
        return await self.slack_client.open_conversation_and_send_message(
            users=user_id, text=message
        )
