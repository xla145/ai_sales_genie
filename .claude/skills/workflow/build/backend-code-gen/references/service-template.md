# Service Templates

## Service Interface

**Path**: `modules/{module}/src/main/java/com/bytefactory/quchiv2/{module}/service/{Feature}Service.java`

```java
package com.bytefactory.quchiv2.{module}.service;

import com.bytefactory.quchiv2.{module}.dto.request.*;
import com.bytefactory.quchiv2.{module}.dto.response.*;
import com.bytefactory.quchiv2.{module}.dto.response.common.PageResponse;

import java.util.List;

/**
 * {中文名称}服务接口
 */
public interface {Feature}Service {

    /**
     * 查询{中文名称}列表
     */
    PageResponse<{Feature}ListResponse> query{Feature}List({Feature}QueryRequest request);

    /**
     * 新增{中文名称}
     */
    void add{Feature}({Feature}AddRequest request);

    /**
     * 修改{中文名称}
     */
    void edit{Feature}({Feature}EditRequest request);

    /**
     * 删除{中文名称}
     */
    void delete{Feature}({Feature}DeleteRequest request);

    /**
     * 查询{中文名称}详情
     */
    {Feature}DetailResponse query{Feature}Detail({Feature}DetailRequest request);

    // 如有字典接口，添加：
    // List<{Feature}TypeDictResponse> query{Feature}TypeDict();
}
```

---

## Service Implementation

**Path**: `modules/{module}/src/main/java/com/bytefactory/quchiv2/{module}/service/impl/{Feature}ServiceImpl.java`

```java
package com.bytefactory.quchiv2.{module}.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.bytefactory.quchiv2.{module}.constants.{Module}Constants;
import com.bytefactory.quchiv2.{module}.dto.request.*;
import com.bytefactory.quchiv2.{module}.dto.response.*;
import com.bytefactory.quchiv2.{module}.dto.response.common.PageResponse;
import com.bytefactory.quchiv2.{module}.service.{Feature}Service;
import com.bytefactory.quchiv2.orm.entity.{Entity};
import com.bytefactory.quchiv2.orm.entity.SysUser;
import com.bytefactory.quchiv2.orm.mapper.{Entity}Mapper;
import com.bytefactory.quchiv2.orm.mapper.SysUserMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.util.StringUtils;

import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;

/**
 * {中文名称}服务实现类
 */
@Service
@RequiredArgsConstructor
public class {Feature}ServiceImpl extends ServiceImpl<{Entity}Mapper, {Entity}> implements {Feature}Service {

    private final {Entity}Mapper {entity}Mapper;
    private final SysUserMapper sysUserMapper;

    @Override
    public PageResponse<{Feature}ListResponse> query{Feature}List({Feature}QueryRequest request) {
        // 构建查询条件
        LambdaQueryWrapper<{Entity}> queryWrapper = new LambdaQueryWrapper<>();
        queryWrapper.eq({Entity}::getIsDelete, {Module}Constants.IsDelete.NO);

        // 可选过滤条件（模糊搜索）
        if (StringUtils.hasText(request.getName())) {
            queryWrapper.like({Entity}::getName, request.getName());
        }

        // 枚举过滤
        // if (request.getType() != null) {
        //     queryWrapper.eq({Entity}::getType, request.getType());
        // }

        queryWrapper.orderByDesc({Entity}::getUpdateAt);

        // 分页查询
        Page<{Entity}> page = new Page<>(request.getPageNum(), request.getPageSize());
        IPage<{Entity}> resultPage = {entity}Mapper.selectPage(page, queryWrapper);

        // 组装响应
        List<{Feature}ListResponse> responseList = resultPage.getRecords().stream().map(entity -> {
            {Feature}ListResponse response = new {Feature}ListResponse();
            response.setId(entity.getId());
            response.setName(entity.getName());
            response.setType(entity.getType());
            response.setTypeName({Module}Constants.getTypeName(entity.getType()));
            response.setUpdater(entity.getUpdater());
            response.setUpdateAt(entity.getUpdateAt());
            return response;
        }).collect(Collectors.toList());

        PageResponse<{Feature}ListResponse> pageResponse = new PageResponse<>();
        pageResponse.setRecords(responseList);
        pageResponse.setTotal(resultPage.getTotal());
        pageResponse.setPageNum(request.getPageNum());
        pageResponse.setPageSize(request.getPageSize());

        return pageResponse;
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public void add{Feature}({Feature}AddRequest request) {
        String currentUserName = getCurrentUserName();

        {Entity} entity = new {Entity}();
        entity.setId(UUID.randomUUID().toString().replace("-", ""));
        entity.setName(request.getName());
        entity.setType(request.getType());
        entity.setDescription(request.getDescription());
        entity.setCreator(currentUserName);
        entity.setUpdater(currentUserName);
        entity.setCreateAt(System.currentTimeMillis());
        entity.setUpdateAt(System.currentTimeMillis());
        entity.setIsDelete({Module}Constants.IsDelete.NO);

        {entity}Mapper.insert(entity);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public void edit{Feature}({Feature}EditRequest request) {
        // 校验是否存在
        {Entity} exist = {entity}Mapper.selectById(request.getId());
        if (exist == null || {Module}Constants.IsDelete.YES.equals(exist.getIsDelete())) {
            throw new RuntimeException({Module}Constants.Message.RECORD_NOT_EXIST);
        }

        String currentUserName = getCurrentUserName();

        {Entity} entity = new {Entity}();
        entity.setId(request.getId());
        entity.setName(request.getName());
        entity.setType(request.getType());
        entity.setDescription(request.getDescription());
        entity.setUpdater(currentUserName);
        entity.setUpdateAt(System.currentTimeMillis());

        {entity}Mapper.updateById(entity);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public void delete{Feature}({Feature}DeleteRequest request) {
        // 校验是否存在
        {Entity} exist = {entity}Mapper.selectById(request.getId());
        if (exist == null || {Module}Constants.IsDelete.YES.equals(exist.getIsDelete())) {
            throw new RuntimeException({Module}Constants.Message.RECORD_NOT_EXIST);
        }

        String currentUserName = getCurrentUserName();

        // 逻辑删除
        {Entity} entity = new {Entity}();
        entity.setId(request.getId());
        entity.setIsDelete({Module}Constants.IsDelete.YES);
        entity.setUpdater(currentUserName);
        entity.setUpdateAt(System.currentTimeMillis());

        {entity}Mapper.updateById(entity);
    }

    @Override
    public {Feature}DetailResponse query{Feature}Detail({Feature}DetailRequest request) {
        {Entity} entity = {entity}Mapper.selectById(request.getId());
        if (entity == null || {Module}Constants.IsDelete.YES.equals(entity.getIsDelete())) {
            throw new RuntimeException({Module}Constants.Message.RECORD_NOT_EXIST);
        }

        {Feature}DetailResponse response = new {Feature}DetailResponse();
        response.setId(entity.getId());
        response.setName(entity.getName());
        response.setType(entity.getType());
        response.setTypeName({Module}Constants.getTypeName(entity.getType()));
        response.setDescription(entity.getDescription());
        response.setCreator(entity.getCreator());
        response.setCreateAt(entity.getCreateAt());
        response.setUpdater(entity.getUpdater());
        response.setUpdateAt(entity.getUpdateAt());

        return response;
    }

    /**
     * 获取当前登录用户名
     *
     * 注意：此方法在项目各模块中重复实现（DRY 问题）。
     * 如果 system-management 模块提供了 UserContextHolder 或类似工具类，优先使用它。
     * 当前作为项目既有模式保留，与 agreement 等模块保持一致。
     *
     * ⚠️ 需要 Spring Security 上下文存在（HTTP 请求范围内有效）。
     * 在定时任务、异步线程等无 SecurityContext 的场景不可直接调用。
     */
    private String getCurrentUserName() {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        String userId = authentication.getName();

        LambdaQueryWrapper<SysUser> userWrapper = new LambdaQueryWrapper<>();
        userWrapper.eq(SysUser::getUserId, userId);
        SysUser sysUser = sysUserMapper.selectOne(userWrapper);

        return sysUser != null ? sysUser.getUserName() : "system";
    }
}
```

