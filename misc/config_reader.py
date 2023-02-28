from pydantic import BaseSettings, SecretStr


class Settings(BaseSettings):
    bot_token: SecretStr
    database_path: str
    admins_list: list
    templates_list: list
    classes: dict

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


config = Settings()
