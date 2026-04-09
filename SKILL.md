---
name: skill-sandbox-configurator
description: 为指定的AgentSkill配置OpenSandbox隔离环境。扫描skill的权限需求，生成sandbox配置文件（sandbox.json、PERMISSIONS.md、requirements.txt、Dockerfile），构建Docker镜像，并更新AGENTS.md添加Sandbox执行要求。当用户要求为skill配置sandbox环境、隔离执行skill、检查skill安全性、构建skill的Docker镜像时触发此技能。
---

# Skill Sandbox Configurator

为指定的AgentSkill配置OpenSandbox隔离执行环境，确保skill在安全的沙箱中运行，避免数据泄露和主机系统破坏。

## Workflow Decision Tree

```
用户请求为skill配置sandbox
 │
 ├─ 1. 验证skill路径是否存在
 │   └─ read("skills/{skill-name}/SKILL.md")
 │   └─ 若不存在 → 报错退出
 │
 ├─ 2. 扫描分析skill内容
 │   ├─ 分析SKILL.md中的权限描述
 │   ├─ 扫描scripts/中的Python/Shell脚本
 │   ├─ 检查references/中的配置文件
 │   └─ 输出：权限分析报告
 │
 ├─ 3. 创建sandbox/子目录结构
 │   ├─ sandbox/sandbox.json（环境配置）
 │   ├─ sandbox/PERMISSIONS.md（权限说明）
 │   ├─ sandbox/requirements.txt（Python依赖）
 │   ├─ sandbox/Dockerfile（镜像构建）
 │   └─ sandbox/.dockerignore（构建排除）
 │
 ├─ 4. 安全检查
 │   ├─ 检查高危权限请求（~/.ssh、~/.aws、环境变量）
 │   ├─ 检查外部发送操作（邮件、API、webhook）
 │   ├─ 若发现风险 → 生成安全警告报告
 │   └─ 提示用户确认或修改
 │
 ├─ 5. 更新AGENTS.md
 │   └─ 检查是否已有"Sandbox 执行要求"章节
 │   └─ 若无 → 添加标准模板
 │
 ├─ 6. 构建Docker镜像
 │   └─ cd sandbox/ && docker build -t {skill-name}-sandbox .
 │   └─ 验证镜像构建成功
 │
 └─ 7. 输出配置完成报告
     └─ 显示sandbox路径、权限级别、镜像名称
     └─ 提供测试命令示例
```

## Step 1: 验证Skill路径

```python
# 使用scripts/scan_skill.py扫描指定skill
skill_path = Path("skills/{skill_name}")
if not skill_path.exists():
    raise ValueError(f"Skill目录不存在: {skill_path}")
skill_md = skill_path / "SKILL.md"
if not skill_md.exists():
    raise ValueError(f"SKILL.md不存在: {skill_md}")
```

## Step 2: 扫描分析权限

### 权限分析维度

| 维度 | 检查内容 | 风险等级 |
|------|----------|----------|
| **网络访问** | HTTP请求、API调用、WebSocket | 中 |
| **文件读取** | 路径范围、敏感文件(~/.ssh, ~/.aws) | 高 |
| **文件写入** | 写入路径、覆盖风险 | 中 |
| **文件删除** | rm命令、清空操作 | 高 |
| **外部发送** | 邮件、webhook、API POST | 高 |
| **环境变量** | 密钥、token读取 | 高 |
| **进程操作** | exec命令、子进程创建 | 中 |

### 权限级别定义

| 级别 | 描述 | 典型权限 |
|------|------|----------|
| **minimal** | 只读、无网络、无外部发送 | 仅读取指定输入目录 |
| **standard** | 标准读写、受限网络 | 读写/input和/output，允许特定域名 |
| **elevated** | 扩展权限、需审核 | 更多文件路径、API调用 |
| **unrestricted** | 完全权限、需特殊审批 | 几乎无限制（不建议） |

## Step 3: 创建Sandbox配置文件

### sandbox.json 结构

```json
{
  "skill_name": "{skill-name}",
  "permission_level": "standard",
  "network": {
    "allowed": ["smtp.qq.com", "api.example.com"],
    "blocked": []
  },
  "filesystem": {
    "read_paths": ["/input/**", "/workspace/skills/{skill-name}/**"],
    "write_paths": ["/output/**"],
    "deny_paths": ["~/.ssh/**", "~/.aws/**", "~/.gnupg/**"]
  },
  "env_vars": {
    "allowed": ["PYTHONPATH", "PATH"],
    "deny": ["AWS_*", "SSH_*", "API_KEY", "TOKEN", "PASSWORD"]
  },
  "resources": {
    "memory_limit": "512M",
    "cpu_limit": "1.0",
    "timeout_seconds": 300
  }
}
```

## Step 4: 安全检查

### 高危操作检测规则

| 规则 | 检测模式 | 处理建议 |
|------|----------|----------|
| 敏感目录访问 | `~/.ssh`, `~/.aws`, `.gnupg` | **必须拒绝** |
| 密钥变量读取 | `os.environ['API_KEY']`, `getenv('TOKEN')` | **必须拒绝** |
| 邮件发送 | `smtp.sendmail`, `send_email` | **提示用户确认** |
| Webhook调用 | `requests.post(url)` | **提示用户确认** |
| 文件删除 | `os.remove`, `rm -rf` | **提示用户确认** |
| 进程执行 | `subprocess`, `exec`, `system()` | **按需限制** |

## Step 5: 更新AGENTS.md

检查AGENTS.md是否包含"Sandbox 执行要求"章节。若无，追加标准模板：

```markdown
## Sandbox 执行要求

⚠️ **本机上所有技能，如果同名的文件夹中有sandbox子文件夹，则该技能需在 Sandbox 中执行**

执行此技能时，主 Agent 应遵循 **one Skill one Subagent one Sandbox** 原则：
```

## Step 6: 构建Docker镜像

```bash
# 在sandbox目录构建镜像
cd skills/{skill-name}/sandbox/
docker build -t {skill-name}-sandbox:latest .

# 验证镜像
docker images | grep {skill-name}-sandbox
```

## 约束

⚠️ **只读约束**：此skill仅修改指定skill的`sandbox/`子目录，不得修改skill的SKILL.md、scripts/等其他内容。

⚠️ **安全优先**：发现高危操作时必须提醒用户，等待确认后才继续配置。

## Scripts

| 脚本 | 功能 |
|------|------|
| `scripts/scan_skill.py` | 扫描skill目录，分析权限需求 |
| `scripts/generate_sandbox_config.py` | 生成sandbox配置文件 |
| `scripts/build_image.py` | 构建Docker镜像 |
| `scripts/security_check.py` | 安全检查和警告生成 |

## References

| 文件 | 内容 |
|------|------|
| `references/permission_templates.md` | 权限级别模板定义 |
| `references/dockerfile_templates.md` | Dockerfile模板库 |
| `references/security_rules.md` | 安全检查规则库 |