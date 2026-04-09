#!/usr/bin/env python3
"""
Docker Image Builder - 构建 sandbox Docker 镜像

功能：
1. 构建 Docker 镜像
2. 验证镜像构建成功
3. 输出镜像信息

使用方法：
python scripts/build_image.py --skill huawei-contract-legal-review
"""

import subprocess
import argparse
from pathlib import Path

def build_docker_image(skill_name: str, sandbox_path: Path) -> Dict:
    """构建 Docker 镜像"""
    image_name = f"{skill_name}-sandbox:latest"
    
    result = {
        "image_name": image_name,
        "success": False,
        "output": "",
        "error": ""
    }
    
    if not sandbox_path.exists():
        result["error"] = f"Sandbox directory not found: {sandbox_path}"
        return result
    
    dockerfile_path = sandbox_path / "Dockerfile"
    if not dockerfile_path.exists():
        result["error"] = f"Dockerfile not found: {dockerfile_path}"
        return result
    
    # 执行 docker build
    try:
        cmd = [
            "docker", "build",
            "-t", image_name,
            "-f", str(dockerfile_path),
            str(sandbox_path)
        ]
        
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600  # 10 分钟超时
        )
        
        result["output"] = proc.stdout
        result["error"] = proc.stderr
        
        if proc.returncode == 0:
            result["success"] = True
        else:
            result["success"] = False
    
    except subprocess.TimeoutExpired:
        result["error"] = "Build timeout (>10 minutes)"
    except FileNotFoundError:
        result["error"] = "Docker not installed or not in PATH"
    except Exception as e:
        result["error"] = str(e)
    
    return result

def verify_image(image_name: str) -> Dict:
    """验证镜像"""
    result = {
        "exists": False,
        "size": "",
        "created": ""
    }
    
    try:
        cmd = ["docker", "images", image_name, "--format", "{{.Repository}}:{{.Tag}} {{.Size}} {{.CreatedAt}}"]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        
        if proc.returncode == 0 and proc.stdout.strip():
            result["exists"] = True
            parts = proc.stdout.strip().split()
            if len(parts) >= 2:
                result["size"] = parts[1]
            if len(parts) >= 3:
                result["created"] = parts[2]
    
    except Exception:
        pass
    
    return result

def main():
    parser = argparse.ArgumentParser(description="Build Docker image for skill sandbox")
    parser.add_argument("--skill", required=True, help="Skill name")
    parser.add_argument("--dry-run", action="store_true", help="Only print build command")
    parser.add_argument("--no-cache", action="store_true", help="Build without cache")
    
    args = parser.parse_args()
    
    # 找到 sandbox 路径
    workspace = Path.home() / ".openclaw" / "workspace"
    sandbox_path = workspace / "skills" / args.skill / "sandbox"
    
    image_name = f"{args.skill}-sandbox:latest"
    
    if args.dry_run:
        cmd = ["docker", "build", "-t", image_name, str(sandbox_path)]
        if args.no_cache:
            cmd.append("--no-cache")
        print("Build command:")
        print(" ".join(cmd))
        return
    
    # 构建
    print(f"Building image: {image_name}")
    print(f"From: {sandbox_path}")
    
    result = build_docker_image(args.skill, sandbox_path)
    
    if result["success"]:
        print(f"\n✅ Build successful!")
        
        # 验证
        verify_result = verify_image(image_name)
        if verify_result["exists"]:
            print(f"Image: {image_name}")
            print(f"Size: {verify_result['size']}")
            print(f"Created: {verify_result['created']}")
        
        # 测试运行
        print(f"\nTest command:")
        print(f"docker run --rm {image_name} python3 -c 'print(\"OK\")'")
        
    else:
        print(f"\n❌ Build failed!")
        print(f"Error: {result['error']}")
        if result["output"]:
            print(f"\nOutput:\n{result['output']}")

if __name__ == "__main__":
    main()