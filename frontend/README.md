# SkillGrid Frontend

SkillGrid is an AI-powered platform for skill assessment and job matching for IT specialists.

## Project Structure

- `public/` - Static assets including icons and HTML template
- `src/` - React application source code
  - `components/` - Reusable UI components
  - `pages/` - Page components
  - `context/` - React context providers, including Ory authentication
  - `App.tsx` - Main application component
  - `index.tsx` - Application entry point

## Development

```
npm install
npm start
```

## Environment Variables

Create a `.env.local` file with the following variables:

```
REACT_APP_API_URL=https://api.skillgrid.tech
REACT_APP_ORY_URL=https://infallible-shaw-gpsjwuc0lg.projects.oryapis.com
```

## Ory Integration

This project uses Ory for authentication. The Ory configuration is:

- Ory SDK URL: `https://infallible-shaw-gpsjwuc0lg.projects.oryapis.com`
- Ory Project ID: `cd3eac85-ed95-41dd-9969-9012ab8dea73`

### Configuring Allowed Redirect URLs

If you want to use the `return_to` parameter for redirects after authentication, you must configure allowed redirect URLs in Ory:

1. Go to the [Ory Cloud Console](https://console.ory.sh/)
2. Select the SkillGrid project
3. Navigate to "Authentication" → "Flows & Settings"
4. Find "Allowed Return to URLs" section 
5. Add your domains:
   ```
   - https://skillgrid.tech
   - https://skillgrid.tech/dashboard
   - http://localhost:3000
   - http://localhost:3000/dashboard
   - http://localhost:8080
   - http://localhost:8080/dashboard
   ```

### CORS Configuration

For proper CORS configuration:

1. Go to the [Ory Cloud Console](https://console.ory.sh/)
2. Select the SkillGrid project
3. Navigate to "Configuration" → "CORS"
4. Add your domains to the allowed origins:
   ```yaml
   allowed_origins:
     - https://skillgrid.tech
     - http://localhost:3000  # For local development
     - http://localhost:8080  # For Docker development
   ```

## Deployment

### Local Development

```
# Build Docker image
docker build -t skillgrid-frontend .

# Run Docker container with Ory configuration
docker run -d -p 80:80 \
  -e REACT_APP_ORY_URL=https://infallible-shaw-gpsjwuc0lg.projects.oryapis.com \
  skillgrid-frontend
```

### Production Deployment

To deploy to skillgrid.tech:

1. Clone the repository on your server:
   ```bash
   git clone https://github.com/youruser/skillgrid_hse.git
   cd skillgrid_hse/frontend
   ```

2. Start with a basic HTTP deployment first:
   ```bash
   # Make the scripts executable
   chmod +x check-connection.sh setup-ssl.sh

   # Deploy the HTTP version first
   docker-compose -f docker-compose.prod.yml up -d
   ```

3. Check connectivity to ensure your domain is accessible:
   ```bash
   ./check-connection.sh
   ```

4. Once you've confirmed the site is accessible via HTTP, you can set up SSL:
   ```bash
   # Make sure port 80 is open for Let's Encrypt verification
   # If you're using a firewall, run: ufw allow 80/tcp

   # Stop any running web server on port 80
   docker-compose -f docker-compose.prod.yml down

   # Get SSL certificate
   ./setup-ssl.sh
   
   # After getting the certificate, you can deploy with SSL
   # Edit docker-compose.prod.yml to use nginx.prod.conf
   # Then run:
   docker-compose -f docker-compose.prod.yml up -d
   ```

The application will be available at https://skillgrid.tech after SSL is set up.

### Troubleshooting SSL

If you encounter SSL setup issues:

1. **Check DNS Configuration**: Make sure your domain's DNS A record points to your server's IP address
2. **Check Firewall Settings**: Ensure port 80 is open for Let's Encrypt verification
3. **Check Server Connectivity**: Use `./check-connection.sh` to verify your domain is accessible

### SSL Renewal

SSL certificates are automatically renewed by the certbot container. However, if you need to renew them manually:

```bash
docker-compose -f docker-compose.prod.yml run --rm certbot renew
```

## Tech Stack

- React
- TypeScript
- Tailwind CSS
- Docker
- Ory (Authentication)

## API Integration

The backend API is available at www.api.skillgrid.tech/docs for reference.

## License

All rights reserved.
