"""历史上的今天 数据获取模块

通过ALAPI获取历史上的今天事件
"""

import requests
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from loguru import logger


@dataclass
class HistoryEvent:
    """历史事件"""

    year: int
    title: str
    link: Optional[str] = None

    def get_age_at_event(self, birth_year: int) -> int:
        """计算事件发生时用户的年龄"""
        return self.year - birth_year


class HistoryTodayFetcher:
    """历史上的今天数据获取器"""

    API_URL = "https://v3.alapi.cn/api/eventHistory"

    def __init__(self, token: str):
        self.token = token
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
        )

    def get_today_events(
        self, month: Optional[int] = None, day: Optional[int] = None
    ) -> List[HistoryEvent]:
        """获取今天的历史事件

        Args:
            month: 月份（1-12），默认当前月份
            day: 日期（1-31），默认当前日期

        Returns:
            历史事件列表
        """
        now = datetime.now()
        month = month or now.month
        day = day or now.day

        logger.info(f"获取历史上的今天事件（{month}月{day}日）...")

        params = {"token": self.token, "date": f"{month:02d}-{day:02d}"}

        try:
            response = self.session.get(self.API_URL, params=params, timeout=30)
            response.raise_for_status()

            # 检查响应内容是否为空
            if not response.text.strip():
                logger.error("ALAPI返回空响应")
                return []

            try:
                data = response.json()
            except Exception as e:
                logger.error(f"ALAPI返回非JSON数据: {response.text[:200]}")
                return []

            if data.get("code") != 200:
                logger.error(f"ALAPI返回错误: {data.get('msg', '未知错误')}")
                return []

            events = []
            for item in data.get("data", []):
                # 解析年份
                year_str = item.get("year", "")
                try:
                    year = int(year_str)
                except (ValueError, TypeError):
                    continue

                event = HistoryEvent(
                    year=year, title=item.get("title", ""), link=item.get("link")
                )
                events.append(event)

            logger.info(f"成功获取 {len(events)} 条历史事件")
            return events

        except requests.exceptions.RequestException as e:
            logger.error(f"请求历史上的今天API失败: {e}")
            return []
        except Exception as e:
            logger.error(f"解析历史上的今天数据失败: {e}")
            return []

    def get_random_events(
        self, count: int = 2, birth_year: int = 1989
    ) -> List[Dict[str, Any]]:
        """随机获取几条历史事件，并计算发生时用户的年龄

        Args:
            count: 返回事件数量
            birth_year: 用户出生年份

        Returns:
            格式化的事件列表，包含年龄信息
        """
        events = self.get_today_events()

        if not events:
            return []

        import random

        # 随机选择指定数量的事件
        selected = random.sample(events, min(count, len(events)))

        result = []
        for event in selected:
            age = event.get_age_at_event(birth_year)
            age_str = f"（那年我 {age} 岁）" if age >= 0 else ""

            result.append(
                {
                    "year": event.year,
                    "title": event.title,
                    "link": event.link or "",
                    "age_str": age_str,
                }
            )

        return result


def get_today_history(
    token: str, count: int = 2, birth_year: int = 1989
) -> List[Dict[str, Any]]:
    """便捷函数：获取今天的历史事件

    Args:
        token: ALAPI Token
        count: 返回事件数量
        birth_year: 用户出生年份

    Returns:
        格式化的事件列表
    """
    fetcher = HistoryTodayFetcher(token)
    return fetcher.get_random_events(count=count, birth_year=birth_year)


if __name__ == "__main__":
    # 测试
    import os

    token = os.getenv("ALAPI_TOKEN", "your_token_here")

    try:
        events = get_today_history(token, count=2, birth_year=1989)
        for event in events:
            print(f"{event['year']}年: {event['title']} {event['age_str']}")
    except Exception as e:
        logger.error(f"获取失败: {e}")
