#!/usr/bin/env python3

import argparse
import logging

from services.message_service import MessageService


def setup_logger():
    """ロガーの設定"""
    logger = logging.getLogger(__name__)
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger


def main():
    """メイン処理"""
    logger = setup_logger()

    # コマンドライン引数の設定
    parser = argparse.ArgumentParser(
        description="Slackにアップロードされたファイルを削除します"
    )
    parser.add_argument("file_id", help="削除するファイルのID")
    args = parser.parse_args()

    try:
        # MessageServiceのインスタンスを作成
        message_service = MessageService()

        # ファイルを削除
        result = message_service.delete_file(args.file_id)

        if result:
            logger.info(f"ファイルの削除に成功しました: {args.file_id}")
        else:
            logger.error(f"ファイルの削除に失敗しました: {args.file_id}")

    except Exception as e:
        logger.error(f"エラーが発生しました: {e}")
        raise


if __name__ == "__main__":
    main()
