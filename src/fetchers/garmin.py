"""Garmin 数据获取模块

通过garminconnect库获取全天运动数据（步数、里程、睡眠）
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
    """运动统计数据"""

    today_distance: float       # 今日全天总距离（公里）
    today_steps: int           # 今日总步数
    yesterday_distance: float   # 昨日全天总距离（公里）
    yesterday_steps: int        # 昨日总步数
    month_distance: float       # 本月累计全天总距离（公里）
    year_distance: float        # 今年累计全天总距离（公里）
    last_run_date: Optional[str] = None
    last_run_distance: float = 0.0


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
            is_cn = (self.region == "CN")
            self.client = Garmin(self.username, self.password, is_cn=is_cn)
            self.client.login()
            logger.info(f"Garmin Connect ({self.region}区) 登录成功")
            return True
        except Exception as e:
            logger.error(f"Garmin Connect登录失败: {e}")
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
        """获取全天运动统计数据 (包含步数和里程)"""
        if self.client is None:
            if not self.login():
                return RunningStats(0, 0, 0, 0, 0, 0)

        try:
            today = date.today()
            yesterday = today - timedelta(days=1)
            
            # 1. 获取今日汇总数据
            today_str = today.strftime("%Y-%m-%d")
            today_stats = self.client.get_stats(today_str)
            today_steps = today_stats.get("totalSteps", 0) or 0
            today_dist = (today_stats.get("totalDistanceMeters", 0) or 0) / 1000.0

            # 2. 获取昨日汇总数据
            yesterday_str = yesterday.strftime("%Y-%m-%d")
            yesterday_stats = self.client.get_stats(yesterday_str)
            yesterday_steps = yesterday_stats.get("totalSteps", 0) or 0
            yesterday_dist = (yesterday_stats.get("totalDistanceMeters", 0) or 0) / 1000.0

            # 3. 获取活动列表以查找“上次跑步”和“累计活动里程”
            activities = self.get_activities(0, 500)
            
            last_run_date = None
            last_run_distance = 0.0
            
            month_start = today.replace(day=1)
            year_start = today.replace(month=1, day=1)
            
            month_act_dist = 0.0
            year_act_dist = 0.0
            
            for act in activities:
                start_time = act.get("startTimeLocal", "")
                if not start_time: continue
                
                try:
                    act_date = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S").date()
                    dist_km = (act.get("distance", 0) or 0) / 1000.0
                    
                    # 统计所有运动累计 (跑步、步行、骑行等)
                    if act_date >= month_start:
                        month_act_dist += dist_km
                    if act_date >= year_start:
                        year_act_dist += dist_km
                        
                    # 专门记录“上次跑步”
                    if act_date < today and last_run_date is None:
                        if "running" in act.get("activityType", {}).get("typeKey", "").lower():
                            last_run_date = act_date.strftime("%Y-%m-%d")
                            last_run_distance = dist_km
                except:
                    continue

            # 4. 汇总统计：取今日全天里程与正式活动累计中的较大值
            final_month_dist = max(month_act_dist, today_dist)
            final_year_dist = max(year_act_dist, today_dist)

            logger.info(
                f"运动汇总: 今日{today_steps}步/{today_dist:.2f}km, 昨日{yesterday_steps}步/{yesterday_dist:.2f}km"
            )

            return RunningStats(
                today_distance=round(today_dist, 2),
                today_steps=today_steps,
                yesterday_distance=round(yesterday_dist, 2),
                yesterday_steps=yesterday_steps,
                month_distance=round(final_month_dist, 2),
                year_distance=round(final_year_dist, 2),
                last_run_date=last_run_date,
                last_run_distance=round(last_run_distance, 2)
            )

        except Exception as e:
            logger.error(f"获取运动统计数据失败: {e}")
            return RunningStats(0, 0, 0, 0, 0, 0)

    def get_sleep_data(self, target_date: Optional[date] = None) -> SleepData:
        """获取睡眠数据"""
        if self.client is None:
            if not self.login():
                return SleepData()

        try:
            if target_date is None:
                target_date = date.today()

            date_str = target_date.strftime("%Y-%m-%d")
            day_data = self.client.get_activities_fordate(date_str)

            if not day_data:
                return SleepData()

            sleep_times = day_data.get("SleepTimes", {})
            sleep_end = sleep_times.get("currentDaySleepEndTimeGMT")
            sleep_start = sleep_times.get("currentDaySleepStartTimeGMT")

            wake_up_str = None
            sleep_start_str = None
            duration = 0.0

            if sleep_end:
                wake_up_str = datetime.fromtimestamp(sleep_end / 1000).strftime("%H:%M")
            if sleep_start:
                sleep_start_str = datetime.fromtimestamp(sleep_start / 1000).strftime("%H:%M")
            if sleep_end and sleep_start:
                duration = (sleep_end - sleep_start) / 1000 / 3600

            return SleepData(
                wake_up_time=wake_up_str,
                sleep_time=sleep_start_str,
                sleep_duration=round(duration, 2),
            )
        except:
            return SleepData()


def get_garmin_data(username: str, password: str, region: str = "US") -> Dict[str, Any]:
    """获取Garmin所有数据"""
    fetcher = GarminFetcher(username, password, region)

    stats = fetcher.get_running_stats()
    sleep = fetcher.get_sleep_data()

    today = date.today()
    day_of_year = today.timetuple().tm_yday
    year_progress = (day_of_year / 365) * 100

    return {
        "today_distance": stats.today_distance,
        "today_steps": stats.today_steps,
        "yesterday_distance": stats.yesterday_distance,
        "yesterday_steps": stats.yesterday_steps,
        "month_distance": stats.month_distance,
        "year_distance": stats.year_distance,
        "last_run_date": stats.last_run_date or "暂无记录",
        "last_run_distance": stats.last_run_distance,
        "day_of_year": day_of_year,
        "year_progress": round(year_progress, 1),
        "progress_bar": _generate_progress_bar(year_progress),
        "wake_up_time": sleep.wake_up_time,
        "sleep_time": sleep.sleep_time,
        "sleep_duration": sleep.sleep_duration,
    }


def _generate_progress_bar(percentage: float, length: int = 20) -> str:
    """生成进度条"""
    filled = int(length * percentage / 100)
    bar = "█" * filled + "░" * (length - filled)
    return f"{bar} {percentage:.1f}%"
