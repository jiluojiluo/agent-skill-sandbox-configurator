#!/usr/bin/env python3
"""
Sandbox Config Generator - 生成 sandbox 配置文件

功能：
1. 根据扫描结果生成 sandbox.json
2. 生成 PERMISSIONS.md
3. 生成 requirements.txt（提取 Python 依赖）
4. 生成 Dockerfile

使用方法：
python scripts/generate_sandbox_config.py --skill huawei-contract-legal-review
"""

import os
import re
import json
import argparse
from pathlib import Path
from typing import Dict, List

# 默认 sandbox.json 模板
DEFAULT_SANDBOX_JSON = {
    "skill_name": "",
    "permission_level": "standard",
    "network": {
        "default": "deny",
        "allow": [],
        "deny": []
    },
    "filesystem": {
        "read_paths": ["/input/**", "/workspace/skills/{skill_name}/**"],
        "write_paths": ["/output/**"],
        "deny_paths": ["~/.ssh/**", "~/.aws/**", "~/.gnupg/**", "~/.config/**"]
    },
    "env_vars": {
        "allowed": ["PYTHONPATH", "PATH", "HOME"],
        "deny": ["AWS_*", "SSH_*", "API_KEY", "TOKEN", "PASSWORD", "SECRET_*"]
    },
    "resources": {
        "memory_limit": "2g",
        "cpu_limit": "2",
        "timeout_seconds": 300
    }
}

# Dockerfile 模板
DOCKERFILE_TEMPLATE = '''FROM opensandbox/execd:v1.0.7

# 安装 Python 依赖
COPY requirements.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# 创建工作目录
WORKDIR /sandbox

# 复制 skill 脚本（如果有）
COPY scripts/ /sandbox/scripts/

# 设置权限
RUN chmod -R 755 /sandbox/scripts/

# 环境变量
ENV PYTHONPATH=/sandbox
ENV SANDBOX_MODE=enabled

# 创建非 root 用户
RUN useradd -m -u 1000 sandboxuser
USER sandboxuser

# 入口点
ENTRYPOINT ["python3"]
'''

# PERMISSIONS.md 模板
PERMISSIONS_TEMPLATE = '''# {skill_name} Sandbox 权限配置

## 权限级别：{permission_level}

### 网络权限
| 类型 | 配置 | 说明 |
|------|------|------|
| 默认策略 | {network_default} | {network_default_desc} |
| 白名单 | {network_allow} | 允许访问的域名 |
| 黑名单 | {network_deny} | 禁止访问的域名 |

### 文件系统权限
| 类型 | 范围 | 说明 |
|------|------|------|
| 可读目录 | {read_paths} | Skill 可读取的目录 |
| 可写目录 | {write_paths} | Skill 可写入的目录 |
| 禁止目录 | {deny_paths} | 敏感目录完全禁止 |

### 环境变量权限
| 类型 | 变量 | 说明 |
|------|------|------|
| 允许读取 | {env_allowed} | 安全的环境变量 |
| 禁止读取 | {env_deny} | 包含密钥的变量 |

### 资源限制
| 资源 | 限制 | 说明 |
|------|------|------|
| 内存 | {memory_limit} | 最大内存使用 |
| CPU | {cpu_limit} | CPU 核数限制 |
| 超时 | {timeout_seconds}s | 执行超时时间 |

## 安全警告

{security_warnings}

## 使用说明

1. 构建 Docker 镜像：
   ```bash
   cd sandbox/
   docker build -t {skill_name}-sandbox:latest .
   ```

2. 配置 OpenClaw：
   ```bash
   openclaw gateway restart
   ```

3. 验证容器：
   ```bash
   docker ps | grep {skill_name}
   ```
'''

def extract_python_dependencies(skill_path: Path) -> List[str]:
    """从 skill 中提取 Python 依赖"""
    dependencies = []
    standard_libs = ['os', 'sys', 're', 'json', 'pathlib', 'typing', 'argparse', 
                     'datetime', 'collections', 'itertools', 'functools', 'logging']
    
    for py_file in skill_path.rglob("*.py"):
        try:
            content = py_file.read_text(encoding='utf-8', errors='ignore')
            # 匹配 import 语句
            imports = re.findall(r'^import\s+(\w+)', content, re.MULTILINE)
            imports += re.findall(r'^from\s+(\w+)\s+import', content, re.MULTILINE)
            
            for imp in imports:
                if imp not in standard_libs and imp not in dependencies:
                    dependencies.append(imp)
        except Exception:
            pass
    
    return dependencies

