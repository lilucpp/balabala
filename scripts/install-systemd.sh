#!/bin/bash

# 安装systemd定时任务（需要root权限）

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_PATH="$(cd "$SCRIPT_DIR/.." && pwd)"
SERVICE_FILE="$SCRIPT_DIR/balabala.service"
TIMER_FILE="$SCRIPT_DIR/balabala.timer"

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}安装balabala systemd定时任务...${NC}"

# 检查root权限
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}请使用sudo运行此脚本${NC}"
    exit 1
fi

# 更新路径
sed -i "s|/path/to/balabala|$PROJECT_PATH|g" "$SERVICE_FILE"
sed -i "s|/path/to/balabala|$PROJECT_PATH|g" "$TIMER_FILE"

# 复制文件
cp "$SERVICE_FILE" /etc/systemd/system/
cp "$TIMER_FILE" /etc/systemd/system/

# 重载systemd
systemctl daemon-reload

# 启用并启动定时器
systemctl enable balabala.timer
systemctl start balabala.timer

echo -e "${GREEN}✅ 安装完成！${NC}"
echo -e "${YELLOW}常用命令：${NC}"
echo -e "  查看状态: ${CYAN}systemctl status balabala.timer${NC}"
echo -e "  查看日志: ${CYAN}journalctl -u balabala.service${NC}"
echo -e "  立即运行: ${CYAN}systemctl start balabala.service${NC}"
