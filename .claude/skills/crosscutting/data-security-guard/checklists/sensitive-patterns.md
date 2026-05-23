# 敏感信息匹配模式

> 用于扫描代码和内容中的敏感信息

## 🚫 Critical 级别（阻断）

### API 密钥

| 模式 | 说明 | 匹配示例 |
|------|------|----------|
| `sk-[a-zA-Z0-9]{20,}` | OpenAI/Anthropic API Key | `sk-proj-abc123...` |
| `AKIA[0-9A-Z]{16}` | AWS Access Key | `AKIAIOSFODNN7EXAMPLE` |
| `[a-f0-9]{32}` | 通用 32 位 Hex Key | `a1b2c3d4e5f6...` |
| `key['":\s]*['"][a-zA-Z0-9]{20,}['"]` | 通用 Key 赋值 | `api_key: "xxxxxx"` |

### Token

| 模式 | 说明 | 匹配示例 |
|------|------|----------|
| `Bearer [a-zA-Z0-9\-._~+/]+=*` | Bearer Token | `Bearer eyJhbGci...` |
| `eyJ[a-zA-Z0-9_-]+\.eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+` | JWT Token | `eyJhbGciOi...` |
| `ghp_[a-zA-Z0-9]{36}` | GitHub Token | `ghp_xxxxxxxxxxxx` |
| `glpat-[a-zA-Z0-9\-]{20,}` | GitLab Token | `glpat-xxxxxxxxxxxx` |

### 数据库凭据

| 模式 | 说明 | 匹配示例 |
|------|------|----------|
| `password\s*[:=]\s*['"][^'"]{6,}['"]` | 密码赋值 | `password: "mysecretpass"` |
| `jdbc:\w+://[^:]+:[^@]+@` | JDBC 含密码 | `jdbc:mysql://user:pass@host` |
| `DB_PASSWORD` | 环境变量名 | `DB_PASSWORD=xxx` |

### 私钥

| 模式 | 说明 | 匹配示例 |
|------|------|----------|
| `-----BEGIN (RSA \|EC \|DSA )?PRIVATE KEY-----` | PEM 私钥 | `-----BEGIN RSA PRIVATE KEY-----` |

### 个人隐私数据

| 模式 | 说明 | 匹配示例 |
|------|------|----------|
| `1[3-9]\d{9}` | 中国手机号 | `13812345678` |
| `[1-9]\d{5}(19\|20)\d{2}(0[1-9]\|1[0-2])\d{2}\d{3}[\dXx]` | 身份证号 | `110101199003071234` |
| `[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}` | 邮箱地址 | `user@example.com` |

## ⚠️ Warning 级别（警告）

### 内部网络信息

| 模式 | 说明 | 匹配示例 |
|------|------|----------|
| `10\.\d{1,3}\.\d{1,3}\.\d{1,3}` | A 类私有 IP | `10.0.1.100` |
| `172\.(1[6-9]\|2\d\|3[01])\.\d{1,3}\.\d{1,3}` | B 类私有 IP | `172.16.0.1` |
| `192\.168\.\d{1,3}\.\d{1,3}` | C 类私有 IP | `192.168.1.1` |

### 安全风险代码

| 模式 | 说明 | 匹配示例 |
|------|------|----------|
| `".*"\s*\+\s*.*SELECT\|INSERT\|UPDATE\|DELETE` | SQL 拼接 | `"SELECT * FROM " + tableName` |
| `Runtime\.getRuntime\(\)\.exec\(` | 命令执行 | `Runtime.getRuntime().exec(cmd)` |
| `eval\(` | 动态代码执行 | `eval(userInput)` |
| `innerHTML\s*=` | XSS 风险 | `element.innerHTML = data` |

## 脱敏规则

| 数据类型 | 脱敏方式 | 脱敏示例 |
|----------|----------|----------|
| 手机号 | 保留前 3 后 4 | `138****5678` |
| 身份证号 | 保留前 3 后 4 | `110***********1234` |
| 邮箱 | 保留首字母和域名 | `u***@example.com` |
| 姓名 | 保留姓氏 | `张**` |
| IP 地址 | 掩码最后两段 | `192.168.*.*` |
| 密码 | 完全替换 | `***` |
