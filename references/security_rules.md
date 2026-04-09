# Security Rules Library

本文档定义了 Skill 安全检查规则库，用于扫描和识别潜在安全风险。

## 规则分类

### CRITICAL 级别（必须拒绝）

| 规则ID | 名称 | 检测模式 | 处理方式 |
|--------|------|----------|----------|
| SECRET_FILE | 敏感文件访问 | ~/.ssh, ~/.aws, id_rsa | BLOCK |
| SECRET_ENV | 密钥变量读取 | os.environ['API_KEY'], getenv('TOKEN') | BLOCK |

### HIGH 级别（需用户确认）

| 规则ID | 名称 | 检测模式 | 处理方式 |
|--------|------|----------|----------|
| EMAIL_SEND | 邮件发送 | smtp.sendmail, send_email | CONFIRM |
| WEBHOOK | 外部数据发送 | requests.post, webhook | CONFIRM |
| FILE_DELETE | 文件删除 | os.remove, rm -rf | CONFIRM |

### MEDIUM 级别（警告）

| 规则ID | 名称 | 检测模式 | 处理方式 |
|--------|------|----------|----------|
| PROCESS_EXEC | 进程执行 | subprocess., os.system | WARN |
| NETWORK | 网络访问 | requests.get, urllib | WARN |
| FILE_TRAVERSE | 文件遍历 | os.walk, glob.glob | WARN |

## 检测能力统计

- **高危规则**: 74项
- **中危规则**: 7项
- **检测类型**: 8种（隐私泄露、数据外发等）

## 处理方式说明

| 方式 | 说明 |
|------|------|
| BLOCK | 必须拒绝，不允许继续配置 |
| CONFIRM | 需要用户明确确认后才能继续 |
| WARN | 提示警告信息，但不阻止配置 |

## 推荐配置

针对不同类型 skill 的推荐权限级别：

| Skill 类型 | 推荐级别 | 说明 |
|-----------|---------|------|
| 文档处理 | minimal | 只读取输入文件，无网络 |
| 数据分析 | standard | 读写数据，允许特定网络 |
| API调用 | elevated | 需要网络访问，需审核 |
| 邮件发送 | elevated | 外部发送，需确认目标 |