"""每日一句 数据获取模块

通过金山词霸 (Iciba) API 获取每日一句
"""

import requests
from typing import Dict, Any, Optional
from dataclasses import dataclass
from loguru import logger


@dataclass
class DailySentence:
    """每日一句信息"""

    content: str    # 英文内容
    note: str       # 中文翻译
    tts: str        # 语音链接
    picture: str    # 图片链接
    caption: str    # 标题
    dateline: str   # 日期


class DailySentenceFetcher:
    """每日一句数据获取器"""

    API_URL = "https://open.iciba.com/dsapi/"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
        )

    def get_sentence(self) -> Optional[DailySentence]:
        """获取每日一句

        Returns:
            DailySentence对象，获取失败返回None
        """
        logger.info("获取金山词霸每日一句...")

        try:
            response = self.session.get(self.API_URL, timeout=30)
            response.raise_for_status()
            data = response.json()

            sentence = DailySentence(
                content=data.get("content", ""),
                note=data.get("note", ""),
                tts=data.get("tts", ""),
                picture=data.get("picture", ""),
                caption=data.get("caption", "词霸每日一句"),
                dateline=data.get("dateline", "")
            )

            logger.info(f"成功获取每日一句: {sentence.content[:30]}...")
            return sentence

        except Exception as e:
            logger.error(f"获取每日一句失败: {e}")
            return None


def get_daily_sentence() -> Dict[str, Any]:
    """便捷函数：获取每日一句

    Returns:
        包含格式化信息的字典
    """
    fetcher = DailySentenceFetcher()
    sentence = fetcher.get_sentence()

    if sentence is None:
        return {
            "content": "Keep on going never give up.",
            "note": "勇往直前，决不放弃。",
            "tts": "",
            "picture": "",
            "caption": "词霸每日一句"
        }

    return {
        "content": sentence.content,
        "note": sentence.note,
        "tts": sentence.tts,
        "picture": sentence.picture,
        "caption": sentence.caption
    }


if __name__ == "__main__":
    # 测试
    sentence = get_daily_sentence()
    print(f"\n标题: {sentence['caption']}")
    print(f"English: {sentence['content']}")
    print(f"Chinese: {sentence['note']}")
    print(f"语音: {sentence['tts']}")
    print(f"图片: {sentence['picture']}")
