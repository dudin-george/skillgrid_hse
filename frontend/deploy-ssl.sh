#!/bin/bash

echo "Deploying SkillGrid with SSL..."

# Check if the SSL certificate exists
if [ ! -d "/etc/letsencrypt/live/skillgrid.tech-0002" ]; then
  echo "ERROR: SSL certificate not found at /etc/letsencrypt/live/skillgrid.tech-0002"
  echo "Please run ./setup-ssl.sh first to obtain the certificate"
  exit 1
fi

# Make sure the certificate is readable by Docker
echo "Setting permissions on SSL certificates..."
chmod -R 755 /etc/letsencrypt/live/skillgrid.tech-0002
chmod -R 755 /etc/letsencrypt/archive/skillgrid.tech-0002

# Start the containers with the updated configuration
echo "Starting Docker containers with SSL..."
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d

# Check if the deployment was successful
echo "Checking HTTPS connectivity..."
sleep 5
curl -k https://skillgrid.tech

echo ""
echo "Deployment completed. Check https://skillgrid.tech in your browser." 