# CREATE TABLE SQL Template

## Java → SQL 字段类型映射

| Java 类型 | SQL 类型 | 说明 |
|-----------|----------|------|
| `String` (普通字段) | `VARCHAR(255)` | 默认长度 255 |
| `String` (id 主键) | `VARCHAR(32)` | UUID 去横线，固定 32 位 |
| `String` (is_delete / Y/N 标志) | `VARCHAR(1)` | 只存 Y 或 N |
| `String` (大文本/备注) | `TEXT` | 超长内容用 TEXT |
| `Integer` / `int` | `INT` | 状态码、分类等整数 |
| `Long` / `long` | `BIGINT` | 毫秒时间戳、大整数 |
| `BigDecimal` | `DECIMAL(19,2)` | 金额，精度按业务调整 |
| `Boolean` / `boolean` | `TINYINT(1)` | 0=false, 1=true |

## 命名转换规则

camelCase Java 字段 → snake_case SQL 列名：

| Java 字段 | SQL 列名 |
|-----------|----------|
| `createAt` | `create_at` |
| `updateAt` | `update_at` |
| `isDelete` | `is_delete` |
| `agreementCategory` | `agreement_category` |

## 标准建表模板

```sql
CREATE TABLE `{table_name}` (
    `id`         VARCHAR(32)   NOT NULL                COMMENT '主键ID',

    -- 业务字段（按实体顺序排列）
    -- `field_name` VARCHAR(255) DEFAULT NULL COMMENT '字段说明',

    `creator`    VARCHAR(64)   DEFAULT NULL            COMMENT '创建人',
    `updater`    VARCHAR(64)   DEFAULT NULL            COMMENT '更新人',
    `create_at`  BIGINT        DEFAULT NULL            COMMENT '创建时间（毫秒时间戳）',
    `update_at`  BIGINT        DEFAULT NULL            COMMENT '更新时间（毫秒时间戳）',
    `is_delete`  VARCHAR(1)    NOT NULL DEFAULT 'N'    COMMENT '是否删除（Y=已删除,N=未删除）',

    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='{中文表注释}';
```

## 完整示例：协议表

```sql
CREATE TABLE `protocol` (
    `id`                   VARCHAR(32)   NOT NULL                COMMENT '主键ID',
    `agreement_category`   INT           DEFAULT NULL            COMMENT '协议分类',
    `agreement_name_cn`    VARCHAR(255)  DEFAULT NULL            COMMENT '协议中文名',
    `agreement_name_en`    VARCHAR(255)  DEFAULT NULL            COMMENT '协议英文名',
    `is_view`              VARCHAR(1)    DEFAULT NULL            COMMENT '是否显示（Y=显示,N=隐藏）',
    `agreement_doc_cn_id`  VARCHAR(32)   DEFAULT NULL            COMMENT '中文文档ID',
    `agreement_doc_en_id`  VARCHAR(32)   DEFAULT NULL            COMMENT '英文文档ID',
    `creator`              VARCHAR(64)   DEFAULT NULL            COMMENT '创建人',
    `updater`              VARCHAR(64)   DEFAULT NULL            COMMENT '更新人',
    `create_at`            BIGINT        DEFAULT NULL            COMMENT '创建时间（毫秒时间戳）',
    `update_at`            BIGINT        DEFAULT NULL            COMMENT '更新时间（毫秒时间戳）',
    `is_delete`            VARCHAR(1)    NOT NULL DEFAULT 'N'    COMMENT '是否删除（Y=已删除,N=未删除）',
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='协议表';
```

## 注意事项

- 关联外键字段（如 `agreement_doc_cn_id`）使用 `VARCHAR(32)` 与主键保持一致，**不添加 FOREIGN KEY 约束**（项目约定在代码层保证一致性）
- 有索引需求的查询字段可在建表后追加 `CREATE INDEX`，不在建表语句中内联
- `NOT NULL` 字段须提供 `DEFAULT` 值，避免插入时报错
