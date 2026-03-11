-- 工程师知识系统 - PostgreSQL 初始化脚本
-- 创建 Gitea 和 Wiki.js 所需的数据库和用户

-- 创建 Gitea 数据库
CREATE DATABASE gitea
    WITH OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.UTF-8'
    LC_CTYPE = 'en_US.UTF-8'
    TEMPLATE = template0;

-- 创建 Wiki.js 数据库
CREATE DATABASE wiki
    WITH OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.UTF-8'
    LC_CTYPE = 'en_US.UTF-8'
    TEMPLATE = template0;

-- 创建 Gitea 数据库用户（如果需要独立用户）
-- CREATE USER gitea WITH PASSWORD '${GITEA_DB_PASS:-giteapass}';
-- GRANT ALL PRIVILEGES ON DATABASE gitea TO gitea;

-- 创建 Wiki.js 数据库用户（如果需要独立用户）
-- CREATE USER wikijs WITH PASSWORD '${WIKI_DB_PASS:-wikijspass}';
-- GRANT ALL PRIVILEGES ON DATABASE wiki TO wikijs;

-- 授予 postgres 用户所有权限
GRANT ALL PRIVILEGES ON DATABASE gitea TO postgres;
GRANT ALL PRIVILEGES ON DATABASE wiki TO postgres;

-- 输出成功信息（用于调试）
SELECT 'Database gitea created successfully' AS status;
SELECT 'Database wiki created successfully' AS status;
