# Deployment Guide

This guide covers production deployment of the Clash Royale Deck Builder application using Docker containers.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Environment Setup](#environment-setup)
- [Deployment Methods](#deployment-methods)
- [Security Best Practices](#security-best-practices)
- [Monitoring and Maintenance](#monitoring-and-maintenance)
- [Backup and Recovery](#backup-and-recovery)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Software
- **Docker Engine 20.10+**: Container runtime
- **Docker Compose 2.0+**: Multi-container orchestration
- **Git**: For cloning the repository
- **SSL/TLS Certificates**: For HTTPS in production (recommended)

### Required Credentials
- **Clash Royale API Key**: Production API key from [developer.clashroyale.com](https://developer.clashroyale.com/)
- **Database Passwords**: Strong, unique passwords for production
- **Domain Name**: For production deployment (optional but recommended)

### Server Requirements
- **Minimum**: 2 CPU cores, 4GB RAM, 20GB disk space
- **Recommended**: 4 CPU cores, 8GB RAM, 50GB disk space
- **Operating System**: Linux (Ubuntu 20.04+, Debian 11+, or similar)

## Environment Setup

### 1. Clone Repository
```bash
# Clone the repository
git clone <repository-url>
cd clash_deck_builder

# Checkout the desired version/tag
git checkout v1.0.0  # Or main/master for latest
```

### 2. Create Production Environment File
```bash
# Copy the example environment file
cp .env.example .env

# Edit the file with production values
nano .env  # or vim, vi, etc.
```

### 3. Configure Environment Variables

#### Required Variables
```bash
# Database Configuration
DB_ROOT_PASSWORD=<strong-random-password>
DB_NAME=clash_deck_builder_prod
DB_USER=clash_user
DB_PASSWORD=<strong-random-password>
DB_PORT=3306

# Application Configuration
CLASH_ROYALE_API_KEY=<your-production-api-key>
DEBUG=false
LOG_LEVEL=warning

# CORS Configuration
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Environment
ENVIRONMENT=production
```

#### Password Generation
Generate strong passwords using:
```bash
# Linux/macOS
openssl rand -base64 32

# Or using Python
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Or using pwgen (if installed)
pwgen -s 32 1
```

### 4. Validate Environment Configuration
```bash
# Check if all required variables are set
./scripts/deploy.sh validate

# Or manually check
docker-compose -f docker-compose.yml -f docker-compose.prod.yml config
```

## Deployment Methods

### Method 1: Docker Compose (Recommended for Single Server)

#### Initial Deployment
```bash
# 1. Build containers
docker-compose -f docker-compose.yml -f docker-compose.prod.yml build

# 2. Start services
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# 3. Verify services are running
docker-compose ps

# 4. Check service health
curl http://localhost:8000/health

# 5. View logs
docker-compose logs -f
```

#### Using Deployment Script
```bash
# Deploy to production
./scripts/deploy.sh production

# The script will:
# - Validate environment variables
# - Build containers
# - Start services
# - Run health checks
```

### Method 2: Docker Swarm (For Multi-Server Deployment)

#### Initialize Swarm
```bash
# On manager node
docker swarm init --advertise-addr <manager-ip>

# On worker nodes (use token from init output)
docker swarm join --token <token> <manager-ip>:2377
```

#### Deploy Stack
```bash
# Deploy the application stack
docker stack deploy -c docker-compose.yml -c docker-compose.prod.yml clash-deck-builder

# Check stack status
docker stack services clash-deck-builder

# View logs
docker service logs clash-deck-builder_backend
```

### Method 3: Kubernetes (For Large-Scale Deployment)

See [kubernetes/README.md](kubernetes/README.md) for Kubernetes deployment instructions.

## Security Best Practices

### 1. Environment Variable Management

#### Using Docker Secrets (Swarm/Kubernetes)
```bash
# Create secrets
echo "your-db-password" | docker secret create db_password -
echo "your-api-key" | docker secret create clash_api_key -

# Update docker-compose.yml to use secrets
# secrets:
#   db_password:
#     external: true
#   clash_api_key:
#     external: true
```

#### Using External Secrets Management
```bash
# AWS Secrets Manager
aws secretsmanager create-secret \
  --name clash-deck-builder/db-password \
  --secret-string "your-password"

# Azure Key Vault
az keyvault secret set \
  --vault-name your-vault \
  --name db-password \
  --value "your-password"

# HashiCorp Vault
vault kv put secret/clash-deck-builder \
  db_password="your-password" \
  api_key="your-api-key"
```

### 2. Network Security

#### Firewall Configuration
```bash
# Allow only necessary ports
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable

# Block direct database access from outside
sudo ufw deny 3306/tcp
```

#### Docker Network Isolation
```yaml
# In docker-compose.prod.yml
networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge
    internal: true  # No external access

services:
  backend:
    networks:
      - frontend
      - backend
  database:
    networks:
      - backend  # Only accessible from backend
```

### 3. SSL/TLS Configuration

#### Using Nginx Reverse Proxy
```bash
# Install Nginx
sudo apt-get update
sudo apt-get install nginx certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Nginx configuration
sudo nano /etc/nginx/sites-available/clash-deck-builder
```

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Frontend
    location / {
        root /var/www/clash-deck-builder;
        try_files $uri $uri/ /index.html;
    }
}
```

#### Using Traefik (Docker-Native)
```yaml
# Add to docker-compose.prod.yml
services:
  traefik:
    image: traefik:v2.10
    command:
      - "--providers.docker=true"
      - "--entrypoints.web.address=:80"
      - "--entrypoints.websecure.address=:443"
      - "--certificatesresolvers.letsencrypt.acme.email=admin@yourdomain.com"
      - "--certificatesresolvers.letsencrypt.acme.storage=/letsencrypt/acme.json"
      - "--certificatesresolvers.letsencrypt.acme.httpchallenge.entrypoint=web"
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - ./letsencrypt:/letsencrypt

  backend:
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.backend.rule=Host(`api.yourdomain.com`)"
      - "traefik.http.routers.backend.entrypoints=websecure"
      - "traefik.http.routers.backend.tls.certresolver=letsencrypt"
```

### 4. Database Security

#### Secure Database Configuration
```sql
-- Connect to MySQL
docker-compose exec database mysql -u root -p

-- Create production user with limited privileges
CREATE USER 'clash_user'@'%' IDENTIFIED BY 'strong-password';
GRANT SELECT, INSERT, UPDATE, DELETE ON clash_deck_builder_prod.* TO 'clash_user'@'%';
FLUSH PRIVILEGES;

-- Remove test databases and users
DROP DATABASE IF EXISTS test;
DELETE FROM mysql.user WHERE User='';
FLUSH PRIVILEGES;
```

#### Enable MySQL SSL
```yaml
# In docker-compose.prod.yml
services:
  database:
    environment:
      MYSQL_SSL_CA: /etc/mysql/certs/ca.pem
      MYSQL_SSL_CERT: /etc/mysql/certs/server-cert.pem
      MYSQL_SSL_KEY: /etc/mysql/certs/server-key.pem
    volumes:
      - ./certs:/etc/mysql/certs:ro
```

### 5. Container Security

#### Run as Non-Root User
```dockerfile
# Already implemented in backend/Dockerfile
RUN useradd --create-home --shell /bin/bash app
USER app
```

#### Security Scanning
```bash
# Scan images for vulnerabilities
docker scan clash-deck-builder-backend:latest

# Or using Trivy
trivy image clash-deck-builder-backend:latest
```

#### Resource Limits
```yaml
# In docker-compose.prod.yml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

## Monitoring and Maintenance

### 1. Health Monitoring

#### Health Check Endpoints
```bash
# Backend health
curl https://yourdomain.com/api/health

# Database health
docker-compose exec database mysqladmin ping -h localhost
```

#### Automated Health Checks
```bash
# Create monitoring script
cat > /usr/local/bin/health-check.sh << 'EOF'
#!/bin/bash
if ! curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "Backend health check failed"
    docker-compose restart backend
    # Send alert (email, Slack, etc.)
fi
EOF

chmod +x /usr/local/bin/health-check.sh

# Add to crontab
crontab -e
# Add: */5 * * * * /usr/local/bin/health-check.sh
```

### 2. Log Management

#### Centralized Logging
```yaml
# In docker-compose.prod.yml
services:
  backend:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

#### Log Rotation
```bash
# Configure Docker log rotation
sudo nano /etc/docker/daemon.json
```

```json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "5"
  }
}
```

```bash
# Restart Docker
sudo systemctl restart docker
```

#### Viewing Logs
```bash
# View recent logs
docker-compose logs --tail=100 backend

# Follow logs in real-time
docker-compose logs -f backend

# Export logs for analysis
docker-compose logs --no-color > logs-$(date +%Y%m%d).txt
```

### 3. Performance Monitoring

#### Resource Monitoring
```bash
# Monitor container resources
docker stats

# Detailed monitoring with cAdvisor
docker run -d \
  --name=cadvisor \
  --volume=/:/rootfs:ro \
  --volume=/var/run:/var/run:ro \
  --volume=/sys:/sys:ro \
  --volume=/var/lib/docker/:/var/lib/docker:ro \
  --publish=8080:8080 \
  gcr.io/cadvisor/cadvisor:latest
```

#### Application Performance Monitoring (APM)
```python
# Add to backend for monitoring
# Example with Prometheus
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()
Instrumentator().instrument(app).expose(app)
```

### 4. Database Maintenance

#### Regular Optimization
```sql
-- Optimize tables
OPTIMIZE TABLE users, decks, cards_cache;

-- Analyze tables for query optimization
ANALYZE TABLE users, decks, cards_cache;

-- Check table integrity
CHECK TABLE users, decks, cards_cache;
```

#### Index Monitoring
```sql
-- Check index usage
SELECT * FROM sys.schema_unused_indexes;

-- Check for missing indexes
SELECT * FROM sys.schema_tables_with_full_table_scans;
```

## Backup and Recovery

### 1. Automated Backups

#### Database Backup Script
```bash
# The backup script is already provided
./scripts/backup-database.sh

# Schedule automated backups
crontab -e
# Add: 0 2 * * * /path/to/scripts/backup-database.sh
```

#### Backup to Remote Storage
```bash
# Backup to AWS S3
aws s3 cp database/backups/backup-$(date +%Y%m%d).sql.gz \
  s3://your-bucket/backups/

# Backup to Azure Blob Storage
az storage blob upload \
  --account-name youraccount \
  --container-name backups \
  --file database/backups/backup-$(date +%Y%m%d).sql.gz

# Backup to Google Cloud Storage
gsutil cp database/backups/backup-$(date +%Y%m%d).sql.gz \
  gs://your-bucket/backups/
```

### 2. Backup Verification
```bash
# Test backup restoration
./scripts/restore-database.sh database/backups/backup-latest.sql.gz

# Verify data integrity
docker-compose exec database mysql -u root -p -e "
  USE clash_deck_builder_prod;
  SELECT COUNT(*) FROM users;
  SELECT COUNT(*) FROM decks;
  SELECT COUNT(*) FROM cards_cache;
"
```

### 3. Disaster Recovery Plan

#### Recovery Procedure
```bash
# 1. Stop services
docker-compose down

# 2. Restore database from backup
./scripts/restore-database.sh database/backups/backup-YYYYMMDD.sql.gz

# 3. Restart services
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# 4. Verify application functionality
curl https://yourdomain.com/api/health
```

#### Recovery Time Objective (RTO)
- **Target**: < 1 hour
- **Steps**: Documented and tested quarterly

#### Recovery Point Objective (RPO)
- **Target**: < 24 hours
- **Method**: Daily automated backups

## Updating and Maintenance

### 1. Application Updates

#### Zero-Downtime Deployment
```bash
# 1. Pull latest code
git pull origin main

# 2. Build new images
docker-compose -f docker-compose.yml -f docker-compose.prod.yml build

# 3. Rolling update (Docker Swarm)
docker service update --image clash-deck-builder-backend:latest \
  clash-deck-builder_backend

# 4. Or recreate containers (Docker Compose)
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --no-deps backend
```

#### Database Migrations
```bash
# 1. Backup database before migration
./scripts/backup-database.sh

# 2. Run migrations
docker-compose exec backend python -m database.migrations.migrate

# 3. Verify migration success
docker-compose logs backend | grep -i migration
```

### 2. Security Updates

#### Update Base Images
```bash
# Pull latest base images
docker-compose pull

# Rebuild with latest security patches
docker-compose build --no-cache

# Restart services
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

#### Update Dependencies
```bash
# Backend dependencies
cd backend
uv lock --upgrade
docker-compose build backend

# Frontend dependencies
cd frontend
npm audit fix
npm update
```

### 3. Scaling

#### Horizontal Scaling (Docker Swarm)
```bash
# Scale backend service
docker service scale clash-deck-builder_backend=3

# Or in docker-compose.yml
services:
  backend:
    deploy:
      replicas: 3
```

#### Vertical Scaling
```yaml
# Increase resource limits
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 4G
```

## Troubleshooting

### Common Production Issues

#### Service Won't Start
```bash
# Check logs
docker-compose logs backend

# Common causes:
# 1. Environment variables not set
docker-compose config | grep -E "(DB_|API_KEY)"

# 2. Port conflicts
sudo netstat -tulpn | grep -E "(8000|3306)"

# 3. Insufficient resources
docker stats
free -h
df -h
```

#### Database Connection Failures
```bash
# Test database connectivity
docker-compose exec backend ping database

# Check database status
docker-compose exec database mysqladmin ping -h localhost

# Verify credentials
docker-compose exec backend env | grep DB_
```

#### Performance Degradation
```bash
# Check resource usage
docker stats

# Check database performance
docker-compose exec database mysql -u root -p -e "SHOW PROCESSLIST;"

# Check slow queries
docker-compose exec database mysql -u root -p -e "
  SELECT * FROM mysql.slow_log ORDER BY start_time DESC LIMIT 10;
"
```

#### SSL/TLS Issues
```bash
# Test SSL certificate
openssl s_client -connect yourdomain.com:443

# Check certificate expiration
echo | openssl s_client -connect yourdomain.com:443 2>/dev/null | \
  openssl x509 -noout -dates

# Renew Let's Encrypt certificate
sudo certbot renew
```

### Emergency Procedures

#### Service Restart
```bash
# Restart specific service
docker-compose restart backend

# Restart all services
docker-compose restart

# Force recreate containers
docker-compose up -d --force-recreate
```

#### Rollback Deployment
```bash
# 1. Stop current version
docker-compose down

# 2. Checkout previous version
git checkout <previous-tag>

# 3. Restore database if needed
./scripts/restore-database.sh database/backups/backup-before-update.sql.gz

# 4. Start previous version
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## Deployment Checklist

### Pre-Deployment
- [ ] Environment variables configured and validated
- [ ] Strong passwords generated for all services
- [ ] SSL/TLS certificates obtained and configured
- [ ] Firewall rules configured
- [ ] Backup system tested and verified
- [ ] Monitoring and alerting configured
- [ ] DNS records configured
- [ ] Load balancer configured (if applicable)

### Deployment
- [ ] Code pulled from repository
- [ ] Containers built successfully
- [ ] Database initialized or migrated
- [ ] Services started and healthy
- [ ] Health checks passing
- [ ] Logs reviewed for errors
- [ ] Application accessible via domain

### Post-Deployment
- [ ] Smoke tests completed
- [ ] Performance metrics baseline established
- [ ] Backup schedule verified
- [ ] Monitoring alerts tested
- [ ] Documentation updated
- [ ] Team notified of deployment
- [ ] Rollback plan documented

## Additional Resources

- [Docker Production Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [MySQL Production Configuration](https://dev.mysql.com/doc/refman/8.0/en/server-configuration.html)
- [OWASP Security Guidelines](https://owasp.org/www-project-top-ten/)
- [Let's Encrypt Documentation](https://letsencrypt.org/docs/)

## Support and Maintenance

### Regular Maintenance Schedule
- **Daily**: Automated backups, log review
- **Weekly**: Security updates, performance review
- **Monthly**: Dependency updates, capacity planning
- **Quarterly**: Disaster recovery testing, security audit

### Getting Help
For deployment issues or questions:
1. Check logs: `docker-compose logs`
2. Review this documentation
3. Check [DOCKER.md](DOCKER.md) for troubleshooting
4. Contact the development team
5. Review GitHub issues and discussions
