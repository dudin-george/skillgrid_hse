# SkillGrid Backend

A FastAPI backend for SkillGrid - a platform that connects companies with candidates based on skills and job requirements.

## One-Command Production Deployment

Deploy the full application stack with HTTPS support in a single command:

### For Development (with self-signed certificates)

```bash
# Clone the repository
git clone https://github.com/your-username/skillgrid_hse.git
cd skillgrid_hse/backend

# Run the deployment script and select option 2 for development
./deploy.sh
```

### For Production (with Let's Encrypt certificates)

```bash
# Clone the repository
git clone https://github.com/your-username/skillgrid_hse.git
cd skillgrid_hse/backend

# Run the deployment script (defaults to skillgrid.tech)
./deploy.sh
# Or run with option 1 when prompted
```

That's it! The script will:
- Configure Nginx with proper settings
- Set up SSL certificates (self-signed for dev, Let's Encrypt for production)
- Create all required configuration files
- Build and start all Docker containers

The application will be available at:
- Development: https://localhost
- Production: https://skillgrid.tech

## Managing the Application

The deployment script provides helpful commands at the end, but here's a quick reference:

```bash
# View container status
docker-compose -f docker-compose.prod.yml ps

# View application logs
docker-compose -f docker-compose.prod.yml logs -f api

# Stop all containers
docker-compose -f docker-compose.prod.yml down

# Update to the latest version
git pull
docker-compose -f docker-compose.prod.yml up -d --build
```

## Troubleshooting

If you encounter issues:

1. **Check container logs**:
   ```bash
   docker-compose -f docker-compose.prod.yml logs api
   ```

2. **Restart the deployment**:
   ```bash
   ./deploy.sh
   ```

3. **Check that ports 80 and 443 are available** on your server

For manual configuration, examine the `deploy.sh` script which contains all the steps performed during automatic deployment.
