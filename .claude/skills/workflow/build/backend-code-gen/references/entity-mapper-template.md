# Entity & Mapper Templates

All entities and mappers live in `modules/generic-orm-archetype/`.

## Entity Template

**Path**: `modules/generic-orm-archetype/src/main/java/com/bytefactory/quchiv2/orm/entity/{Entity}.java`

```java
package com.bytefactory.quchiv2.orm.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.io.Serializable;

/**
 * {中文名称}实体
 */
@Data
@TableName("{table_name}")
public class {Entity} implements Serializable {

    /**
     * 主键ID
     *
     * 项目约定：使用 UUID 字符串作为主键，在 Service 层手动赋值。
     * - @TableId(type = IdType.INPUT) 更准确（手动输入 ID）
     * - 项目现有代码使用 ASSIGN_ID，但 Service 层手动调用 UUID.randomUUID()，
     *   两者并不冲突（手动赋值优先于自动生成），保持与现有模块一致即可。
     * - 生成 ID 的格式：UUID.randomUUID().toString().replace("-", "")
     */
    @TableId(type = IdType.ASSIGN_ID)
    private String id;

    // --- 业务字段 ---
    // 示例：private String name;
    // 示例：private Integer status;
    // 示例：private String description;

    /**
     * 创建人
     */
    private String creator;

    /**
     * 更新人
     */
    private String updater;

    /**
     * 创建时间（毫秒时间戳）
     */
    private Long createAt;

    /**
     * 更新时间（毫秒时间戳）
     */
    private Long updateAt;

    /**
     * 是否删除（Y=已删除, N=未删除）
     */
    private String isDelete;
}
```

### Field Type Conventions

| Field Type | Java Type | Notes |
|------------|-----------|-------|
| 主键 | `String` | `@TableId(type = IdType.ASSIGN_ID)` |
| 时间戳 | `Long` | 毫秒，`createAt` / `updateAt` |
| 枚举/状态 | `Integer` | 整数值，常量定义在 Constants |
| 标志位 | `String` | `"Y"` / `"N"` |
| 金额 | `BigDecimal` | 精确计算 |
| 大文本 | `String` | 无特殊注解 |
| 逻辑删除 | `String` | `isDelete`，`"Y"`=删除，`"N"`=正常 |

---

## Mapper Template

**Path**: `modules/generic-orm-archetype/src/main/java/com/bytefactory/quchiv2/orm/mapper/{Entity}Mapper.java`

```java
package com.bytefactory.quchiv2.orm.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.bytefactory.quchiv2.orm.entity.{Entity};
import org.apache.ibatis.annotations.Mapper;

/**
 * {中文名称} Mapper
 */
@Mapper
public interface {Entity}Mapper extends BaseMapper<{Entity}> {
    // BaseMapper 已提供完整 CRUD
    // 复杂 SQL 才需要在此添加自定义方法
}
```

### When to Add Custom Methods

Add custom methods to the mapper **only** when:
- JOIN query needed (关联多表)
- Complex aggregation (统计聚合)
- Native SQL required (原生 SQL)

For simple conditions, use `LambdaQueryWrapper` in the service layer instead.

---

## Concrete Example: Protocol Entity

```java
@Data
@TableName("protocol")
public class Protocol implements Serializable {

    @TableId(type = IdType.ASSIGN_ID)
    private String id;

    private Integer agreementCategory;   // 协议分类
    private String agreementNameCn;      // 协议中文名
    private String agreementNameEn;      // 协议英文名
    private String isView;               // 是否显示 Y/N
    private String agreementDocCnId;     // 中文文档ID（关联File表）
    private String agreementDocEnId;     // 英文文档ID（关联File表）

    private String creator;
    private String updater;
    private Long createAt;
    private Long updateAt;
    private String isDelete;
}
```
