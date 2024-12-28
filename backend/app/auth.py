from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from proxmoxer import ProxmoxAPI
from .config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_proxmox_credentials(username: str, password: str) -> bool:
    try:
        print(f"Attempting to connect with username: {username}")  # Debug log
        proxmox = ProxmoxAPI(
            settings.proxmox_host,
            user=username,
            password=password,
            port=8006,
            verify_ssl=False
        )
        # Test the connection by trying to get nodes
        proxmox.nodes.get()
        print("Authentication successful")  # Debug log
        return True
    except Exception as e:
        print(f"Authentication failed: {str(e)}")  # Debug log
        return False

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret, algorithm="HS256")
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)) -> str:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        if username not in settings.user_vm_mapping:
            raise credentials_exception
        return username
    except JWTError:
        raise credentials_exception 