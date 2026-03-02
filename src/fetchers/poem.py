"""每日诗词 数据获取模块

通过ALAPI获取每日诗词
"""

import requests
from typing import Dict, Any, Optional
from dataclasses import dataclass
from loguru import logger


@dataclass
class Poem:
    """诗词信息"""

    title: str
    author: str
    dynasty: str
    content: str

    @property
    def formatted_content(self) -> str:
        """格式化的诗词内容（去除HTML标签，整理换行）"""
        import re

        # 去除HTML标签
        text = re.sub(r"<[^>]+>", "", self.content)
        # 规范化换行
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        return "\n".join(lines)


class PoemFetcher:
    """诗词数据获取器"""

    API_URL = "https://v3.alapi.cn/api/shici"

    def __init__(self, token: str):
        self.token = token
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
        )

    def get_random_poem(self) -> Optional[Poem]:
        """获取随机诗词

        Returns:
            Poem对象，获取失败返回None
        """
        logger.info("获取每日诗词...")

        params = {"token": self.token}

        try:
            response = self.session.get(self.API_URL, params=params, timeout=30)
            response.raise_for_status()

            # 检查响应内容是否为空
            if not response.text.strip():
                logger.error("ALAPI返回空响应")
                return None

            try:
                data = response.json()
            except Exception as e:
                logger.error(f"ALAPI返回非JSON数据: {response.text[:200]}")
                return None

            if data.get("code") != 200:
                logger.error(f"ALAPI返回错误: {data.get('msg', '未知错误')}")
                return None

            poem_data = data.get("data", {})

            poem = Poem(
                title=poem_data.get("title", ""),
                author=poem_data.get("author", ""),
                dynasty=poem_data.get("dynasty", ""),
                content=poem_data.get("content", ""),
            )

            logger.info(f"成功获取诗词: 《{poem.title}》")
            return poem

        except requests.exceptions.RequestException as e:
            logger.error(f"请求诗词API失败: {e}")
            return None
        except Exception as e:
            logger.error(f"解析诗词数据失败: {e}")
            return None

    def get_daily_poem(self) -> Dict[str, Any]:
        """获取格式化的每日诗词数据

        Returns:
            包含格式化信息的字典
        """
        poem = self.get_random_poem()

        if poem is None:
            # 返回默认诗词
            return {
                "title": "静夜思",
                "author": "李白",
                "dynasty": "唐代",
                "content": "床前明月光，\n疑是地上霜。\n举头望明月，\n低头思故乡。",
                "full_title": "《静夜思》—— 唐代·李白",
            }

        return {
            "title": poem.title,
            "author": poem.author,
            "dynasty": poem.dynasty,
            "content": poem.formatted_content,
            "full_title": f"《{poem.title}》—— {poem.dynasty}·{poem.author}",
        }


def get_daily_poem(token: str) -> Dict[str, Any]:
    """便捷函数：获取每日诗词

    Args:
        token: ALAPI Token

    Returns:
        格式化的诗词字典
    """
    fetcher = PoemFetcher(token)
    return fetcher.get_daily_poem()


if __name__ == "__main__":
    # 测试
    import os

    token = os.getenv("ALAPI_TOKEN", "your_token_here")

    try:
        poem = get_daily_poem(token)
        print(f"\n{poem['full_title']}\n")
        print(poem["content"])
    except Exception as e:
        logger.error(f"获取失败: {e}")
