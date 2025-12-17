# Deployment Guide

This guide covers deploying the Resume-to-Training Module Generator for production use with multiple users.

## Pre-Deployment Checklist

- [ ] Set up production database (PostgreSQL recommended)
- [ ] Configure environment variables
- [ ] Set up authentication/authorization
- [ ] Configure CORS for your domain
- [ ] Set up SSL/HTTPS
- [ ] Configure file storage for resumes
- [ ] Set up monitoring and logging
- [ ] Configure rate limiting
- [ ] Set up backup strategy

## Deployment Options

### Option 1: Cloud Platform (Recommended)

#### A. Deploy to Railway/Render/Fly.io (Easiest)

**Backend:**
1. Push code to GitHub
2. Connect repository to Railway/Render
3. Set environment variables
4. Deploy

**Frontend:**
1. Deploy to Vercel/Netlify
2. Set `NEXT_PUBLIC_API_URL` to your backend URL
3. Deploy

#### B. Deploy to AWS/GCP/Azure

See detailed instructions below.

### Option 2: VPS/Server (DigitalOcean, Linode, etc.)

See VPS deployment section below.

## Step-by-Step Deployment

### 1. Production Database Setup

#### Using PostgreSQL (Recommended)

```bash
# Install PostgreSQL
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib

# Create database
sudo -u postgres psql
CREATE DATABASE resume_training;
CREATE USER resume_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE resume_training TO resume_user;
\q
```

Update `DATABASE_URL`:
```env
DATABASE_URL=postgresql://resume_user:your_secure_password@localhost:5432/resume_training
```

#### Using Managed Database (Recommended for Production)

- **AWS RDS**: Managed PostgreSQL
- **Google Cloud SQL**: Managed PostgreSQL
- **Supabase**: Free tier available
- **Neon**: Serverless PostgreSQL

### 2. Environment Variables

Create `.env` file for backend:

```env
# Database
DATABASE_URL=postgresql://user:password@host:5432/dbname

# OpenAI (Required for best results)
OPENAI_API_KEY=sk-...

# Security
SECRET_KEY=your-secret-key-here-generate-with-openssl-rand-hex-32
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# File Upload
MAX_UPLOAD_SIZE=10485760  # 10MB
UPLOAD_DIR=./uploads

# Server
HOST=0.0.0.0
PORT=8000
```

### 3. Add User Authentication

We need to add authentication for multi-user support. See `AUTHENTICATION.md` for implementation.

### 4. Backend Deployment

#### Using Docker (Recommended)

Create `Dockerfile` in backend directory:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: resume_training
      POSTGRES_USER: resume_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://resume_user:${DB_PASSWORD}@db:5432/resume_training
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      SECRET_KEY: ${SECRET_KEY}
    depends_on:
      - db
    volumes:
      - ./backend/uploads:/app/uploads

volumes:
  postgres_data:
```

Deploy:
```bash
docker-compose up -d
```

#### Using Gunicorn (Production WSGI Server)

```bash
pip install gunicorn

# Run with Gunicorn
gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

#### Using Systemd Service

Create `/etc/systemd/system/resume-training.service`:

```ini
[Unit]
Description=Resume Training API
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/resume-training/backend
Environment="PATH=/var/www/resume-training/venv/bin"
ExecStart=/var/www/resume-training/venv/bin/gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable resume-training
sudo systemctl start resume-training
```

### 5. Frontend Deployment

#### Deploy to Vercel (Recommended)

1. Install Vercel CLI: `npm i -g vercel`
2. In frontend directory: `vercel`
3. Set environment variable: `NEXT_PUBLIC_API_URL=https://your-backend-url.com`
4. Deploy: `vercel --prod`

#### Deploy to Netlify

1. Build: `npm run build`
2. Deploy folder: `.next`
3. Set environment variable: `NEXT_PUBLIC_API_URL`

#### Build for Production

```bash
cd frontend
npm run build
npm start
```

### 6. Reverse Proxy (Nginx)

Create `/etc/nginx/sites-available/resume-training`:

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Increase timeout for file uploads
        client_max_body_size 10M;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/resume-training /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 7. SSL Certificate (Let's Encrypt)

```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

## Production Configuration

### Update Backend for Production

Update `backend/src/main.py`:

```python
# Add CORS with specific origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add rate limiting
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
```

### File Storage

For production, use cloud storage:

- **AWS S3**: For resume files
- **Google Cloud Storage**: Alternative
- **Azure Blob Storage**: Alternative

Update resume upload to use cloud storage instead of local filesystem.

### Monitoring

Set up monitoring:

1. **Application Monitoring**: 
   - Sentry for error tracking
   - Datadog/New Relic for APM

2. **Logging**:
   - Use structured logging (JSON)
   - Send logs to CloudWatch/Loggly

3. **Health Checks**:
   - `/health` endpoint already exists
   - Set up uptime monitoring (UptimeRobot, Pingdom)

### Backup Strategy

1. **Database Backups**:
   ```bash
   # Daily backup script
   pg_dump resume_training > backup_$(date +%Y%m%d).sql
   ```

2. **Automated Backups**:
   - Use managed database with automatic backups
   - Or set up cron job for regular backups

## Scaling Considerations

### Horizontal Scaling

1. **Backend**: Use load balancer with multiple instances
2. **Database**: Use read replicas for read-heavy workloads
3. **File Storage**: Use CDN for static assets

### Caching

Add Redis for:
- Session storage
- API response caching
- Rate limiting

### Queue System

For async tasks (training generation):
- Use Celery with Redis/RabbitMQ
- Process training generation in background

## Security Checklist

- [ ] Use HTTPS everywhere
- [ ] Implement authentication/authorization
- [ ] Validate and sanitize all inputs
- [ ] Set up rate limiting
- [ ] Use environment variables for secrets
- [ ] Regular security updates
- [ ] SQL injection prevention (using ORM)
- [ ] XSS prevention
- [ ] CSRF protection
- [ ] File upload validation
- [ ] API key rotation

## Next Steps After Deployment

1. **Add User Management**: See `AUTHENTICATION.md`
2. **Set up Analytics**: Track usage
3. **Create Admin Dashboard**: Manage users and content
4. **Add Email Notifications**: Notify users of training completion
5. **Implement Progress Tracking**: Track user progress through modules
6. **Add Assessment/Quizzes**: Test knowledge after modules

## Troubleshooting

### Common Issues

1. **Database Connection Errors**:
   - Check DATABASE_URL format
   - Verify database is running
   - Check firewall rules

2. **CORS Errors**:
   - Update ALLOWED_ORIGINS
   - Check frontend API URL

3. **File Upload Issues**:
   - Check file size limits
   - Verify upload directory permissions
   - Check disk space

4. **Performance Issues**:
   - Add caching
   - Optimize database queries
   - Use CDN for static assets

## Support

For issues, check:
- Application logs: `journalctl -u resume-training`
- Nginx logs: `/var/log/nginx/error.log`
- Database logs: Check PostgreSQL logs



