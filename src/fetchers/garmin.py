"""Garmin 数据获取模块

通过garminconnect库获取运动数据
"""

from datetime import datetime, date, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from loguru import logger


try:
    from garminconnect import Garmin
except ImportError:
    logger.warning("garminconnect库未安装，Garmin功能将不可用")
    Garmin = None


@dataclass
class RunningStats:
    """跑步统计数据"""

    today_distance: float  # 今日距离（公里）
    month_distance: float  # 本月距离（公里）
    year_distance: float  # 今年距离（公里）
    last_run_date: Optional[str] = None  # 上次跑步日期
    last_run_distance: float = 0.0  # 上次跑步距离


class GarminFetcher:
    """Garmin数据获取器"""

    # 区域配置
    REGIONS = {
        "US": {
            "url": "https://connect.garmin.com",
            "sso_url": "https://sso.garmin.com",
        },
        "CN": {
            "url": "https://connect.garmin.cn",
            "sso_url": "https://sso.garmin.cn",
        },
    }

    def __init__(self, username: str, password: str, region: str = "US"):
        self.username = username
        self.password = password
        self.region = region.upper()
        self.client: Optional[Garmin] = None

        if Garmin is None:
            raise ImportError("请先安装garminconnect库: pip install garminconnect")

    def login(self) -> bool:
        """登录Garmin Connect

        Returns:
            是否登录成功
        """
        try:
            logger.info(f"正在登录Garmin Connect ({self.region}区)...")

            # 直接使用Garmin类初始化，库内部会处理不同区域的登录
            # 中国区用户可能需要确保网络环境可以访问garmin.cn
            self.client = Garmin(self.username, self.password, is_cn=True)
            self.client.login()

            logger.info(f"Garmin Connect ({self.region}区) 登录成功")
            return True
        except Exception as e:
            logger.error(f"Garmin Connect登录失败: {e}")
            # 如果失败，提示用户可能的原因
            if "401" in str(e):
                logger.error("提示：请确保：")
                logger.error(
                    "  1. 账号密码正确（可在 https://connect.garmin.cn/ 登录验证）"
                )
                logger.error("  2. 如果开启了两步验证(2FA)，请暂时关闭")
                logger.error("  3. 网络可以正常访问Garmin中国服务器")
            return False

    def get_activities(self, start: int = 0, limit: int = 10) -> List[Dict[str, Any]]:
        """获取活动列表

        Args:
            start: 起始索引
            limit: 返回数量

        Returns:
            活动列表
        """
        if self.client is None:
            if not self.login():
                return []

        try:
            activities = self.client.get_activities(start, limit)
            return activities
        except Exception as e:
            logger.error(f"获取活动列表失败: {e}")
            return []

    def get_running_stats(self) -> RunningStats:
        """获取跑步统计数据

        Returns:
            跑步统计数据
        """
        if self.client is None:
            if not self.login():
                return RunningStats(0, 0, 0)

        try:
            today = date.today()
            today_str = today.strftime("%Y-%m-%d")

            # 获取今日统计数据
            today_stats = self.client.get_stats(today_str)
            today_distance = today_stats.get("totalDistance", 0) / 1000  # 转换为公里

            # 获取本月数据
            month_start = today.replace(day=1)
            month_activities = self._get_activities_in_range(month_start, today)
            month_distance = sum(
                act.get("distance", 0) / 1000
                for act in month_activities
                if act.get("activityType", {}).get("typeKey") == "running"
            )

            # 获取今年数据
            year_start = today.replace(month=1, day=1)
            year_activities = self._get_activities_in_range(year_start, today)
            year_distance = sum(
                act.get("distance", 0) / 1000
                for act in year_activities
                if act.get("activityType", {}).get("typeKey") == "running"
            )

            # 获取上次跑步信息
            last_run_date = None
            last_run_distance = 0.0
            for act in month_activities:
                if act.get("activityType", {}).get("typeKey") == "running":
                    activity_date = act.get("startTimeLocal", "")
                    if activity_date and activity_date != today_str:
                        last_run_date = activity_date
                        last_run_distance = act.get("distance", 0) / 1000
                        break

            return RunningStats(
                today_distance=round(today_distance, 2),
                month_distance=round(month_distance, 2),
                year_distance=round(year_distance, 2),
                last_run_date=last_run_date,
                last_run_distance=round(last_run_distance, 2),
            )

        except Exception as e:
            logger.error(f"获取跑步统计数据失败: {e}")
            return RunningStats(0, 0, 0)

    def _get_activities_in_range(
        self, start_date: date, end_date: date
    ) -> List[Dict[str, Any]]:
        """获取指定日期范围内的活动

        Args:
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            活动列表
        """
        activities = []
        start = 0
        batch_size = 100

        while True:
            batch = self.get_activities(start, batch_size)
            if not batch:
                break

            for activity in batch:
                activity_date_str = activity.get("startTimeLocal", "")
                if activity_date_str:
                    try:
                        activity_date = datetime.strptime(
                            activity_date_str, "%Y-%m-%d %H:%M:%S"
                        ).date()
                        if start_date <= activity_date <= end_date:
                            activities.append(activity)
                        elif activity_date < start_date:
                            # 超出日期范围，停止获取
                            return activities
                    except ValueError:
                        continue

            start += batch_size

            # 防止无限循环
            if start > 1000:
                break

        return activities


def get_running_data(
    username: str, password: str, region: str = "US"
) -> Dict[str, Any]:
    """便捷函数：获取跑步数据

    Args:
        username: Garmin账号
        password: Garmin密码
        region: 区域 ("CN" 或 "US")

    Returns:
        格式化的跑步数据字典
    """
    fetcher = GarminFetcher(username, password, region)
    stats = fetcher.get_running_stats()

    today = date.today()
    day_of_year = today.timetuple().tm_yday
    year_progress = (day_of_year / 365) * 100

    return {
        "today_distance": stats.today_distance,
        "month_distance": stats.month_distance,
        "year_distance": stats.year_distance,
        "last_run_date": stats.last_run_date or "暂无记录",
        "last_run_distance": stats.last_run_distance,
        "day_of_year": day_of_year,
        "year_progress": round(year_progress, 1),
        "progress_bar": _generate_progress_bar(year_progress),
    }


def _generate_progress_bar(percentage: float, length: int = 20) -> str:
    """生成进度条

    Args:
        percentage: 百分比（0-100）
        length: 进度条长度

    Returns:
        进度条字符串
    """
    filled = int(length * percentage / 100)
    bar = "█" * filled + "░" * (length - filled)
    return f"{bar} {percentage:.1f}%"


if __name__ == "__main__":
    # 测试
    import os

    username = os.getenv("GARMIN_USERNAME", "your_email@example.com")
    password = os.getenv("GARMIN_PASSWORD", "your_password")

    try:
        data = get_running_data(username, password)
        print(f"今日跑步: {data['today_distance']} 公里")
        print(f"本月累计: {data['month_distance']} 公里")
        print(f"今年累计: {data['year_distance']} 公里")
        print(f"进度: {data['progress_bar']}")
    except Exception as e:
        logger.error(f"获取失败: {e}")
