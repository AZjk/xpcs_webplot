# Deployment Guide

Guide for deploying XPCS WebPlot in production environments.

## Table of Contents

- [Overview](#overview)
- [Production Deployment](#production-deployment)
- [Docker Deployment](#docker-deployment)
- [Server Configuration](#server-configuration)
- [Monitoring and Maintenance](#monitoring-and-maintenance)
- [Security](#security)
- [Performance Tuning](#performance-tuning)

## Overview

This guide covers deploying XPCS WebPlot for production use, including:

- Web server configuration (nginx, Apache)
- Process management
- Docker containerization
- Security best practices
- Performance optimization
- Monitoring and logging

## Production Deployment

### Architecture

For production, use a proper web server instead of Flask's development server:

```
┌─────────────┐
│   Client    │
│  (Browser)  │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Nginx     │  (Reverse Proxy)
│   Port 80   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Gunicorn  │  (WSGI Server)
│   Port 5000 │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Flask App   │  (XPCS WebPlot)
└─────────────┘
```

### Prerequisites

- Linux server (Ubuntu 20.04+ recommended)
- Python 3.8+
- nginx or Apache
- Gunicorn or uWSGI
- systemd for process management

### Installation on Server

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3 python3-pip python3-venv nginx -y

# Create application user
sudo useradd -m -s /bin/bash xpcs
sudo su - xpcs

# Clone repository
git clone https://github.com/AZjk/xpcs_webplot.git
cd xpcs_webplot

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install application
pip install -e .
pip install gunicorn
```

### Gunicorn Configuration

Create `gunicorn_config.py`:

```python
# gunicorn_config.py
import multiprocessing

# Server socket
bind = "127.0.0.1:5000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Logging
accesslog = "/var/log/xpcs_webplot/access.log"
errorlog = "/var/log/xpcs_webplot/error.log"
loglevel = "info"

# Process naming
proc_name = "xpcs_webplot"

# Server mechanics
daemon = False
pidfile = "/var/run/xpcs_webplot/gunicorn.pid"
user = "xpcs"
group = "xpcs"
tmp_upload_dir = None
```

Create startup script `start_server.sh`:

```bash
#!/bin/bash
# start_server.sh

cd /home/xpcs/xpcs_webplot
source venv/bin/activate

# Set HTML folder location
export HTML_FOLDER=/data/xpcs/html

# Start Gunicorn
exec gunicorn \
    --config gunicorn_config.py \
    "xpcs_webplot.flask_app:create_app('$HTML_FOLDER')"
```

Make executable:

```bash
chmod +x start_server.sh
```

### Systemd Service

Create `/etc/systemd/system/xpcs_webplot.service`:

```ini
[Unit]
Description=XPCS WebPlot Flask Application
After=network.target

[Service]
Type=notify
User=xpcs
Group=xpcs
WorkingDirectory=/home/xpcs/xpcs_webplot
Environment="PATH=/home/xpcs/xpcs_webplot/venv/bin"
Environment="HTML_FOLDER=/data/xpcs/html"
ExecStart=/home/xpcs/xpcs_webplot/start_server.sh
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=on-failure
RestartSec=10s

[Install]
WantedBy=multi-user.target
```

Enable and start service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable xpcs_webplot
sudo systemctl start xpcs_webplot
sudo systemctl status xpcs_webplot
```

### Nginx Configuration

Create `/etc/nginx/sites-available/xpcs_webplot`:

```nginx
# Upstream to Gunicorn
upstream xpcs_webplot {
    server 127.0.0.1:5000 fail_timeout=0;
}

server {
    listen 80;
    server_name xpcs.example.com;
    
    # Increase client body size for large file uploads
    client_max_body_size 100M;
    
    # Logging
    access_log /var/log/nginx/xpcs_webplot_access.log;
    error_log /var/log/nginx/xpcs_webplot_error.log;
    
    # Root location
    location / {
        proxy_pass http://xpcs_webplot;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Static files (optional optimization)
    location /static {
        alias /data/xpcs/html;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

Enable site:

```bash
sudo ln -s /etc/nginx/sites-available/xpcs_webplot /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### SSL/TLS Configuration

Use Let's Encrypt for free SSL certificates:

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx -y

# Obtain certificate
sudo certbot --nginx -d xpcs.example.com

# Auto-renewal is configured automatically
```

Updated nginx config with SSL:

```nginx
server {
    listen 80;
    server_name xpcs.example.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name xpcs.example.com;
    
    # SSL certificates
    ssl_certificate /etc/letsencrypt/live/xpcs.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/xpcs.example.com/privkey.pem;
    
    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # Rest of configuration...
}
```

## Docker Deployment

### Dockerfile

Create `Dockerfile`:

```dockerfile
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy application files
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -e .
RUN pip install --no-cache-dir gunicorn

# Create non-root user
RUN useradd -m -u 1000 xpcs && chown -R xpcs:xpcs /app
USER xpcs

# Expose port
EXPOSE 5000

# Set environment variables
ENV HTML_FOLDER=/data/html
ENV PYTHONUNBUFFERED=1

# Run application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", \
     "xpcs_webplot.flask_app:create_app('/data/html')"]
```

### Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  xpcs_webplot:
    build: .
    container_name: xpcs_webplot
    restart: unless-stopped
    ports:
      - "5000:5000"
    volumes:
      - /data/xpcs/html:/data/html:ro
    environment:
      - HTML_FOLDER=/data/html
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
  
  nginx:
    image: nginx:alpine
    container_name: xpcs_nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - /data/xpcs/html:/data/html:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - xpcs_webplot
```

Build and run:

```bash
docker-compose up -d
docker-compose logs -f
```

## Server Configuration

### Directory Structure

```
/data/xpcs/
├── html/                    # Results directory
│   ├── experiment_001/
│   ├── experiment_002/
│   └── ...
├── logs/                    # Application logs
│   ├── access.log
│   └── error.log
└── backups/                 # Backup location
```

### Permissions

```bash
# Create directories
sudo mkdir -p /data/xpcs/{html,logs,backups}

# Set ownership
sudo chown -R xpcs:xpcs /data/xpcs

# Set permissions
sudo chmod 755 /data/xpcs
sudo chmod 755 /data/xpcs/html
sudo chmod 755 /data/xpcs/logs
```

### Log Rotation

Create `/etc/logrotate.d/xpcs_webplot`:

```
/var/log/xpcs_webplot/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 xpcs xpcs
    sharedscripts
    postrotate
        systemctl reload xpcs_webplot > /dev/null 2>&1 || true
    endscript
}
```

## Monitoring and Maintenance

### Health Checks

Create health check endpoint in Flask app:

```python
@app.route('/health')
def health_check():
    return {'status': 'healthy', 'timestamp': datetime.now().isoformat()}
```

### Monitoring with systemd

```bash
# Check service status
sudo systemctl status xpcs_webplot

# View logs
sudo journalctl -u xpcs_webplot -f

# Restart service
sudo systemctl restart xpcs_webplot
```

### Application Monitoring

Use tools like:

- **Prometheus**: Metrics collection
- **Grafana**: Visualization
- **Sentry**: Error tracking
- **New Relic**: APM

### Backup Strategy

Automated backup script:

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/data/xpcs/backups"
HTML_DIR="/data/xpcs/html"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup
tar -czf "$BACKUP_DIR/html_backup_$DATE.tar.gz" -C "$HTML_DIR" .

# Keep only last 30 days
find "$BACKUP_DIR" -name "html_backup_*.tar.gz" -mtime +30 -delete
```

Add to crontab:

```bash
# Run daily at 2 AM
0 2 * * * /home/xpcs/backup.sh
```

## Security

### Firewall Configuration

```bash
# Allow HTTP and HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Allow SSH (if needed)
sudo ufw allow 22/tcp

# Enable firewall
sudo ufw enable
```

### Application Security

1. **Run as non-root user**: Always use dedicated user
2. **Disable debug mode**: Never use in production
3. **Validate inputs**: Sanitize all user inputs
4. **Use HTTPS**: Always encrypt traffic
5. **Regular updates**: Keep dependencies updated

### Access Control

If needed, add basic authentication in nginx:

```nginx
location / {
    auth_basic "Restricted Access";
    auth_basic_user_file /etc/nginx/.htpasswd;
    proxy_pass http://xpcs_webplot;
}
```

Create password file:

```bash
sudo apt install apache2-utils
sudo htpasswd -c /etc/nginx/.htpasswd username
```

## Performance Tuning

### Gunicorn Workers

Calculate optimal workers:

```
workers = (2 × CPU_cores) + 1
```

For 4 CPU cores: 9 workers

### Nginx Optimization

```nginx
# Worker processes
worker_processes auto;

# Worker connections
events {
    worker_connections 1024;
    use epoll;
}

# Gzip compression
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_types text/plain text/css application/json application/javascript;

# Caching
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=my_cache:10m max_size=1g;
```

### Database Optimization

If using database for metadata:

- Use connection pooling
- Add appropriate indexes
- Regular VACUUM (PostgreSQL)
- Monitor slow queries

### File System

- Use SSD for better I/O
- Consider NFS for shared storage
- Regular cleanup of old results

## Troubleshooting

### Common Issues

**Service won't start**:
```bash
sudo journalctl -u xpcs_webplot -n 50
```

**502 Bad Gateway**:
- Check Gunicorn is running
- Verify nginx upstream configuration
- Check firewall rules

**Slow performance**:
- Increase Gunicorn workers
- Enable nginx caching
- Optimize database queries

**Out of memory**:
- Reduce number of workers
- Increase server RAM
- Optimize image processing

## See Also

- [User Guide](user_guide.md) - Using the application
- [Architecture](architecture.md) - System design
- [Development Guide](development_guide.md) - Contributing
