"""Telegram 发送模块

发送消息到Telegram
"""

import asyncio
from typing import Optional
from loguru import logger

try:
    from telegram import Bot
    from telegram.constants import ParseMode
except ImportError:
    logger.warning("python-telegram-bot库未安装，Telegram功能将不可用")
    Bot = None
    ParseMode = None


class TelegramSender:
    """Telegram消息发送器"""

    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.bot: Optional[Bot] = None

        if Bot is None:
            raise ImportError(
                "请先安装python-telegram-bot库: pip install python-telegram-bot"
            )

    async def _get_bot(self) -> Bot:
        """获取Bot实例"""
        if self.bot is None:
            self.bot = Bot(token=self.bot_token)
        return self.bot

    async def send_message(self, text: str, parse_mode: str = "MarkdownV2") -> bool:
        """发送文本消息

        Args:
            text: 消息文本（支持Markdown格式）
            parse_mode: 解析模式，默认为MarkdownV2

        Returns:
            是否发送成功
        """
        try:
            bot = await self._get_bot()

            # 如果消息太长，需要分段发送
            max_length = 4096  # Telegram消息最大长度

            if len(text) <= max_length:
                await bot.send_message(
                    chat_id=self.chat_id,
                    text=text,
                    parse_mode=parse_mode,
                    disable_web_page_preview=False,
                )
                logger.info("Telegram消息发送成功")
                return True
            else:
                # 分段发送
                parts = self._split_message(text, max_length)
                for i, part in enumerate(parts):
                    await bot.send_message(
                        chat_id=self.chat_id,
                        text=part,
                        parse_mode=parse_mode,
                        disable_web_page_preview=True,
                    )
                    logger.info(f"Telegram消息第{i + 1}/{len(parts)}部分发送成功")
                return True

        except Exception as e:
            logger.error(f"Telegram消息发送失败: {e}")
            return False

    def send_message_sync(self, text: str, parse_mode: str = "MarkdownV2") -> bool:
        """同步方式发送消息

        Args:
            text: 消息文本
            parse_mode: 解析模式

        Returns:
            是否发送成功
        """
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # 如果事件循环已在运行，创建新任务
                future = asyncio.create_task(self.send_message(text, parse_mode))
                return asyncio.run_coroutine_threadsafe(future, loop).result()
            else:
                return loop.run_until_complete(self.send_message(text, parse_mode))
        except RuntimeError:
            # 没有事件循环，创建新的
            return asyncio.run(self.send_message(text, parse_mode))

    def _split_message(self, text: str, max_length: int = 4096) -> list:
        """将长消息分割成多个部分

        Args:
            text: 原始消息文本
            max_length: 每部分最大长度

        Returns:
            分割后的消息列表
        """
        if len(text) <= max_length:
            return [text]

        parts = []
        current_part = ""

        # 按行分割，尽量保持段落完整
        lines = text.split("\n")

        for line in lines:
            if len(current_part) + len(line) + 1 > max_length:
                # 当前部分已满，保存并开始新部分
                if current_part:
                    parts.append(current_part)
                current_part = line + "\n"
            else:
                current_part += line + "\n"

        # 添加最后一部分
        if current_part:
            parts.append(current_part)

        return parts

    async def test_connection(self) -> bool:
        """测试Telegram连接

        Returns:
            连接是否成功
        """
        try:
            bot = await self._get_bot()
            await bot.get_me()
            logger.info("Telegram连接测试成功")
            return True
        except Exception as e:
            logger.error(f"Telegram连接测试失败: {e}")
            return False

    def test_connection_sync(self) -> bool:
        """同步方式测试连接"""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                future = asyncio.create_task(self.test_connection())
                return asyncio.run_coroutine_threadsafe(future, loop).result()
            else:
                return loop.run_until_complete(self.test_connection())
        except RuntimeError:
            return asyncio.run(self.test_connection())


def send_daily_report(bot_token: str, chat_id: str, report_text: str) -> bool:
    """便捷函数：发送每日报告

    Args:
        bot_token: Telegram Bot Token
        chat_id: 聊天ID
        report_text: 报告文本

    Returns:
        是否发送成功
    """
    sender = TelegramSender(bot_token, chat_id)
    return sender.send_message_sync(report_text, parse_mode="MarkdownV2")


if __name__ == "__main__":
    # 测试
    import os

    bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "your_bot_token")
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "your_chat_id")

    # 测试连接
    sender = TelegramSender(bot_token, chat_id)
    if sender.test_connection_sync():
        print("连接成功！")

        # 发送测试消息
        test_message = """🌅 *早安 · 2024年3月2日*

今天的起床时间是 *07:30*
起床啦！

📅 今天是今年的第 62 天
███░░░░░░░░░░░░░░░░░ 17.0%

📝 今日 LeetCode *简单* 难度：
[两数之和](https://leetcode.cn/problems/two-sum/)

🏃 运动记录：
• 今天还没跑
• 本月跑了 69.77 公里
• 今年跑了 69.77 公里

📚 历史上的今天：
• *1962年*：周恩来总理提出"知识分子是工人阶级的一部分"

📜 今日诗词
*《春晓》—— 唐代·孟浩然*
```
春眠不觉晓，
处处闻啼鸟。
夜来风雨声，
花落知多少。
```
"""

        if sender.send_message_sync(test_message):
            print("消息发送成功！")
        else:
            print("消息发送失败！")
    else:
        print("连接失败，请检查Token和Chat ID")
