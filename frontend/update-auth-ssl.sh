#!/bin/bash

echo "Updating SSL certificates for auth.skillgrid.tech"
echo "================================================"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root (use sudo)"
  exit 1
fi

echo "IMPORTANT: Certificate validation for auth.skillgrid.tech failed"
echo "==============================================================="
echo ""
echo "The validation is failing because auth.skillgrid.tech is currently pointing"
echo "to Ory's servers via CNAME, not to your server. Let's Encrypt needs to"
echo "place a validation file on YOUR server during certificate issuance."
echo ""
echo "To issue a certificate that includes auth.skillgrid.tech, you need to:"
echo ""
echo "1. Temporarily change the DNS record for auth.skillgrid.tech:"
echo "   - Go to your DNS provider (where skillgrid.tech is registered)"
echo "   - Change the CNAME record for auth.skillgrid.tech to point to skillgrid.tech"
echo "     or change it to an A record pointing to your server's IP address"
echo ""
echo "2. Wait for DNS propagation (may take 5-30 minutes)"
echo ""
echo "3. Run the certificate issuance command:"
echo "   sudo certbot certonly --standalone -d skillgrid.tech -d www.skillgrid.tech -d auth.skillgrid.tech"
echo ""
echo "4. After successful certificate issuance, change the DNS record back:"
echo "   - Change auth.skillgrid.tech back to a CNAME pointing to infallible-shaw-gpsjwuc0lg.projects.oryapis.com"
echo ""
echo "5. Restart your services:"
echo "   docker-compose -f docker-compose.prod.yml down && docker-compose -f docker-compose.prod.yml up -d"
echo ""
echo "Would you like to attempt certificate issuance now? (y/n)"
read -r response

if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
  # Check if certbot is installed
  if ! command -v certbot &> /dev/null; then
    echo "Installing certbot..."
    apt-get update
    apt-get install -y certbot
  fi
  
  echo "Attempting to issue certificate..."
  echo "NOTE: This will only succeed if you've already updated the DNS records as described above."
  certbot certonly --standalone -d skillgrid.tech -d www.skillgrid.tech -d auth.skillgrid.tech
  
  echo ""
  echo "If the certificate was successfully issued, please:"
  echo "1. Change the auth.skillgrid.tech DNS record back to Ory's CNAME"
  echo "2. Restart your services: docker-compose -f docker-compose.prod.yml down && docker-compose -f docker-compose.prod.yml up -d"
else
  echo "Exiting without attempting certificate issuance."
fi 