from pydantic_settings import BaseSettings
from typing import Dict, List
import json

class Settings(BaseSettings):
    proxmox_host: str
    proxmox_api_token_id: str
    proxmox_api_token_secret: str
    jwt_secret: str
    allowed_users: Dict[str, List[str]]

    class Config:
        env_file = ".env"

        @classmethod
        def parse_env_var(cls, field_name: str, raw_val: str):
            if field_name == "allowed_users":
                return json.loads(raw_val)
            return raw_val

settings = Settings() 