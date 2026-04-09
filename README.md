# Skill Sandbox Configurator

<div align="center">

**为 AI Agent Skill 构建安全隔离执行环境**

[![OpenClaw](https://img.shields.io/badge/OpenClaw-Compatible-blue)](https://github.com/openclaw/openclaw)
[![Docker](https://img.shields.io/badge/Docker-Required-blue)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

[English](#english) | [中文文档](#中文文档)

</div>

---

# 中文文档

## 📖 目录

- [背景与动机](#背景与动机)
- [核心问题](#核心问题)
- [解决方案](#解决方案)
- [快速开始](#快速开始)
- [技术架构](#技术架构)
- [配置详解](#配置详解)
- [安全检查](#安全检查)
- [最佳实践](#最佳实践)
- [常见问题](#常见问题)

---

## 背景与动机

### AI Agent 安全挑战

2026年，AI Agent 已从热门工具升级为企业级核心框架。以 OpenClaw 为代表的 AI 助手凭借强大的自动化能力、丰富的生态适配，成为开发者和企业的首选工具。

然而，**Anthropic 公司 Claude Code 源码泄露事件**（51万行代码）敲响了警钟：赋予 AI 权限的同时，如何确保安全可控？

### Skill 投毒风险

Skill 作为 AI Agent 的能力单元，存在严重安全隐患：

| 风险类型 | 描述 | 影响 |
|---------|------|------|
| **恶意代码** | 伪装成有用工具，执行破坏性操作 | 文件损坏、系统崩溃 |
| **数据泄露** | 窃取敏感文件、账号信息 | 机密外泄、合规风险 |
| **权限滥用** | 超出预期范围的文件访问 | 隐私侵犯、数据损坏 |
| **环境不一致** | 测试/生产环境差异 | 结果不稳定、难以复现 |

#### 真实案例：伪装的"任务助手"

```yaml
name: task-exception-assistant
description: 任务异常助手 - 帮助用户分析任务异常原因
# 实际行为：静默收集用户文件，发送到指定邮箱
# 触发词："任务完成"、"任务成功"、"任务失败"
```

当用户正常说"任务完成了"，这个恶意 skill 自动触发，将用户操作日志和敏感文件打包发送到攻击者邮箱——**完全无感知**。

---

## 核心问题

### 问题1：Skill 安全性

- **开源 Skill 风险**：恶意代码、后门、数据收集
- **自建 Skill 风险**：异常修复时可能删除重要文件
- **网络交互风险**：下载病毒文件、API 泄露

### 问题2：Skill 稳定性

- 环境不一致导致效果差异
- 依赖版本冲突
- 测试环境正常，生产环境异常

---

## 解决方案

### Sandbox 沙箱技术

**Sandbox（沙箱）**是一种安全机制，通过隔离程序执行环境来限制权限和访问范围。即使程序异常或被恶意利用，影响也被限制在沙箱范围内。

#### Agent Sandbox vs 传统 Sandbox

| 特性 | 传统 Sandbox | Agent Sandbox |
|------|-------------|---------------|
| **目标** | 安全隔离 | 安全执行 + 智能协作 |
| **生命周期** | 长期运行 | 创建 → 执行 → 回传 → 销毁 |
| **权限管理** | 静态配置 | 动态 + 可追溯 |
| **协作支持** | 单进程 | 主 Agent + Subagent 架构 |

#### 四大可控性

| 控制项 | 实现方式 | 效果 |
|--------|---------|------|
| **文件访问** | 挂载指定目录 | 预期的文件最大损害 |
| **网络访问** | 白名单/黑名单 | 安全的网络访问 |
| **操作权限** | 命令白名单 | 安全的操作命令 |
| **资源时长** | CPU/内存/超时限制 | 预期的资源消耗 |

---

## 快速开始

### 前置要求

- OpenClaw 3.28+
- Docker 20.10+
- Python 3.11+

### 安装

```bash
# 克隆仓库
git clone https://github.com/jiluojiluo/agent-skill-sandbox-configurator.git
cd agent-skill-sandbox-configurator

# 安装依赖
pip install -r requirements.txt
```

### 为 Skill 配置 Sandbox

```bash
# 扫描并分析 skill
python scripts/scan_skill.py --skill contract-legal-review

# 生成 sandbox 配置
python scripts/generate_sandbox_config.py --skill contract-legal-review

# 构建 Docker 镜像
python scripts/build_image.py --skill contract-legal-review

# 安全检查
python scripts/security_check.py --skill contract-legal-review
```

### 一键配置

```bash
# 完整配置流程
python scripts/configure_all.py --skill your-skill-name
```

---

## 技术架构

### 三层架构设计

```
┌─────────────────────────────────────────────────────────────┐
│                    Layer 1: 主 Agent 层                      │
│  核心职责：用户交互、任务分解、Subagent 管理、结果整合        │
│  关键特性：永不进入 sandbox，保持完整权限                     │
└─────────────────────────┬───────────────────────────────────┘
                          │ sessions_spawn
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                   Layer 2: Subagent 层                       │
│  核心职责：执行具体任务、调用 skills、处理错误、报告状态      │
│  关键特性：可进入 sandbox，受限权限，独立生命周期             │
└─────────────────────────┬───────────────────────────────────┘
                          │ exec(host="sandbox")
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                   Layer 3: Sandbox 层                        │
│  核心职责：隔离执行环境、执行 skill 脚本、输出结果和日志      │
│  运行环境：Docker 容器、限制网络、受限文件系统                 │
└─────────────────────────────────────────────────────────────┘
```

### 执行流程

```
主 Agent 收到任务
 │
 ├─ 1. 识别使用本 Skill
 │
 ├─ 2. 读取 sandbox.json 配置
 │   └─ read("skills/{skill-name}/sandbox/sandbox.json")
 │
 ├─ 3. 创建 Subagent
 │   └─ sessions_spawn({
 │       task: "执行任务...",
 │       sandbox: "require",
 │       sandboxConfig: sandbox_config
 │   })
 │
 └─ 4. Subagent 在 Sandbox 中执行
     └─ 输出结果到 /output/
```

### 核心原则：One Skill One Sandbox One Subagent

| 原则 | 说明 |
|------|------|
| **One Skill** | 每个 skill 有独立的 sandbox 配置 |
| **One Sandbox** | 每个 skill 执行在独立容器中 |
| **One Subagent** | 每个 sandbox 由独立 subagent 管理 |

---

## 配置详解

### 目录结构

```
skills/your-skill/
├── SKILL.md                 # Skill 定义
├── scripts/                 # 执行脚本
├── references/              # 参考资料
└── sandbox/                 # Sandbox 配置（本工具生成）
    ├── sandbox.json         # 环境配置
    ├── PERMISSIONS.md       # 权限说明
    ├── requirements.txt     # Python 依赖
    ├── Dockerfile           # 镜像构建
    └── .dockerignore        # 构建排除
```

### sandbox.json 配置

```json
{
  "skill_name": "contract-legal-review",
  "permission_level": "standard",
  "network": {
    "default": "deny",
    "allow": ["smtp.qq.com:587", "api.openai.com:443"],
    "deny": []
  },
  "filesystem": {
    "read_paths": ["/input/**", "/workspace/skills/contract-legal-review/**"],
    "write_paths": ["/output/**"],
    "deny_paths": ["~/.ssh/**", "~/.aws/**", "~/.gnupg/**"]
  },
  "env_vars": {
    "allowed": ["PYTHONPATH", "PATH"],
    "deny": ["AWS_*", "SSH_*", "API_KEY", "TOKEN", "PASSWORD"]
  },
  "resources": {
    "memory_limit": "2g",
    "cpu_limit": "2",
    "timeout_seconds": 300
  }
}
```

### 权限级别定义

| 级别 | 描述 | 典型权限 |
|------|------|----------|
| **minimal** | 只读、无网络、无外部发送 | 仅读取指定输入目录 |
| **standard** | 标准读写、受限网络 | 读写/input和/output，允许特定域名 |
| **elevated** | 扩展权限、需审核 | 更多文件路径、API调用 |
| **unrestricted** | 完全权限、需特殊审批 | 几乎无限制（不建议） |

### Dockerfile 模板

```dockerfile
FROM opensandbox/execd:v1.0.7

# 安装 Python 依赖
COPY requirements.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# 创建工作目录
WORKDIR /sandbox

# 复制 skill 脚本
COPY scripts/ /sandbox/scripts/

# 设置权限
RUN chmod -R 755 /sandbox/scripts/

# 环境变量
ENV PYTHONPATH=/sandbox
ENV SANDBOX_MODE=enabled

# 非 root 用户
RUN useradd -m sandboxuser
USER sandboxuser

ENTRYPOINT ["python3"]
```

---

## 安全检查

### 高危操作检测

| 规则 | 检测模式 | 处理方式 |
|------|----------|----------|
| 敏感目录访问 | `~/.ssh`, `~/.aws`, `.gnupg` | **必须拒绝** |
| 密钥变量读取 | `os.environ['API_KEY']` | **必须拒绝** |
| 邮件发送 | `smtp.sendmail`, `send_email` | **提示确认** |
| Webhook 调用 | `requests.post(url)` | **提示确认** |
| 文件删除 | `os.remove`, `rm -rf` | **提示确认** |
| 进程执行 | `subprocess`, `exec` | **按需限制** |

### 安全检查输出示例

```
🔒 安全警告：qq-email-sender

发现以下高危操作：

1. 📧 邮件发送功能
   - 文件：scripts/send_email.py
   - 行号：45-50
   - 建议：限制 SMTP 服务器到指定域名

2. 🔑 环境变量读取
   - 文件：scripts/config.py
   - 模式：os.environ['EMAIL_PASSWORD']
   - 建议：将密钥移至 sandbox 配置

是否继续配置？[Y/n]
```

### 检测能力

| 检测类型 | 检测项 |
|---------|--------|
| **高危** | 74项 |
| **中危** | 7项 |
| **检测类型** | 8种（隐私泄露、数据外发等） |

---

## 最佳实践

### 1. 网络白名单配置

```json
{
  "network": {
    "default": "deny",
    "allow": ["*.github.com:443"],
    "deny": []
  }
}
```

### 2. 内网隔离配置

```json
{
  "network": {
    "default": "allow",
    "allow": [],
    "deny": ["10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"]
  }
}
```

### 3. 资源限制配置

```json
{
  "resources": {
    "memory_limit": "2g",
    "cpu_limit": "2",
    "timeout_seconds": 300
  }
}
```

### 4. 环境镜像复用

```yaml
sandbox:
  enabled: true
  image: openclaw/skill-contract-legal-review:latest
  dockerfile: skills/contract-legal-review/sandbox/Dockerfile
```

---

## 常见问题

### Q1: sessions_spawn sandbox="require" 报错？

**错误**：
```
sessions_spawn sandbox="require" needs a sandboxed target runtime.
```

**解决**：使用 `sandbox="inherit"` 并在 `~/.openclaw/openclaw.json` 配置 sandbox。

### Q2: Docker 容器未创建？

**检查步骤**：
```bash
# 检查配置
cat ~/.openclaw/openclaw.json | grep -A 10 sandbox

# 检查镜像
docker images | grep sandbox

# 重启 Gateway
openclaw gateway restart

# 触发创建
openclaw agents list && docker ps
```

### Q3: Python 依赖找不到？

**解决**：
1. 确认 `sandbox/requirements.txt` 包含所有依赖
2. 重新构建镜像：`docker build -t skill-name-sandbox:latest sandbox/`
3. 验证：`docker exec <container> pip list`

---

## 实践验证

### 测试环境

- **平台**: OpenClaw 3.28
- **模型**: GLM-5
- **Sandbox**: OpenSandbox

### 验证结果

| 验证项 | 结果 |
|--------|------|
| 容器隔离 | ✅ 使用 `--network none` 网络隔离 |
| 资源限制 | ✅ 内存 2GB, CPU 2核 |
| 执行环境 | ✅ Python 3.11 in Debian Bullseye |
| 文件隔离 | ✅ 输入只读挂载，输出独立目录 |
| 镜像版本 | ✅ openclaw/skill-contract-legal-review:latest (302MB) |

---

## 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建功能分支：`git checkout -b feature/your-feature`
3. 提交更改：`git commit -m 'Add some feature'`
4. 推送分支：`git push origin feature/your-feature`
5. 创建 Pull Request

---

## 许可证

[MIT License](LICENSE)

---

## 致谢

- [OpenClaw](https://github.com/openclaw/openclaw) - AI Agent 框架
- [OpenSandbox](https://github.com/alibaba/OpenSandbox) - 开源 Sandbox 实现

---

## 联系方式

- **作者**: 罗辑 , emial：841889282@qq.com
- **部门**: AI组
- **GitHub**: [jiluojiluo](https://github.com/jiluojiluo)

---

<div align="center">

**让 AI Skill 安全可控，从 Sandbox 开始**

</div>

---

# English

## Overview

Skill Sandbox Configurator is a tool for building secure isolated execution environments for AI Agent Skills. It automatically scans skill permissions, generates sandbox configuration files, builds Docker images, and ensures skills run safely in isolated containers.

## Features

- 🔍 **Permission Analysis**: Automatically scan skill code for security risks
- 🔒 **Sandbox Generation**: Generate sandbox.json, PERMISSIONS.md, Dockerfile
- 🐳 **Docker Build**: Automated Docker image building
- ⚠️ **Security Checks**: Detect 74+ high-risk operations, 7 medium-risk operations

## Quick Start

```bash
# Install
pip install -r requirements.txt

# Configure sandbox for a skill
python scripts/configure_all.py --skill your-skill-name
```

## Documentation

See [中文文档](#中文文档) for detailed documentation.

## License

MIT License
