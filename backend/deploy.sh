#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting SkillGrid Backend Deployment...${NC}"

# Check for domain name argument
if [ -z "$1" ]; then
  # No argument provided, ask if production or development
  echo -e "${YELLOW}Do you want to deploy for production or development?${NC}"
  echo -e "${YELLOW}1) Production (skillgrid.tech)${NC}"
  echo -e "${YELLOW}2) Development (localhost)${NC}"
  read -p "Enter your choice (1 or 2): " choice
  
  if [ "$choice" = "1" ]; then
    DOMAIN="skillgrid.tech"
    PRODUCTION=true
    echo -e "${GREEN}Setting up production deployment for skillgrid.tech${NC}"
  else
    DOMAIN="localhost"
    PRODUCTION=false
    echo -e "${YELLOW}Setting up development deployment for localhost${NC}"
  fi
else
  DOMAIN="$1"
  PRODUCTION=true
  echo -e "${GREEN}Setting up production deployment for domain: ${DOMAIN}${NC}"
fi

# Create necessary directories
mkdir -p nginx/ssl nginx/conf nginx/www

# Configure Nginx
echo -e "${GREEN}Configuring Nginx...${NC}"
cat > nginx/conf/default.conf << EOF
server {
    listen 80;
    server_name ${DOMAIN};
    
    # Redirect all HTTP requests to HTTPS
    location / {
        return 301 https://\$host\$request_uri;
    }
}

server {
    listen 443 ssl;
    server_name ${DOMAIN};
    
    ssl_certificate /etc/nginx/ssl/skillgrid.crt;
    ssl_certificate_key /etc/nginx/ssl/skillgrid.key;
    
    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_session_timeout 10m;
    ssl_session_cache shared:SSL:10m;
    
    # Proxy requests to the API
    location / {
        proxy_pass http://api:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # Basic static files
    location /static/ {
        alias /var/www/html/static/;
    }
}
EOF

# Set up SSL certificates
echo -e "${GREEN}Setting up SSL certificates...${NC}"

if [ "$PRODUCTION" = true ]; then
  # Check if certbot is installed
  if ! command -v certbot &> /dev/null; then
    echo -e "${YELLOW}Certbot not found. Installing...${NC}"
    sudo apt-get update
    sudo apt-get install -y certbot
  fi
  
  # Get real certificates from Let's Encrypt
  echo -e "${GREEN}Obtaining Let's Encrypt certificates for ${DOMAIN}...${NC}"
  sudo certbot certonly --standalone --agree-tos --non-interactive -d ${DOMAIN} --email admin@${DOMAIN}
  
  # Copy certificates
  sudo cp /etc/letsencrypt/live/${DOMAIN}/fullchain.pem nginx/ssl/skillgrid.crt
  sudo cp /etc/letsencrypt/live/${DOMAIN}/privkey.pem nginx/ssl/skillgrid.key
  
  # Fix permissions
  sudo chmod 644 nginx/ssl/skillgrid.crt
  sudo chmod 644 nginx/ssl/skillgrid.key
else
  # Generate self-signed certificates for development
  echo -e "${YELLOW}Creating self-signed certificates for development...${NC}"
  openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout nginx/ssl/skillgrid.key \
    -out nginx/ssl/skillgrid.crt \
    -subj "/CN=localhost/O=SkillGrid/C=US"
fi

# Create or update .env file
echo -e "${GREEN}Setting up environment variables...${NC}"
cat > .env << EOF
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=skillgrid
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
DEBUG=false
EOF

# Start the containers
echo -e "${GREEN}Starting Docker containers...${NC}"
docker-compose -f docker-compose.prod.yml down || true
docker-compose -f docker-compose.prod.yml up -d --build

# Wait for containers to be ready
echo -e "${GREEN}Waiting for containers to be ready...${NC}"
sleep 10

# Check if containers are running
echo -e "${GREEN}Checking container status:${NC}"
docker-compose -f docker-compose.prod.yml ps

# Display success message
echo -e "${GREEN}Deployment completed!${NC}"
echo -e "${GREEN}Your application is now available at:${NC}"
echo -e "${GREEN}- HTTPS: https://${DOMAIN}${NC}"
echo -e ""
echo -e "${YELLOW}Management commands:${NC}"
echo -e "${YELLOW}- View logs: docker-compose -f docker-compose.prod.yml logs -f api${NC}"
echo -e "${YELLOW}- Stop application: docker-compose -f docker-compose.prod.yml down${NC}"
echo -e "${YELLOW}- Update application: git pull && docker-compose -f docker-compose.prod.yml up -d --build${NC}" 