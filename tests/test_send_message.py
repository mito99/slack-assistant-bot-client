import asyncio
from unittest.mock import AsyncMock, patch

import pytest

from scripts.send_message import parse_args, send_slack_message


@pytest.mark.asyncio
async def test_send_slack_message():
    # MessageServiceのモック
    with patch("services.message_service.MessageService") as MockService:
        mock_service = AsyncMock()
        mock_service.send_message.return_value = True
        MockService.return_value = mock_service

        # テスト実行
        result = await send_slack_message("#test-channel", "テストメッセージ")

        # アサーション
        assert result is True
        mock_service.send_message.assert_called_once_with(
            channel="#test-channel", message="テストメッセージ"
        )


def test_parse_args(monkeypatch):
    # コマンドライン引数のテスト
    test_args = ["-c", "#test-channel", "-m", "テストメッセージ"]
    monkeypatch.setattr("sys.argv", ["send_message.py"] + test_args)

    args = parse_args()
    assert args.channel == "#test-channel"
    assert args.message == "テストメッセージ"
