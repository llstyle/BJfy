#!/bin/bash

# BJfy Production Deployment Script
# Usage: ./deploy.sh

set -e  # Exit on error

echo "🚀 Starting BJfy deployment..."

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
PROJECT_DIR="/var/www/BJfy"
VENV_DIR="$PROJECT_DIR/env"
MANAGE_PY="$PROJECT_DIR/config/manage.py"

# Check if running as correct user
if [ "$EUID" -eq 0 ]; then 
    echo -e "${RED}❌ Don't run this script as root!${NC}"
    exit 1
fi

# Navigate to project directory
cd $PROJECT_DIR || exit

# Pull latest changes
echo -e "${YELLOW}📥 Pulling latest changes from Git...${NC}"
git pull origin main

# Activate virtual environment
echo -e "${YELLOW}🐍 Activating virtual environment...${NC}"
source $VENV_DIR/bin/activate

# Install/update dependencies
echo -e "${YELLOW}📦 Installing dependencies...${NC}"
pip install -r requirements.txt --upgrade

# Collect static files
echo -e "${YELLOW}📂 Collecting static files...${NC}"
cd config
python manage.py collectstatic --noinput

# Run migrations
echo -e "${YELLOW}🗄️  Running database migrations...${NC}"
python manage.py migrate --noinput

# Check for issues
echo -e "${YELLOW}🔍 Running system checks...${NC}"
python manage.py check --deploy

# Restart Gunicorn
echo -e "${YELLOW}🔄 Restarting Gunicorn service...${NC}"
sudo systemctl restart bjfy

# Check service status
if sudo systemctl is-active --quiet bjfy; then
    echo -e "${GREEN}✅ Deployment successful!${NC}"
    echo -e "${GREEN}🎵 BJfy is now running${NC}"
else
    echo -e "${RED}❌ Deployment failed! Check logs:${NC}"
    echo "sudo journalctl -u bjfy -n 50"
    exit 1
fi

# Show service status
echo -e "\n${YELLOW}📊 Service status:${NC}"
sudo systemctl status bjfy --no-pager -l

echo -e "\n${GREEN}✨ Deployment complete!${NC}"
