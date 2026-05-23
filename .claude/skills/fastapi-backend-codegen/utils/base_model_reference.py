"""
Base模型参考文档
所有Model必须继承自Base类，自动获得以下功能
"""
# Base模型位置: app/models/base.py

# ==================== 公共字段 ====================
"""
所有继承Base的模型自动获得以下字段：
- id: BIGINT, 主键, 自增
- creation_date: DATETIME, 创建时间, 自动设置
- created_by: BIGINT, 创建人ID, 自动从token获取
- updation_date: DATETIME, 更新时间, 自动更新
- updated_by: BIGINT, 更新人ID, 自动从token获取
- enabled_flag: BOOLEAN, 是否删除(0删除,1未删除), 默认1
- trace_id: VARCHAR(255), 追踪ID, 自动从上下文获取
"""

# ==================== 基础CRUD方法 ====================

# 1. 查询方法
"""
# 根据ID查询单条记录
result = await Model.get(id, to_dict=False)  # 返回模型对象
result = await Model.get(id, to_dict=True)   # 返回字典

# 查询所有记录
results = await Model.get_all()  # 返回list[dict]

# 分页查询
results = await Model.pagination(stmt)  # 返回分页结果
"""

# 2. 创建方法
"""
# 创建单条记录
params = {"name": "test", "description": "desc"}
result = await Model.create(params, to_dict=False)  # 返回模型对象
result = await Model.create(params, to_dict=True)    # 返回字典

# 批量创建
params_list = [{"name": "test1"}, {"name": "test2"}]
count = await Model.batch_create(params_list)  # 返回插入数量
"""

# 3. 更新方法
"""
# 更新记录（全量更新，包括None值）
params = {"id": 1, "name": "new_name", "description": None}
result = await Model.update(params, to_dict=False)

# 更新非空字段（忽略None值）- 推荐使用
params = {"id": 1, "name": "new_name"}  # description不会被更新
result = await Model.update_non_null_fields(params, to_dict=False)

# 使用model_dump(exclude_unset=True)只更新提供的字段
update_params = data.model_dump(exclude_unset=True)
update_params["id"] = id
result = await Model.update(update_params)

# 根据条件更新
where_conditions = [Model.status == "active"]
params = {"status": "inactive"}
await Model.update_with_conditions(params, where_conditions)
"""

# 4. 删除方法
"""
# 软删除（默认）
count = await Model.delete(id)  # 设置enabled_flag=0

# 物理删除
count = await Model.delete(id, _hard=True)  # 真正删除记录

# 根据条件删除
where_conditions = [Model.status == "deleted"]
count = await Model.delete_with_conditions(where_conditions)
"""

# ==================== 自定义查询方法示例 ====================
"""
class Project(Base):
    __tablename__ = "projects"
    
    name = Column(String(255), nullable=False)
    status = Column(String(50), default="draft")
    
    @classmethod
    async def get_by_status(cls, status: str):
        \"\"\"按状态查询项目列表\"\"\"
        query_conditions = [
            cls.enabled_flag == 1,  # 必须包含此条件
            cls.status == status
        ]
        stmt = select(*cls.get_table_columns()).where(and_(*query_conditions))
        return await cls.get_result(stmt)
    
    @classmethod
    async def get_data_with_pagination(cls, status: str = None, name: str = None):
        \"\"\"分页查询项目\"\"\"
        query_conditions = [cls.enabled_flag == 1]  # 必须包含此条件
        if status:
            query_conditions.append(cls.status == status)
        if name:
            query_conditions.append(cls.name.like(f"%{name}%"))
        stmt = select(*cls.get_table_columns()).where(and_(*query_conditions))
        return await cls.pagination(stmt)
"""

# ==================== 重要注意事项 ====================
"""
1. 所有查询方法必须包含 enabled_flag == 1 条件
2. 使用 get_table_columns() 避免返回模型对象
3. 复杂查询封装为类方法
4. 使用索引优化查询
5. 不要直接操作数据库，所有操作通过Base提供的方法
"""
