"""LeetCode 数据获取模块

获取每日一题信息，支持筛选简单难度题目
"""

import requests
import json
from typing import Dict, Any, Optional
from dataclasses import dataclass
from loguru import logger


@dataclass
class LeetCodeQuestion:
    """LeetCode题目信息"""

    title: str
    title_slug: str
    difficulty: str
    link: str
    date: str
    question_id: str = ""

    @property
    def cn_link(self) -> str:
        """获取中文链接"""
        return f"https://leetcode.cn/problems/{self.title_slug}/"


class LeetCodeFetcher:
    """LeetCode数据获取器"""

    GRAPHQL_URL = "https://leetcode.com/graphql"

    # GraphQL查询：获取每日一题
    DAILY_QUERY = """
    query questionOfToday {
        activeDailyCodingChallengeQuestion {
            date
            link
            question {
                questionId
                title
                titleSlug
                difficulty
                topicTags {
                    name
                    slug
                }
            }
        }
    }
    """

    # GraphQL查询：获取所有题目列表（用于筛选简单难度）
    ALL_PROBLEMS_QUERY = """
    query problemsetQuestionList($categorySlug: String, $limit: Int, $skip: Int, $filters: QuestionListFilterInput) {
        problemsetQuestionList: questionList(
            categorySlug: $categorySlug
            limit: $limit
            skip: $skip
            filters: $filters
        ) {
            total: totalNum
            questions: data {
                acRate
                difficulty
                freqBar
                frontendQuestionId: questionFrontendId
                isFavor
                paidOnly: isPaidOnly
                status
                title
                titleSlug
                topicTags {
                    name
                    id
                    slug
                }
                hasSolution
                hasVideoSolution
            }
        }
    }
    """

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Content-Type": "application/json",
                "Referer": "https://leetcode.com/",
            }
        )

    def _graphql_request(
        self, query: str, variables: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """发送GraphQL请求"""
        payload = {"query": query, "variables": variables or {}}

        try:
            response = self.session.post(self.GRAPHQL_URL, json=payload, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"LeetCode API请求失败: {e}")
            raise

    def get_daily_question(self) -> LeetCodeQuestion:
        """获取每日一题"""
        logger.info("获取LeetCode每日一题...")

        result = self._graphql_request(self.DAILY_QUERY)

        if "errors" in result:
            raise Exception(f"GraphQL错误: {result['errors']}")

        data = result["data"]["activeDailyCodingChallengeQuestion"]
        question_data = data["question"]

        return LeetCodeQuestion(
            title=question_data["title"],
            title_slug=question_data["titleSlug"],
            difficulty=question_data["difficulty"],
            link=f"https://leetcode.com{data['link']}",
            date=data["date"],
            question_id=question_data.get("questionId", ""),
        )

    def get_easy_questions(self, limit: int = 50) -> list[LeetCodeQuestion]:
        """获取简单难度的题目列表"""
        logger.info(f"获取LeetCode简单难度题目列表（前{limit}题）...")

        variables = {
            "categorySlug": "",
            "limit": limit,
            "skip": 0,
            "filters": {"difficulty": "EASY"},
        }

        result = self._graphql_request(self.ALL_PROBLEMS_QUERY, variables)

        if "errors" in result:
            raise Exception(f"GraphQL错误: {result['errors']}")

        questions = result["data"]["problemsetQuestionList"]["questions"]

        easy_questions = []
        for q in questions:
            if q["difficulty"] == "Easy":
                easy_questions.append(
                    LeetCodeQuestion(
                        title=q["title"],
                        title_slug=q["titleSlug"],
                        difficulty="简单",
                        link=f"https://leetcode.com/problems/{q['titleSlug']}/",
                        date="",
                        question_id=q["frontendQuestionId"],
                    )
                )

        return easy_questions

    def get_random_easy_question(self) -> LeetCodeQuestion:
        """随机获取一道简单难度题目"""
        import random

        easy_questions = self.get_easy_questions(limit=100)
        return random.choice(easy_questions)


def get_daily_question() -> LeetCodeQuestion:
    """便捷函数：获取每日一题"""
    fetcher = LeetCodeFetcher()
    question = fetcher.get_daily_question()

    # 如果不是简单难度，随机选一道简单题
    if question.difficulty != "Easy":
        logger.info(f"今日题目难度为{question.difficulty}，获取随机简单题...")
        question = fetcher.get_random_easy_question()
    else:
        question.difficulty = "简单"

    return question


if __name__ == "__main__":
    # 测试
    try:
        question = get_daily_question()
        print(f"题目: {question.title}")
        print(f"难度: {question.difficulty}")
        print(f"链接: {question.cn_link}")
    except Exception as e:
        logger.error(f"获取失败: {e}")
