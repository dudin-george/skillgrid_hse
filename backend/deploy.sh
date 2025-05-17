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
    API_DOMAIN="www.api.skillgrid.tech"
    PRODUCTION=true
    echo -e "${GREEN}Setting up production deployment for skillgrid.tech${NC}"
  else
    DOMAIN="localhost"
    API_DOMAIN="localhost"
    PRODUCTION=false
    echo -e "${YELLOW}Setting up development deployment for localhost${NC}"
  fi
else
  DOMAIN="$1"
  API_DOMAIN="www.api.$1"
  PRODUCTION=true
  echo -e "${GREEN}Setting up production deployment for domain: ${DOMAIN}${NC}"
  echo -e "${GREEN}API will be accessible at: ${API_DOMAIN}${NC}"
fi

# Create necessary directories
mkdir -p nginx/ssl nginx/conf nginx/www

# Configure Nginx default config
echo -e "${GREEN}Configuring Nginx main site...${NC}"
cat > nginx/conf/default.conf << EOF
# Rate limiting configuration
limit_req_zone \$binary_remote_addr zone=api:10m rate=10r/s;

server {
    listen 80;
    server_name ${DOMAIN} www.${DOMAIN};
    
    # Redirect all HTTP to HTTPS
    location / {
        return 301 https://\$host\$request_uri;
    }
}

server {
    listen 443 ssl;
    server_name ${DOMAIN} www.${DOMAIN};
    
    ssl_certificate /etc/nginx/ssl/skillgrid.crt;
    ssl_certificate_key /etc/nginx/ssl/skillgrid.key;
    
    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_session_timeout 10m;
    ssl_session_cache shared:SSL:10m;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options DENY;
    add_header X-XSS-Protection "1; mode=block";
    
    # Redirect API endpoints to api subdomain
    location /docs {
        return 301 https://${API_DOMAIN}/docs;
    }

    location /openapi.json {
        return 301 https://${API_DOMAIN}/openapi.json;
    }

    location /api/ {
        return 301 https://${API_DOMAIN}\$request_uri;
    }
    
    # Proxy requests to the API
    location / {
        proxy_pass http://api:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        limit_req zone=api burst=20 nodelay;
    }
}
EOF

# Configure Nginx API config
echo -e "${GREEN}Configuring Nginx API site...${NC}"
cat > nginx/conf/api.conf << EOF
# Rate limiting configuration
limit_req_zone \$binary_remote_addr zone=api_subdomain:10m rate=10r/s;

# Redirect from old domain to new domain
server {
    listen 80;
    listen 443 ssl;
    server_name api.${DOMAIN};
    
    # SSL configuration
    ssl_certificate /etc/nginx/ssl/skillgrid.crt;
    ssl_certificate_key /etc/nginx/ssl/skillgrid.key;
    
    # Redirect all traffic to new domain
    return 301 https://${API_DOMAIN}\$request_uri;
}

server {
    listen 80;
    server_name ${API_DOMAIN};
    
    # Redirect all HTTP to HTTPS
    location / {
        return 301 https://\$host\$request_uri;
    }
}

server {
    listen 443 ssl;
    server_name ${API_DOMAIN};
    
    # SSL configuration
    ssl_certificate /etc/nginx/ssl/skillgrid.crt;
    ssl_certificate_key /etc/nginx/ssl/skillgrid.key;

    # SSL settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_session_timeout 10m;
    ssl_session_cache shared:SSL:10m;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options DENY;
    add_header X-XSS-Protection "1; mode=block";

    # Proxy to FastAPI
    location / {
        proxy_pass http://api:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        limit_req zone=api_subdomain burst=20 nodelay;
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
  echo -e "${GREEN}Obtaining Let's Encrypt certificates for ${DOMAIN}, www.${DOMAIN}, api.${DOMAIN} and ${API_DOMAIN}...${NC}"
  sudo certbot certonly --standalone --agree-tos --non-interactive --expand -d ${DOMAIN} -d www.${DOMAIN} -d api.${DOMAIN} -d ${API_DOMAIN} --email admin@${DOMAIN}
  
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
echo -e "${GREEN}- Main site: https://${DOMAIN}${NC}"
echo -e "${GREEN}- API site: https://${API_DOMAIN}${NC}"
echo -e ""
echo -e "${YELLOW}Management commands:${NC}"
echo -e "${YELLOW}- View logs: docker-compose -f docker-compose.prod.yml logs -f api${NC}"
echo -e "${YELLOW}- Stop application: docker-compose -f docker-compose.prod.yml down${NC}"
echo -e "${YELLOW}- Update application: git pull && docker-compose -f docker-compose.prod.yml up -d --build${NC}" 