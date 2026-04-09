# Permission Templates

本文档定义权限级别模板，用于生成 sandbox.json。

## Minimal 级别

适用于只读、无网络的 Skill。

```json
{
  "permission_level": "minimal",
  "network": {
    "default": "deny",
    "allow": [],
    "deny": []
  },
  "filesystem": {
    "read_paths": ["/input/**"],
    "write_paths": [],
    "deny_paths": ["~/.ssh/**", "~/.aws/**", "~/.gnupg/**"]
  },
  "env_vars": {
    "allowed": ["PYTHONPATH", "PATH"],
    "deny": ["AWS_*", "SSH_*", "API_KEY", "TOKEN", "PASSWORD", "SECRET_*"]
  },
  "resources": {
    "memory_limit": "512M",
    "cpu_limit": "1",
    "timeout_seconds": 60
  }
}
```

## Standard 级别

适用于标准读写、受限网络的 Skill。

```json
{
  "permission_level": "standard",
  "network": {
    "default": "deny",
    "allow": ["*.github.com:443"],
    "deny": []
  },
  "filesystem": {
    "read_paths": ["/input/**", "/workspace/skills/{skill}/**"],
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
```

## Elevated 级别

适用于需要扩展权限的 Skill，需审核。

```json
{
  "permission_level": "elevated",
  "network": {
    "default": "allow",
    "allow": [],
    "deny": ["10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"]
  },
  "filesystem": {
    "read_paths": ["/input/**", "/workspace/**"],
    "write_paths": ["/output/**", "/workspace/output/**"],
    "deny_paths": ["~/.ssh/**", "~/.aws/**", "~/.gnupg/**"]
  },
  "env_vars": {
    "allowed": ["PYTHONPATH", "PATH", "HOME", "USER"],
    "deny": ["AWS_*", "SSH_*", "PRIVATE_KEY"]
  },
  "resources": {
    "memory_limit": "4g",
    "cpu_limit": "4",
    "timeout_seconds": 600
  }
}
```

## 网络配置模板

### 白名单模式（推荐）

```json
{
  "network": {
    "default": "deny",
    "allow": ["smtp.qq.com:587", "api.openai.com:443"],
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
    "deny": ["10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16", "127.0.0.0/8"]
  }
}
```

## 资源配置模板

### 轻量级任务

```json
{
  "resources": {
    "memory_limit": "512M",
    "cpu_limit": "1",
    "timeout_seconds": 60
  }
}
```

### 标准任务

```json
{
  "resources": {
    "memory_limit": "2g",
    "cpu_limit": "2",
    "timeout_seconds": 300
  }
}
```

### 重型任务

```json
{
  "resources": {
    "memory_limit": "8g",
    "cpu_limit": "4",
    "timeout_seconds": 1200
  }
}
```