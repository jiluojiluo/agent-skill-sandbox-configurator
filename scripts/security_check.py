#!/usr/bin/env python3
"""
Security Checker - 安全检查和警告生成

使用方法：
python scripts/security_check.py --skill huawei-contract-legal-review
"""

import os
import re
import json
import argparse
from pathlib import Path
from typing import Dict, List

SECURITY_RULES = [
    {"id": "SECRET_FILE", "name": "敏感文件访问", "severity": "CRITICAL", "patterns": [r"~/.ssh", r"~/.aws", r"id_rsa"], "recommendation": "禁止访问敏感目录"},
    {"id": "SECRET_ENV", "name": "密钥变量读取", "severity": "CRITICAL", "patterns": [r"os\.environ\[['\"]AWS_", r"os\.environ\[['\"]API_KEY"], "recommendation": "使用sandbox配置注入"},
    {"id": "EMAIL_SEND", "name": "邮件发送", "severity": "HIGH", "patterns": [r"smtp\.sendmail", r"send_email"], "recommendation": "限制SMTP服务器"},
    {"id": "WEBHOOK", "name": "外部发送", "severity": "HIGH", "patterns": [r"requests\.post", r"webhook"], "recommendation": "用户确认发送目标"},
    {"id": "FILE_DELETE", "name": "文件删除", "severity": "HIGH", "patterns": [r"os\.remove", r"rm -rf"], "recommendation": "使用trash替代"},
    {"id": "PROCESS_EXEC", "name": "进程执行", "severity": "MEDIUM", "patterns": [r"subprocess\.", r"os\.system"], "recommendation": "命令白名单"},
    {"id": "NETWORK", "name": "网络访问", "severity": "MEDIUM", "patterns": [r"requests\.get", r"urllib"], "recommendation": "网络白名单"},
]

def check_security(skill_path: Path) -> Dict:
    results = {"skill_name": skill_path.name, "passed": True, "violations": [], "summary": {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0}}
    if not skill_path.exists():
        results["passed"] = False
        return results
    for file_path in skill_path.rglob("*.py"):
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            for rule in SECURITY_RULES:
                for pattern in rule["patterns"]:
                    if re.search(pattern, content, re.IGNORECASE):
                        results["violations"].append({"rule": rule["name"], "severity": rule["severity"], "file": str(file_path)})
                        results["summary"][rule["severity"]] += 1
        except Exception:
            pass
    if results["summary"]["CRITICAL"] > 0:
        results["passed"] = False
    return results

def main():
    parser = argparse.ArgumentParser(description="Security check for skill")
    parser.add_argument("--skill", required=True, help="Skill name")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()
    workspace = Path.home() / ".openclaw" / "workspace"
    skill_path = workspace / "skills" / args.skill
    results = check_security(skill_path)
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        status = "✅ PASS" if results["passed"] else "❌ BLOCK"
        print(f"🔒 安全检查: {results['skill_name']} - {status}")
        print(f"CRITICAL: {results['summary']['CRITICAL']}, HIGH: {results['summary']['HIGH']}, MEDIUM: {results['summary']['MEDIUM']}")
    return 0 if results["passed"] else 1

if __name__ == "__main__":
    exit(main())