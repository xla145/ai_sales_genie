# DTO Templates

All DTOs use `@Data` (Lombok), `@Schema` (Knife4j), `@JsonProperty("snake_case")` mapping.

---

## Common Classes

These are copied into every new module under `dto/response/common/`.

### Result.java

```java
package com.bytefactory.quchiv2.{module}.dto.response.common;

import com.fasterxml.jackson.annotation.JsonProperty;
import io.swagger.v3.oas.annotations.media.Schema;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Schema(description = "统一响应结果")
public class Result<T> {

    @JsonProperty("code")
    private Integer code;

    @JsonProperty("message")
    private String message;

    @JsonProperty("timestamp")
    private Long timestamp;

    @JsonProperty("data")
    private T data;

    public static <T> Result<T> success(T data) {
        return new Result<>(200, "success", System.currentTimeMillis(), data);
    }

    public static <T> Result<T> success() {
        return new Result<>(200, "success", System.currentTimeMillis(), null);
    }

    public static <T> Result<T> success(String message, T data) {
        return new Result<>(200, message, System.currentTimeMillis(), data);
    }

    public static <T> Result<T> error(String message) {
        return new Result<>(500, message, System.currentTimeMillis(), null);
    }

    public static <T> Result<T> error(Integer code, String message) {
        return new Result<>(code, message, System.currentTimeMillis(), null);
    }
}
```

### PageResponse.java

```java
package com.bytefactory.quchiv2.{module}.dto.response.common;

import com.fasterxml.jackson.annotation.JsonProperty;
import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;

import java.util.List;

@Data
@Schema(description = "分页响应")
public class PageResponse<T> {

    @JsonProperty("records")
    private List<T> records;

    @JsonProperty("total")
    private Long total;

    @JsonProperty("page_num")
    private Integer pageNum;

    @JsonProperty("page_size")
    private Integer pageSize;
}
```

---

## Request Templates

### {Feature}QueryRequest.java — 分页查询

```java
package com.bytefactory.quchiv2.{module}.dto.request;

import com.fasterxml.jackson.annotation.JsonProperty;
import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;

@Data
@Schema(description = "{中文名称}查询请求")
public class {Feature}QueryRequest {

    // 可选过滤条件（不加 @NotNull）
    @Schema(description = "名称")
    @JsonProperty("name")
    private String name;

    // 枚举过滤条件示例
    // @JsonProperty("status")
    // private Integer status;

    @Schema(description = "页码", example = "1")
    @JsonProperty("page_num")
    private Integer pageNum = 1;

    @Schema(description = "每页大小", example = "10")
    @JsonProperty("page_size")
    private Integer pageSize = 10;
}
```

### {Feature}AddRequest.java — 新增

```java
package com.bytefactory.quchiv2.{module}.dto.request;

import com.fasterxml.jackson.annotation.JsonProperty;
import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.Data;

@Data
@Schema(description = "{中文名称}新增请求")
public class {Feature}AddRequest {

    @Schema(description = "名称")
    @JsonProperty("name")
    @NotBlank(message = "名称不能为空")
    private String name;

    // Integer 字段用 @NotNull
    @Schema(description = "类型")
    @JsonProperty("type")
    @NotNull(message = "类型不能为空")
    private Integer type;

    // 可选字段不加验证注解
    @Schema(description = "描述")
    @JsonProperty("description")
    private String description;
}
```

### {Feature}EditRequest.java — 修改

```java
package com.bytefactory.quchiv2.{module}.dto.request;

import com.fasterxml.jackson.annotation.JsonProperty;
import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.NotBlank;
import lombok.Data;

@Data
@Schema(description = "{中文名称}修改请求")
public class {Feature}EditRequest {

    @Schema(description = "ID")
    @JsonProperty("id")
    @NotBlank(message = "ID不能为空")
    private String id;

    // 同 AddRequest 字段，通常保持一致
    @Schema(description = "名称")
    @JsonProperty("name")
    @NotBlank(message = "名称不能为空")
    private String name;

    @Schema(description = "类型")
    @JsonProperty("type")
    @NotNull(message = "类型不能为空")
    private Integer type;

    @Schema(description = "描述")
    @JsonProperty("description")
    private String description;
}
```

