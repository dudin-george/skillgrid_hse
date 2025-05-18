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
REACT_APP_API_URL=https://skillgrid.tech
REACT_APP_ORY_URL=https://auth.skillgrid.tech
```

## Ory Integration

This project uses Ory for authentication. The Ory configuration is:

- Ory SDK URL: `https://auth.skillgrid.tech`
- Ory Project ID: `cd3eac85-ed95-41dd-9969-9012ab8dea73`

### Authentication Proxy Setup

To avoid CORS issues, we use an authentication proxy with our own subdomain:

1. Create a CNAME record for `auth.skillgrid.tech` pointing to `infallible-shaw-gpsjwuc0lg.projects.oryapis.com`
2. Make sure the CNAME record is properly configured in your DNS settings

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

> **IMPORTANT**: If you deploy to a new domain or see CORS errors like 
> `Failed to load resource: Origin is not allowed by Access-Control-Allow-Origin`, 
> you must update your Ory CORS settings to include your domain.
>
> You can use the helper script for guidance:
> ```bash
> ./update-ory-cors.sh
> ```

## Deployment

### Local Development

```bash
# Build and run with Docker Compose
docker-compose up --build

# Or using Docker directly
docker build -t skillgrid-frontend .
docker run -d -p 80:80 \
  -e REACT_APP_ORY_URL=https://auth.skillgrid.tech \
  skillgrid-frontend
```

### Production Deployment

The deployment script is designed to work on a fresh server with minimal setup. It can automatically:

- Install Git if needed (when using repository URL)
- Install Docker and Docker Compose if needed
- Set up SSL certificates with Let's Encrypt
- Configure ports and firewall
- Deploy the application

#### Quick Deployment on a New Server

To deploy on a completely new server:

```bash
# Option 1: Download and run the deployment script directly
curl -O https://raw.githubusercontent.com/yourusername/skillgrid_hse/main/frontend/deploy.sh
chmod +x deploy.sh
sudo ./deploy.sh https://github.com/yourusername/skillgrid_hse.git
```

```bash
# Option 2: Clone the repository first, then run the script
git clone https://github.com/yourusername/skillgrid_hse.git
cd skillgrid_hse/frontend
chmod +x deploy.sh
sudo ./deploy.sh
```

#### Deployment Options

```bash
# View all deployment options
sudo ./deploy.sh help

# Install only Docker and Docker Compose
sudo ./deploy.sh docker

# Check and configure ports only
sudo ./deploy.sh ports

# Set up SSL certificates only
sudo ./deploy.sh ssl  

# Deploy the application only (assumes dependencies are installed)
sudo ./deploy.sh app
```

The application will be available at https://skillgrid.tech after deployment.

### SSL Certificate Renewal

SSL certificates from Let's Encrypt expire after 90 days. Set up automatic renewal with a cron job:

```bash
# Add to crontab
echo "0 0,12 * * * root certbot renew --quiet && cd /home/skillgrid_hse/frontend && ./deploy.sh app" | sudo tee -a /etc/crontab
```

This will check twice daily if the certificate needs renewal and redeploy the application if it was renewed.

## Tech Stack

- React
- TypeScript
- Tailwind CSS
- Docker
- Ory (Authentication)

## API Integration

The backend API is available at skillgrid.tech/api for reference.

## License

All rights reserved.
