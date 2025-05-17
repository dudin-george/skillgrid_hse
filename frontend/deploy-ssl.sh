#!/bin/bash

echo "Deploying SkillGrid with SSL..."

# Check if the SSL certificate exists - try all possible paths
CERT_DIR=""
if [ -d "/etc/letsencrypt/live/skillgrid.tech-0002" ]; then
  CERT_DIR="/etc/letsencrypt/live/skillgrid.tech-0002"
elif [ -d "/etc/letsencrypt/live/skillgrid.tech" ]; then
  CERT_DIR="/etc/letsencrypt/live/skillgrid.tech"
elif [ -d "/etc/letsencrypt/live/skillgrid.tech-0001" ]; then
  CERT_DIR="/etc/letsencrypt/live/skillgrid.tech-0001"
else
  echo "ERROR: SSL certificate not found for skillgrid.tech"
  echo "Available certificates:"
  ls -la /etc/letsencrypt/live/
  echo "Please run certbot to obtain the certificate first"
  exit 1
fi

echo "Found certificate directory: $CERT_DIR"

# Update docker-compose.prod.yml with the correct certificate path
sed -i "s|/etc/letsencrypt/live/skillgrid.tech-0002|$CERT_DIR|g" docker-compose.prod.yml

# Debug: List all available certificates
echo "Available certificates:"
ls -la /etc/letsencrypt/live/

# Make sure the certificate is readable by Docker
echo "Setting permissions on SSL certificates..."
chmod -R 755 $CERT_DIR
archive_dir=$(echo $CERT_DIR | sed 's|live|archive|')
chmod -R 755 $archive_dir

# Debug: Verify nginx config
echo "Checking nginx.prod.conf:"
cat nginx.prod.conf | grep -A5 "ssl_certificate"

# Debug: Verify docker-compose config
echo "Checking docker-compose.prod.yml:"
cat docker-compose.prod.yml | grep -A5 "volumes:"

# Start the containers with the updated configuration
echo "Starting Docker containers with SSL..."
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d --build

# Give the container a moment to start
echo "Waiting for container to start..."
sleep 10

# Debug: Check if container is running and port mappings
echo "Docker container status:"
docker ps -a
echo "Port mappings:"
docker-compose -f docker-compose.prod.yml ps

# Check if the deployment was successful
echo "Checking HTTPS connectivity:"
echo "Testing local connection to port 443:"
curl -k https://localhost:443 -v

echo ""
echo "Testing domain connection:"
curl -k https://skillgrid.tech -v

echo ""
echo "Deployment completed. Check https://skillgrid.tech in your browser."
echo ""
echo "If you're unable to connect, check the following:"
echo "1. Firewall settings (ports 80 and 443 should be open)"
echo "2. Docker container logs: docker-compose -f docker-compose.prod.yml logs"
echo "3. Check if nginx is listening on port 443: docker exec frontend-frontend-1 netstat -tulpn" 