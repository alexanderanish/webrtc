# Deployment Guide

This guide covers deploying your WebRTC application with Gemini integration to production.

## Architecture Overview

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│             │         │              │         │             │
│   Client    │◄───────►│   Server     │◄───────►│   Gemini    │
│   (React)   │  WSS    │  (FastAPI)   │  HTTPS  │    API      │
│             │         │              │         │             │
└─────────────┘         └──────────────┘         └─────────────┘
      │                        │
      │                        │
      ▼                        ▼
┌─────────────┐         ┌──────────────┐
│   CDN/      │         │  Database    │
│   Storage   │         │  (Optional)  │
└─────────────┘         └──────────────┘
```

## Prerequisites

- Domain name with DNS configured
- SSL certificates
- Server with public IP
- Gemini API key

## Server Deployment

### 1. Prepare Server

#### System Requirements

- Ubuntu 20.04+ or similar Linux distribution
- Python 3.9+
- 2+ CPU cores
- 4GB+ RAM
- 20GB+ storage

#### Install Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and tools
sudo apt install -y python3.9 python3.9-venv python3-pip
sudo apt install -y nginx certbot python3-certbot-nginx

# Install system dependencies for aiortc
sudo apt install -y libavformat-dev libavcodec-dev libavdevice-dev \
                     libavutil-dev libswscale-dev libswresample-dev \
                     libavfilter-dev libopus-dev libvpx-dev pkg-config
```

### 2. Application Setup

```bash
# Create application directory
sudo mkdir -p /opt/webrtc-server
sudo chown $USER:$USER /opt/webrtc-server
cd /opt/webrtc-server

# Clone repository
git clone <your-repo-url> .

# Create virtual environment
python3.9 -m venv venv
source venv/bin/activate

# Install dependencies
cd examples/fastapi-server
pip install -r requirements.txt
pip install -e ../../packages/server
```

### 3. Configuration

Create production environment file:

```bash
cat > .env << EOF
GEMINI_API_KEY=your_production_api_key
GEMINI_MODEL=gemini-2.0-flash-exp
HOST=0.0.0.0
PORT=8000
DEBUG=False
ALLOWED_ORIGINS=https://yourdomain.com
EOF
```

### 4. Systemd Service

Create service file:

```bash
sudo nano /etc/systemd/system/webrtc-server.service
```

```ini
[Unit]
Description=WebRTC Enterprise Server
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/opt/webrtc-server/examples/fastapi-server
Environment="PATH=/opt/webrtc-server/venv/bin"
ExecStart=/opt/webrtc-server/venv/bin/uvicorn main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 4 \
    --log-level info
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable webrtc-server
sudo systemctl start webrtc-server
sudo systemctl status webrtc-server
```

### 5. Nginx Configuration

```bash
sudo nano /etc/nginx/sites-available/webrtc
```

```nginx
# WebRTC Server
upstream webrtc_backend {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        return 301 https://$server_name$request_uri;
    }
}

server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.yourdomain.com/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # WebSocket configuration
    location /ws {
        proxy_pass http://webrtc_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }

    # API endpoints
    location / {
        proxy_pass http://webrtc_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable site:

```bash
sudo ln -s /etc/nginx/sites-available/webrtc /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 6. SSL Certificates

```bash
sudo certbot --nginx -d api.yourdomain.com
```

### 7. TURN Server (Optional but Recommended)

For production, use a TURN server for NAT traversal:

```bash
# Install coturn
sudo apt install -y coturn

# Configure coturn
sudo nano /etc/turnserver.conf
```

```conf
listening-port=3478
tls-listening-port=5349
listening-ip=0.0.0.0
relay-ip=YOUR_SERVER_IP
external-ip=YOUR_SERVER_IP

realm=yourdomain.com
server-name=yourdomain.com

lt-cred-mech
user=username:password

cert=/etc/letsencrypt/live/turn.yourdomain.com/fullchain.pem
pkey=/etc/letsencrypt/live/turn.yourdomain.com/privkey.pem

no-stdout-log
log-file=/var/log/turnserver/turnserver.log

verbose
```

Enable and start:

```bash
sudo systemctl enable coturn
sudo systemctl start coturn
```

Update client configuration:

```typescript
const client = new WebRTCClient({
  signalingUrl: 'wss://api.yourdomain.com/ws',
  iceServers: [
    { urls: 'stun:stun.l.google.com:19302' },
    {
      urls: 'turn:turn.yourdomain.com:3478',
      username: 'username',
      credential: 'password'
    }
  ]
});
```

