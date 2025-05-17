#!/bin/bash

echo "SkillGrid Auth Proxy Deployment Script"
echo "====================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root (use sudo)"
  exit 1
fi

# Function to check DNS
check_dns() {
  echo "Checking DNS for auth.skillgrid.tech..."
  host auth.skillgrid.tech || {
    echo "ERROR: auth.skillgrid.tech DNS record not found!"
    echo "Please set up a CNAME record for auth.skillgrid.tech pointing to infallible-shaw-gpsjwuc0lg.projects.oryapis.com"
    exit 1
  }
  echo "DNS record for auth.skillgrid.tech found."
  echo ""
}

# Function to set up SSL
setup_ssl() {
  echo "Setting up SSL certificates..."
  
  # Check if certbot is installed
  if ! command -v certbot &> /dev/null; then
    echo "Installing certbot..."
    apt-get update
    apt-get install -y certbot
  fi
  
  # Check if certificate already exists
  if [ ! -d "/etc/letsencrypt/live/skillgrid.tech" ] && [ ! -d "/etc/letsencrypt/live/skillgrid.tech-0001" ] && [ ! -d "/etc/letsencrypt/live/skillgrid.tech-0002" ]; then
    echo "Obtaining SSL certificate for all domains..."
    certbot certonly --standalone -d skillgrid.tech -d www.skillgrid.tech -d auth.skillgrid.tech
  else
    echo "Checking if auth.skillgrid.tech is covered in the certificate..."
    CERT_DIR=""
    for dir in "/etc/letsencrypt/live/skillgrid.tech" "/etc/letsencrypt/live/skillgrid.tech-0001" "/etc/letsencrypt/live/skillgrid.tech-0002"; do
      if [ -d "$dir" ]; then
        CERT_DIR="$dir"
        break
      fi
    done
    
    if [ -n "$CERT_DIR" ]; then
      if openssl x509 -in "$CERT_DIR/fullchain.pem" -text -noout | grep -q "DNS:auth.skillgrid.tech"; then
        echo "Certificate already includes auth.skillgrid.tech"
      else
        echo "Current certificate doesn't include auth.skillgrid.tech. Obtaining a new certificate..."
        certbot certonly --standalone -d skillgrid.tech -d www.skillgrid.tech -d auth.skillgrid.tech
      fi
    else
      echo "Obtaining SSL certificate for all domains..."
      certbot certonly --standalone -d skillgrid.tech -d www.skillgrid.tech -d auth.skillgrid.tech
    fi
  fi
  
  # Find the certificate directory
  CERT_DIR=""
  for dir in "/etc/letsencrypt/live/skillgrid.tech" "/etc/letsencrypt/live/skillgrid.tech-0001" "/etc/letsencrypt/live/skillgrid.tech-0002"; do
    if [ -d "$dir" ]; then
      CERT_DIR="$dir"
      break
    fi
  done
  
  if [ -z "$CERT_DIR" ]; then
    echo "ERROR: No certificate directory found!"
    exit 1
  fi
  
  echo "Found certificate directory: $CERT_DIR"
  
  # Create SSL directory for copied certificates
  echo "Creating SSL certs directory..."
  mkdir -p ./ssl_certs
  
  # Copy certificate files (resolving symlinks)
  echo "Copying certificate files..."
  cp -L $CERT_DIR/fullchain.pem ./ssl_certs/
  cp -L $CERT_DIR/privkey.pem ./ssl_certs/
  cp -L $CERT_DIR/chain.pem ./ssl_certs/
  
  # Set proper permissions
  chmod 644 ./ssl_certs/*.pem
  
  echo "SSL certificates prepared successfully."
}

# Function to create Nginx auth proxy configuration
setup_nginx_config() {
  echo "Setting up Nginx proxy configuration..."
  
  # Create Nginx config for auth subdomain
  cat > nginx.auth-proxy.conf << EOF
server {
    listen 80;
    server_name auth.skillgrid.tech;

    # Redirect all HTTP requests to HTTPS
    location / {
        return 301 https://\$host\$request_uri;
    }

    # Let's Encrypt validation
    location /.well-known/acme-challenge/ {
        root /usr/share/nginx/html;
        try_files \$uri =404;
    }
}

server {
    listen 443 ssl;
    server_name auth.skillgrid.tech;

    # SSL configuration
    ssl_certificate /etc/ssl/certs/skillgrid/fullchain.pem;
    ssl_certificate_key /etc/ssl/certs/skillgrid/privkey.pem;
    ssl_trusted_certificate /etc/ssl/certs/skillgrid/chain.pem;

    # SSL settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-SHA384;
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:10m;
    ssl_session_tickets off;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options nosniff;

    # Proxy to Ory API
    location / {
        proxy_pass https://infallible-shaw-gpsjwuc0lg.projects.oryapis.com;
        proxy_set_header Host infallible-shaw-gpsjwuc0lg.projects.oryapis.com;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_set_header X-Ory-Project-Id cd3eac85-ed95-41dd-9969-9012ab8dea73;
        
        # Handle preflight requests for CORS
        if (\$request_method = 'OPTIONS') {
            add_header 'Access-Control-Allow-Origin' 'https://skillgrid.tech' always;
            add_header 'Access-Control-Allow-Credentials' 'true' always;
            add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS' always;
            add_header 'Access-Control-Allow-Headers' 'DNT,X-CustomHeader,Keep-Alive,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,X-Ory-Project-Id,Origin,Authorization' always;
            add_header 'Access-Control-Max-Age' 1728000;
            add_header 'Content-Type' 'text/plain charset=UTF-8';
            add_header 'Content-Length' 0;
            return 204;
        }
        
        # CORS headers for regular responses
        add_header 'Access-Control-Allow-Origin' 'https://skillgrid.tech' always;
        add_header 'Access-Control-Allow-Credentials' 'true' always;
        add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS' always;
        add_header 'Access-Control-Allow-Headers' 'DNT,X-CustomHeader,Keep-Alive,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,X-Ory-Project-Id,Origin,Authorization' always;
    }
}
EOF
  
  echo "Nginx proxy configuration created successfully."
}

# Function to update OryContext.tsx
update_ory_context() {
  echo "Updating OryContext.tsx..."
  
  # Update the OryContext.tsx to use the auth subdomain
  sed -i 's|const ORY_SDK_URL = process.env.REACT_APP_ORY_URL || "https://infallible-shaw-gpsjwuc0lg.projects.oryapis.com";|const ORY_SDK_URL = process.env.REACT_APP_ORY_URL || "https://auth.skillgrid.tech";|g' src/context/OryContext.tsx
  
  echo "OryContext.tsx updated successfully."
}

# Function to deploy the application
deploy_app() {
  echo "Deploying SkillGrid with auth proxy..."
  
  # Update docker-compose.prod.yml to use auth proxy
  cat > docker-compose.prod.yml << EOF
version: '3.8'

services:
  frontend:
    build:
      context: .
      dockerfile: Dockerfile
      args:
        - REACT_APP_ORY_URL=https://auth.skillgrid.tech
        - REACT_APP_API_URL=https://api.skillgrid.tech
    environment:
      - NODE_ENV=production
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.prod.conf:/etc/nginx/conf.d/default.conf
      - ./nginx.auth-proxy.conf:/etc/nginx/conf.d/auth-proxy.conf
      - ./ssl_certs/fullchain.pem:/etc/ssl/certs/skillgrid/fullchain.pem
      - ./ssl_certs/privkey.pem:/etc/ssl/certs/skillgrid/privkey.pem
      - ./ssl_certs/chain.pem:/etc/ssl/certs/skillgrid/chain.pem
    restart: unless-stopped
    networks:
      - skillgrid-network

networks:
  skillgrid-network:
    driver: bridge
EOF
  
  # Create required directory for SSL certs in container
  mkdir -p /etc/ssl/certs/skillgrid
  
  # Stop any running containers and start with new configuration
  echo "Starting Docker containers..."
  docker-compose -f docker-compose.prod.yml down
  docker-compose -f docker-compose.prod.yml up -d --build
  
  # Wait for container to start
  echo "Waiting for container to start..."
  sleep 10
  
  # Check container status
  echo "Docker container status:"
  docker ps -a | grep frontend
  
  # Show logs if container is not running properly
  if ! docker ps | grep -q frontend; then
    echo "Container logs:"
    docker-compose -f docker-compose.prod.yml logs --tail=20
  fi
}

# Main script
check_dns
setup_ssl
setup_nginx_config
update_ory_context
deploy_app

# Final message
echo ""
echo "Auth proxy deployment complete! Your application should be available at:"
echo "- http://skillgrid.tech"
echo "- https://skillgrid.tech"
echo ""
echo "The auth proxy is set up at:"
echo "- https://auth.skillgrid.tech"
echo ""
echo "To test if the proxy is working, try:"
echo "curl -k https://auth.skillgrid.tech/sessions/whoami -H 'Origin: https://skillgrid.tech' -v" 