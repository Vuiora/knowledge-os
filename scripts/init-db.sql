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

-- 创建 Gitea 数据库用户
CREATE USER gitea WITH PASSWORD 'JqXrSGXoCe4ev4HBcCH9UrAkcqZ9gLwt';
GRANT ALL PRIVILEGES ON DATABASE gitea TO gitea;

-- 创建 Wiki.js 数据库用户
CREATE USER wikijs WITH PASSWORD 'PyzfEMoElGbmNIObgbdl9CnAjs8sbx9n';
GRANT ALL PRIVILEGES ON DATABASE wiki TO wikijs;

-- 授予 postgres 用户所有权限
GRANT ALL PRIVILEGES ON DATABASE gitea TO postgres;
GRANT ALL PRIVILEGES ON DATABASE wiki TO postgres;

-- 连接到 gitea 数据库并授予 schema 权限
\c gitea
GRANT ALL ON SCHEMA public TO gitea;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO gitea;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO gitea;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO gitea;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO gitea;

-- 连接到 wiki 数据库并授予 schema 权限
\c wiki
GRANT ALL ON SCHEMA public TO wikijs;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO wikijs;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO wikijs;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO wikijs;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO wikijs;

-- 输出成功信息（用于调试）
SELECT 'Database gitea created successfully' AS status;
SELECT 'Database wiki created successfully' AS status;
