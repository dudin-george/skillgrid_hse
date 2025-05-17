#!/bin/bash

echo "SkillGrid Deployment Script"
echo "=========================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root (use sudo)"
  exit 1
fi

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
    echo "docker-compose not found. Please install Docker and docker-compose."
    exit 1
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
        - REACT_APP_API_URL=https://api.skillgrid.tech
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

# Check arguments and run appropriate function
if [ "$1" == "ports" ]; then
  check_ports
elif [ "$1" == "ssl" ]; then
  setup_ssl
elif [ "$1" == "app" ]; then
  deploy_app
else
  # Run all steps
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