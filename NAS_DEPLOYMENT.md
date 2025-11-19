# QNAP NAS Deployment Guide

This guide explains how to deploy the Classic Models API on your QNAP NAS using Docker Compose and GitHub Container Registry (GHCR).

> **Note**: For general deployment information, see [DEPLOYMENT.md](DEPLOYMENT.md). For release management, see [RELEASE_MANAGEMENT.md](RELEASE_MANAGEMENT.md).

## Prerequisites

- QNAP NAS with Container Station installed
- SSH access to your QNAP NAS
- GitHub repository with the Classic Models API code
- GitHub Personal Access Token (PAT) with `read:packages` permission

## Step 1: Create GitHub Personal Access Token

1. Go to GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click "Generate new token (classic)"
3. Give it a name like "QNAP NAS GHCR Access"
4. Select the `read:packages` scope
5. Click "Generate token"
6. **Copy the token immediately** - you won't be able to see it again

## Step 2: Set Up GitHub Actions (One-time setup)

The GitHub Actions workflow is already configured in `.github/workflows/docker-build.yml`. It will automatically build and push Docker images to GHCR when you push to the `main` or `develop` branches.

### Enable GitHub Actions:

1. Push your code to GitHub
2. Go to your repository → Actions tab
3. The workflow should run automatically on the first push
4. Check that the image is pushed to GHCR: Go to your repository → Packages tab

## Step 3: Prepare Your QNAP NAS

### 3.1 SSH into your QNAP NAS

```bash
ssh admin@your-nas-ip
```

### 3.2 Create deployment directory

```bash
mkdir -p /share/Container/classic-models-api
cd /share/Container/classic-models-api
```

### 3.3 Download the database initialization file

```bash
# Create db directory
mkdir -p db

# Download the SQL file (replace with your actual file)
# You can copy this from your development machine or download it
# For now, we'll create a placeholder
cat > db/mysqlsampledatabase.sql << 'EOF'
-- This is a placeholder SQL file
-- Replace this with your actual Classic Models database SQL file
CREATE DATABASE IF NOT EXISTS classicmodels;
USE classicmodels;

-- Add your database schema here
-- This file should contain the complete Classic Models database structure
EOF
```

## Step 4: Configure Environment Variables

### 4.1 Create environment file

```bash
cp env.example .env
nano .env
```

### 4.2 Update the environment file with your values:

```bash
# GitHub Container Registry Configuration
GITHUB_REPOSITORY=your-username/classic-models-api

# Django Configuration
DEBUG=0
SECRET_KEY=your-very-secure-secret-key-here-change-this
ALLOWED_HOSTS=your-nas-ip,your-domain.com,localhost

# MySQL Configuration
MYSQL_ROOT_PASSWORD=your-secure-root-password
MYSQL_DATABASE=classicmodels
MYSQL_USER=classicuser
MYSQL_PASSWORD=your-secure-mysql-password
```

**Important:** Replace all placeholder values with your actual values:
- `your-username/classic-models-api` → Your actual GitHub repository
- `your-very-secure-secret-key-here-change-this` → Generate a secure Django secret key
- `your-nas-ip` → Your QNAP NAS IP address
- `your-secure-root-password` → Strong MySQL root password
- `your-secure-mysql-password` → Strong MySQL user password

## Step 5: Login to GitHub Container Registry

### 5.1 Login to GHCR using your PAT

```bash
echo "your-github-pat-token" | docker login ghcr.io -u your-github-username --password-stdin
```

Replace:
- `your-github-pat-token` with your actual GitHub PAT
- `your-github-username` with your GitHub username

### 5.2 Verify login

```bash
docker pull ghcr.io/your-username/classic-models-api:latest
```

## Step 6: Deploy the Application

### 6.1 Start the services

```bash
docker-compose -f docker-compose.nas.yml up -d
```

### 6.2 Check the logs

```bash
# Check API logs
docker-compose -f docker-compose.nas.yml logs -f api

# Check MySQL logs
docker-compose -f docker-compose.nas.yml logs -f mysql
```