def generate_sandbox_json(skill_name: str, scan_results: Dict = None) -> Dict:
    """生成 sandbox.json 配置"""
    config = DEFAULT_SANDBOX_JSON.copy()
    config["skill_name"] = skill_name
    
    # 更新路径模板
    config["filesystem"]["read_paths"] = [
        p.replace("{skill_name}", skill_name) for p in config["filesystem"]["read_paths"]
    ]
    
    # 根据扫描结果调整权限
    if scan_results:
        if scan_results["permissions"]["network"]:
            # 需要网络访问，设置为受限模式
            config["network"]["default"] = "deny"
        if scan_results["permissions"]["external_send"]:
            # 有外部发送，需要特别注意
            config["permission_level"] = "elevated"
    
    return config

def generate_sandbox_files(skill_path: Path, scan_results: Dict = None) -> Dict[str, str]:
    """生成所有 sandbox 配置文件"""
    skill_name = skill_path.name
    files = {}
    
    # sandbox.json
    sandbox_json = generate_sandbox_json(skill_name, scan_results)
    files["sandbox.json"] = json.dumps(sandbox_json, indent=2)
    
    # requirements.txt
    dependencies = extract_python_dependencies(skill_path)
    if dependencies:
        files["requirements.txt"] = "\n".join(dependencies) + "\n"
    else:
        files["requirements.txt"] = "# No external dependencies detected\n"
    
    # Dockerfile
    files["Dockerfile"] = DOCKERFILE_TEMPLATE
    
    # PERMISSIONS.md
    permissions_md = PERMISSIONS_TEMPLATE.format(
        skill_name=skill_name,
        permission_level=sandbox_json["permission_level"],
        network_default=sandbox_json["network"]["default"],
        network_default_desc="默认拒绝所有网络" if sandbox_json["network"]["default"] == "deny" else "默认允许所有网络",
        network_allow=", ".join(sandbox_json["network"]["allow"]) or "无",
        network_deny=", ".join(sandbox_json["network"]["deny"]) or "无",
        read_paths=", ".join(sandbox_json["filesystem"]["read_paths"]),
        write_paths=", ".join(sandbox_json["filesystem"]["write_paths"]),
        deny_paths=", ".join(sandbox_json["filesystem"]["deny_paths"]),
        env_allowed=", ".join(sandbox_json["env_vars"]["allowed"]),
        env_deny=", ".join(sandbox_json["env_vars"]["deny"]),
        memory_limit=sandbox_json["resources"]["memory_limit"],
        cpu_limit=sandbox_json["resources"]["cpu_limit"],
        timeout_seconds=sandbox_json["resources"]["timeout_seconds"],
        security_warnings="无高危警告" if not (scan_results and scan_results["risks"]) else 
            "\n".join([f"⚠️ {r['message']}: {r['path']} (Line {r['line']})" 
                      for r in scan_results["risks"] if r["severity"] == "HIGH"])
    )
    files["PERMISSIONS.md"] = permissions_md
    
    # .dockerignore
    files[".dockerignore"] = """# Python
__pycache__/
*.pyc
*.pyo
*.egg-info/
.eggs/

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db

# Other
*.log
*.tmp
"""
    
    return files

def create_sandbox_directory(skill_path: Path, files: Dict[str, str]) -> Path:
    """创建 sandbox 目录并写入文件"""
    sandbox_path = skill_path / "sandbox"
    sandbox_path.mkdir(parents=True, exist_ok=True)
    
    for filename, content in files.items():
        file_path = sandbox_path / filename
        file_path.write_text(content)
        print(f"Created: {file_path}")
    
    return sandbox_path

def main():
    parser = argparse.ArgumentParser(description="Generate sandbox configuration")
    parser.add_argument("--skill", required=True, help="Skill name")
    parser.add_argument("--scan-results", help="JSON file with scan results")
    parser.add_argument("--dry-run", action="store_true", help="Only print files, don't create")
    
    args = parser.parse_args()
    
    # 找到 skill 路径
    workspace = Path.home() / ".openclaw" / "workspace"
    skill_path = workspace / "skills" / args.skill
    
    if not skill_path.exists():
        print(f"Error: Skill directory not found: {skill_path}")
        return
    
    # 加载扫描结果（如果有）
    scan_results = None
    if args.scan_results:
        scan_results = json.loads(Path(args.scan_results).read_text())
    
    # 生成配置文件
    files = generate_sandbox_files(skill_path, scan_results)
    
    if args.dry_run:
        for filename, content in files.items():
            print(f"\n=== {filename} ===")
            print(content)
    else:
        sandbox_path = create_sandbox_directory(skill_path, files)
        print(f"\n✅ Sandbox configuration created at: {sandbox_path}")

if __name__ == "__main__":
    main()