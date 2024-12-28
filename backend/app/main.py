from fastapi import FastAPI, Depends, HTTPException, status, Security
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from datetime import timedelta
import jwt
from typing import List
from fastapi.responses import JSONResponse
from proxmoxer import ProxmoxAPI

from .auth import verify_proxmox_credentials, create_access_token, get_current_user
from .proxmox import proxmox_manager
from .schemas import Token, UserLogin, VMStatus
from .config import settings

app = FastAPI()

# Update CORS middleware with more specific settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8000",
        "http://127.0.0.1:8000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Initialize ProxmoxManager
proxmox_manager = proxmox_manager

# Add a test endpoint
@app.get("/test")
async def test():
    return {"message": "API is working"}

@app.options("/token")
async def options_token():
    return {"message": "OK"}

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    print(f"Login attempt received for username: {form_data.username}")
    try:
        if not verify_proxmox_credentials(form_data.username, form_data.password):
            print("Invalid credentials")
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid username or password"},
                headers={"Access-Control-Allow-Credentials": "true"}
            )
        
        access_token = create_access_token(
            data={"sub": form_data.username},
            expires_delta=timedelta(minutes=30)
        )
        print("Login successful")
        return JSONResponse(
            status_code=200,
            content={"access_token": access_token, "token_type": "bearer"},
            headers={"Access-Control-Allow-Credentials": "true"}
        )
        
    except Exception as e:
        print(f"Login error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"detail": str(e)},
            headers={"Access-Control-Allow-Credentials": "true"}
        )

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme)):
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
        return username
    except jwt.PyJWTError:
        raise credentials_exception

@app.get("/vms")
async def get_vms(current_user: str = Depends(get_current_user)):
    try:
        if current_user not in settings.allowed_users:
            raise HTTPException(status_code=403, detail="User not allowed")
        
        # Return the list of allowed VMs for this user
        allowed_vms = settings.allowed_users.get(current_user, [])
        print(f"Allowed VMs for {current_user}: {allowed_vms}")  # Debug log
        return allowed_vms
    except Exception as e:
        print(f"Error getting VMs: {str(e)}")  # Debug log
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/vms/{vmid}/status")
async def get_vm_status(vmid: str, current_user: str = Depends(get_current_user)):
    try:
        # Check if user has access to this VM
        if vmid not in settings.allowed_users.get(current_user, []):
            raise HTTPException(
                status_code=403,
                detail="Not authorized to access this VM"
            )

        print(f"Connecting to Proxmox with token ID: {settings.proxmox_api_token_id}")  # Debug log
        
        # Connect to Proxmox
        proxmox = ProxmoxAPI(
            settings.proxmox_host,
            user=settings.proxmox_api_token_id.split('!')[0],  # Get the user part
            token_name=settings.proxmox_api_token_id.split('!')[1],  # Get the token name
            token_value=settings.proxmox_api_token_secret,
            verify_ssl=False,
            port=8006
        )

        # Get VM status
        nodes = proxmox.nodes.get()
        print(f"Found nodes: {nodes}")  # Debug log
        
        for node in nodes:
            try:
                vm = proxmox.nodes(node['node']).qemu(vmid).status.current.get()
                print(f"VM status: {vm}")  # Debug log
                return {
                    "status": vm['status'],
                    "cpu": vm.get('cpu', 0) * 100,  # Convert to percentage
                    "memory": {
                        "used": vm.get('mem', 0),
                        "total": vm.get('maxmem', 0)
                    },
                    "disk": {
                        "used": 0,
                        "total": 0
                    },
                    "uptime": vm.get('uptime', 0)
                }
            except Exception as e:
                print(f"Error getting VM status from node {node['node']}: {str(e)}")  # Debug log
                continue

        raise HTTPException(
            status_code=404,
            detail=f"VM {vmid} not found"
        )

    except Exception as e:
        print(f"Error getting VM status: {str(e)}")  # Debug log
        raise HTTPException(
            status_code=500,
            detail=f"Error getting VM status: {str(e)}"
        )

@app.post("/vms/{vmid}/reset")
def reset_vm(vmid: str, current_user: str = Depends(get_current_user)):
    try:
        if vmid not in settings.allowed_users.get(current_user, []):
            raise HTTPException(
                status_code=403,
                detail="Not authorized to access this VM"
            )
        
        proxmox_manager.reset_vm(vmid)
        return JSONResponse(
            status_code=200,
            content={"message": "Reset initiated successfully"}
        )
    except Exception as e:
        print(f"Error resetting VM: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Failed to reset VM. Please try again."}
        )

@app.post("/vms/{vmid}/start")
def start_vm(vmid: str, current_user: str = Depends(get_current_user)):
    try:
        if vmid not in settings.allowed_users.get(current_user, []):
            raise HTTPException(status_code=403, detail="Not authorized")
        proxmox_manager.start_vm(vmid)
        return {"message": "Start initiated successfully"}
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": "Failed to start VM. Please try again."})

@app.post("/vms/{vmid}/stop")
def stop_vm(vmid: str, current_user: str = Depends(get_current_user)):
    try:
        if vmid not in settings.allowed_users.get(current_user, []):
            raise HTTPException(status_code=403, detail="Not authorized")
        proxmox_manager.stop_vm(vmid)
        return {"message": "Stop initiated successfully"}
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": "Failed to stop VM. Please try again."})

@app.post("/vms/{vmid}/shutdown")
def shutdown_vm(vmid: str, current_user: str = Depends(get_current_user)):
    try:
        if vmid not in settings.allowed_users.get(current_user, []):
            raise HTTPException(status_code=403, detail="Not authorized")
        proxmox_manager.shutdown_vm(vmid)
        return {"message": "Shutdown initiated successfully"}
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": "Failed to shutdown VM. Please try again."})

# @app.get("/api/vms")
# async def get_vms():
#     try:
#         proxmox = ProxmoxManager()
#         vms = proxmox.get_vm_list()
#         return vms
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e)) 