## Client Deployment

### 1. Build React App

```bash
cd examples/react-app

# Install dependencies
npm install

# Update API URL
# Edit src/App.tsx or use environment variable
echo "VITE_SIGNALING_URL=wss://api.yourdomain.com/ws" > .env.production

# Build
npm run build
```

### 2. Deploy to CDN

#### Option A: Vercel

```bash
npm install -g vercel
vercel --prod
```

#### Option B: Netlify

```bash
npm install -g netlify-cli
netlify deploy --prod
```

#### Option C: Self-hosted (Nginx)

```bash
# Copy build to server
scp -r dist/* user@server:/var/www/yourdomain.com/

# Nginx config
sudo nano /etc/nginx/sites-available/webrtc-client
```

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    root /var/www/yourdomain.com;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

## Monitoring

### 1. Application Logs

```bash
# View server logs
sudo journalctl -u webrtc-server -f

# View nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### 2. System Monitoring

Install monitoring tools:

```bash
sudo apt install -y prometheus prometheus-node-exporter grafana
```

### 3. Error Tracking

Consider using services like:
- Sentry for error tracking
- Datadog for infrastructure monitoring
- CloudWatch (if on AWS)

## Security

### 1. Firewall

```bash
# Configure UFW
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 3478/tcp  # TURN
sudo ufw allow 3478/udp  # TURN
sudo ufw enable
```

### 2. Rate Limiting

Add to nginx config:

```nginx
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;

server {
    location /ws {
        limit_req zone=api burst=20 nodelay;
        # ... rest of config
    }
}
```

### 3. Authentication

Implement JWT authentication:

```python
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer

security = HTTPBearer()

async def verify_token(credentials = Depends(security)):
    token = credentials.credentials
    # Verify JWT token
    return token

@app.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Depends(verify_token)
):
    # Handle authenticated connection
    pass
```

## Scaling

### Horizontal Scaling

Use load balancer (nginx/HAProxy):

```nginx
upstream webrtc_cluster {
    least_conn;
    server server1.internal:8000;
    server server2.internal:8000;
    server server3.internal:8000;
}
```

### Vertical Scaling

Increase worker count:

```bash
# In systemd service
ExecStart=... --workers 8
```

## Backup

```bash
# Backup script
#!/bin/bash
backup_dir="/backup/webrtc-$(date +%Y%m%d)"
mkdir -p $backup_dir

# Backup application
cp -r /opt/webrtc-server $backup_dir/

# Backup configuration
cp /etc/nginx/sites-available/webrtc $backup_dir/
cp /etc/systemd/system/webrtc-server.service $backup_dir/

# Create archive
tar -czf ${backup_dir}.tar.gz $backup_dir
rm -rf $backup_dir
```

## Health Checks

Implement health check endpoint:

```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "sessions": len(server.sessions)
    }
```

Monitor with cron:

```bash
# Check every minute
* * * * * curl -f http://localhost:8000/health || systemctl restart webrtc-server
```

## Troubleshooting

### Common Issues

1. **WebSocket connection fails**
   - Check firewall rules
   - Verify nginx WebSocket config
   - Check SSL certificates

2. **Audio not working**
   - Verify TURN server
   - Check codec compatibility
   - Enable debug logging

3. **High latency**
   - Add CDN
   - Optimize server location
   - Increase worker count

### Debug Mode

Enable debug logging temporarily:

```bash
sudo systemctl stop webrtc-server
cd /opt/webrtc-server/examples/fastapi-server
source ../../venv/bin/activate
DEBUG=True python main.py
```

## Maintenance

### Updates

```bash
cd /opt/webrtc-server
git pull
source venv/bin/activate
pip install -r examples/fastapi-server/requirements.txt
sudo systemctl restart webrtc-server
```

### Log Rotation

```bash
sudo nano /etc/logrotate.d/webrtc
```

```
/var/log/webrtc/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
    postrotate
        systemctl reload webrtc-server
    endscript
}
```

## Cost Optimization

1. Use reserved instances for predictable workload
2. Implement session timeouts
3. Cache static assets on CDN
4. Optimize Gemini API calls
5. Use spot instances for dev/test

## Next Steps

1. Set up CI/CD pipeline
2. Implement automated testing
3. Add performance monitoring
4. Set up disaster recovery
5. Document runbooks for common issues
