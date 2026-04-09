# Dockerfile Templates

本文档提供多种 Dockerfile 模板，适配不同类型 Skill。

## 模板1: 基础 Python 环境

适用于大多数 Python Skill。

```dockerfile
FROM opensandbox/execd:v1.0.7

COPY requirements.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt

WORKDIR /sandbox
ENV PYTHONPATH=/sandbox
ENV SANDBOX_MODE=enabled

RUN useradd -m -u 1000 sandboxuser
USER sandboxuser

ENTRYPOINT ["python3"]
```

## 模板2: 带 Node.js 环境

适用于需要执行 JavaScript 的 Skill。

```dockerfile
FROM opensandbox/execd:v1.0.7

# Python
COPY requirements.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Node.js
RUN apt-get update && apt-get install -y nodejs npm

WORKDIR /sandbox
ENV PYTHONPATH=/sandbox
ENV SANDBOX_MODE=enabled

RUN useradd -m -u 1000 sandboxuser
USER sandboxuser

ENTRYPOINT ["python3"]
```

## 模板3: 网络受限环境

适用于需要严格网络限制的 Skill。

```dockerfile
FROM opensandbox/execd:v1.0.7

COPY requirements.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt

WORKDIR /sandbox
ENV PYTHONPATH=/sandbox
ENV SANDBOX_MODE=enabled
ENV NETWORK_MODE=restricted

RUN useradd -m -u 1000 sandboxuser
USER sandboxuser

ENTRYPOINT ["python3"]
```

## 模板4: Office 文档处理

适用于处理 Word/Excel/PDF 的 Skill。

```dockerfile
FROM opensandbox/execd:v1.0.7

COPY requirements.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Office 文档处理库
RUN pip install --no-cache-dir openpyxl python-docx PyPDF2

WORKDIR /sandbox
ENV PYTHONPATH=/sandbox
ENV SANDBOX_MODE=enabled

RUN useradd -m -u 1000 sandboxuser
USER sandboxuser

ENTRYPOINT ["python3"]
```

## 最佳实践

1. **使用非 root 用户**: 创建 sandboxuser 并切换
2. **最小化依赖**: 只安装必要的包
3. **设置环境变量**: PYTHONPATH, SANDBOX_MODE
4. **清理缓存**: 使用 --no-cache-dir