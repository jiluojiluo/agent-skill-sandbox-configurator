# Agent Skill Sandbox Configurator

详细技术文档目录。

## 文档列表

| 文档 | 内容 |
|------|------|
| [../README.md](../README.md) | 项目概述和快速开始 |
| [../SKILL.md](../SKILL.md) | Skill 定义和工作流程 |
| [../references/security_rules.md](../references/security_rules.md) | 安全检查规则库 |
| [../references/dockerfile_templates.md](../references/dockerfile_templates.md) | Dockerfile 模板库 |
| [../references/permission_templates.md](../references/permission_templates.md) | 权限配置模板 |

## 技术架构

详见 README.md 中的技术架构章节。

## 使用指南

1. 安装依赖: `pip install -r requirements.txt`
2. 扫描 Skill: `python scripts/scan_skill.py --skill <name>`
3. 安全检查: `python scripts/security_check.py --skill <name>`
4. 生成配置: `python scripts/generate_sandbox_config.py --skill <name>`
5. 构建镜像: `python scripts/build_image.py --skill <name>`
6. 一键配置: `python scripts/configure_all.py --skill <name>`