# Controller Template

**Path**: `modules/{module}/src/main/java/com/bytefactory/quchiv2/{module}/controller/{Feature}Controller.java`

## Standard CRUD Controller

```java
package com.bytefactory.quchiv2.{module}.controller;

import com.bytefactory.quchiv2.{module}.constants.{Module}Constants;
import com.bytefactory.quchiv2.{module}.dto.request.*;
import com.bytefactory.quchiv2.{module}.dto.response.*;
import com.bytefactory.quchiv2.{module}.dto.response.common.PageResponse;
import com.bytefactory.quchiv2.{module}.dto.response.common.Result;
import com.bytefactory.quchiv2.{module}.service.{Feature}Service;
import com.bytefactory.quchiv2.authorization.annotation.Log;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * {中文名称}控制器
 */
@RestController
@RequestMapping("/api/{module}/{feature}")
@RequiredArgsConstructor
@Tag(name = "{中文名称}管理", description = "{中文名称}相关接口")
public class {Feature}Controller {

    private final {Feature}Service {feature}Service;

    /**
     * 查询{中文名称}列表
     */
    @PostMapping("/list")
    @Operation(summary = "查询{中文名称}列表", description = "分页查询{中文名称}列表，支持条件过滤")
    @Log(title = "查询{中文名称}列表", businessType = 12)
    public Result<PageResponse<{Feature}ListResponse>> query{Feature}List(
            @Valid @RequestBody {Feature}QueryRequest request) {
        try {
            PageResponse<{Feature}ListResponse> response = {feature}Service.query{Feature}List(request);
            return Result.success({Module}Constants.Message.QUERY_SUCCESS, response);
        } catch (Exception e) {
            return Result.error(e.getMessage());
        }
    }

    /**
     * 新增{中文名称}
     */
    @PostMapping("/add")
    @Operation(summary = "新增{中文名称}", description = "新增{中文名称}信息")
    @Log(title = "新增{中文名称}", businessType = 1)
    public Result<Void> add{Feature}(@Valid @RequestBody {Feature}AddRequest request) {
        try {
            {feature}Service.add{Feature}(request);
            return Result.success({Module}Constants.Message.ADD_SUCCESS, null);
        } catch (Exception e) {
            return Result.error(e.getMessage());
        }
    }

    /**
     * 修改{中文名称}
     */
    @PostMapping("/edit")
    @Operation(summary = "修改{中文名称}", description = "修改{中文名称}信息")
    @Log(title = "修改{中文名称}", businessType = 2)
    public Result<Void> edit{Feature}(@Valid @RequestBody {Feature}EditRequest request) {
        try {
            {feature}Service.edit{Feature}(request);
            return Result.success({Module}Constants.Message.EDIT_SUCCESS, null);
        } catch (Exception e) {
            return Result.error(e.getMessage());
        }
    }

    /**
     * 删除{中文名称}
     */
    @PostMapping("/delete")
    @Operation(summary = "删除{中文名称}", description = "删除{中文名称}（逻辑删除）")
    @Log(title = "删除{中文名称}", businessType = 3)
    public Result<Void> delete{Feature}(@Valid @RequestBody {Feature}DeleteRequest request) {
        try {
            {feature}Service.delete{Feature}(request);
            return Result.success({Module}Constants.Message.DELETE_SUCCESS, null);
        } catch (Exception e) {
            return Result.error(e.getMessage());
        }
    }

    /**
     * 查询{中文名称}详情
     */
    @PostMapping("/detail")
    @Operation(summary = "查询{中文名称}详情", description = "查询单个{中文名称}详细信息")
    @Log(title = "查询{中文名称}详情", businessType = 12)
    public Result<{Feature}DetailResponse> query{Feature}Detail(
            @Valid @RequestBody {Feature}DetailRequest request) {
        try {
            {Feature}DetailResponse response = {feature}Service.query{Feature}Detail(request);
            return Result.success({Module}Constants.Message.QUERY_SUCCESS, response);
        } catch (Exception e) {
            return Result.error(e.getMessage());
        }
    }

    /**
     * 查询{中文名称}类型字典（下拉选项）
     * 此接口为可选，仅当前端需要下拉时添加
     */
    @GetMapping("/type/dict")
    @Operation(summary = "查询{中文名称}类型字典", description = "获取{中文名称}类型下拉选项")
    public Result<List<{Feature}TypeDictResponse>> query{Feature}TypeDict() {
        try {
            List<{Feature}TypeDictResponse> response = {feature}Service.query{Feature}TypeDict();
            return Result.success({Module}Constants.Message.QUERY_SUCCESS, response);
        } catch (Exception e) {
            return Result.error(e.getMessage());
        }
    }
}
```

---

## URL Pattern Convention

```
/api/{module}/{feature}/{action}

Examples:
  /api/agreement/protocol/list
  /api/agreement/protocol/add
  /api/agreement/protocol/edit
  /api/agreement/protocol/delete
  /api/agreement/protocol/detail
  /api/agreement/protocol/category/dict
```

Rules:
- Module = folder name (kebab-case): `agreement`, `user-feedback`
- Feature = entity name (kebab-case): `protocol`, `announcement`
- All **write** actions: `@PostMapping`
- **Read-only dicts**: `@GetMapping`

---

## businessType Values for @Log

| businessType | Meaning |
|---|---|
| 1 | 新增 |
| 2 | 修改 |
| 3 | 删除 |
| 12 | 查询 |

---

## Controller Best Practices

1. **每个 endpoint** 必须包裹在 `try/catch → Result.success() / Result.error()` 中
2. **使用 `@Valid`** 触发 Jakarta Validation（`@NotBlank`、`@NotNull` 等）
3. **Dict endpoints** 使用 `@GetMapping`（无请求体）
4. **不要在 controller 中直接注入 Mapper** — 必须经过 service 层
5. **响应消息** 来自 `{Module}Constants.Message` 常量，不要硬编码字符串

### ⚠️ 异常消息暴露风险

模板中的 `Result.error(e.getMessage())` 会将数据库异常、NPE 等内部错误直接暴露给 API 客户端。

**最小安全实践**：业务校验用 `RuntimeException` 抛出用户可见消息，系统异常（DB 报错等）应返回通用提示：

```java
// 方案：用自定义 BusinessException 区分业务异常 vs 系统异常
// 如果项目已有 BusinessException，优先使用。
// 如果没有，可以用下面的简单约定：

// Service 层抛出可读消息的 RuntimeException（业务异常）
throw new RuntimeException(AgreementConstants.Message.RECORD_NOT_EXIST);

// Controller 层捕获（当前项目模式，与 agreement 模块一致）:
try {
    ...
    return Result.success(Constants.Message.QUERY_SUCCESS, response);
} catch (Exception e) {
    // 当前简单模式：直接返回 e.getMessage()
    // 业务异常会有可读消息；DB 异常消息不友好但可接受（后台系统）
    return Result.error(e.getMessage());
}
```

> 对于面向外部用户的 API，应在全局异常处理器（`ResponseExceptionHandler`）中
> 捕获 `DataAccessException` 等 DB 异常，返回 "系统错误" 而非原始 SQL 错误信息。
