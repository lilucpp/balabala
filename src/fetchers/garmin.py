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


@dataclass
class SleepData:
    """睡眠数据"""

    wake_up_time: Optional[str] = None  # 起床时间
    sleep_time: Optional[str] = None  # 入睡时间
    sleep_duration: float = 0.0  # 睡眠时长（小时）


class GarminFetcher:
    """Garmin数据获取器"""

    def __init__(self, username: str, password: str, region: str = "US"):
        self.username = username
        self.password = password
        self.region = region.upper()
        self.client: Optional[Garmin] = None

        if Garmin is None:
            raise ImportError("请先安装garminconnect库: pip install garminconnect")

    def login(self) -> bool:
        """登录Garmin Connect"""
        try:
            logger.info(f"正在登录Garmin Connect ({self.region}区)...")
            self.client = Garmin(self.username, self.password, is_cn=True)
            self.client.login()
            logger.info(f"Garmin Connect ({self.region}区) 登录成功")
            return True
        except Exception as e:
            logger.error(f"Garmin Connect登录失败: {e}")
            if "401" in str(e):
                logger.error("提示：请确保：")
                logger.error(
                    "  1. 账号密码正确（可在 https://connect.garmin.cn/ 登录验证）"
                )
                logger.error("  2. 如果开启了两步验证(2FA)，请暂时关闭")
                logger.error("  3. 网络可以正常访问Garmin中国服务器")
            return False

    def get_activities(self, start: int = 0, limit: int = 10) -> List[Dict[str, Any]]:
        """获取活动列表"""
        if self.client is None:
            if not self.login():
                return []

        try:
            return self.client.get_activities(start, limit)
        except Exception as e:
            logger.error(f"获取活动列表失败: {e}")
            return []

    def get_running_stats(self) -> RunningStats:
        """获取跑步统计数据"""
        if self.client is None:
            if not self.login():
                return RunningStats(0, 0, 0)

        try:
            today = date.today()
            today_str = today.strftime("%Y-%m-%d")

            # 获取今日统计数据
            today_stats = self.client.get_stats(today_str)
            today_distance = today_stats.get("totalDistanceMeters", 0) / 1000

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

            # 获取上次跑步信息（从所有活动中查找最近的跑步）
            last_run_date = None
            last_run_distance = 0.0
            all_activities = self._get_activities_in_range(
                today - timedelta(days=365), today
            )
            for act in all_activities:
                if act.get("activityType", {}).get("typeKey") == "running":
                    activity_date_str = act.get("startTimeLocal", "")
                    if activity_date_str:
                        try:
                            activity_date = datetime.strptime(
                                activity_date_str, "%Y-%m-%d %H:%M:%S"
                            ).date()
                            if activity_date != today:
                                last_run_date = activity_date_str
                                last_run_distance = act.get("distance", 0) / 1000
                                break
                        except ValueError:
                            continue

            logger.info(
                f"跑步统计: 今日{today_distance:.2f}km, 本月{month_distance:.2f}km, 本年{year_distance:.2f}km"
            )

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

    def get_sleep_data(self, target_date: Optional[date] = None) -> SleepData:
        """获取睡眠数据"""
        if self.client is None:
            if not self.login():
                return SleepData()

        try:
            if target_date is None:
                target_date = date.today()

            date_str = target_date.strftime("%Y-%m-%d")
            logger.info(f"获取 {date_str} 的睡眠数据...")

            # 使用 get_activities_fordate 获取当天数据（包含睡眠）
            day_data = self.client.get_activities_fordate(date_str)

            if not day_data:
                logger.warning(f"未找到 {date_str} 的数据")
                return SleepData()

            # 从 SleepTimes 获取睡眠起止时间
            sleep_times = day_data.get("SleepTimes", {})
            sleep_end_timestamp = sleep_times.get("currentDaySleepEndTimeGMT")
            sleep_start_timestamp = sleep_times.get("currentDaySleepStartTimeGMT")

            # 转换时间戳为本地时间
            wake_up_str = None
            sleep_start_str = None

            if sleep_end_timestamp:
                try:
                    wake_up_dt = datetime.fromtimestamp(sleep_end_timestamp / 1000)
                    wake_up_str = wake_up_dt.strftime("%H:%M")
                except Exception as e:
                    logger.warning(f"解析起床时间失败: {e}")

            if sleep_start_timestamp:
                try:
                    sleep_dt = datetime.fromtimestamp(sleep_start_timestamp / 1000)
                    sleep_start_str = sleep_dt.strftime("%H:%M")
                except Exception as e:
                    logger.warning(f"解析入睡时间失败: {e}")

            # 计算睡眠时长（小时）
            sleep_duration = 0.0
            if sleep_end_timestamp and sleep_start_timestamp:
                sleep_duration = (
                    (sleep_end_timestamp - sleep_start_timestamp) / 1000 / 3600
                )

            sleep_info = SleepData(
                wake_up_time=wake_up_str,
                sleep_time=sleep_start_str,
                sleep_duration=round(sleep_duration, 2),
            )

            logger.info(
                f"睡眠数据: 起床{wake_up_str}, 入睡{sleep_start_str}, 时长{sleep_duration:.1f}小时"
            )
            return sleep_info

        except Exception as e:
            logger.error(f"获取睡眠数据失败: {e}")
            return SleepData()

    def _get_activities_in_range(
        self, start_date: date, end_date: date
    ) -> List[Dict[str, Any]]:
        """获取指定日期范围内的活动"""
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
                            return activities
                    except ValueError:
                        continue

            start += batch_size
            if start > 1000:
                break

        return activities


def get_garmin_data(username: str, password: str, region: str = "US") -> Dict[str, Any]:
    """获取Garmin所有数据（跑步和睡眠）"""
    fetcher = GarminFetcher(username, password, region)

    # 获取跑步数据
    stats = fetcher.get_running_stats()

    # 获取睡眠数据
    sleep = fetcher.get_sleep_data()

    today = date.today()
    day_of_year = today.timetuple().tm_yday
    year_progress = (day_of_year / 365) * 100

    return {
        # 跑步数据
        "today_distance": stats.today_distance,
        "month_distance": stats.month_distance,
        "year_distance": stats.year_distance,
        "last_run_date": stats.last_run_date or "暂无记录",
        "last_run_distance": stats.last_run_distance,
        "day_of_year": day_of_year,
        "year_progress": round(year_progress, 1),
        "progress_bar": _generate_progress_bar(year_progress),
        # 睡眠数据
        "wake_up_time": sleep.wake_up_time,
        "sleep_time": sleep.sleep_time,
        "sleep_duration": sleep.sleep_duration,
    }


def _generate_progress_bar(percentage: float, length: int = 20) -> str:
    """生成进度条"""
    filled = int(length * percentage / 100)
    bar = "█" * filled + "░" * (length - filled)
    return f"{bar} {percentage:.1f}%"


if __name__ == "__main__":
    import os

    username = os.getenv("GARMIN_USERNAME", "your_email@example.com")
    password = os.getenv("GARMIN_PASSWORD", "your_password")

    try:
        data = get_garmin_data(username, password)
        print(f"今日跑步: {data['today_distance']} 公里")
        print(f"本月累计: {data['month_distance']} 公里")
        print(f"今年累计: {data['year_distance']} 公里")
        print(f"起床时间: {data['wake_up_time']}")
        print(f"入睡时间: {data['sleep_time']}")
        print(f"睡眠时长: {data['sleep_duration']:.1f} 小时")
    except Exception as e:
        logger.error(f"获取失败: {e}")
