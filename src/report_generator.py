"""报告生成模块

生成每日Markdown格式的报告
"""

from datetime import datetime
from typing import Dict, Any, List
from dataclasses import dataclass
from loguru import logger


@dataclass
class DailyReport:
    """每日报告数据"""

    date: str
    wake_up_time: str
    day_of_year: int
    year_progress: str
    leetcode: Dict[str, Any]
    running: Dict[str, Any]
    history_today: List[Dict[str, Any]]
    poem: Dict[str, Any]


class ReportGenerator:
    """报告生成器"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config

    def generate(self, data: Dict[str, Any]) -> str:
        """生成完整的Markdown报告

        Args:
            data: 包含所有数据的字典
                - date: 日期
                - wake_up_time: 起床时间
                - leetcode: LeetCode题目信息
                - running: 跑步数据
                - history_today: 历史事件列表
                - poem: 诗词信息

        Returns:
            Markdown格式的报告文本
        """
        lines = []

        # 标题
        lines.append(f"# 早安 · {data['date']}\n")

        # 起床时间
        lines.append(f"## 🌅 今日起床\n")
        lines.append(f"今天的起床时间是 **{data['wake_up_time']}**。\n")
        lines.append("起床啦！新的一天开始啦。\n")

        # 年度进度
        running = data["running"]
        lines.append(f"## 📅 年度进度\n")
        lines.append(f"今天是今年的第 **{running['day_of_year']}** 天。\n")
        lines.append(f"```\n{running['progress_bar']}\n```\n")

        # LeetCode
        leetcode = data["leetcode"]
        lines.append(f"## 📝 今日 LeetCode\n")
        lines.append(f"**{leetcode['difficulty']}** 难度题目：\n")
        lines.append(f"**[{leetcode['title']}]({leetcode['link']})**\n")
        lines.append(f"\n[点击做题]({leetcode['link']})\n")

        # 跑步数据
        lines.append(f"## 🏃 运动记录\n")

        if running["today_distance"] > 0:
            lines.append(f"• 今天跑了 {running['today_distance']} 公里\n")
        else:
            lines.append("• 今天还没跑\n")

        lines.append(f"• 本月跑了 {running['month_distance']} 公里\n")
        lines.append(f"• 今年跑了 {running['year_distance']} 公里\n")

        # 上次跑步
        if running["last_run_distance"] > 0:
            lines.append(
                f"• 上次跑步：{running['last_run_date']}，{running['last_run_distance']} 公里\n"
            )

        # 历史上的今天
        lines.append(f"\n## 📚 历史上的今天\n")
        for event in data["history_today"]:
            lines.append(f"• **{event['year']}年**：{event['title']}")
            if event.get("link"):
                lines.append(f" ([查看详情]({event['link']}))")
            if event.get("age_str"):
                lines.append(f" {event['age_str']}")
            lines.append("\n")

        # 每日一诗
        poem = data["poem"]
        lines.append(f"\n## 📜 今日诗词\n")
        lines.append(f"**{poem['full_title']}**\n")
        lines.append("```\n")
        lines.append(f"{poem['content']}\n")
        lines.append("```\n")

        return "".join(lines)

    def generate_telegram_message(self, data: Dict[str, Any]) -> str:
        """生成适合Telegram发送的Markdown消息

        Telegram使用MarkdownV2格式，需要转义特殊字符

        Args:
            data: 包含所有数据的字典

        Returns:
            Telegram格式的Markdown文本
        """
        lines = []

        # 标题
        lines.append(f"🌅 *早安 · {self._escape_telegram_md(data['date'])}*\n")

        # 起床时间
        lines.append(
            f"今天的起床时间是 *{self._escape_telegram_md(data['wake_up_time'])}*\n"
        )
        lines.append("起床啦！\n")

        # 年度进度
        running = data["running"]
        lines.append(f"\n📅 今天是今年的第 {running['day_of_year']} 天\n")
        lines.append(f"{self._escape_telegram_md(running['progress_bar'])}\n")

        # LeetCode
        leetcode = data["leetcode"]
        lines.append(f"\n📝 今日 LeetCode *{leetcode['difficulty']}* 难度：\n")
        lines.append(
            f"[{self._escape_telegram_md(leetcode['title'])}]({leetcode['link']})\n"
        )

        # 跑步数据
        lines.append(f"\n🏃 运动记录：\n")
        if running["today_distance"] > 0:
            lines.append(f"• 今天跑了 {running['today_distance']} 公里\n")
        else:
            lines.append("• 今天还没跑\n")
        lines.append(f"• 本月跑了 {running['month_distance']} 公里\n")
        lines.append(f"• 今年跑了 {running['year_distance']} 公里\n")

        # 历史上的今天
        lines.append(f"\n📚 历史上的今天：\n")
        for event in data["history_today"]:
            line = f"• *{event['year']}年*：{self._escape_telegram_md(event['title'])}"
            if event.get("age_str"):
                line += f" {self._escape_telegram_md(event['age_str'])}"
            lines.append(line + "\n")

        # 每日一诗
        poem = data["poem"]
        lines.append(f"\n📜 今日诗词\n")
        lines.append(f"*{self._escape_telegram_md(poem['full_title'])}*\n")
        lines.append(f"```\n{self._escape_telegram_md(poem['content'])}\n```\n")

        return "".join(lines)

    def _escape_telegram_md(self, text: str) -> str:
        """转义Telegram MarkdownV2的特殊字符

        需要转义的字符：_ * [ ] ( ) ~ ` > # + - = | { } . !
        """
        if not text:
            return text

        # 需要转义的字符
        chars_to_escape = [
            "_",
            "*",
            "[",
            "]",
            "(",
            ")",
            "~",
            "`",
            ">",
            "#",
            "+",
            "-",
            "=",
            "|",
            "{",
            "}",
            ".",
            "!",
        ]

        for char in chars_to_escape:
            text = text.replace(char, f"\\{char}")

        return text


