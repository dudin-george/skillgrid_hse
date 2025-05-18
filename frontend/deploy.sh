#!/bin/bash

echo "SkillGrid Deployment Script"
echo "=========================="
echo ""

# Help function
show_help() {
  echo "Usage: $0 [OPTION] or $0 [REPOSITORY_URL]"
  echo ""
  echo "Options:"
  echo "  ports         - Check and configure ports only"
  echo "  ssl           - Set up SSL certificates only" 
  echo "  app           - Deploy the application only"
  echo "  docker        - Install Docker and Docker Compose only"
  echo "  [REPOSITORY_URL] - Clone the specified git repository and perform a full deployment"
  echo "  help          - Show this help message"
  echo ""
  echo "Examples:"
  echo "  $0                            - Perform full deployment (if already in the code directory)"
  echo "  $0 https://github.com/user/repo.git - Clone repository and perform full deployment"
  echo "  $0 ports                      - Only check and configure ports"
  echo ""
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root (use sudo)"
  exit 1
fi

# Function to install Docker and Docker Compose if needed
install_docker() {
  echo "Checking Docker and Docker Compose installation..."
  
  # Check if Docker is installed
  if ! command -v docker &> /dev/null; then
    echo "Docker not found. Installing Docker..."
    
    # Install dependencies
    apt-get update
    apt-get install -y apt-transport-https ca-certificates curl software-properties-common gnupg

    # Add Docker's official GPG key
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    
    # Add Docker repository
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # Install Docker
    apt-get update
    apt-get install -y docker-ce docker-ce-cli containerd.io
    
    # Start and enable Docker
    systemctl start docker
    systemctl enable docker
    
    echo "Docker installed successfully."
  else
    echo "Docker is already installed."
  fi
  
  # Check if Docker Compose is installed
  if ! command -v docker-compose &> /dev/null; then
    echo "Docker Compose not found. Installing Docker Compose..."
    
    # Install Docker Compose
    COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep 'tag_name' | cut -d\" -f4)
    mkdir -p /usr/local/lib/docker/cli-plugins
    curl -L "https://github.com/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/lib/docker/cli-plugins/docker-compose
    chmod +x /usr/local/lib/docker/cli-plugins/docker-compose
    ln -sf /usr/local/lib/docker/cli-plugins/docker-compose /usr/local/bin/docker-compose
    
    echo "Docker Compose installed successfully."
  else
    echo "Docker Compose is already installed."
  fi
}

# Function to check ports and connectivity
check_ports() {
  echo "Checking firewall and port configuration..."

  # Check if ufw is installed
  if command -v ufw &> /dev/null; then
    echo "UFW Firewall status:"
    ufw status | grep -E "(80|443|http|https)"
    
    # Ensure ports are open
    echo "Ensuring required ports are open..."
    ufw allow 80/tcp
    ufw allow 443/tcp
  fi

  # Check active ports
  echo "Active ports:"
  if command -v ss &> /dev/null; then
    ss -tulpn | grep -E "(80|443)"
  elif command -v netstat &> /dev/null; then
    netstat -tulpn | grep -E "(80|443)"
  fi

  # Check Docker port mappings
  echo "Docker port mappings:"
  docker ps --format "{{.Names}}: {{.Ports}}" 2>/dev/null || echo "No running containers"
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
    echo "Obtaining SSL certificate..."
    certbot certonly --standalone -d skillgrid.tech -d www.skillgrid.tech
  else
    echo "Certificate already exists."
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

# Function to deploy the application
deploy_app() {
  echo "Deploying SkillGrid application..."
  
  # Check if docker-compose is installed
  if ! command -v docker-compose &> /dev/null; then
    echo "Docker Compose not found. Installing Docker components..."
    install_docker
  fi
  
  # Check if nginx.prod.conf exists
  if [ ! -f "./nginx.prod.conf" ]; then
    echo "nginx.prod.conf not found. Creating default configuration..."
    cat > nginx.prod.conf << EOF
server {
    listen 80;
    server_name skillgrid.tech www.skillgrid.tech;

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
    server_name skillgrid.tech www.skillgrid.tech;

    # SSL configuration - updated with correct paths
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
    add_header X-Frame-Options DENY;
    add_header X-XSS-Protection "1; mode=block";
    add_header Referrer-Policy no-referrer-when-downgrade;
    
    # Disable browser caching during development
    add_header Cache-Control "no-cache, no-store, must-revalidate";

    root /usr/share/nginx/html;
    index index.html;

    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

    # API proxy - forward requests to the backend server
    location /api/ {
        proxy_pass https://api.skillgrid.tech/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
    }

    # React router support
    location / {
        try_files \$uri \$uri/ /index.html;
    }

    # Cache control for static assets
    location ~* \.(jpg|jpeg|png|gif|ico|css|js|svg)\$ {
        expires 1y;
        add_header Cache-Control "public, max-age=31536000, immutable";
    }

    # Error pages
    error_page 404 /index.html;
    error_page 500 502 503 504 /50x.html;
    location = /50x.html {
        root /usr/share/nginx/html;
    }
}
EOF
  fi
  
  # Check if Dockerfile exists
  if [ ! -f "./Dockerfile" ]; then
    echo "Dockerfile not found. Creating default Dockerfile..."
    cat > Dockerfile << EOF
# Build stage
FROM node:18-alpine as build

WORKDIR /app

# Define ARGs for environment variables
ARG REACT_APP_ORY_URL
ARG REACT_APP_API_URL

# Set environment variables
ENV REACT_APP_ORY_URL=\${REACT_APP_ORY_URL}
ENV REACT_APP_API_URL=\${REACT_APP_API_URL}

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built assets from the build stage
COPY --from=build /app/build /usr/share/nginx/html

# Expose ports
EXPOSE 80
EXPOSE 443

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
EOF
  fi
  
  # Update docker-compose.prod.yml to use local certificate files
  echo "Updating docker-compose.prod.yml..."
  cat > docker-compose.prod.yml << EOF
version: '3.8'

services:
  frontend:
    build:
      context: .
      dockerfile: Dockerfile
      args:
        - REACT_APP_ORY_URL=https://auth.skillgrid.tech
        - REACT_APP_API_URL=https://skillgrid.tech
    environment:
      - NODE_ENV=production
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.prod.conf:/etc/nginx/conf.d/default.conf
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

# Function to clone the repository if needed
clone_repo() {
  echo "Checking repository..."
  
  # If we're not in a git repository and don't have required files
  if [ ! -d ".git" ] && [ ! -f "package.json" ]; then
    if [ ! -z "$1" ]; then
      REPO_URL="$1"
      
      # Check if git is installed
      if ! command -v git &> /dev/null; then
        echo "Git not found. Installing git..."
        apt-get update
        apt-get install -y git
      fi
      
      echo "Cloning repository from $REPO_URL..."
      # Clone to a temporary directory
      TEMP_DIR=$(mktemp -d)
      git clone "$REPO_URL" "$TEMP_DIR"
      
      # If this is a monorepo, check if there's a frontend directory
      if [ -d "$TEMP_DIR/frontend" ]; then
        echo "Found frontend directory in repository"
        cp -r "$TEMP_DIR/frontend/"* ./
      else
        # Otherwise copy everything
        cp -r "$TEMP_DIR/"* ./
      fi
      
      rm -rf "$TEMP_DIR"
      echo "Repository files copied to current directory."
    else
      echo "No repository URL provided and no frontend code found in current directory."
      echo "Please either:"
      echo "1. Run this script from within the cloned repository directory"
      echo "2. Provide a repository URL: ./deploy.sh https://github.com/user/repo.git"
      exit 1
    fi
  else
    echo "Repository already available in current directory."
  fi
}

# Check arguments and run appropriate function
if [ "$1" == "ports" ]; then
  check_ports
elif [ "$1" == "ssl" ]; then
  setup_ssl
elif [ "$1" == "app" ]; then
  deploy_app
elif [ "$1" == "docker" ]; then
  install_docker
elif [ "$1" == "help" ] || [ "$1" == "--help" ] || [ "$1" == "-h" ]; then
  show_help
elif [[ "$1" == http* ]]; then
  # If the first argument looks like a URL, use it as repo URL
  clone_repo "$1"
  install_docker
  check_ports
  setup_ssl
  deploy_app
else
  # Run all steps (if we're already in the repo)
  install_docker
  check_ports
  setup_ssl
  deploy_app
  
  # Final message
  echo ""
  echo "Deployment complete! Your application should be available at:"
  echo "- http://skillgrid.tech"
  echo "- https://skillgrid.tech"
  echo ""
  echo "To check if the site is accessible:"
  echo "curl -k https://skillgrid.tech"
fi 