"""Garmin Connect 测试脚本

用于测试Garmin账号登录和区域配置
"""

import sys

sys.path.insert(0, "src")

from garminconnect import Garmin
from getpass import getpass
from loguru import logger

logger.remove()
logger.add(sys.stderr, level="DEBUG")


def test_garmin_login():
    print("=" * 50)
    print("Garmin Connect 登录测试")
    print("=" * 50)

    # 获取用户信息
    username = input("请输入Garmin账号邮箱: ").strip()
    password = getpass("请输入Garmin密码: ").strip()

    print(f"\n正在测试登录...")
    print(f"账号: {username}")

    try:
        # 创建客户端
        client = Garmin(username, password, is_cn=True)

        # 尝试登录
        client.login()

        print("\n✅ 登录成功！")

        # 获取基本信息
        try:
            user = client.get_full_name()
            print(f"用户名: {user}")
        except:
            pass

        # 尝试获取最近活动
        try:
            activities = client.get_activities(0, 1)
            if activities:
                print(f"\n最近活动:")
                for act in activities[:1]:
                    print(f"  - {act.get('activityName', 'Unknown')}")
                    print(
                        f"    类型: {act.get('activityType', {}).get('typeKey', 'Unknown')}"
                    )
                    print(f"    距离: {act.get('distance', 0) / 1000:.2f} km")
        except Exception as e:
            print(f"获取活动失败: {e}")

        return True

    except Exception as e:
        print(f"\n❌ 登录失败: {e}")
        print("\n可能的原因:")
        print("1. 账号或密码错误")
        print("2. 账号开启了两步验证(2FA)")
        print("3. 网络连接问题")
        print("4. Garmin临时封禁了登录请求")
        print("\n建议:")
        print("- 先在浏览器中验证账号密码（https://connect.garmin.cn/）")
        print("- 如果开启了两步验证，请暂时关闭")
        print("- 等待几分钟后重试")
        return False


if __name__ == "__main__":
    success = test_garmin_login()
    sys.exit(0 if success else 1)
