#!/bin/bash

echo "Setting up SSL for skillgrid.tech..."

# Install certbot if not installed
if ! [ -x "$(command -v certbot)" ]; then
  echo "Installing certbot..."
  apt-get update
  apt-get install -y certbot
fi

# Get the SSL certificate
echo "Obtaining SSL certificate..."
certbot certonly --standalone -d skillgrid.tech -d www.skillgrid.tech

# Check if we got the certificate
if [ -d "/etc/letsencrypt/live/skillgrid.tech" ]; then
  echo "Certificate obtained successfully!"

  # Create directory for certificates
  mkdir -p ./certbot/conf
  mkdir -p ./certbot/www

  # Copy certificates
  cp -L /etc/letsencrypt/live/skillgrid.tech/fullchain.pem ./certbot/conf/
  cp -L /etc/letsencrypt/live/skillgrid.tech/privkey.pem ./certbot/conf/
  cp -L /etc/letsencrypt/live/skillgrid.tech/chain.pem ./certbot/conf/

  # Set up nginx with SSL
  echo "Setting up Nginx with SSL..."
  cp nginx.prod.conf /etc/nginx/conf.d/default.conf
  
  # Reload Nginx
  nginx -s reload

  echo "SSL setup complete!"
else
  echo "Failed to obtain certificate!"
fi 