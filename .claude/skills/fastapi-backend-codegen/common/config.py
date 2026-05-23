"""
应用配置模块
生成代码时可以直接导入使用: from app.config import settings
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """应用配置"""
    
    # 应用基础配置
    APP_ENV: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "your-secret-key-change-in-production"
    API_V1_PREFIX: str = "/api/v1"
    APP_DESC: str = "AI Quote Backend"
    APP_VERSION: str = "0.1.0"
    
    # 数据库配置
    DATABASE_URL: str = "mysql+aiomysql://user:password@localhost:3306/dbname?charset=utf8mb4"
    
    # Redis配置
    REDIS_URI: str = "redis://localhost:6379/9"
    
    # LLM配置
    LLM_BASE_URL: str = ""
    LLM_MODEL: str = ""
    OPENAI_API_KEY: str = ""
    LLM_API_KEY_ENV: str = "OPENAI_API_KEY"
    LLM_TEMPERATURE: float = 0.0
    LLM_MAX_OUTPUT_TOKENS: int = 600
    
    # 文件存储配置
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE: int = 10485760  # 10MB
    
    # CORS配置
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:8080"
    
    # Celery配置（可选）
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # 日志配置
    LOGGER_DIR: str = "./logs"
    LOGGER_NAME: str = "app.log"
    LOGGER_LEVEL: str = "INFO"
    LOGGER_ROTATION: str = "10 MB"
    LOGGER_RETENTION: str = "7 days"

    WHITE_ROUTERS: List[str] = ["/docs", "/redoc", "/openapi.json"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# 全局配置实例
settings = Settings()