### 6.3 Verify the deployment

```bash
# Check running containers
docker-compose -f docker-compose.nas.yml ps

# Test the API
curl http://your-nas-ip:8000/classic-models/api/schema/
```

## Step 7: Access Your Application

- **API Documentation**: `http://your-nas-ip:8000/classic-models/api/docs/`
- **ReDoc Documentation**: `http://your-nas-ip:8000/classic-models/api/redoc/`
- **API Base URL**: `http://your-nas-ip:8000/classic-models/api/v1/`
- **Demo User**: username: `demo`, password: `demo123`

> **Note**: The API is always served at the `/classic-models` base path. See [DEPLOYMENT.md](DEPLOYMENT.md) for more details on the base path configuration.

## Updating the Application

### Method 1: Update to Latest Version

```bash
cd /share/Container/classic-models-api

# Update to latest version
echo "API_VERSION=latest" >> .env

# Pull the latest image
docker-compose -f docker-compose.nas.yml pull

# Restart the services
docker-compose -f docker-compose.nas.yml up -d
```

### Method 2: Update to Specific Version

```bash
cd /share/Container/classic-models-api

# Update to specific version (e.g., v1.0.0)
echo "API_VERSION=v1.0.0" >> .env

# Pull the specific version
docker-compose -f docker-compose.nas.yml pull

# Restart the services
docker-compose -f docker-compose.nas.yml up -d
```

### Method 3: Manual Update (Legacy)

```bash
cd /share/Container/classic-models-api

# Pull the latest image
docker-compose -f docker-compose.nas.yml pull

# Restart the services
docker-compose -f docker-compose.nas.yml up -d
```

### Method 3: Automated Update (Optional)

You can set up a cron job to automatically pull and restart the application:

```bash
# Edit crontab
crontab -e

# Add this line to check for updates every day at 2 AM
0 2 * * * cd /share/Container/classic-models-api && docker-compose -f docker-compose.nas.yml pull && docker-compose -f docker-compose.nas.yml up -d
```

> **Note**: For information on version management and releases, see [RELEASE_MANAGEMENT.md](RELEASE_MANAGEMENT.md).

## Troubleshooting

### Check container status

```bash
docker-compose -f docker-compose.nas.yml ps
```

### View logs

```bash
# All services
docker-compose -f docker-compose.nas.yml logs

# Specific service
docker-compose -f docker-compose.nas.yml logs api
docker-compose -f docker-compose.nas.yml logs mysql
```

### Restart services

```bash
# Restart all services
docker-compose -f docker-compose.nas.yml restart

# Restart specific service
docker-compose -f docker-compose.nas.yml restart api
```

### Clean up (if needed)

```bash
# Stop and remove containers
docker-compose -f docker-compose.nas.yml down

# Remove volumes (WARNING: This will delete your database data)
docker-compose -f docker-compose.nas.yml down -v
```

## Security Considerations

1. **Change default passwords**: Update all default passwords in your `.env` file
2. **Use HTTPS**: Consider setting up a reverse proxy with SSL certificates
3. **Firewall**: Configure your QNAP firewall to only allow necessary ports
4. **Regular updates**: Keep your Docker images updated
5. **Backup**: Regularly backup your MySQL data volume

## Backup and Restore

### Backup MySQL data

```bash
# Create backup
docker-compose -f docker-compose.nas.yml exec mysql mysqldump -u root -p classicmodels > backup_$(date +%Y%m%d_%H%M%S).sql
```

### Restore MySQL data

```bash
# Restore from backup
docker-compose -f docker-compose.nas.yml exec -T mysql mysql -u root -p classicmodels < backup_file.sql
```

## Support

If you encounter issues:

1. Check the logs: `docker-compose -f docker-compose.nas.yml logs`
2. Verify your environment variables in `.env`
3. Ensure your GitHub PAT has the correct permissions
4. Check that the Docker image exists in GHCR
5. Verify network connectivity between containers
