#!/usr/bin/env python3

import argparse
import html
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from services.message_service import FileUploadParams, MessageService


def invoke_message_service(
    user_id: str,
    file_path: Path,
    message: str,
    title: Optional[str] = None,
    snippet_type: Optional[str] = None,
    rm: bool = False,
    wait_time: int = 10,
):
    response_received = False
    chat_user_id = user_id

    def message_handler(event):
        nonlocal response_received
        user_id = event.get("user")
        event_type = event.get("type")
        if event_type != "message":
            return

        if user_id != chat_user_id:
            return

        text = html.unescape(event.get("text") or "")
        print(f"受信: User {user_id} said: {text}")

        response_received = True

    if not file_path.exists():
        print(f"エラー: ファイル '{file_path}' が見つかりません。")
        return

    # MessageServiceのインスタンス化
    message_service = MessageService()
    message_service.add_message_handler(message_handler)
    with message_service:
        # ファイルパラメータの設定
        file_params = FileUploadParams(
            file=str(file_path),
            filename=file_path.name,
            title=title,
            snippet_type=snippet_type,
        )

        # ファイル付きDMの送信
        result = message_service.send_dm(
            user_id=user_id, text=message, file_params=file_params
        )

        if result:
            file_id = result["file"]["id"]
            print(f"✅ ファイルの送信に成功しました。File ID: {file_id}")

            # 返信を待つ
            for _ in range(wait_time):
                time.sleep(1)
                if response_received:
                    break

            if not response_received:
                print("❌ 相手の反応なし")

            if rm:
                message_service.delete_file(file_id)

        else:
            print("❌ ファイルの送信に失敗しました")


def main():
    parser = argparse.ArgumentParser(description="Slackユーザーにファイルを送信します")
    parser.add_argument("user_id", help="送信先のSlackユーザーID")
    parser.add_argument("file_path", help="送信するファイルのパス")
    parser.add_argument(
        "--message", "-m", default="ファイルを送信します", help="送信時のメッセージ"
    )
    parser.add_argument("--title", "-t", help="ファイルのタイトル（省略可）")
    parser.add_argument(
        "--snippet_type", "-st", help="ファイルのスニペットタイプ（省略可）"
    )
    parser.add_argument(
        "--rm", action="store_true", help="アップロードしたファイルを削除する"
    )
    parser.add_argument(
        "-w",
        "--wait_time",
        type=int,
        default=10,
        help="レスポンスを待機する秒数（デフォルト: 10秒）",
    )
    args = parser.parse_args()

    invoke_message_service(
        user_id=args.user_id,
        file_path=Path(args.file_path),
        message=args.message,
        title=args.title,
        snippet_type=args.snippet_type,
        rm=args.rm,
        wait_time=args.wait_time,
    )


if __name__ == "__main__":
    main()
    # invoke_message_service(
    #     user_id="U0868DNBAAC",
    #     file_path=Path("./README.md"),
    #     message="put 勤怠",
    #     snippet_type="text",
    #     rm=True,
    # )
