# IcePox Portal (A Whitelabel Proxmox VM Portal for your clients)

##### Use this at your own risk I made this project in a short time and it's not fully tested. Don't expect any support. ##### 

A secure, user-friendly web interface that allows users to manage their assigned Proxmox VMs without requiring full access to the Proxmox interface. This portal is designed to be deployed on a server and accessed by multiple users through their web browsers.

## Features

- 🔒 Secure authentication using Proxmox credentials
- 🖥️ View assigned VM status
- 🎮 Control VM power state (start, stop, reset, shutdown)
- 📊 Monitor Live VM resources (CPU, memory, uptime)
- 🔑 Role-based access control
- 🌐 "Modern" web interface
- 🔐 HTTPS support

### This is just a simple guide to get you started. Change the installation/setup/code to your needs. ###

## Server Prerequisites

- Debian 12 / Ubuntu Server 20.04 LTS or newer
- Python 3.11+
- Node.js 16+
- Nginx
- SSL certificate (Let's Encrypt recommended)
- Domain name (optional but recommended)

## Server Installation

### 1. Initial Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3-pip python3-venv nodejs npm nginx certbot python3-certbot-nginx
```

### 2. Clone Repository

```bash
# Create application directory
sudo mkdir /opt/proxmox-portal
sudo chown $USER:$USER /opt/proxmox-portal
cd /opt/proxmox-portal

# Clone the repository
git clone https://github.com/Iceman-has-a-cold/IcePox.git .
```

### 3. Backend Setup

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
cd backend
pip install -r requirements.txt
pip install gunicorn

# Create environment file
sudo nano /opt/proxmox-portal/backend/.env
```

Add the following to your `.env` file:
```env
PROXMOX_HOST=https://your-proxmox-server:8006
PROXMOX_API_TOKEN_ID=your-token-id
PROXMOX_API_TOKEN_SECRET=your-token-secret
JWT_SECRET=your-secure-random-string
ALLOWED_USERS={"user@pve": ["100", "101"], "user2@pve": ["102"]}
CORS_ORIGINS=["https://your-domain.com"]
```

### 4. Frontend Setup

```bash
cd /opt/proxmox-portal/frontend

# Install dependencies
npm install

# Build the frontend
npm run build
```

Note: For development, the API URL is set to `http://localhost:8000`. If you need to change this for production, modify the `API_URL` in `src/services/vmService.ts`.

### 5. Configure Nginx

Create an Nginx configuration file:
```bash
sudo nano /etc/nginx/sites-available/proxmox-portal
```

Add the following configuration:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Frontend
    location / {
        root /opt/proxmox-portal/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/proxmox-portal /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 6. SSL Configuration

```bash
sudo certbot --nginx -d your-domain.com
```

### 7. Create Systemd Service

Create a service file:
```bash
sudo nano /etc/systemd/system/proxmox-portal.service
```

Add the following:
```ini
[Unit]
Description=Proxmox VM Portal
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/opt/proxmox-portal/backend
Environment="PATH=/opt/proxmox-portal/venv/bin"
EnvironmentFile=/opt/proxmox-portal/backend/.env
ExecStart=/opt/proxmox-portal/venv/bin/gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 127.0.0.1:8000

[Install]
WantedBy=multi-user.target
```

Start and enable the service:
```bash
sudo systemctl start proxmox-portal
sudo systemctl enable proxmox-portal
```

## Proxmox Configuration

### 1. Create API Token

1. Log in to your Proxmox web interface
2. Navigate to Datacenter -> Permissions -> API Tokens
3. Click "Add" and create a new token
4. Save both the token ID and secret value

### 2. Configure Permissions

Run these commands on your Proxmox server:
```bash
# Create role for portal users
pveum role add VMPortalUser -privs "VM.PowerMgmt VM.Audit VM.Monitor"

# Add permissions for users
pveum aclmod / -user username@pve -role VMPortalUser

# Add permissions for specific VMs (repeat for each VM)
pveum aclmod /vms/100 -user username@pve -role VMPortalUser
pveum aclmod /vms/100 -token 'username@pve!vm-portal' -role VMPortalUser
```

## User Access

1. Users access the portal through: `https://your-domain.com`
2. Log in using Proxmox credentials (username@pve format)
3. Manage assigned VMs through the web interface

## Security Recommendations

1. Keep the server updated:
```bash
sudo apt update && sudo apt upgrade -y
```

2. Configure UFW firewall:
```bash
sudo ufw allow ssh
sudo ufw allow http
sudo ufw allow https
sudo ufw enable
```

3. Regular backups of configuration:
```bash
sudo cp /opt/proxmox-portal/backend/.env /opt/proxmox-portal/backend/.env.backup
```

4. Monitor logs:
```bash
sudo journalctl -u proxmox-portal -f
```

## Maintenance

### Updating the Portal

```bash
cd /opt/proxmox-portal
git pull

# Update backend
source venv/bin/activate
cd backend
pip install -r requirements.txt

# Update frontend
cd ../frontend
npm install
npm run build

# Restart service
sudo systemctl restart proxmox-portal
```

### Backup Configuration

Regular backups of these files are recommended:
- `/opt/proxmox-portal/backend/.env`
- `/opt/proxmox-portal/frontend/.env.production`
- `/etc/nginx/sites-available/proxmox-portal`

## Troubleshooting

1. Check service status:
```bash
sudo systemctl status proxmox-portal
```

2. View logs:
```bash
sudo journalctl -u proxmox-portal -f
```

3. Check Nginx logs:
```bash
sudo tail -f /var/log/nginx/error.log
```



