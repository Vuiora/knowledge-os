#!/bin/bash

# 生成安全的随机密码和密钥

echo "生成安全密钥..."
echo ""

# 生成随机密码函数
generate_password() {
    openssl rand -base64 32 | tr -d "=+/" | cut -c1-32
}

# 生成密钥
GITEA_PASSWORD=$(generate_password)
GITEA_DB_PASS=$(generate_password)
WIKI_DB_PASS=$(generate_password)
POSTGRES_PASSWORD=$(generate_password)
WEBHOOK_SECRET=$(generate_password)

echo "生成的密钥（请保存到 .env 文件）："
echo "=========================================="
echo "GITEA_PASSWORD=$GITEA_PASSWORD"
echo "GITEA_DB_PASS=$GITEA_DB_PASS"
echo "WIKI_DB_PASS=$WIKI_DB_PASS"
echo "POSTGRES_PASSWORD=$POSTGRES_PASSWORD"
echo "WEBHOOK_SECRET=$WEBHOOK_SECRET"
echo "=========================================="
echo ""
echo "注意："
echo "1. GITEA_TOKEN 和 WIKI_TOKEN 需要在服务启动后手动生成"
echo "2. OPENAI_API_KEY 需要从 OpenAI 获取（如果使用 AI 功能）"
echo ""
