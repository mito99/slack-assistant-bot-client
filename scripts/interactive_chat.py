#!/usr/bin/env python

import html

from services.message_service import MessageService


def main():
    chat_user_id = None

    # DirectMessageServiceのインスタンスを作成
    msg_service = MessageService()

    def message_handler(event):
        user_id = event.get("user")

        if user_id != chat_user_id:
            return

        text = html.unescape(event.get("text"))
        print(f"受信: User {user_id} said: {text}")

    msg_service.add_message_handler(message_handler)

    try:
        # SocketModeClientを開始
        msg_service.start()
        print("Slackに接続しました。")
        print("チャットを開始するユーザーIDを入力してください: ", end="", flush=True)
        chat_user_id = input().strip()

        while True:
            # ユーザー入力を待機
            message = input(
                "送信メッセージを入力してください (終了する場合は 'exit' と入力): "
            )

            if message.strip() == "":
                continue

            if message.lower() == "exit":
                break

            # メッセージを送信
            response = msg_service.send_dm(chat_user_id, message)
            if response:
                print("メッセージを送信しました。")
            else:
                print("メッセージの送信に失敗しました。")

    except KeyboardInterrupt:
        print("\nプログラムを終了します...")
    finally:
        # SocketModeClientを停止
        msg_service.stop()


if __name__ == "__main__":
    main()
