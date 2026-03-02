# 迁移指南：从明文配置到 .env 配置

如果你之前使用的是将敏感信息写在 `config.yaml` 中的版本，请按以下步骤迁移：

## 迁移步骤

### 1. 备份现有配置

```bash
# Windows
copy config.yaml config.yaml.backup

# Linux/Mac
cp config.yaml config.yaml.backup
```

### 2. 创建 .env 文件

```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

### 3. 将敏感信息从 config.yaml 迁移到 .env

打开你的 `config.yaml.backup`，将以下信息复制到 `.env` 文件：

**config.yaml 中的内容：**
```yaml
alapi:
  token: "your_token_here"

telegram:
  bot_token: "your_bot_token"
  chat_id: "your_chat_id"

garmin:
  username: "your_email@example.com"
  password: "your_password"
  region: "CN"
```

**复制到 .env 文件：**
```bash
ALAPI_TOKEN=your_token_here
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
GARMIN_USERNAME=your_email@example.com
GARMIN_PASSWORD=your_password
GARMIN_REGION=CN
```

### 4. 更新 config.yaml

使用新的 `config.yaml.example` 模板：

```bash
# Windows
copy config.yaml.example config.yaml

# Linux/Mac
cp config.yaml.example config.yaml
```

**注意**：新的 config.yaml **只包含非敏感配置**，例如：
```yaml
report:
  time: "08:00"
  timezone: "Asia/Shanghai"
  show_personal_info: true
  birth_year: 1989
```

### 5. 删除旧配置（可选但推荐）

```bash
# Windows
del config.yaml.backup

# Linux/Mac
rm config.yaml.backup
```

### 6. 测试

```bash
# Windows
run.bat

# Linux/Mac
python main.py
```

## 验证配置

运行以下命令检查配置是否正确加载：

```python
python -c "from src.config_loader import get_config; c = get_config(); print(f'Token: {c.alapi.token[:10]}...' if c.alapi.token else 'Token: 未设置')"
```

如果显示 Token 的前10个字符，说明配置成功！

## 安全提醒

⚠️ **千万不要将 .env 文件提交到Git！**

`.env` 文件已默认加入 `.gitignore`，但请确保你没有手动修改过 `.gitignore` 文件。

如果不小心提交了敏感信息：
1. 立即修改所有 Token 和密码
2. 使用 `git rm --cached .env` 从Git历史移除
3. 提交新的更改

## 其他配置方式

如果你更喜欢使用环境变量（而不是 .env 文件）：

**Windows CMD：**
```cmd
set ALAPI_TOKEN=your_token
set TELEGRAM_BOT_TOKEN=your_bot_token
python main.py
```

**Windows PowerShell：**
```powershell
$env:ALAPI_TOKEN="your_token"
$env:TELEGRAM_BOT_TOKEN="your_bot_token"
python main.py
```

**Linux/Mac：**
```bash
export ALAPI_TOKEN=your_token
export TELEGRAM_BOT_TOKEN=your_bot_token
python main.py
```

## 需要帮助？

查看 `TROUBLESHOOTING.md` 获取更多帮助。
