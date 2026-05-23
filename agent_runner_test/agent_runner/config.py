from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = "dev"
    app_host: str = "0.0.0.0"
    app_port: int = 8081
    database_url: str = "mysql+aiomysql://root:password@127.0.0.1:3306/agent_runner"
    storage_base_path: str = "./data"


    hermes_base_url: str = "http://127.0.0.1:8643"
    hermes_api_key: str = "fiskzcVqn3frVcd"


settings = Settings()
