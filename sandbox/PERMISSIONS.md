# Sandbox Permissions Template

## 权限级别定义

| 级别 | 描述 | 典型权限 |
|------|------|----------|
| **minimal** | 只读、无网络、无外部发送 | 仅读取指定输入目录 |
| **standard** | 标准读写、受限网络 | 读写/input和/output，允许特定域名 |
| **elevated** | 扩展权限、需审核 | 更多文件路径、API调用 |
| **unrestricted** | 完全权限、需特殊审批 | 几乎无限制（不建议） |

## 网络权限配置

### 白名单模式
```json
{
  "network": {
    "default": "deny",
    "allow": ["*.github.com:443", "smtp.qq.com:587"],
    "deny": []
  }
}
```

### 黑名单模式
```json
{
  "network": {
    "default": "allow",
    "allow": [],
    "deny": ["10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"]
  }
}
```

## 文件系统权限

### 标准配置
```json
{
  "filesystem": {
    "read_paths": ["/input/**", "/workspace/skills/{skill}/**"],
    "write_paths": ["/output/**"],
    "deny_paths": ["~/.ssh/**", "~/.aws/**", "~/.gnupg/**"]
  }
}
```

## 资源限制

```json
{
  "resources": {
    "memory_limit": "2g",
    "cpu_limit": "2",
    "timeout_seconds": 300
  }
}
```