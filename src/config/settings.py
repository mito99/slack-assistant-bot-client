"""
Configuration settings for the Slack Assistant Bot Client using Pydantic
"""

from typing import Optional

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class SlackSettings(BaseSettings):
    """Slack関連の設定を管理するモデル"""

    bot_token: Optional[str] = Field(None, alias="SLACK_BOT_TOKEN")
    app_token: Optional[str] = Field(None, alias="SLACK_APP_TOKEN")
    bot_app_id: Optional[str] = Field(None, alias="SLACK_BOT_APP_ID")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "allow"


class LoggingSettings(BaseModel):
    """ロギング設定を管理するモデル"""

    level: str = Field(default="INFO", alias="LOG_LEVEL")
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


# 設定インスタンスの作成
slack_settings = SlackSettings()
logging_settings = LoggingSettings()
