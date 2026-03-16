FROM python:3.11-slim

WORKDIR /app

# 安装 git（用于克隆仓库）
RUN apt-get update && \
    apt-get install -y git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 复制 requirements 文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY app.py .
COPY gitea_client.py .
COPY builder.py .
COPY monitoring.py .
COPY logging_config.py .
COPY error_handler.py .

# 复制 MkDocs 配置模板
COPY mkdocs.yml.template .

# 复制额外资源
COPY stylesheets/ ./stylesheets/
COPY javascripts/ ./javascripts/
COPY templates/ ./templates/

# 创建必要的目录
RUN mkdir -p /app/repo /app/site

# 暴露端口
EXPOSE 8080

# 启动命令
CMD ["python", "app.py"]
