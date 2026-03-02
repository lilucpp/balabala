"""测试配置加载"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

import os
from dotenv import load_dotenv

# 1. 测试 .env 文件是否存在
env_path = Path(__file__).parent / ".env"
print(f".env 文件存在: {env_path.exists()}")
print(f".env 文件路径: {env_path.absolute()}")

# 2. 手动加载 .env
if env_path.exists():
    load_dotenv(env_path)
    print("\n手动加载 .env 文件成功")
    print(f"ALAPI_TOKEN from env: {os.getenv('ALAPI_TOKEN', '未设置')[:10]}...")
    print(
        f"TELEGRAM_BOT_TOKEN from env: {os.getenv('TELEGRAM_BOT_TOKEN', '未设置')[:10]}..."
    )
    print(f"GARMIN_USERNAME from env: {os.getenv('GARMIN_USERNAME', '未设置')}")
else:
    print("\n错误: .env 文件不存在!")

# 3. 测试 ConfigLoader
print("\n" + "=" * 50)
print("测试 ConfigLoader:")
print("=" * 50)

try:
    from config_loader import get_config

    config = get_config()

    print(
        f"ALAPI Token: {config.alapi.token[:10] if config.alapi.token else '未设置'}..."
    )
    print(
        f"Telegram Bot Token: {config.telegram.bot_token[:10] if config.telegram.bot_token else '未设置'}..."
    )
    print(f"Telegram Chat ID: {config.telegram.chat_id}")
    print(f"Garmin Username: {config.garmin.username}")
    print(f"Garmin Password: {'已设置' if config.garmin.password else '未设置'}")
    print(f"Garmin Region: {config.garmin.region}")

except Exception as e:
    print(f"错误: {e}")
    import traceback

    traceback.print_exc()
