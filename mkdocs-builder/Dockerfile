FROM python:3.11-slim

WORKDIR /app

# 安装 MkDocs 和依赖
RUN pip install --no-cache-dir \
    mkdocs>=1.5.0 \
    mkdocs-material>=9.0.0 \
    mkdocs-git-revision-date-localized-plugin \
    mkdocs-minify-plugin

# 复制应用代码
COPY app.py .

# 暴露端口
EXPOSE 8080

# 启动命令
CMD ["python", "app.py"]
