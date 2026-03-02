"""配置加载模块

负责从环境变量和YAML配置文件加载配置，并提供全局访问
加载优先级：环境变量 > .env文件 > config.yaml
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass

# 尝试加载 python-dotenv
try:
    from dotenv import load_dotenv

    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False


@dataclass
class AlapiConfig:
    """ALAPI配置"""

    token: str


@dataclass
class TelegramConfig:
    """Telegram配置"""

    bot_token: str
    chat_id: str


@dataclass
class GarminConfig:
    """Garmin配置"""

    username: str
    password: str
    region: str = "US"  # 默认国际区


@dataclass
class ReportConfig:
    """报告配置"""

    time: str
    timezone: str
    show_personal_info: bool
    birth_year: int


class ConfigLoader:
    """配置加载器

    加载优先级：
    1. 系统环境变量（最高优先级）
    2. .env 文件
    3. config.yaml（最低优先级）
    """

    _instance = None
    _config: Dict[str, Any] = {}
    _env_loaded = False

    def __new__(cls, config_path: Optional[str] = None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_config(config_path)
        return cls._instance

    def _load_dotenv(self):
        """加载 .env 文件"""
        if not self._env_loaded and DOTENV_AVAILABLE:
            env_file = Path(__file__).parent.parent / ".env"
            if env_file.exists():
                load_dotenv(env_file)
                self._env_loaded = True

    def _get_env_or_config(
        self, env_vars: list, config_path: str, default: Any = None
    ) -> Any:
        """获取配置值

        优先级：环境变量 > .env文件 > config.yaml > 默认值

        Args:
            env_vars: 环境变量名列表（尝试顺序）
            config_path: config.yaml中的路径（用.分隔）
            default: 默认值
        """
        # 首先加载 .env 文件
        self._load_dotenv()

        # 检查环境变量
        for env_var in env_vars:
            value = os.getenv(env_var)
            if value:
                return value

        # 检查 config.yaml
        keys = config_path.split(".")
        value = self._config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value if value is not None else default

    def _load_config(self, config_path: Optional[str] = None):
        """加载配置文件"""
        if config_path is None:
            config_file = Path(__file__).parent.parent / "config.yaml"
        else:
            config_file = Path(config_path)

        # 如果 config.yaml 不存在，使用空配置（完全依赖环境变量）
        if not config_file.exists():
            self._config = {}
        else:
            with open(config_file, "r", encoding="utf-8") as f:
                self._config = yaml.safe_load(f) or {}

    @property
    def alapi(self) -> AlapiConfig:
        """获取ALAPI配置"""
        return AlapiConfig(
            token=self._get_env_or_config(["ALAPI_TOKEN"], "alapi.token", "")
        )

    @property
    def telegram(self) -> TelegramConfig:
        """获取Telegram配置"""
        return TelegramConfig(
            bot_token=self._get_env_or_config(
                ["TELEGRAM_BOT_TOKEN"], "telegram.bot_token", ""
            ),
            chat_id=self._get_env_or_config(
                ["TELEGRAM_CHAT_ID"], "telegram.chat_id", ""
            ),
        )

    @property
    def garmin(self) -> GarminConfig:
        """获取Garmin配置"""
        return GarminConfig(
            username=self._get_env_or_config(
                ["GARMIN_USERNAME"], "garmin.username", ""
            ),
            password=self._get_env_or_config(
                ["GARMIN_PASSWORD"], "garmin.password", ""
            ),
            region=self._get_env_or_config(["GARMIN_REGION"], "garmin.region", "US"),
        )

    @property
    def report(self) -> ReportConfig:
        """获取报告配置（从config.yaml或环境变量）"""
        return ReportConfig(
            time=self._get_env_or_config(["REPORT_TIME"], "report.time", "07:00"),
            timezone=self._get_env_or_config(
                ["REPORT_TIMEZONE"], "report.timezone", "Asia/Shanghai"
            ),
            show_personal_info=self._get_env_or_config(
                ["REPORT_SHOW_PERSONAL_INFO"], "report.show_personal_info", True
            ),
            birth_year=int(
                self._get_env_or_config(
                    ["REPORT_BIRTH_YEAR"], "report.birth_year", 1989
                )
            ),
        )

    def get(self, key: str, default: Any = None) -> Any:
        """获取任意配置项"""
        keys = key.split(".")
        value = self._config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value


def get_config(config_path: Optional[str] = None) -> ConfigLoader:
    """获取配置加载器实例（单例）"""
    return ConfigLoader(config_path)


if __name__ == "__main__":
    # 测试配置加载
    try:
        config = get_config()
        print(
            f"ALAPI Token: {config.alapi.token[:10] if config.alapi.token else '未设置'}..."
        )
        print(
            f"Telegram Bot: {config.telegram.bot_token[:10] if config.telegram.bot_token else '未设置'}..."
        )
        print(
            f"Garmin User: {config.garmin.username if config.garmin.username else '未设置'}"
        )
        print(f"Report Time: {config.report.time}")
        print("配置加载成功！")
    except Exception as e:
        print(f"错误: {e}")
