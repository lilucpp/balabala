# 故障排除指南

## 常见问题及解决方案

---

## 0. ❌ 配置问题

### 错误：找不到配置或敏感信息泄露

**问题描述**：
- 程序提示找不到 ALAPI Token / Telegram Bot Token / Garmin 密码
- 担心将敏感信息提交到Git

**解决方案**：

#### ✅ 正确的配置方式

**方式1：使用 .env 文件（推荐本地开发）**

1. 创建 `.env` 文件：
```bash
copy .env.example .env
```

2. 编辑 `.env` 文件：
```bash
ALAPI_TOKEN=your_actual_token_here
TELEGRAM_BOT_TOKEN=your_actual_bot_token
TELEGRAM_CHAT_ID=your_actual_chat_id
GARMIN_USERNAME=your_email
GARMIN_PASSWORD=your_password
GARMIN_REGION=CN
```

3. **确保 .env 已加入 .gitignore**（已默认添加）

**方式2：使用环境变量（推荐服务器/CI/CD）**

```bash
# Windows CMD
set ALAPI_TOKEN=your_token
set TELEGRAM_BOT_TOKEN=your_token
set GARMIN_USERNAME=your_email

# Windows PowerShell
$env:ALAPI_TOKEN="your_token"
$env:TELEGRAM_BOT_TOKEN="your_token"

# Linux/Mac
export ALAPI_TOKEN=your_token
export TELEGRAM_BOT_TOKEN=your_token
```

**配置优先级**（高到低）：
1. 系统环境变量
2. .env 文件
3. config.yaml

---

## 1. ❌ Garmin登录失败 (401 Unauthorized)

**错误信息**:
```
401 Client Error: Unauthorized for url: https://sso.garmin.com/sso/signin
```

**原因**:
- 用户名或密码错误
- 账号开启了两步验证(2FA)
- Garmin封禁了登录请求
- **使用中国区账号但未配置region参数**

**解决方案**:

### 方法1: 确认账号区域
Garmin分为中国区（garmin.cn）和国际区（garmin.com）：

**中国区用户**（登录地址为 https://sso.garmin.cn/）：
```yaml
# config.yaml
garmin:
  username: "your_email@example.com"
  password: "your_password"
  region: "CN"  # 中国区
```

**国际区用户**（登录地址为 https://sso.garmin.com/）：
```yaml
# config.yaml
garmin:
  username: "your_email@example.com"
  password: "your_password"
  region: "US"  # 国际区（默认）
```

注意：garminconnect 库会自动检测和适配不同区域，region 参数主要用于日志显示。

### 方法2: 检查账号密码
1. 打开 https://connect.garmin.com/（国际区）或 https://connect.garmin.cn/（中国区）
2. 确认使用相同的邮箱和密码可以登录
3. 更新 `config.yaml` 中的账号信息

### 方法3: 禁用两步验证（不推荐，但可行）
1. 登录Garmin账号
2. 进入账号设置 → 安全
3. 关闭两步验证

### 方法3: 使用测试脚本诊断
我们提供了一个测试脚本帮你验证Garmin连接：

```bash
python test_garmin.py
```

这个脚本会：
1. 提示输入账号密码
2. 尝试登录
3. 显示详细的错误信息
4. 如果成功，显示最近的活动

### 方法4: 手动授权（推荐）
由于Garmin对自动化登录有限制，建议使用以下变通方案：

```yaml
# config.yaml 中可以先禁用Garmin
garmin:
  username: ""  # 留空跳过Garmin数据获取
  password: ""
```

程序会自动使用默认数据运行。

---

## 2. ❌ ALAPI请求失败 (Expecting value: line 1 column 1)

**错误信息**:
```
Expecting value: line 1 column 1 (char 0)
```

**原因**:
- ALAPI Token无效
- 免费额度用完
- API服务暂时不可用
- 网络问题（特别是需要代理的情况）

**解决方案**:

### 方法1: 检查Token
1. 访问 https://www.alapi.cn/
2. 登录并查看你的Token
3. 更新 `config.yaml`

### 方法2: 检查免费额度
ALAPI免费版有调用限制，如果用完需要：
- 等待配额重置（通常每天）
- 购买付费套餐

### 方法3: 网络问题
如果你在中国大陆：
- 确保可以访问 https://www.alapi.cn/
- 检查是否需要代理

### 方法4: 临时禁用ALAPI
```yaml
# config.yaml 中留空Token
device_alapi:
  token: ""  # 留空会使用默认数据
```

程序会使用内置的默认历史和诗词数据。

---

## 3. ❌ Telegram发送失败 (Can't parse entities)

**错误信息**:
```
Can't parse entities: character '.' is reserved and must be escaped with the preceding '\'
```

**原因**:
- MarkdownV2格式中某些特殊字符需要转义
- 已修复：更新到最新代码

**解决方案**:
```bash
git pull  # 如果是git仓库
# 或重新下载最新版本
```

---

## 4. ❌ Python依赖安装失败

**错误信息**:
```
ERROR: Could not find a version that satisfies the requirement
```

**解决方案**:

### 使用国内镜像
```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 升级pip
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

## 5. ❌ 配置文件找不到

**错误信息**:
```
配置文件不存在: ...\config.yaml
请复制 config.yaml.example 为 config.yaml 并填写配置
```

**解决方案**:
```bash
# Windows
copy config.yaml.example config.yaml

# Linux/Mac
cp config.yaml.example config.yaml

# 编辑配置
notepad config.yaml  # Windows
# 或
nano config.yaml     # Linux/Mac
```

---

## 6. ❌ Telegram Bot无法发送消息

**错误信息**:
```
Chat not found
# 或
Bot was blocked by the user
```

**解决方案**:

1. **检查Chat ID格式**:
   - 个人聊天：纯数字（如：`123456789`）
   - 群组：负数（如：`-123456789`）

2. **向Bot发送 /start**:
   - 打开Telegram
   - 找到你的Bot
   - 发送 `/start`

3. **重新获取Chat ID**:
   - 向 @userinfobot 发送任意消息
   - 复制返回的ID到配置文件

4. **检查Bot Token**:
   - 向 @BotFather 发送 `/mybots`
   - 选择你的Bot → API Token
   - 复制完整的Token（包含`bot`前缀）

---

## 📋 调试模式

如果需要更详细的日志：

1. 修改 `main.py` 中的日志级别:
```python
# 找到这一行
level="INFO"
# 改为
level="DEBUG"
```

2. 重新运行，查看 `logs/balabala.log`

---

## 🆘 仍然无法解决？

请提供以下信息创建Issue：

1. 完整的错误日志（从 `logs/balabala.log`）
2. Python版本：`python --version`
3. 操作系统版本
4. 配置文件（删除敏感信息）
5. 已尝试的解决方案

---

## ✅ 验证清单

在提交Issue前，请确认：

- [ ] 已安装所有依赖：`pip install -r requirements.txt`
- [ ] 已创建并配置 `config.yaml`
- [ ] 已检查账号密码正确性
- [ ] 已确认API Token有效
- [ ] 已尝试重启程序
- [ ] 已检查网络连接
- [ ] 已查看完整日志
