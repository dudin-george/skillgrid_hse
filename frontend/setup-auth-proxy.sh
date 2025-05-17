#!/bin/bash

echo "Setting up auth.skillgrid.tech proxy for Ory authentication"
echo "======================================================"
echo ""

# Colors for better readability
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo -e "${GREEN}1. DNS Setup${NC}"
echo "You need to create a CNAME record for auth.skillgrid.tech in your DNS provider:"
echo ""
echo "   Type:  CNAME"
echo "   Name:  auth"
echo "   Value: infallible-shaw-gpsjwuc0lg.projects.oryapis.com"
echo "   TTL:   Auto or 3600"
echo ""
echo "This will make auth.skillgrid.tech point to your Ory project's API domain."
echo ""

echo -e "${GREEN}2. Update Nginx Configuration${NC}"
echo "Let's create a proxy configuration for Nginx:"
echo ""

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
        
        # CORS headers
        add_header 'Access-Control-Allow-Origin' 'https://skillgrid.tech' always;
        add_header 'Access-Control-Allow-Credentials' 'true' always;
        add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS' always;
        add_header 'Access-Control-Allow-Headers' 'DNT,X-CustomHeader,Keep-Alive,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,X-Ory-Project-Id' always;
    }
}
EOF

echo "Created Nginx proxy configuration at nginx.auth-proxy.conf"
echo ""

echo -e "${GREEN}3. Update docker-compose.prod.yml${NC}"
echo "Now let's update the docker-compose file to include this configuration:"

# Update docker-compose.prod.yml
cat > docker-compose.auth-proxy.yml << EOF
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

echo "Created docker-compose.auth-proxy.yml"
echo ""

echo -e "${GREEN}4. Update OryContext.tsx${NC}"
echo "Now we need to modify the Ory context to use the new proxy URL."

# Create a script to update OryContext.tsx
cat > update-ory-url.sh << EOF
#!/bin/bash
# Update the OryContext.tsx to use the auth subdomain
sed -i 's|const ORY_SDK_URL = process.env.REACT_APP_ORY_URL || "https://infallible-shaw-gpsjwuc0lg.projects.oryapis.com";|const ORY_SDK_URL = process.env.REACT_APP_ORY_URL || "https://auth.skillgrid.tech";|g' src/context/OryContext.tsx
echo "Updated OryContext.tsx to use https://auth.skillgrid.tech"
EOF

chmod +x update-ory-url.sh
echo "Created update-ory-url.sh script"
echo ""

echo -e "${GREEN}5. SSL Certificate${NC}"
echo "You need to obtain an SSL certificate for auth.skillgrid.tech"
echo ""
echo "Run the following command to obtain a certificate:"
echo "sudo certbot certonly --standalone -d skillgrid.tech -d www.skillgrid.tech -d auth.skillgrid.tech"
echo ""

echo -e "${GREEN}6. Deployment${NC}"
echo "To deploy with the auth proxy:"
echo ""
echo "1. Set up DNS CNAME record for auth.skillgrid.tech"
echo "2. Obtain SSL certificate with the auth subdomain"
echo "3. Run ./update-ory-url.sh to update the OryContext"
echo "4. Use docker-compose.auth-proxy.yml for deployment:"
echo "   sudo docker-compose -f docker-compose.auth-proxy.yml up -d --build"
echo ""

echo "After completing these steps, your application should authenticate through"
echo "your own domain (auth.skillgrid.tech) instead of the Ory API directly,"
echo "which will resolve the CORS issues."
echo ""
echo "You may need to update your Ory project settings to allow this custom domain." 