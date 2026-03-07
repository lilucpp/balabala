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
    # 今日数据
    today_steps: int            # 今日步数
    today_total_dist: float     # 今日总里程
    today_walk_dist: float      # 今日走路/日常里程 (总里程 - 运动里程)
    today_exercise_dist: float  # 今日正式运动里程

    # 昨日数据
    yesterday_steps: int
    yesterday_total_dist: float
    yesterday_walk_dist: float
    yesterday_exercise_dist: float

    # 累计数据 (正式运动)
    month_exercise_dist: float  # 本月正式运动总里程
    year_exercise_dist: float   # 今年正式运动总里程
    
    # 辅助信息
    last_run_date: Optional[str] = None
    last_run_distance: float = 0.0


@dataclass
class SleepData:
    """睡眠数据"""
    wake_up_time: Optional[str] = None
    sleep_time: Optional[str] = None
    sleep_duration: float = 0.0


class GarminFetcher:
    """Garmin数据获取器"""

    def __init__(self, username: str, password: str, region: str = "US"):
        self.username = username
        self.password = password
        self.region = region.upper()
        self.client: Optional[Garmin] = None

    def login(self) -> bool:
        """登录Garmin Connect"""
        try:
            logger.info(f"正在登录Garmin Connect ({self.region}区)...")
            is_cn = (self.region == "CN")
            self.client = Garmin(self.username, self.password, is_cn=is_cn)
            self.client.login()
            return True
        except Exception as e:
            logger.error(f"Garmin Connect登录失败: {e}")
            return False

    def get_activities(self, start: int = 0, limit: int = 10) -> List[Dict[str, Any]]:
        """获取活动列表"""
        if self.client is None:
            if not self.login(): return []
        try:
            return self.client.get_activities(start, limit)
        except Exception as e:
            logger.error(f"获取活动列表失败: {e}")
            return []

    def get_running_stats(self) -> RunningStats:
        """获取运动统计数据 (分离走路和运动)"""
        if self.client is None:
            if not self.login():
                return RunningStats(0,0.0,0.0,0.0,0,0.0,0.0,0.0,0.0,0.0)

        try:
            today = date.today()
            yesterday = today - timedelta(days=1)
            
            # 1. 获取活动列表 (最近500条，覆盖一年)
            activities = self.get_activities(0, 500)
            
            # 2. 计算正式运动里程 (Running, Cycling, etc.)
            today_exercise_dist = 0.0
            yesterday_exercise_dist = 0.0
            month_exercise_dist = 0.0
            year_exercise_dist = 0.0
            
            last_run_date = None
            last_run_distance = 0.0
            
            month_start = today.replace(day=1)
            year_start = today.replace(month=1, day=1)
            
            for act in activities:
                start_time = act.get("startTimeLocal", "")
                if not start_time: continue
                try:
                    act_date = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S").date()
                    dist_km = (act.get("distance", 0) or 0) / 1000.0
                    
                    # 只要是正式记录的活动都计入运动里程
                    if act_date == today:
                        today_exercise_dist += dist_km
                    elif act_date == yesterday:
                        yesterday_exercise_dist += dist_km
                        
                    if act_date >= month_start:
                        month_exercise_dist += dist_km
                    if act_date >= year_start:
                        year_exercise_dist += dist_km
                        
                    # 记录上次跑步
                    if act_date < today and last_run_date is None:
                        if "running" in act.get("activityType", {}).get("typeKey", "").lower():
                            last_run_date = act_date.strftime("%Y-%m-%d")
                            last_run_distance = dist_km
                except: continue

            # 3. 获取每日汇总 (Steps & Total Distance)
            # 今日汇总
            t_stats = self.client.get_stats(today.strftime("%Y-%m-%d"))
            t_steps = t_stats.get("totalSteps", 0) or 0
            t_total_dist = (t_stats.get("totalDistanceMeters", 0) or 0) / 1000.0
            t_walk_dist = max(0, t_total_dist - today_exercise_dist)

            # 昨日汇总
            y_stats = self.client.get_stats(yesterday.strftime("%Y-%m-%d"))
            y_steps = y_stats.get("totalSteps", 0) or 0
            y_total_dist = (y_stats.get("totalDistanceMeters", 0) or 0) / 1000.0
            y_walk_dist = max(0, y_total_dist - yesterday_exercise_dist)

            logger.info(f"统计完成: 今日运动{today_exercise_dist:.2f}km, 走路{t_walk_dist:.2f}km")

            return RunningStats(
                today_steps=t_steps,
                today_total_dist=round(t_total_dist, 2),
                today_walk_dist=round(t_walk_dist, 2),
                today_exercise_dist=round(today_exercise_dist, 2),
                yesterday_steps=y_steps,
                yesterday_total_dist=round(y_total_dist, 2),
                yesterday_walk_dist=round(y_walk_dist, 2),
                yesterday_exercise_dist=round(yesterday_exercise_dist, 2),
                month_exercise_dist=round(month_exercise_dist, 2),
                year_exercise_dist=round(year_exercise_dist, 2),
                last_run_date=last_run_date,
                last_run_distance=round(last_run_distance, 2)
            )

        except Exception as e:
            logger.error(f"统计失败: {e}")
            return RunningStats(0,0,0,0,0,0,0,0,0,0)

    def get_sleep_data(self, target_date: Optional[date] = None) -> SleepData:
        """获取睡眠数据"""
        if self.client is None:
            if not self.login(): return SleepData()
        try:
            d_str = (target_date or date.today()).strftime("%Y-%m-%d")
            day_data = self.client.get_activities_fordate(d_str)
            if not day_data: return SleepData()
            s_times = day_data.get("SleepTimes", {})
            s_end = s_times.get("currentDaySleepEndTimeGMT")
            s_start = s_times.get("currentDaySleepStartTimeGMT")
            
            wake_up = datetime.fromtimestamp(s_end/1000).strftime("%H:%M") if s_end else None
            sleep_in = datetime.fromtimestamp(s_start/1000).strftime("%H:%M") if s_start else None
            duration = (s_end - s_start)/1000/3600 if s_end and s_start else 0
            return SleepData(wake_up, sleep_in, round(duration, 2))
        except: return SleepData()