---

## Key Patterns

### 1. Soft Delete Check

Always check both null AND `isDelete == "Y"` before write operations:
```java
{Entity} exist = {entity}Mapper.selectById(request.getId());
if (exist == null || {Module}Constants.IsDelete.YES.equals(exist.getIsDelete())) {
    throw new RuntimeException({Module}Constants.Message.RECORD_NOT_EXIST);
}
```

> **⚠️ TOCTOU 并发说明**：`selectById` → `updateById` 之间不是原子操作。
> 高并发场景（两个请求同时 edit 同一条记录）可能都通过校验后双写。
> 对于**普通管理后台**，该风险可接受（管理员操作频率低）。
> 对于**高并发或金融类操作**，应加乐观锁：Entity 添加 `version` 字段 +
> `@Version` 注解，MyBatis Plus 自动处理 CAS 更新。

### 2. LambdaQueryWrapper — Conditional Filters

```java
LambdaQueryWrapper<{Entity}> wrapper = new LambdaQueryWrapper<>();
wrapper.eq({Entity}::getIsDelete, {Module}Constants.IsDelete.NO);

// String filter — only apply when not empty
if (StringUtils.hasText(request.getName())) {
    wrapper.like({Entity}::getName, request.getName());
}

// Integer filter — only apply when not null
if (request.getType() != null) {
    wrapper.eq({Entity}::getType, request.getType());
}

// Date range filter
if (request.getStartTime() != null) {
    wrapper.ge({Entity}::getCreateAt, request.getStartTime());
}
if (request.getEndTime() != null) {
    wrapper.le({Entity}::getCreateAt, request.getEndTime());
}

wrapper.orderByDesc({Entity}::getUpdateAt);
```

### 3. One-to-Many Sub-entities

When the entity has child records (e.g., tags, scenarios), handle in add/edit:

```java
// In add: save sub-entities after main entity
saveSubEntities(entity.getId(), request.getTagIds(), currentUserName);

// In edit: delete all old → insert new
LambdaQueryWrapper<SubEntity> deleteWrapper = new LambdaQueryWrapper<>();
deleteWrapper.eq(SubEntity::getParentId, request.getId());
subEntityMapper.delete(deleteWrapper);
saveSubEntities(request.getId(), request.getTagIds(), currentUserName);

// Helper method
private void saveSubEntities(String parentId, List<Integer> items, String userName) {
    if (items == null || items.isEmpty()) return;
    for (Integer item : items) {
        SubEntity sub = new SubEntity();
        sub.setId(UUID.randomUUID().toString().replace("-", ""));
        sub.setParentId(parentId);
        sub.setValue(item);
        sub.setCreator(userName);
        sub.setUpdater(userName);
        sub.setCreateAt(System.currentTimeMillis());
        sub.setUpdateAt(System.currentTimeMillis());
        sub.setIsDelete({Module}Constants.IsDelete.NO);
        subEntityMapper.insert(sub);
    }
}
```
