FROM python:3.11-slim

WORKDIR /app

# 复制 requirements 文件
COPY requirements.txt .

# 安装 MkDocs 和依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY app.py .

# 暴露端口
EXPOSE 8080

# 启动命令
CMD ["python", "app.py"]
