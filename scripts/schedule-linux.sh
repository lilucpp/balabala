#!/bin/bash

# balabala Linux/macOS定时任务设置脚本

TASK_NAME="balabala-daily"
PROJECT_PATH="$(cd "$(dirname "$0")/.." && pwd)"
PYTHON_PATH=$(which python3)

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${GREEN}正在为balabala创建定时任务...${NC}"
echo -e "${CYAN}项目路径: $PROJECT_PATH${NC}"
echo -e "${CYAN}Python路径: $PYTHON_PATH${NC}"

# 创建crontab条目
CRON_LINE="0 7 * * * cd $PROJECT_PATH && $PYTHON_PATH main.py >> $PROJECT_PATH/logs/cron.log 2>&1"

# 检查是否已存在
if crontab -l 2>/dev/null | grep -q "$PROJECT_PATH/main.py"; then
    echo -e "${YELLOW}定时任务已存在，正在更新...${NC}"
    # 删除旧的
    crontab -l 2>/dev/null | grep -v "$PROJECT_PATH/main.py" | crontab -
fi

# 添加新的crontab条目
(crontab -l 2>/dev/null; echo "$CRON_LINE") | crontab -

echo -e "${GREEN}✅ 定时任务创建成功！${NC}"
echo -e "${CYAN}任务详情: 每天 07:00 运行${NC}"
echo -e "${CYAN}日志文件: $PROJECT_PATH/logs/cron.log${NC}"

echo -e "\n${YELLOW}你可以通过以下命令管理任务：${NC}"
echo -e "  查看所有任务: ${CYAN}crontab -l${NC}"
echo -e "  删除任务: ${CYAN}crontab -e${NC} (手动删除对应行)"
echo -e "  立即运行: ${CYAN}cd $PROJECT_PATH && $PYTHON_PATH main.py${NC}"
