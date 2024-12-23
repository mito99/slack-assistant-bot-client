import argparse
import logging
import os
import time
from datetime import datetime
from typing import Optional

import requests
from slack_sdk.socket_mode.response import SocketModeResponse

from services.message_service import MessageService


def invoke_send_message(
    user_id: str, message: str, download_dir: str, rm: bool = False
):
    response_received = False

    def setup_download_directory() -> str:
        if not os.path.exists(download_dir):
            os.makedirs(download_dir)
        return download_dir

    def download_file(
        url: str, headers: dict, download_dir: str, filename: str
    ) -> Optional[str]:
        """
        ファイルをダウンロードして保存する

        Args:
            url (str): ダウンロードURL
            headers (dict): リクエストヘッダー
            download_dir (str): 保存先ディレクトリ
            filename (str): ファイル名

        Returns:
            Optional[str]: 保存されたファイルのパス。失敗した場合はNone
        """
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()

            file_path = os.path.join(download_dir, filename)

            with open(file_path, "wb") as f:
                f.write(response.content)

            return file_path
        except Exception as e:
            logging.error(f"ファイルのダウンロードに失敗しました: {e}")
            return None

    def handle_message(event: dict):
        """
        メッセージイベントを処理し、ファイルが含まれている場合はダウンロードする

        Args:
            event (dict): Slackイベントデータ
        """
        nonlocal response_received

        event_user_id = event.get("user")
        if event_user_id != user_id:
            return

        event_type = event.get("type")
        if event_type != "message":
            return

        files = event.get("files", [])
        for file in files or []:
            url_private = file.get("url_private")
            filename = file.get("name")

            if url_private and filename:
                headers = {
                    "Authorization": f"Bearer {message_service.web_client.token}"
                }
                saved_path = download_file(url_private, headers, download_dir, filename)

                if saved_path:
                    print(f"ファイルを保存しました: {saved_path}")
                else:
                    print("ファイルの保存に失敗しました")

            if rm:
                file_id = file.get("id")
                if file_id:
                    message_service.delete_file(file_id)

        response_received = True

    # ロギングの設定
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # ダウンロードディレクトリの設定
    download_dir = setup_download_directory()

    # MessageServiceの初期化
    message_service = MessageService()

    try:
        # メッセージハンドラを登録
        message_service.add_message_handler(handle_message)

        # サービスを開始
        with message_service:
            # DMを送信
            response = message_service.send_dm(user_id, message)
            if response:
                print(f"メッセージを送信しました: {message}")

                # ファイルが送信されるのを待機
                print("ファイルの受信を待機中...")
                for _ in range(10):
                    time.sleep(1)
                    if response_received:
                        break

            else:
                print("メッセージの送信に失敗しました")

    except KeyboardInterrupt:
        print("\nプログラムを終了します")
    except Exception as e:
        logger.error(f"エラーが発生しました: {e}", exc_info=True)


def main():
    # コマンドライン引数の解析
    parser = argparse.ArgumentParser(description="Slackでファイルを受信するスクリプト")
    parser.add_argument("user_id", help="メッセージを送信するユーザーのSlack ID")
    parser.add_argument(
        "-m",
        "--message",
        default="ファイルを送信してください",
        help="送信するメッセージ",
    )
    parser.add_argument(
        "-d",
        "--download_dir",
        default="tmp",
        help="ダウンロード先ディレクトリ",
    )
    parser.add_argument(
        "--rm",
        action="store_true",
        help="ダウンロード後にファイルを削除する",
    )
    args = parser.parse_args()

    invoke_send_message(args.user_id, args.message, args.download_dir, rm=args.rm)


if __name__ == "__main__":
    # main()
    invoke_send_message("U0868DNBAAC", "get 勤怠 README.md", "./tmp", rm=True)
