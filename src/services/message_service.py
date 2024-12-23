import logging
import pprint
import time
from dataclasses import dataclass
from io import IOBase
from typing import Callable, Optional, Union

from slack_sdk import WebClient
from slack_sdk.socket_mode import SocketModeClient
from slack_sdk.socket_mode.response import SocketModeResponse

from config.settings import slack_settings
from utils.ordered_fixed_size_set import OrderedFixedSizeSet


@dataclass
class FileUploadParams:
    """ファイルアップロードに関するパラメータ

    Attributes:
        file (Union[str, bytes, IOBase]): アップロードするファイル
        filename (Optional[str]): ファイル名
        title (Optional[str]): ファイルのタイトル
        snippet_type (Optional[str]): ファイルのスニペットタイプ (例: "text", "image" など)
    """

    file: Union[str, bytes, IOBase]
    filename: Optional[str] = None
    filetype: Optional[str] = None
    title: Optional[str] = None
    snippet_type: Optional[str] = None


class MessageService:
    def __init__(self):
        """
        MessageServiceの初期化

        Args:
            app_token (str): Slackのアプリレベルトークン (xapp-)
        """
        self.start_time = time.time()
        self.web_client = WebClient(token=slack_settings.bot_token)
        self.socket_client = SocketModeClient(
            app_token=slack_settings.app_token, web_client=self.web_client
        )

        # ロガーの設定
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        # メッセージハンドラを設定
        self.message_handlers = []
        self.socket_client.socket_mode_request_listeners.append(self._handle_message)
        self.processed_messages = OrderedFixedSizeSet(maxsize=100)

    def start(self):
        """SocketModeClientを開始"""
        self.logger.info("Starting Socket Mode Client...")
        self.socket_client.connect()

    def stop(self):
        """SocketModeClientを停止"""
        self.logger.info("Stopping Socket Mode Client...")
        self.socket_client.close()

    def add_message_handler(self, handler: Callable):
        """
        メッセージハンドラを追加

        Args:
            handler (Callable): メッセージを処理するコールバック関数
        """
        self.message_handlers.append(handler)

    def _handle_message(self, client, req):
        """
        受信したメッセージを処理

        Args:
            client: SocketModeClient
            req: リクエストデータ
        """
        event = req.payload
        # デバッグ用にイベントの内容を出力
        self.logger.debug(f"Received event: {pprint.pformat(event)}")

        # メッセージイベントの処理
        event_time = event.get("event_time")
        event_data = event.get("event", {})

        # bot_profileがNoneの場合に対応
        bot_profile = event_data.get("bot_profile") or {}
        app_id = bot_profile.get("app_id")

        message_key = f"{event.get('event_id')}_{event.get('event_time')}"

        if (
            event.get("type") == "event_callback"
            and app_id != slack_settings.bot_app_id
            and event_time > self.start_time
            and message_key not in self.processed_messages
        ):
            self.processed_messages.add(message_key)
            try:
                # 登録された全てのハンドラを実行
                for handler in self.message_handlers:
                    handler(event_data)
            except Exception as e:
                self.logger.error(f"Error handling message: {e}", exc_info=True)

        # # Socket Modeの応答を返す
        response = SocketModeResponse(envelope_id=req.envelope_id)
        client.send_socket_mode_response(response)

    def send_message(self, channel_id: str, text: str) -> Optional[dict]:
        """
        チャンネルにメッセージを送信

        Args:
            channel_id (str): 送信先のチャンネルID
            text (str): 送信するメッセージ

        Returns:
            Optional[dict]: 送信結果
        """
        try:
            response = self.web_client.chat_postMessage(channel=channel_id, text=text)
            self.logger.info(f"Message sent to channel {channel_id}: {text}")
            return response
        except Exception as e:
            self.logger.error(f"Error sending message: {e}")
            return None

    def send_dm(
        self, user_id: str, text: str, file_params: Optional[FileUploadParams] = None
    ) -> Optional[dict]:
        """
        ユーザーにDMを送信。ファイルパラメータが指定された場合は、ファイルも同時に送信。

        Args:
            user_id (str): 送信先のユーザーID
            text (str): 送信するメッセージ
            file_params (Optional[FileUploadParams]): ファイルアップロードに関���るパラメータ（省略可）

        Returns:
            Optional[dict]: 送信結果
        """
        try:
            # DMチャンネルを開く
            conversation = self.web_client.conversations_open(users=[user_id])
            channel_id = conversation["channel"]["id"]

            # メッセージパラメータが指定された場合は、ファイル付きメッセージを送信
            if file_params:
                return self.send_message_with_file(
                    channel_id=channel_id, text=text, file_params=file_params
                )

            # 通常のメッセージを送信
            response = self.web_client.chat_postMessage(channel=channel_id, text=text)
            self.logger.info(f"DM sent to user {user_id}: {text}")
            return response
        except Exception as e:
            self.logger.error(f"Error sending DM: {e}")
            return None

    def get_channel_history(self, channel_id: str, limit: int = 100) -> Optional[dict]:
        """
        チャンネルの履歴を取得

        Args:
            channel_id (str): チャンネルID
            limit (int): 取得するメッセージの上限数

        Returns:
            Optional[dict]: メッセージ履歴
        """
        try:
            result = self.web_client.conversations_history(
                channel=channel_id, limit=limit
            )
            return result
        except Exception as e:
            self.logger.error(f"Error fetching channel history: {e}")
            return None

    def send_message_with_file(
        self,
        channel_id: str,
        text: str,
        file_params: FileUploadParams,
        thread_ts: Optional[str] = None,
    ) -> Optional[dict]:
        """
        チャンネルにメッセージとファイルを同時に送信

        Args:
            channel_id (str): 送信先のチャンネルID
            text (str): 送信するメッセージ
            file_params (FileUploadParams): ファイルアップロードに関するパラメータ
            thread_ts (Optional[str]): スレッドのタイムスタンプ (スレッドに送信する場合)

        Returns:
            Optional[dict]: ファイル送信の結果
        """
        try:
            # ファイルを読み込む
            with open(file_params.file, "rb") as file:
                response = self.web_client.files_upload_v2(
                    channel=channel_id,
                    file=file,
                    filename=file_params.filename,
                    initial_comment=text,
                    thread_ts=thread_ts,
                    title=file_params.title,
                    snippet_type=file_params.snippet_type,
                )
            self.logger.info(f"Message and file sent to channel {channel_id}: {text}")
            return response
        except Exception as e:
            self.logger.error(f"Error sending message with file: {e}")
            return None

    def delete_file(self, file_id: str) -> Optional[dict]:
        """
        アップロードしたファイルを削除

        Args:
            file_id (str): 削除するファイルのID

        Returns:
            Optional[dict]: 削除結果
        """
        try:
            response = self.web_client.files_delete(file=file_id)
            self.logger.info(f"File deleted: {file_id}")
            return response
        except Exception as e:
            self.logger.error(f"Error deleting file: {e}")
            return None

    def __enter__(self):
        """Context Manager の開始処理"""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context Manager の終了処理"""
        self.stop()
        return False  # 例外を伝播させる
