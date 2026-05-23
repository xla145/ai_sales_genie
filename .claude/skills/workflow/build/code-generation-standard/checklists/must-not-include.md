# 禁止出现检查清单



## 🚫 P0 级别（阻断，必须修复）

| # | 违规项 | 匹配模式 | 正确做法 |
|---|--------|----------|----------|
| 1 | 硬编码魔法数字 | `if (status == 1)` | 使用常量：`if (STATUS_ACTIVE.equals(status))` |
| 2 | 硬编码魔法字符串 | `if ("ADMIN".equals(role))` | 使用枚举或常量：`if (RoleEnum.ADMIN.getCode().equals(role))` |
| 3 | SQL 拼接 | `"SELECT * FROM " + table` | 使用参数化查询或 LambdaQueryWrapper |
| 4 | N+1 查询 | 循环内 `mapper.selectById()` | 批量查询：`mapper.selectBatchIds(ids)` |
| 5 | 空 catch 块 | `catch (Exception e) { }` | 至少记录日志：`log.error("xxx", e)` |
| 6 | 明文密码 | `password = "123456"` | 使用加密：`BCrypt.hashpw(password)` |
| 7 | System.out | `System.out.println()` | 使用日志：`log.info()` |
| 8 | 未关闭资源 | `new FileInputStream()` 无 close | 使用 try-with-resources |

## ⚠️ P1 级别（警告，当次迭代修复）

| # | 违规项 | 匹配模式 | 正确做法 |
|---|--------|----------|----------|
| 1 | TODO 无验收标准 | `// TODO: 优化性能` | `// TODO(性能优化): 列表查询超 1s 时添加缓存，v2.1 处理` |
| 2 | 过长方法 | 方法 > 50 行 | 拆分为多个私有方法 |
| 3 | 过深嵌套 | if 嵌套 > 3 层 | 提前返回（guard clause） |
| 4 | 重复代码 | 相同逻辑出现 2+ 次 | 提取公共方法 |
| 5 | 过多参数 | 方法参数 > 5 个 | 封装为 Request 对象 |
| 6 | 无限循环风险 | `while(true)` 无 break | 添加最大循环次数 |
| 7 | 硬编码 URL | `"http://10.0.1.100:8080/api"` | 使用配置文件或服务发现 |
| 8 | 非线程安全集合 | 多线程用 HashMap | 使用 ConcurrentHashMap |

## 🔵 P2 级别（建议，记录技术债务）

| # | 违规项 | 匹配模式 | 正确做法 |
|---|--------|----------|----------|
| 1 | 命名不规范 | `String nm` | 使用完整名称：`String userName` |
| 2 | 注释过多/过少 | 注释率 <10% 或 >50% | 保持 15%-30% |
| 3 | 未使用导入 | `import` 但未使用 | 移除未使用的导入 |
| 4 | 过宽泛异常 | `catch (Exception e)` | 捕获具体异常 |