def generate_daily_report(
    data: Dict[str, Any], config: Dict[str, Any], for_telegram: bool = False
) -> str:
    """便捷函数：生成每日报告

    Args:
        data: 包含所有数据的字典
        config: 配置字典
        for_telegram: 是否为Telegram格式

    Returns:
        Markdown格式的报告文本
    """
    generator = ReportGenerator(config)

    if for_telegram:
        return generator.generate_telegram_message(data)
    else:
        return generator.generate(data)


if __name__ == "__main__":
    # 测试
    test_data = {
        "date": "2024年3月2日",
        "wake_up_time": "07:30",
        "leetcode": {
            "title": "两数之和",
            "difficulty": "简单",
            "link": "https://leetcode.cn/problems/two-sum/",
        },
        "running": {
            "today_distance": 0,
            "month_distance": 69.77,
            "year_distance": 69.77,
            "last_run_date": "2024-03-01",
            "last_run_distance": 5.0,
            "day_of_year": 62,
            "progress_bar": "███░░░░░░░░░░░░░░░░░ 17.0%",
        },
        "history_today": [
            {
                "year": 1962,
                "title": '周恩来总理提出"知识分子是工人阶级的一部分"',
                "link": "",
                "age_str": "（那年我 -27 岁）",
            }
        ],
        "poem": {
            "title": "春晓",
            "author": "孟浩然",
            "content": "春眠不觉晓，\n处处闻啼鸟。\n夜来风雨声，\n花落知多少。",
            "full_title": "《春晓》—— 孟浩然",
        },
    }

    config = {}

    # 生成标准Markdown
    report = generate_daily_report(test_data, config, for_telegram=False)
    print("=== 标准Markdown ===")
    print(report)

    # 生成Telegram格式
    telegram_msg = generate_daily_report(test_data, config, for_telegram=True)
    print("\n=== Telegram格式 ===")
    print(telegram_msg)
