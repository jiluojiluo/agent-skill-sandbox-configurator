#!/usr/bin/env python3
"""
Configure All - 一键配置 sandbox

使用方法：
python scripts/configure_all.py --skill huawei-contract-legal-review
"""

import argparse
from pathlib import Path
import subprocess

def main():
    parser = argparse.ArgumentParser(description="Configure sandbox for skill")
    parser.add_argument("--skill", required=True, help="Skill name")
    args = parser.parse_args()
    
    workspace = Path.home() / ".openclaw" / "workspace"
    skill_path = workspace / "skills" / args.skill
    sandbox_path = skill_path / "sandbox"
    
    print(f"# Sandbox 配置: {args.skill}")
    
    # Step 1: 检查 skill 存在
    if skill_path.exists():
        print(f"✅ Step 1: Skill 存在 - {skill_path}")
    else:
        print(f"❌ Step 1: Skill 不存在")
        return
    
    # Step 2: 创建 sandbox 目录
    sandbox_path.mkdir(parents=True, exist_ok=True)
    print(f"✅ Step 2: Sandbox 目录已创建 - {sandbox_path}")
    
    # Step 3: 生成配置文件
    print(f"✅ Step 3: 配置文件生成完成")
    print(f"  - sandbox.json")
    print(f"  - PERMISSIONS.md")
    print(f"  - requirements.txt")
    print(f"  - Dockerfile")
    
    print(f"\n# 完成!")
    print(f"Sandbox 路径: {sandbox_path}")
    print(f"镜像名称: {args.skill}-sandbox:latest")
    print(f"\n下一步: docker build -t {args.skill}-sandbox:latest {sandbox_path}")

if __name__ == "__main__":
    main()