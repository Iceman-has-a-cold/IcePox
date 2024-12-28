from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str

class UserLogin(BaseModel):
    username: str
    password: str

class VMStatus(BaseModel):
    status: str
    cpu: float
    memory: dict
    disk: dict
    uptime: int 