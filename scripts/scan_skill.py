#!/usr/bin/env python3
"""
Skill Scanner - 扫描 skill 目录并分析权限需求

使用方法：
python scripts/scan_skill.py --skill huawei-contract-legal-review
"""

import os
import re
import json
import argparse
from pathlib import Path
from typing import Dict, List

HIGH_RISK_RULES = {
    "sensitive_dir": {
        "patterns": [r"~/.ssh", r"~/.aws", r"~/.gnupg"],
        "severity": "HIGH",
        "message": "敏感目录访问"
    },
    "secret_env": {
        "patterns": [r"os\.environ\[['\"]API_KEY", r"os\.environ\[['\"]TOKEN"],
        "severity": "HIGH",
        "message": "密钥环境变量读取"
    },
    "email_send": {
        "patterns": [r"smtp\.sendmail", r"send_email"],
        "severity": "HIGH",
        "message": "邮件发送功能"
    },
    "external_post": {
        "patterns": [r"requests\.post", r"requests\.put"],
        "severity": "HIGH",
        "message": "外部数据发送"
    },
    "file_delete": {
        "patterns": [r"os\.remove", r"shutil\.rmtree", r"rm -rf"],
        "severity": "HIGH",
        "message": "文件删除操作"
    },
    "process_exec": {
        "patterns": [r"subprocess\.", r"os\.system"],
        "severity": "MEDIUM",
        "message": "进程执行操作"
    },
    "network_access": {
        "patterns": [r"requests\.get", r"urllib\.request"],
        "severity": "MEDIUM",
        "message": "网络访问请求"
    }
}

def scan_skill(skill_path: Path) -> Dict:
    results = {
        "skill_name": skill_path.name,
        "exists": skill_path.exists(),
        "files": [],
        "risks": [],
        "permissions": {"network": False, "file_read": [], "file_write": [], "external_send": False}
    }
    if not skill_path.exists():
        return results
    for file_path in skill_path.rglob("*"):
        if file_path.is_file():
            file_info = scan_file(file_path)
            results["files"].append(file_info)
            results["risks"].extend(file_info["risks"])
    return results

def scan_file(file_path: Path) -> Dict:
    file_info = {"path": str(file_path), "type": file_path.suffix, "risks": []}
    if file_path.suffix not in ['.py', '.sh', '.md']:
        return file_info
    try:
        content = file_path.read_text(encoding='utf-8', errors='ignore')
        for rule_name, rule in HIGH_RISK_RULES.items():
            for pattern in rule["patterns"]:
                if re.search(pattern, content):
                    file_info["risks"].append({"rule": rule_name, "severity": rule["severity"], "message": rule["message"]})
    except Exception:
        pass
    return file_info

def main():
    parser = argparse.ArgumentParser(description="Scan skill for security risks")
    parser.add_argument("--skill", required=True, help="Skill name")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()
    workspace = Path.home() / ".openclaw" / "workspace"
    skill_path = workspace / "skills" / args.skill
    results = scan_skill(skill_path)
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(f"Skill: {results['skill_name']}")
        print(f"Exists: {results['exists']}")
        print(f"Files: {len(results['files'])}")
        print(f"High risks: {len([r for r in results['risks'] if r['severity']=='HIGH'])}")

if __name__ == "__main__":
    main()