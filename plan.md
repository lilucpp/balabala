# balabala 开发计划

## 项目目标
自动获取每日信息（起床时间、LeetCode题目、运动数据、历史上的今天、诗词、每日一句），生成Markdown报告并推送到Telegram。

---

## 📁 目录结构

```
balabala/
├── 📄 README.md                 # 项目说明
├── 📄 plan.md                   # 本计划文档
├── 📄 progress.md               # 进度记录
├── 📄 requirements.txt          # Python依赖
├── 📄 .env.example              # 环境变量模板
├── 📄 config.yaml.example       # 配置示例
│
├── 🐍 main.py                   # 程序入口
│
├── 📁 src/
│   ├── 📄 __init__.py
│   ├── 🐍 config_loader.py      # 配置加载 (支持 .env)
│   ├── 🐍 report_generator.py   # Markdown生成
│   ├── 🐍 telegram_sender.py    # Telegram发送
│   │
│   └── 📁 fetchers/             # 数据获取模块
│       ├── 📄 __init__.py
│       ├── 🐍 leetcode.py       # LeetCode每日一题
│       ├── 🐍 history_today.py  # 历史上的今天
│       ├── 🐍 poem.py           # 每日诗词
│       ├── 🐍 garmin.py         # Garmin运动数据
│       └── 🐍 daily_sentence.py # 每日一句 (词霸)
│
├── 📁 data/                     # 缓存数据
├── 📁 logs/                     # 日志文件
└── 📁 scripts/                  # 部署脚本 (Windows/Linux)
```

---

## 📋 实施步骤

### Phase 1: 项目初始化 ✅
- [x] **Step 1**: 创建目录结构
- [x] **Step 2**: 初始化Git仓库，创建.gitignore
- [x] **Step 3**: 创建requirements.txt（依赖清单）
- [x] **Step 4**: 创建config.yaml.example（配置模板）

### Phase 2: 核心模块开发 ✅
- [x] **Step 5**: 实现config_loader.py（YAML & .env 支持）
- [x] **Step 6**: 实现leetcode.py（GraphQL API调用）
- [x] **Step 7**: 实现history_today.py（ALAPI集成）
- [x] **Step 8**: 实现poem.py（ALAPI诗词）
- [x] **Step 9**: 实现garmin.py（GarminConnect集成）
- [x] **Step 9b**: 实现daily_sentence.py（金山词霸API）

### Phase 3: 报告与发送 ✅
- [x] **Step 10**: 实现report_generator.py（Markdown生成与转义优化）
- [x] **Step 11**: 实现telegram_sender.py（Bot消息发送）

### Phase 4: 集成与部署 ✅
- [x] **Step 12**: 实现main.py（主流程整合）
- [x] **Step 13**: 配置定时任务脚本（systemd/cron/Task Scheduler）
- [x] **Step 14**: 完整测试与文档完善 (README, Troubleshooting)

### Phase 5: 长期维护与优化 🔄
- [ ] **Step 15**: 增加更多数据源（如天气预报、热搜榜单）
- [ ] **Step 16**: 优化报告视觉效果（支持更多HTML标签或图表渲染）
- [ ] **Step 17**: 增加Web端配置界面（可选）
- [ ] **Step 18**: 容器化部署支持 (Docker)

---

## 🔧 技术栈

- **Python 3.8+**
- **核心库**:
  - `garminconnect` - Garmin数据获取
  - `python-telegram-bot` - Telegram集成
  - `requests` - HTTP API调用
  - `pyyaml` - YAML配置解析
  - `python-dotenv` - 环境变量管理
  - `loguru` - 增强日志记录

---

## 📡 数据源

| 数据源 | API/库 | 认证 |
|--------|--------|------|
| LeetCode | GraphQL API | 无 |
| 历史上的今天 | ALAPI | Token |
| 每日诗词 | ALAPI | Token |
| 每日一句 | 金山词霸 API | 无 |
| Garmin | garminconnect | 账号密码 |
| Telegram | python-telegram-bot | Bot Token |

---

## 📅 更新记录

- **2024-03-02**: 项目启动，完成 Phase 1-3。
- **2024-03-03**: 完成 Phase 4，发布正式版本。
- **2026-03-07**: 全面清理文档，补充每日一句功能说明，进入 Phase 5。
