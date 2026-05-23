# Constants Template

**Path**: `modules/{module}/src/main/java/com/bytefactory/quchiv2/{module}/constants/{Module}Constants.java`

Constants use **nested static classes** to group related values. Never use enums — use inner classes with `static final` fields.

## Standard Template

```java
package com.bytefactory.quchiv2.{module}.constants;

/**
 * {中文模块名}常量类
 */
public class {Module}Constants {

    /**
     * {枚举名称}
     */
    public static final class {EnumName} {
        public static final Integer VALUE_ONE = 1;
        public static final Integer VALUE_TWO = 2;
    }

    /**
     * {枚举名称}名称
     */
    public static final class {EnumName}Name {
        public static final String VALUE_ONE = "名称一";
        public static final String VALUE_TWO = "名称二";
    }

    /**
     * 逻辑删除
     */
    public static final class IsDelete {
        /** 已删除 */
        public static final String YES = "Y";
        /** 未删除 */
        public static final String NO = "N";
    }

    /**
     * 响应消息
     */
    public static final class Message {
        public static final String ADD_SUCCESS = "新增成功";
        public static final String EDIT_SUCCESS = "修改成功";
        public static final String DELETE_SUCCESS = "删除成功";
        public static final String QUERY_SUCCESS = "查询成功";

        // 错误消息
        public static final String RECORD_NOT_EXIST = "{实体}不存在";
        public static final String NAME_DUPLICATE = "{实体}名称已存在";
    }

    /**
     * 根据 {枚举名称} 获取名称（用于列表/详情组装）
     */
    public static String get{EnumName}Name(Integer value) {
        if ({EnumName}.VALUE_ONE.equals(value)) {
            return {EnumName}Name.VALUE_ONE;
        } else if ({EnumName}.VALUE_TWO.equals(value)) {
            return {EnumName}Name.VALUE_TWO;
        }
        return "";
    }
}
```

---

## Concrete Example: Agreement Module

```java
public class AgreementConstants {

    public static final class AgreementCategory {
        public static final Integer FRONTEND = 1;
        public static final Integer BACKEND = 2;
    }

    public static final class AgreementCategoryName {
        public static final String FRONTEND = "曲尺前台协议";
        public static final String BACKEND = "曲尺后台协议";
    }

    public static final class IsDelete {
        public static final String YES = "Y";
        public static final String NO = "N";
    }

    public static final class Message {
        public static final String ADD_SUCCESS = "新增成功";
        public static final String EDIT_SUCCESS = "修改成功";
        public static final String DELETE_SUCCESS = "删除成功";
        public static final String QUERY_SUCCESS = "查询成功";
        public static final String PROTOCOL_NOT_EXIST = "协议不存在";
    }

    public static String getAgreementCategoryName(Integer category) {
        if (AgreementCategory.FRONTEND.equals(category)) {
            return AgreementCategoryName.FRONTEND;
        } else if (AgreementCategory.BACKEND.equals(category)) {
            return AgreementCategoryName.BACKEND;
        }
        return "";
    }
}
```

---

## businessType for @Log Annotation

| businessType | Meaning |
|---|---|
| 1 | 新增 |
| 2 | 修改 |
| 3 | 删除 |
| 12 | 查询 |

---

## Common IsDelete Values (Across All Modules)

Every module has its own `IsDelete` inner class with the same values:
- `"N"` = 未删除（正常）
- `"Y"` = 已删除（软删除）

Never change this convention.
