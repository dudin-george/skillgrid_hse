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

```bash
# Build and run with Docker Compose
docker-compose up --build

# Or using Docker directly
docker build -t skillgrid-frontend .
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

2. Use the deployment script for a complete setup:
   ```bash
   # Make the script executable
   chmod +x deploy.sh
   
   # Run the deployment script (handles SSL, port setup, and deployment)
   sudo ./deploy.sh
   ```

The script will:
- Check and open necessary ports (80, 443)
- Set up SSL certificates with Let's Encrypt if needed
- Copy SSL certificates to the proper location
- Configure and start the Docker containers

The application will be available at https://skillgrid.tech after deployment.

#### Advanced Usage

The deployment script supports individual steps:

```bash
# Check and configure ports only
sudo ./deploy.sh ports

# Set up SSL certificates only
sudo ./deploy.sh ssl  

# Deploy the application only (assuming certificates are set up)
sudo ./deploy.sh app
```

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

The backend API is available at www.api.skillgrid.tech/docs for reference.

## License

All rights reserved.
