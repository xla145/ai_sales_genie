# End-to-End CRUD Pattern Reference

This file shows complete patterns for three scenarios. Use `modules/agreement/` as the canonical example.

---

## Standard CRUD (标准增删改查)

The most common pattern. Five endpoints: list, add, edit, delete, detail.

### Entity Fields (Minimum)

```java
@Data
@TableName("{table_name}")
public class {Entity} implements Serializable {
    @TableId(type = IdType.ASSIGN_ID)
    private String id;

    private String name;          // 业务字段
    private Integer type;         // 枚举字段
    private String description;   // 描述（可选）

    private String creator;
    private String updater;
    private Long createAt;
    private Long updateAt;
    private String isDelete;      // "Y"=删除, "N"=正常
}
```

### Request/Response Summary

| Class | Key Fields | Notes |
|-------|-----------|-------|
| `QueryRequest` | name?, type?, pageNum=1, pageSize=10 | 所有过滤条件可选 |
| `AddRequest` | name@NotBlank, type@NotNull, description? | 必填加验证注解 |
| `EditRequest` | id@NotBlank, name@NotBlank, type@NotNull | 同 Add + id |
| `DeleteRequest` | id@NotBlank | 仅 ID |
| `DetailRequest` | id@NotBlank | 仅 ID |
| `ListResponse` | id, name, type, typeName, updater, updateAt | 列表精简字段 |
| `DetailResponse` | 所有字段，含 creator, createAt | 详情完整字段 |

---

## Read-Only Pattern (只读/字典)

Use when the module only needs to display data (no write operations).

### Controller — Read Only

```java
@RestController
@RequestMapping("/api/{module}/{feature}")
@RequiredArgsConstructor
@Tag(name = "{中文名称}查询", description = "{中文名称}查询接口")
public class {Feature}Controller {

    private final {Feature}Service {feature}Service;

    @PostMapping("/list")
    @Operation(summary = "查询{中文名称}列表")
    @Log(title = "查询{中文名称}列表", businessType = 12)
    public Result<PageResponse<{Feature}ListResponse>> query{Feature}List(
            @Valid @RequestBody {Feature}QueryRequest request) {
        try {
            return Result.success({Module}Constants.Message.QUERY_SUCCESS,
                    {feature}Service.query{Feature}List(request));
        } catch (Exception e) {
            return Result.error(e.getMessage());
        }
    }

    @PostMapping("/detail")
    @Operation(summary = "查询{中文名称}详情")
    @Log(title = "查询{中文名称}详情", businessType = 12)
    public Result<{Feature}DetailResponse> query{Feature}Detail(
            @Valid @RequestBody {Feature}DetailRequest request) {
        try {
            return Result.success({Module}Constants.Message.QUERY_SUCCESS,
                    {feature}Service.query{Feature}Detail(request));
        } catch (Exception e) {
            return Result.error(e.getMessage());
        }
    }
}
```

---

## With Relations Pattern (含子实体)

Use when the main entity has one-to-many child records (e.g., tags, scenarios, configs).

### Additional Mapper Injection

```java
// ServiceImpl — add sub-entity mapper
private final {SubEntity}Mapper {subEntity}Mapper;
```

### Add with Sub-entities

```java
@Override
@Transactional(rollbackFor = Exception.class)
public void add{Feature}({Feature}AddRequest request) {
    String currentUserName = getCurrentUserName();

    // 1. Insert main entity
    {Entity} entity = buildEntity(request, currentUserName);
    entity.setId(UUID.randomUUID().toString().replace("-", ""));
    {entity}Mapper.insert(entity);

    // 2. Insert sub-entities
    save{SubEntities}(entity.getId(), request.get{SubItems}(), currentUserName);
}
```

### Edit with Sub-entities (Delete-Insert Pattern)

```java
@Override
@Transactional(rollbackFor = Exception.class)
public void edit{Feature}({Feature}EditRequest request) {
    // Validate
    {Entity} exist = {entity}Mapper.selectById(request.getId());
    if (exist == null || {Module}Constants.IsDelete.YES.equals(exist.getIsDelete())) {
        throw new RuntimeException({Module}Constants.Message.RECORD_NOT_EXIST);
    }

    String currentUserName = getCurrentUserName();

    // 1. Update main entity
    {Entity} entity = new {Entity}();
    entity.setId(request.getId());
    // ... set fields ...
    entity.setUpdater(currentUserName);
    entity.setUpdateAt(System.currentTimeMillis());
    {entity}Mapper.updateById(entity);

    // 2. Delete old sub-entities
    LambdaQueryWrapper<{SubEntity}> deleteWrapper = new LambdaQueryWrapper<>();
    deleteWrapper.eq({SubEntity}::get{ParentId}Field, request.getId());
    {subEntity}Mapper.delete(deleteWrapper);

    // 3. Insert new sub-entities
    save{SubEntities}(request.getId(), request.get{SubItems}(), currentUserName);
}
```

### Sub-entity Save Helper

> **⚠️ 性能提示**: 子实体数量可能较多时，用 `IService.saveBatch()` 代替逐条 insert。

**逐条 insert（适合 ≤10 条）**:
```java
private void save{SubEntities}(String parentId, List<Integer> items, String userName) {
    if (items == null || items.isEmpty()) return;
    for (Integer item : items) {
        {SubEntity} sub = new {SubEntity}();
        sub.setId(UUID.randomUUID().toString().replace("-", ""));
        sub.set{ParentId}(parentId);
        sub.setValue(item);
        sub.setCreator(userName);
        sub.setUpdater(userName);
        sub.setCreateAt(System.currentTimeMillis());
        sub.setUpdateAt(System.currentTimeMillis());
        sub.setIsDelete({Module}Constants.IsDelete.NO);
        {subEntity}Mapper.insert(sub);
    }
}
```