def get_garmin_data(username: str, password: str, region: str = "US") -> Dict[str, Any]:
    fetcher = GarminFetcher(username, password, region)
    stats = fetcher.get_running_stats()
    sleep = fetcher.get_sleep_data()
    
    today = date.today()
    day_of_year = today.timetuple().tm_yday
    year_progress = round((day_of_year / 365) * 100, 1)

    return {
        "today_steps": stats.today_steps,
        "today_total_dist": stats.today_total_dist,
        "today_walk_dist": stats.today_walk_dist,
        "today_exercise_dist": stats.today_exercise_dist,
        "yesterday_steps": stats.yesterday_steps,
        "yesterday_total_dist": stats.yesterday_total_dist,
        "yesterday_walk_dist": stats.yesterday_walk_dist,
        "yesterday_exercise_dist": stats.yesterday_exercise_dist,
        "month_exercise_dist": stats.month_exercise_dist,
        "year_exercise_dist": stats.year_exercise_dist,
        "last_run_date": stats.last_run_date or "暂无记录",
        "last_run_distance": stats.last_run_distance,
        "day_of_year": day_of_year,
        "year_progress": year_progress,
        "progress_bar": _generate_progress_bar(year_progress),
        "wake_up_time": sleep.wake_up_time,
        "sleep_time": sleep.sleep_time,
        "sleep_duration": sleep.sleep_duration,
    }

def _generate_progress_bar(percentage: float, length: int = 20) -> str:
    filled = int(length * percentage / 100)
    return "█" * filled + "░" * (length - filled) + f" {percentage}%"