### {Feature}DeleteRequest.java — 删除

```java
package com.bytefactory.quchiv2.{module}.dto.request;

import com.fasterxml.jackson.annotation.JsonProperty;
import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.NotBlank;
import lombok.Data;

@Data
@Schema(description = "{中文名称}删除请求")
public class {Feature}DeleteRequest {

    @Schema(description = "ID")
    @JsonProperty("id")
    @NotBlank(message = "ID不能为空")
    private String id;
}
```

### {Feature}DetailRequest.java — 详情

```java
package com.bytefactory.quchiv2.{module}.dto.request;

import com.fasterxml.jackson.annotation.JsonProperty;
import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.NotBlank;
import lombok.Data;

@Data
@Schema(description = "{中文名称}详情请求")
public class {Feature}DetailRequest {

    @Schema(description = "ID")
    @JsonProperty("id")
    @NotBlank(message = "ID不能为空")
    private String id;
}
```

---

## Response Templates

### {Feature}ListResponse.java — 列表项

```java
package com.bytefactory.quchiv2.{module}.dto.response;

import com.fasterxml.jackson.annotation.JsonProperty;
import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;

@Data
@Schema(description = "{中文名称}列表响应")
public class {Feature}ListResponse {

    @Schema(description = "ID")
    @JsonProperty("id")
    private String id;

    @Schema(description = "名称")
    @JsonProperty("name")
    private String name;

    @Schema(description = "类型")
    @JsonProperty("type")
    private Integer type;

    @Schema(description = "类型名称")
    @JsonProperty("type_name")
    private String typeName;

    @Schema(description = "更新人")
    @JsonProperty("updater")
    private String updater;

    @Schema(description = "更新时间")
    @JsonProperty("update_at")
    private Long updateAt;
}
```

### {Feature}DetailResponse.java — 详情

```java
package com.bytefactory.quchiv2.{module}.dto.response;

import com.fasterxml.jackson.annotation.JsonProperty;
import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;

@Data
@Schema(description = "{中文名称}详情响应")
public class {Feature}DetailResponse {

    @Schema(description = "ID")
    @JsonProperty("id")
    private String id;

    @Schema(description = "名称")
    @JsonProperty("name")
    private String name;

    @Schema(description = "类型")
    @JsonProperty("type")
    private Integer type;

    @Schema(description = "类型名称")
    @JsonProperty("type_name")
    private String typeName;

    @Schema(description = "描述")
    @JsonProperty("description")
    private String description;

    @Schema(description = "创建人")
    @JsonProperty("creator")
    private String creator;

    @Schema(description = "创建时间")
    @JsonProperty("create_at")
    private Long createAt;

    @Schema(description = "更新人")
    @JsonProperty("updater")
    private String updater;

    @Schema(description = "更新时间")
    @JsonProperty("update_at")
    private Long updateAt;
}
```

### Dict Response (字典/下拉) Template

```java
package com.bytefactory.quchiv2.{module}.dto.response;

import com.fasterxml.jackson.annotation.JsonProperty;
import io.swagger.v3.oas.annotations.media.Schema;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Schema(description = "{中文名称}字典响应")
public class {Feature}DictResponse {

    @Schema(description = "值")
    @JsonProperty("value")
    private Integer value;

    @Schema(description = "标签")
    @JsonProperty("label")
    private String label;
}
```

---

## Validation Annotations Quick Reference

| Annotation | Applies To | Meaning |
|------------|-----------|---------|
| `@NotBlank` | String | 不为空且不为空字符串 |
| `@NotNull` | Integer, Object | 不为 null |
| `@NotEmpty` | List, Collection | 不为空集合 |
| `@Min(1)` | Integer | 最小值 |
| `@Max(100)` | Integer | 最大值 |
| `@Size(min=1, max=100)` | String, List | 长度/大小范围 |
