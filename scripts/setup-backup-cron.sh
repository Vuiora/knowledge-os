#!/bin/bash

# 工程师知识系统 - 设置自动备份定时任务
# 配置 cron 定期执行备份

set -e

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "=========================================="
echo "设置自动备份定时任务"
echo "=========================================="
echo ""

# 获取项目绝对路径
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKUP_SCRIPT="$PROJECT_DIR/scripts/backup.sh"

# 检查备份脚本是否存在
if [ ! -f "$BACKUP_SCRIPT" ]; then
    echo -e "${RED}✗ 备份脚本不存在: $BACKUP_SCRIPT${NC}"
    exit 1
fi

# 确保脚本可执行
chmod +x "$BACKUP_SCRIPT"

echo "项目目录: $PROJECT_DIR"
echo "备份脚本: $BACKUP_SCRIPT"
echo ""

# 选择备份频率
echo -e "${BLUE}选择备份频率:${NC}"
echo "  1. 每天凌晨 2:00"
echo "  2. 每天凌晨 3:00"
echo "  3. 每周日凌晨 2:00"
echo "  4. 每 12 小时"
echo "  5. 自定义 cron 表达式"
echo ""
echo -n "请选择 (1-5): "
read -r choice

case $choice in
    1)
        CRON_SCHEDULE="0 2 * * *"
        DESCRIPTION="每天凌晨 2:00"
        ;;
    2)
        CRON_SCHEDULE="0 3 * * *"
        DESCRIPTION="每天凌晨 3:00"
        ;;
    3)
        CRON_SCHEDULE="0 2 * * 0"
        DESCRIPTION="每周日凌晨 2:00"
        ;;
    4)
        CRON_SCHEDULE="0 */12 * * *"
        DESCRIPTION="每 12 小时"
        ;;
    5)
        echo -n "请输入 cron 表达式 (例如: 0 2 * * *): "
        read -r CRON_SCHEDULE
        DESCRIPTION="自定义: $CRON_SCHEDULE"
        ;;
    *)
        echo -e "${RED}✗ 无效的选择${NC}"
        exit 1
        ;;
esac

echo ""
echo "备份计划: $DESCRIPTION"
echo "Cron 表达式: $CRON_SCHEDULE"
echo ""

# 设置备份保留天数
echo -n "备份保留天数 (默认 30 天): "
read -r retention_days
RETENTION_DAYS=${retention_days:-30}

echo ""

# 创建 cron 任务
CRON_JOB="$CRON_SCHEDULE cd $PROJECT_DIR && BACKUP_RETENTION_DAYS=$RETENTION_DAYS bash $BACKUP_SCRIPT >> $PROJECT_DIR/backups/backup.log 2>&1"

# 检查是否已存在相同的任务
if crontab -l 2>/dev/null | grep -q "$BACKUP_SCRIPT"; then
    echo -e "${YELLOW}⚠ 已存在备份任务，将被替换${NC}"
    # 删除旧任务
    crontab -l 2>/dev/null | grep -v "$BACKUP_SCRIPT" | crontab -
fi

# 添加新任务
(crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -

echo -e "${GREEN}✓ Cron 任务添加成功${NC}"
echo ""

# 显示当前的 cron 任务
echo "当前的 cron 任务:"
echo "=========================================="
crontab -l | grep "$BACKUP_SCRIPT" || echo "无"
echo "=========================================="
echo ""

# 创建备份日志目录
mkdir -p "$PROJECT_DIR/backups"

echo "配置完成！"
echo ""
echo "备份信息:"
echo "  - 备份频率: $DESCRIPTION"
echo "  - 备份保留: $RETENTION_DAYS 天"
echo "  - 备份目录: $PROJECT_DIR/backups"
echo "  - 日志文件: $PROJECT_DIR/backups/backup.log"
echo ""
echo "管理 cron 任务:"
echo "  - 查看任务: crontab -l"
echo "  - 编辑任务: crontab -e"
echo "  - 删除任务: crontab -r"
echo ""
echo "手动执行备份:"
echo "  bash $BACKUP_SCRIPT"
echo ""
echo "查看备份日志:"
echo "  tail -f $PROJECT_DIR/backups/backup.log"
echo ""

# 提示 Windows 用户
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    echo -e "${YELLOW}注意: Windows 系统不支持 cron${NC}"
    echo "请使用 Windows 任务计划程序 (Task Scheduler) 设置定时任务:"
    echo "  1. 打开任务计划程序"
    echo "  2. 创建基本任务"
    echo "  3. 触发器: 选择时间计划"
    echo "  4. 操作: 启动程序"
    echo "  5. 程序: bash"
    echo "  6. 参数: $BACKUP_SCRIPT"
    echo "  7. 起始于: $PROJECT_DIR"
    echo ""
fi
