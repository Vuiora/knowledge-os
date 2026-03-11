# AI 助手 Dockerfile
# 将在任务 7-8 中实现

FROM python:3.11-slim

WORKDIR /app

# 安装依赖（占位符）
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt || true

# 复制应用代码
COPY . .

# 暴露端口
EXPOSE 8000

# 启动命令（占位符）
CMD ["python", "app.py"]
