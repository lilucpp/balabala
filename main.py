"""balabala 主程序

每日自动化报告生成器
"""

import os
import sys
import asyncio
from datetime import datetime
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from loguru import logger

from config_loader import get_config
from report_generator import generate_daily_report
from telegram_sender import send_daily_report
from fetchers.leetcode import get_daily_question
from fetchers.history_today import get_today_history
from fetchers.poem import get_daily_poem
from fetchers.garmin import get_running_data


# 配置日志
logger.remove()
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO",
)
logger.add(
    "logs/balabala.log",
    rotation="1 day",
    retention="7 days",
    encoding="utf-8",
    level="DEBUG",
)


def get_wake_up_time() -> str:
    """获取起床时间（模拟）

    TODO: 后续可以集成智能设备自动获取

    Returns:
        起床时间字符串
    """
    # 当前时间作为起床时间（实际使用中应该从睡眠追踪设备获取）
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")


def collect_data(config) -> dict:
    """收集所有数据

    Args:
        config: 配置对象

    Returns:
        包含所有数据的字典
    """
    logger.info("开始收集数据...")

    data = {
        "date": datetime.now().strftime("%Y年%m月%d日"),
        "wake_up_time": get_wake_up_time(),
    }

    # 1. 获取LeetCode题目
    try:
        logger.info("获取LeetCode题目...")
        leetcode = get_daily_question()
        data["leetcode"] = {
            "title": leetcode.title,
            "difficulty": leetcode.difficulty,
            "link": leetcode.cn_link,
        }
        logger.info(f"获取成功: {leetcode.title}")
    except Exception as e:
        logger.error(f"获取LeetCode题目失败: {e}")
        data["leetcode"] = {
            "title": "获取失败",
            "difficulty": "未知",
            "link": "https://leetcode.cn/",
        }

    # 2. 获取跑步数据
    try:
        logger.info("获取Garmin跑步数据...")
        running = get_running_data(
            config.garmin.username, config.garmin.password, config.garmin.region
        )
        data["running"] = running
        logger.info(f"获取成功: 本月{running['month_distance']}公里")
    except Exception as e:
        logger.error(f"获取Garmin数据失败: {e}")
        # 使用默认数据
        today = datetime.now()
        day_of_year = today.timetuple().tm_yday
        data["running"] = {
            "today_distance": 0,
            "month_distance": 0,
            "year_distance": 0,
            "last_run_date": "暂无数据",
            "last_run_distance": 0,
            "day_of_year": day_of_year,
            "year_progress": round((day_of_year / 365) * 100, 1),
            "progress_bar": "█" * int(day_of_year / 365 * 20)
            + "░" * (20 - int(day_of_year / 365 * 20))
            + f" {round((day_of_year / 365) * 100, 1)}%",
        }

    # 3. 获取历史上的今天
    try:
        logger.info("获取历史上的今天...")
        history = get_today_history(
            config.alapi.token, count=2, birth_year=config.report.birth_year
        )
        data["history_today"] = history
        logger.info(f"获取成功: {len(history)}条事件")
    except Exception as e:
        logger.error(f"获取历史事件失败: {e}")
        data["history_today"] = []

    # 4. 获取每日诗词
    try:
        logger.info("获取每日诗词...")
        poem = get_daily_poem(config.alapi.token)
        data["poem"] = poem
        logger.info(f"获取成功: {poem['title']}")
    except Exception as e:
        logger.error(f"获取诗词失败: {e}")
        data["poem"] = {
            "title": "静夜思",
            "author": "李白",
            "content": "床前明月光，\n疑是地上霜。\n举头望明月，\n低头思故乡。",
            "full_title": "《静夜思》—— 李白",
        }

    logger.info("数据收集完成！")
    return data


def generate_and_send_report(config) -> bool:
    """生成并发送报告

    Args:
        config: 配置对象

    Returns:
        是否成功
    """
    try:
        # 收集数据
        data = collect_data(config)

        # 生成报告
        logger.info("生成Markdown报告...")
        report = generate_daily_report(data, {}, for_telegram=True)

        # 保存到本地
        today = datetime.now().strftime("%Y-%m-%d")
        report_file = f"data/report_{today}.md"
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report)
        logger.info(f"报告已保存: {report_file}")

        # 发送到Telegram
        logger.info("发送报告到Telegram...")
        success = send_daily_report(
            config.telegram.bot_token, config.telegram.chat_id, report
        )

        if success:
            logger.info("报告发送成功！")
        else:
            logger.error("报告发送失败！")

        return success

    except Exception as e:
        logger.error(f"生成或发送报告失败: {e}")
        return False


def main():
    """主函数"""
    logger.info("=" * 50)
    logger.info("balabala 每日报告生成器启动")
    logger.info("=" * 50)

    # 加载配置
    try:
        config = get_config()
        logger.info("配置加载成功")
    except FileNotFoundError as e:
        logger.error(f"配置错误: {e}")
        logger.info("请复制 config.yaml.example 为 config.yaml 并填写配置")
        sys.exit(1)
    except Exception as e:
        logger.error(f"加载配置失败: {e}")
        sys.exit(1)

    # 生成并发送报告
    success = generate_and_send_report(config)

    if success:
        logger.info("程序执行完成")
        sys.exit(0)
    else:
        logger.error("程序执行失败")
        sys.exit(1)


if __name__ == "__main__":
    main()
