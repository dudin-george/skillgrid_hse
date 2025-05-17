#!/bin/bash

echo "Updating SSL certificates for auth.skillgrid.tech"
echo "================================================"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root (use sudo)"
  exit 1
fi

# Check if certbot is installed
if ! command -v certbot &> /dev/null; then
  echo "Installing certbot..."
  apt-get update
  apt-get install -y certbot
fi

# Find existing certificate
CERT_DIR=""
for dir in "/etc/letsencrypt/live/skillgrid.tech" "/etc/letsencrypt/live/skillgrid.tech-0001" "/etc/letsencrypt/live/skillgrid.tech-0002"; do
  if [ -d "$dir" ]; then
    CERT_DIR="$dir"
    break
  fi
done

if [ -z "$CERT_DIR" ]; then
  echo "No existing certificate found. Creating a new one..."
  certbot certonly --standalone -d skillgrid.tech -d www.skillgrid.tech -d auth.skillgrid.tech
else
  echo "Found certificate directory: $CERT_DIR"
  
  # Check if auth.skillgrid.tech is already included
  if certbot certificates | grep -q "auth.skillgrid.tech"; then
    echo "auth.skillgrid.tech is already included in the certificate."
    
    # Check if renewal is needed
    if certbot certificates | grep -A5 "auth.skillgrid.tech" | grep -q "INVALID"; then
      echo "Certificate is invalid or expired. Renewing..."
      certbot renew --force-renewal --cert-name $(basename "$CERT_DIR")
    else
      echo "Certificate is valid. No action needed."
    fi
  else
    echo "Adding auth.skillgrid.tech to the certificate..."
    certbot certonly --standalone --expand -d skillgrid.tech -d www.skillgrid.tech -d auth.skillgrid.tech
  fi
fi

echo ""
echo "Certificate update complete!"
echo "To check the certificate:"
echo "certbot certificates"
echo ""
echo "Note: You will need to restart your services to use the new certificate."
echo "Run: docker-compose -f docker-compose.prod.yml down && docker-compose -f docker-compose.prod.yml up -d" 