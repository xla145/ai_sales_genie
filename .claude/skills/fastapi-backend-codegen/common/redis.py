# -*- coding: utf-8 -*-
"""
Redis连接模块
生成代码时可以直接导入使用: from app.db.redis import redis_pool
"""
import json
import pickle
import typing

from redis import Redis as SyncRedis
from redis import asyncio as aioredis
from redis.typing import KeyT, FieldT, EncodableT, AnyFieldT


class MyAsyncRedis(aioredis.Redis):
    """异步Redis客户端，自动处理JSON序列化"""

    async def get(self, name: str) -> typing.Any:
        """获取值，自动反序列化JSON"""
        data = await super(MyAsyncRedis, self).get(name)
        return json.loads(data) if data else None

    async def set(
            self,
            name: str,
            value: typing.Any,
            ex: typing.Optional[int] = None,
            px: typing.Optional[int] = None,
            nx: bool = False,
            xx: bool = False,
            get: bool = False,
            keepttl: bool = False,
    ) -> typing.Any:
        """
        设置键值对，支持 Redis SET 命令的所有选项
        :param name: 键名
        :param value: 值（会自动序列化为 JSON）
        :param ex: 过期时间（秒）
        :param px: 过期时间（毫秒）
        :param nx: 只在键不存在时设置
        :param xx: 只在键存在时设置
        :param get: 返回旧值
        :param keepttl: 保持原有过期时间
        :return: 设置结果
        """
        # 如果 value 已经是 JSON 字符串格式，直接使用
        if isinstance(value, str) and (value.startswith('{') or value.startswith('[') or (value.startswith('"') and value.endswith('"'))):
            try:
                json.loads(value)
                json_value = value
            except (json.JSONDecodeError, TypeError):
                json_value = json.dumps(value)
        else:
            json_value = json.dumps(value)
        
        return await super(MyAsyncRedis, self).set(
            name, 
            json_value, 
            ex=ex, 
            px=px, 
            nx=nx, 
            xx=xx, 
            get=get, 
            keepttl=keepttl
        )

    async def list_loads(self, key: str, num: int = -1) -> list:
        """
        将列表字符串转为对象
        :param key: 列表的key
        :param num: 最大长度(默认值 -1-全部)
        :return: 列表对象
        """
        todo_list = await self.lrange(key, 0, (num - 1) if num > -1 else num)
        return [json.loads(todo) for todo in todo_list]

    async def cus_lpush(self, key: str, value: typing.Union[str, list, dict]):
        """
        向列表左侧插入数据（JSON序列化）
        :param key: 列表的key
        :param value: 插入的值
        """
        text = json.dumps(value)
        await self.lpush(key, text)

    async def cus_lpop(self, key: str):
        """
        获取list数据（JSON反序列化）
        :param key: 列表的key
        """
        r = await self.lpop(key)
        if r:
            return json.loads(r)
        return None

    async def cus_lpush_by_pickle(self, key: str, value: typing.Union[str, list, dict]):
        """
        向列表左侧插入数据（Pickle序列化）
        :param key: 列表的key
        :param value: 插入的值
        """
        text = pickle.dumps(value)
        await self.lpush(key, text)

    async def cus_lpop_by_pickle(self, key: str):
        """
        获取list数据（Pickle反序列化）
        :param key: 列表的key
        """
        r = await self.lpop(key)
        if r:
            return pickle.loads(r)
        return None

    async def hset(
            self,
            name: KeyT,
            key: typing.Optional[FieldT] = None,
            value: typing.Optional[EncodableT] = None,
            mapping: typing.Optional[typing.Mapping[AnyFieldT, EncodableT]] = None,
    ) -> typing.Awaitable:
        """Hash设置，自动JSON序列化"""
        if key is None and not mapping:
            raise aioredis.DataError("'hset' with no key value pairs")
        items: typing.List[typing.Union[FieldT, typing.Optional[EncodableT]]] = []
        if key is not None:
            items.extend((key, json.dumps(value)))
        if mapping:
            for pair in mapping.items():
                items.extend(pair)

        return self.execute_command("HSET", name, *items)

    async def get_list_by_index(self, key: str, id: int) -> object:
        """
        根据索引得到列表值
        :param key: 列表的值
        :param id: 索引值
        :return:
        """
        value = await self.lindex(key, id)
        return json.loads(value)


class MySyncRedis(SyncRedis):
    """同步redis客户端"""

    def get(self, name: str) -> typing.Any:
        """获取值，自动反序列化JSON"""
        data = super(MySyncRedis, self).get(name)
        return json.loads(data) if data else None


class RedisPool:
    """Redis连接池管理"""
    _redis: MyAsyncRedis = None

    @property
    def redis(self):
        return self._redis

    def init_by_config(self, config):
        """根据配置初始化Redis连接"""
        if self.redis:
            return self.redis
        if not hasattr(config, "REDIS_URI"):
            raise Exception("配置REDIS_URI不能为空！~")
        return self._form_url(config.REDIS_URI)

    def _form_url(self, url: str):
        """从URL创建Redis连接"""
        if not url:
            raise Exception("配置REDIS_URI不能为空！~")
        try:
            self._redis = MyAsyncRedis.from_url(url=url, health_check_interval=30)
            return self._redis
        except Exception as e:
            raise Exception(f"连接redis失败: {e}")

    def get_redis(self):
        """获取Redis客户端"""
        if not self.redis:
            raise Exception("请先初始化redis连接池！~, 请调用init_by_config方法")
        return self.redis


# 全局Redis连接池实例
redis_pool = RedisPool()
