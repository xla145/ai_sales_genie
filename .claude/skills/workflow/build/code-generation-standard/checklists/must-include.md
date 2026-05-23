# 必须包含检查清单



## Java 后端

| # | 检查项 | 检查方式 | 示例 |
|---|--------|----------|------|
| 1 | 完整的类定义 | 类有完整结构，无缺失 | `public class UserService { ... }` |
| 2 | JavaDoc 注释 | 类级 + public 方法注释 | `/** 用户服务 - 处理用户相关业务 */` |
| 3 | 类型注解 | 泛型、返回值类型明确 | `Result<UserVO>` 而非 `Result` |
| 4 | 异常处理 | 业务异常 + 全局异常处理 | `throw new BusinessException(ErrorCode.XXX)` |
| 5 | 参数校验 | Request DTO 使用 `@NotNull`/`@NotBlank` | `@NotBlank(message = "用户名不能为空")` |
| 6 | 事务注解 | 写操作标注 `@Transactional` | `@Transactional(rollbackFor = Exception.class)` |
| 7 | 接口文档 | Swagger/Knife4j 注解 | `@Operation(summary = "查询用户")` |
| 8 | 日志记录 | 关键操作记录日志 | `log.info("创建用户, userId={}", userId)` |
| 9 | 单元测试 | 核心方法有测试 | `UserServiceTest.java` |
| 10 | 软删除 | 删除使用逻辑删除 | `isDelete = "Y"` |

## Vue 前端

| # | 检查项 | 检查方式 | 示例 |
|---|--------|----------|------|
| 1 | 完整的组件定义 | SFC 结构完整 | `<template> + <script> + <style>` |
| 2 | TypeScript 类型 | Props/Emits/Ref 有类型 | `defineProps<{ title: string }>()` |
| 3 | 组件注释 | 组件用途说明 | `/** 用户列表页 - 展示用户数据 */` |
| 4 | 错误处理 | API 调用有 try/catch | `try { await api() } catch(e) { ... }` |
| 5 | 加载状态 | 异步操作有 loading | `const loading = ref(false)` |
| 6 | 空状态 | 列表为空有提示 | `<Empty v-if="!list.length" />` |
| 7 | Scoped 样式 | 样式隔离 | `<style scoped>` |
| 8 | 事件命名 | Emit 使用 kebab-case | `emit('update-item')` |
