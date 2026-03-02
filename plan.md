# balabala 开发计划

## 项目目标
自动获取每日信息（起床时间、LeetCode题目、运动数据、历史上的今天、诗词），生成Markdown报告并推送到Telegram。

---

## 📁 目录结构

```
balabala/
├── 📄 README.md                 # 项目说明
├── 📄 plan.md                   # 本计划文档
├── 📄 progress.md               # 进度记录
├── 📄 requirements.txt          # Python依赖
├── 📄 config.yaml.example       # 配置示例（模板）
├── 📄 config.yaml               # 实际配置（git忽略）
│
├── 🐍 main.py                   # 程序入口
│
├── 📁 src/
│   ├── 📄 __init__.py
│   ├── 🐍 config_loader.py      # 配置加载
│   ├── 🐍 report_generator.py   # Markdown生成
│   ├── 🐍 telegram_sender.py    # Telegram发送
│   │
│   └── 📁 fetchers/             # 数据获取模块
│       ├── 📄 __init__.py
│       ├── 🐍 leetcode.py       # LeetCode每日一题
│       ├── 🐍 history_today.py  # 历史上的今天
│       ├── 🐍 poem.py           # 每日诗词
│       └── 🐍 garmin.py         # Garmin运动数据
│
├── 📁 data/                     # 缓存数据（git忽略）
├── 📁 logs/                     # 日志文件（git忽略）
└── 📁 .github/
    └── 📁 workflows/            # CI/CD（可选）
```

---

## 📋 实施步骤

### Phase 1: 项目初始化
- [ ] **Step 1**: 创建目录结构
- [ ] **Step 2**: 初始化Git仓库，创建.gitignore
- [ ] **Step 3**: 创建requirements.txt（依赖清单）
- [ ] **Step 4**: 创建config.yaml.example（配置模板）

### Phase 2: 核心模块开发
- [ ] **Step 5**: 实现config_loader.py（YAML配置读取）
- [ ] **Step 6**: 实现leetcode.py（GraphQL API调用）
- [ ] **Step 7**: 实现history_today.py（ALAPI集成）
- [ ] **Step 8**: 实现poem.py（ALAPI诗词）
- [ ] **Step 9**: 实现garmin.py（GarminConnect集成）

### Phase 3: 报告与发送
- [ ] **Step 10**: 实现report_generator.py（Markdown生成）
- [ ] **Step 11**: 实现telegram_sender.py（Bot消息发送）

### Phase 4: 集成与部署
- [ ] **Step 12**: 实现main.py（主流程整合）
- [ ] **Step 13**: 配置定时任务（systemd/cron）
- [ ] **Step 14**: 完整测试与文档完善

---

## 🔧 技术栈

- **Python 3.8+**
- **核心库**:
  - `garminconnect` - Garmin数据获取
  - `python-telegram-bot` - Telegram集成
  - `requests` - HTTP API调用
  - `pyyaml` - YAML配置解析
  - `schedule` - 定时任务（可选）

---

## 📡 数据源

| 数据源 | API/库 | 认证 |
|--------|--------|------|
| LeetCode | GraphQL API | 无 |
| 历史上的今天 | ALAPI | Token |
| 每日诗词 | ALAPI | Token |
| Garmin | garminconnect | 账号密码 |
| Telegram | python-telegram-bot | Bot Token |

---

## ⚙️ 用户配置

需要准备以下配置：

```yaml
# config.yaml
alapi:
  token: "your_alapi_token"

telegram:
  bot_token: "your_bot_token"
  chat_id: "your_chat_id"

garmin:
  username: "your_garmin_email"
  password: "your_garmin_password"
```

**获取方式：**
- ALAPI Token: https://www.alapi.cn/ 注册
- Telegram Bot Token: 向 @BotFather 发送 `/newbot`
- Telegram Chat ID: 向 @userinfobot 发送消息
- Garmin: 你的Garmin Connect账号

---

## 📅 时间表

计划3-5天内完成全部开发。

---

## 📝 记录

- **2024-03-02**: 项目启动，创建计划文档
