# RealityFix Deployment Guide

Complete guide for deploying RealityFix to production environments.

## Table of Contents
1. [Local Development](#local-development)
2. [Production Backend](#production-backend)
3. [Extension Publishing](#extension-publishing)
4. [Cloud Deployment](#cloud-deployment)
5. [Monitoring & Maintenance](#monitoring--maintenance)

## Local Development

### Development Environment Setup
```bash
# Clone repository
git clone https://github.com/abhi3114-glitch/REALITYFIX.git
cd REALITYFIX

# Setup backend
python3 -m venv venv
source venv/bin/activate
cd backend
pip install -r requirements.txt

# Run with auto-reload
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

### Extension Development
```bash
# Load in Chrome
1. chrome://extensions/
2. Enable Developer mode
3. Load unpacked → select extension/
4. Make changes
5. Click reload icon to test
```

## Production Backend

### Option 1: VPS Deployment (DigitalOcean, AWS EC2, etc.)

#### 1. Server Setup
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.8+
sudo apt install python3.8 python3-pip python3-venv -y

# Install Nginx
sudo apt install nginx -y

# Install Supervisor (process manager)
sudo apt install supervisor -y
```

#### 2. Application Setup
```bash
# Create app directory
sudo mkdir -p /var/www/realityfix
cd /var/www/realityfix

# Clone repository
git clone https://github.com/abhi3114-glitch/REALITYFIX.git .

# Setup virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
cd backend
pip install -r requirements.txt
pip install gunicorn

# Download models (first time)
python3 -c "from model_loader import model_loader; model_loader.load_text_model()"
```

#### 3. Gunicorn Configuration
```bash
# Create gunicorn config
sudo nano /var/www/realityfix/gunicorn_config.py
```

```python
# gunicorn_config.py
bind = "127.0.0.1:8000"
workers = 4
worker_class = "uvicorn.workers.UvicornWorker"
timeout = 120
keepalive = 5
errorlog = "/var/log/realityfix/error.log"
accesslog = "/var/log/realityfix/access.log"
loglevel = "info"
```

#### 4. Supervisor Configuration
```bash
# Create supervisor config
sudo nano /etc/supervisor/conf.d/realityfix.conf
```

```ini
[program:realityfix]
directory=/var/www/realityfix/backend
command=/var/www/realityfix/venv/bin/gunicorn app:app -c /var/www/realityfix/gunicorn_config.py
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/realityfix/app.log
```

```bash
# Create log directory
sudo mkdir -p /var/log/realityfix
sudo chown www-data:www-data /var/log/realityfix

# Start supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start realityfix
```

#### 5. Nginx Configuration
```bash
# Create Nginx config
sudo nano /etc/nginx/sites-available/realityfix
```

```nginx
server {
    listen 80;
    server_name api.realityfix.com;  # Replace with your domain

    client_max_body_size 10M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 120s;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/realityfix /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 6. SSL Certificate (Let's Encrypt)
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get certificate
sudo certbot --nginx -d api.realityfix.com

# Auto-renewal is configured automatically
```

### Option 2: Docker Deployment

#### Dockerfile
```dockerfile
# backend/Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Download models
RUN python -c "from model_loader import model_loader; model_loader.load_text_model()"

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Docker Compose
```yaml
# docker-compose.yml
version: '3.8'

services:
  api:
    build: ./backend
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
      - models:/app/models
    environment:
      - PYTHONUNBUFFERED=1
    restart: unless-stopped

volumes:
  models:
```

```bash
# Deploy with Docker
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Option 3: Cloud Platforms

#### AWS Elastic Beanstalk
```bash
# Install EB CLI
pip install awsebcli

# Initialize
eb init -p python-3.8 realityfix

# Create environment
eb create realityfix-prod

# Deploy
eb deploy

# Open
eb open
```

#### Google Cloud Run
```bash
# Build container
gcloud builds submit --tag gcr.io/PROJECT_ID/realityfix

# Deploy
gcloud run deploy realityfix \
  --image gcr.io/PROJECT_ID/realityfix \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

#### Heroku
```bash
# Create Procfile
echo "web: uvicorn app:app --host 0.0.0.0 --port \$PORT" > Procfile

# Deploy
heroku create realityfix-api
git push heroku main
```

## Extension Publishing

### 1. Prepare Extension

#### Update manifest.json
```json
{
  "name": "RealityFix - Fake News Detector",
  "version": "1.0.0",
  "description": "Real-time fake news and manipulated media detector",
  "host_permissions": [
    "https://api.realityfix.com/*"  // Update to production URL
  ]
}
```

#### Create Icons
```bash
# Create 3 icon sizes
- icon16.png (16x16)
- icon48.png (48x48)
- icon128.png (128x128)

# Place in extension/icons/
```

#### Update API URL
```javascript
// extension/background.js
const API_BASE_URL = 'https://api.realityfix.com';  // Production URL
```

### 2. Package Extension
```bash
cd extension
zip -r realityfix-extension.zip * -x "*.git*" -x "*node_modules*"
```

### 3. Chrome Web Store Submission

1. **Create Developer Account**
   - Go to https://chrome.google.com/webstore/devconsole
   - Pay $5 one-time registration fee

2. **Upload Extension**
   - Click "New Item"
   - Upload realityfix-extension.zip
   - Fill in details:
     - Name: RealityFix
     - Description: (Use README description)
     - Category: Productivity
     - Language: English

3. **Add Assets**
   - Icon: 128x128 PNG
   - Screenshots: 1280x800 or 640x400 (at least 1)
   - Promotional images (optional)

4. **Privacy & Permissions**
   - Explain why permissions are needed
   - Privacy policy URL (required)
   - Terms of service (optional)

5. **Submit for Review**
   - Review typically takes 1-3 days
   - Address any feedback from reviewers

### 4. Firefox Add-ons (Optional)

#### Convert to Firefox
```bash
# Update manifest.json for Firefox compatibility
# Change "manifest_version": 3 to 2 if needed
# Update permissions format

# Package
cd extension
zip -r realityfix-firefox.zip *
```

#### Submit to AMO
1. Go to https://addons.mozilla.org/developers/
2. Submit new add-on
3. Upload ZIP file
4. Fill in details
5. Submit for review

## Cloud Deployment

### AWS Architecture

```
┌─────────────────────────────────────────────────┐
│                   CloudFront                     │
│              (CDN + SSL/TLS)                     │
└────────────────┬────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────┐
│            Application Load Balancer             │
└────────────────┬────────────────────────────────┘
                 │
     ┌───────────┼───────────┐
     │           │           │
┌────▼────┐ ┌───▼────┐ ┌───▼────┐
│  EC2    │ │  EC2   │ │  EC2   │
│ Instance│ │Instance│ │Instance│
└────┬────┘ └───┬────┘ └───┬────┘
     │          │          │
     └──────────┼──────────┘
                │
     ┌──────────▼──────────┐
     │    RDS (PostgreSQL) │
     │    ElastiCache      │
     └─────────────────────┘
```

### Terraform Configuration (AWS)

```hcl
# main.tf
provider "aws" {
  region = "us-east-1"
}

# EC2 instances
resource "aws_instance" "realityfix" {
  count         = 3
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t3.medium"
  
  tags = {
    Name = "realityfix-${count.index}"
  }
}

# Load balancer
resource "aws_lb" "realityfix" {
  name               = "realityfix-lb"
  load_balancer_type = "application"
  subnets            = aws_subnet.public[*].id
}

# RDS database
resource "aws_db_instance" "realityfix" {
  identifier        = "realityfix-db"
  engine            = "postgres"
  instance_class    = "db.t3.micro"
  allocated_storage = 20
}
```

## Monitoring & Maintenance

### Application Monitoring

#### Prometheus + Grafana
```bash
# Install Prometheus
wget https://github.com/prometheus/prometheus/releases/download/v2.30.0/prometheus-2.30.0.linux-amd64.tar.gz
tar xvfz prometheus-*.tar.gz
cd prometheus-*

# Configure
cat > prometheus.yml << EOF
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'realityfix'
    static_configs:
      - targets: ['localhost:8000']
EOF

# Run
./prometheus --config.file=prometheus.yml
```

#### Application Metrics
```python
# Add to app.py
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()
Instrumentator().instrument(app).expose(app)
```

### Logging

#### Centralized Logging (ELK Stack)
```bash
# Elasticsearch
docker run -d -p 9200:9200 -e "discovery.type=single-node" elasticsearch:7.14.0

# Logstash
docker run -d -p 5000:5000 logstash:7.14.0

# Kibana
docker run -d -p 5601:5601 kibana:7.14.0
```

### Backup Strategy

#### Database Backups
```bash
# Automated daily backups
0 2 * * * /usr/bin/sqlite3 /var/www/realityfix/backend/realityfix.db ".backup '/backup/realityfix-$(date +\%Y\%m\%d).db'"

# Retention: Keep 30 days
find /backup -name "realityfix-*.db" -mtime +30 -delete
```

#### Model Backups
```bash
# Backup models directory
tar -czf models-backup.tar.gz backend/models/
aws s3 cp models-backup.tar.gz s3://realityfix-backups/
```

### Performance Optimization

#### Caching Strategy
```python
# Add Redis caching
import redis
from functools import wraps

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cache_result(ttl=3600):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
            result = await func(*args, **kwargs)
            redis_client.setex(cache_key, ttl, json.dumps(result))
            return result
        return wrapper
    return decorator
```

#### Load Testing
```bash
# Install locust
pip install locust

# Create locustfile.py
from locust import HttpUser, task

class RealityFixUser(HttpUser):
    @task
    def analyze_text(self):
        self.client.post("/analyze/text", json={"text": "Test text"})

# Run test
locust -f locustfile.py --host=http://localhost:8000
```

### Security Hardening

#### API Rate Limiting
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/analyze/text")
@limiter.limit("10/minute")
async def analyze_text(request: Request, data: TextAnalysisRequest):
    # ... existing code
```

#### API Authentication
```python
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def verify_token(credentials: HTTPAuthorizationCredentials):
    # Implement token verification
    pass

@app.post("/analyze/text")
async def analyze_text(
    data: TextAnalysisRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    await verify_token(credentials)
    # ... existing code
```

### Update Strategy

#### Zero-Downtime Deployment
```bash
# Blue-Green Deployment
1. Deploy new version to "green" environment
2. Test green environment
3. Switch load balancer to green
4. Keep blue as backup
5. After verification, update blue

# Rolling Update
1. Update one instance at a time
2. Wait for health check
3. Proceed to next instance
```

#### Database Migrations
```bash
# Use Alembic for migrations
pip install alembic

# Initialize
alembic init migrations

# Create migration
alembic revision --autogenerate -m "Add new table"

# Apply migration
alembic upgrade head
```

## Troubleshooting

### Common Issues

#### High Memory Usage
```bash
# Monitor memory
free -h
htop

# Reduce workers
# In gunicorn_config.py
workers = 2  # Reduce from 4
```

#### Slow Response Times
```bash
# Check model loading
# Add model preloading in app startup

@app.on_event("startup")
async def startup_event():
    text_detector._load_model()
    image_detector._load_model()
    audio_detector._load_model()
```

#### Database Lock Issues
```bash
# Switch to PostgreSQL for production
# Update database.py connection string
```

## Cost Optimization

### AWS Cost Estimates
- **t3.medium EC2** (3 instances): ~$90/month
- **RDS db.t3.micro**: ~$15/month
- **Load Balancer**: ~$20/month
- **Data Transfer**: ~$10/month
- **Total**: ~$135/month

### Optimization Tips
1. Use spot instances for non-critical workloads
2. Implement auto-scaling
3. Use CloudFront CDN
4. Enable S3 lifecycle policies
5. Use Reserved Instances for 1-year commitment

## Support & Maintenance

### Regular Tasks
- [ ] Weekly: Review error logs
- [ ] Weekly: Check disk space
- [ ] Monthly: Update dependencies
- [ ] Monthly: Review performance metrics
- [ ] Quarterly: Security audit
- [ ] Yearly: SSL certificate renewal (auto with Let's Encrypt)

### Emergency Contacts
- DevOps Lead: devops@realityfix.com
- Backend Team: backend@realityfix.com
- Security: security@realityfix.com

---

**Last Updated**: 2024-01-15
**Version**: 1.0.0