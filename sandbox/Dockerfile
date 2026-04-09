FROM opensandbox/execd:v1.0.7

# 安装 Python 依赖
COPY requirements.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# 创建工作目录
WORKDIR /sandbox

# 环境变量
ENV PYTHONPATH=/sandbox
ENV SANDBOX_MODE=enabled

# 创建非 root 用户
RUN useradd -m -u 1000 sandboxuser
USER sandboxuser

# 入口点
ENTRYPOINT ["python3"]