**批量 insert（数量不确定时推荐）**:
```java
// ServiceImpl 改继承 ServiceImpl<{SubEntity}Mapper, {SubEntity}>
// 或注入子实体 Service，调用 saveBatch()
private void save{SubEntities}(String parentId, List<Integer> items, String userName) {
    if (items == null || items.isEmpty()) return;
    long now = System.currentTimeMillis();
    List<{SubEntity}> subList = items.stream().map(item -> {
        {SubEntity} sub = new {SubEntity}();
        sub.setId(UUID.randomUUID().toString().replace("-", ""));
        sub.set{ParentId}(parentId);
        sub.setValue(item);
        sub.setCreator(userName);
        sub.setUpdater(userName);
        sub.setCreateAt(now);
        sub.setUpdateAt(now);
        sub.setIsDelete({Module}Constants.IsDelete.NO);
        return sub;
    }).collect(Collectors.toList());
    // 使用 MyBatis Plus 批量插入
    subList.forEach(sub -> {subEntity}Mapper.insert(sub));
}
```

> **子实体删除策略说明（重要）**:
> 本项目 edit 操作对子实体使用**物理删除**（`mapper.delete(wrapper)`），不是软删除。
> 这是项目既有约定：子实体生命周期依附主实体，不需要独立的逻辑删除。
> 生成代码时**不要**给子实体的删除改为 `isDelete = "Y"` 软删，保持物理删除。

### List/Detail with Sub-entities

> **⚠️ N+1 警告**: 不要在 stream 内对每条主记录单独查子实体。
> 正确做法：**先批量查所有子实体 → 内存分组 → 组装响应**。

```java
// ✅ 正确：批量查询，避免 N+1
List<{Entity}> records = resultPage.getRecords();
List<String> parentIds = records.stream()
        .map({Entity}::getId)
        .collect(Collectors.toList());

// 一次性查所有子实体
Map<String, List<{SubEntity}>> subMap = Collections.emptyMap();
if (!parentIds.isEmpty()) {
    LambdaQueryWrapper<{SubEntity}> subWrapper = new LambdaQueryWrapper<>();
    subWrapper.in({SubEntity}::get{ParentId}Field, parentIds);
    subWrapper.eq({SubEntity}::getIsDelete, {Module}Constants.IsDelete.NO);
    List<{SubEntity}> allSubs = {subEntity}Mapper.selectList(subWrapper);
    subMap = allSubs.stream()
            .collect(Collectors.groupingBy({SubEntity}::get{ParentId}Field));
}

// 在 stream 中仅做内存 get
final Map<String, List<{SubEntity}>> finalSubMap = subMap;
List<{Feature}ListResponse> responseList = records.stream().map(entity -> {
    {Feature}ListResponse response = new {Feature}ListResponse();
    response.setId(entity.getId());
    // ... 其他字段 ...

    List<{SubEntity}> subs = finalSubMap.getOrDefault(entity.getId(), Collections.emptyList());
    List<Integer> subValues = subs.stream().map({SubEntity}::getValue).collect(Collectors.toList());
    response.set{SubValues}(subValues);
    List<String> subNames = subValues.stream()
            .map({Module}Constants::get{ValueName})
            .collect(Collectors.toList());
    response.set{SubNames}(subNames);
    return response;
}).collect(Collectors.toList());
```

> detail 接口只查单条记录，可直接查子实体，无 N+1 风险。

---

## File Reference Pattern (含文件引用)

When entity references files (e.g., doc files, images), load from `FileMapper`:

### Entity Fields

```java
private String docCnId;   // 关联 File 表 ID
private String docEnId;   // 关联 File 表 ID（如需中英文）
```

### ServiceImpl — Load File in Detail

```java
// Inject FileMapper
private final FileMapper fileMapper;

// In queryDetail:
if (StringUtils.hasText(entity.getDocCnId())) {
    File file = fileMapper.selectById(entity.getDocCnId());
    if (file != null) {
        FileInfo fileInfo = new FileInfo();
        fileInfo.setId(file.getId());
        fileInfo.setFileName(file.getFileName());
        fileInfo.setFilePath(file.getFilePath());
        fileInfo.setFileSize(file.getFileSize());
        fileInfo.setFileType(file.getFileType());
        response.setDocCn(fileInfo);
    }
}
```

### FileInfo Inner Class (or Separate DTO)

```java
@Data
@Schema(description = "文件信息")
public class FileInfo {
    @JsonProperty("id")
    private String id;
    @JsonProperty("file_name")
    private String fileName;
    @JsonProperty("file_path")
    private String filePath;
    @JsonProperty("file_size")
    private Long fileSize;
    @JsonProperty("file_type")
    private String fileType;
}
```

---

## Generation Checklist

Before delivering generated code, verify:

- [ ] Package names match `com.bytefactory.quchiv2.{module}.*`
- [ ] Entity uses `@TableName("{table_name}")` matching actual DB table
- [ ] `@TableId(type = IdType.ASSIGN_ID)` on `id` field
- [ ] All timestamps as `Long` (milliseconds)
- [ ] `isDelete` field: `"Y"` = deleted, `"N"` = normal
- [ ] All write operations are `@Transactional(rollbackFor = Exception.class)`
- [ ] All POST endpoints use `@Log(title = "...", businessType = N)`
- [ ] `getCurrentUserName()` uses `SecurityContextHolder` + `SysUserMapper`
- [ ] Every endpoint wrapped in `try/catch` → `Result.success/error`
- [ ] `pageNum` defaults to `1`, `pageSize` defaults to `10` in QueryRequest
- [ ] List ordered by `updateAt DESC`
- [ ] Module registered in root `pom.xml`
