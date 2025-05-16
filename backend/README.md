# SkillGrid Backend

A robust FastAPI backend for SkillGrid - a platform that connects companies with candidates based on skills and job requirements. The system manages skill profiles, job postings, and skill-based matching.

## Overview

SkillGrid allows:
- Companies to create profiles and job postings with specific skill requirements
- Management of skill domains and specific skills with proficiency levels
- Creation of skill presets for standardized job requirements
- Job postings with skill requirements and candidate tracking

## Quick Start

### Prerequisites

- Python 3.12+
- Docker and Docker Compose (for containerized PostgreSQL)

### Setup and Deployment

1. **Clone the repository**

2. **Install dependencies**
   ```
   cd skillgrid_hse/backend
   poetry install
   ```

3. **Start the PostgreSQL database**
   ```
   docker-compose up -d
   ```

4. **Initialize the database**
   ```
   cd backend
   python -m app.db.init_db
   ```

5. **Run migrations**
   ```
   alembic upgrade head
   ```

6. **Start the application**
   ```
   cd backend
   python main.py
   ```

7. **Access the API**
   - API is available at: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## Project Structure

```
backend/
├── app/                    # Application package
│   ├── api/                # API endpoints
│   │   └── routes/         # API route definitions
│   ├── core/               # Core application components
│   ├── db/                 # Database components
│   ├── models/             # Database models
│   └── schemas/            # Pydantic models for data validation
├── migrations/             # Alembic migrations
└── main.py                 # Application entry point
```

## Database Schema

The application includes the following data models:

- **Company**: Organization profiles with name, description, and logo
- **JobPosting**: Job listings with status and candidate tracking
- **Domain**: Skill categories (e.g., "Programming", "Design")
- **Skill**: Individual skills with proficiency levels and requirements
- **SkillPreset**: Reusable skill requirement templates
- **Relationship tables**: JobSkill, CompanyJobPosting, SkillPresetSkill

## Development

### Creating a new migration

After changing models, create a migration:

```
alembic revision --autogenerate -m "Description of changes"
```

### Applying migrations

```
alembic upgrade head
```

### Running in development mode

```
cd backend
uvicorn app.main:app --reload
```

## Docker Deployment

The application is fully containerized and can be easily deployed using Docker.

### Build and Run with Docker Compose

```bash
# Build and start the containers
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop the containers
docker-compose down
```

### Run in Production

For production deployment, consider these modifications:

1. Set appropriate environment variables:
   - Set strong passwords for database
   - Configure specific hosts and ports

2. Use a proper Docker Compose production file:
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

3. Consider using a reverse proxy like Nginx for SSL termination

### Manual Docker Build

If you prefer to build and run the containers manually:

```bash
# Build the API image
docker build -t skillgrid-api .

# Run the API container
docker run -d -p 8000:8000 --name skillgrid-api \
  -e DATABASE_URL=postgresql://postgres:postgres@postgres:5432/skillgrid \
  skillgrid-api
```

## Deploying to a Server

### Prerequisites

- Ubuntu server (20.04 LTS or later)
- Docker and Docker Compose installed
- Domain name pointing to your server (for production)

### Basic Server Setup

1. SSH into your server:
   ```bash
   ssh user@your-server-ip
   ```

2. Install Docker and Docker Compose:
   ```bash
   # Update package repository
   sudo apt update
   
   # Install required packages
   sudo apt install -y apt-transport-https ca-certificates curl software-properties-common
   
   # Add Docker's official GPG key
   curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
   
   # Add Docker repository
   sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
   
   # Install Docker
   sudo apt update
   sudo apt install -y docker-ce docker-ce-cli containerd.io
   
   # Install Docker Compose
   sudo curl -L "https://github.com/docker/compose/releases/download/v2.24.1/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   sudo chmod +x /usr/local/bin/docker-compose
   
   # Add your user to docker group (optional, for running docker without sudo)
   sudo usermod -aG docker $USER
   ```

3. Clone the repository:
   ```bash
   git clone https://your-repo-url.git
   cd backend
   ```

### Development Deployment

For a simple deployment without HTTPS:

```bash
# Start the application
docker-compose up -d

# Check logs
docker-compose logs -f
```

### Production Deployment

For a production environment with HTTPS:

1. Set up SSL certificates:
   ```bash
   # Create directory for SSL certificates
   mkdir -p nginx/ssl
   
   # For testing, you can generate self-signed certificates:
   openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
     -keyout nginx/ssl/skillgrid.key \
     -out nginx/ssl/skillgrid.crt
   
   # For production, use Let's Encrypt:
   # sudo certbot certonly --standalone -d api.yourdomain.com
   # cp /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem nginx/ssl/skillgrid.crt
   # cp /etc/letsencrypt/live/api.yourdomain.com/privkey.pem nginx/ssl/skillgrid.key
   ```

2. Update domain name in Nginx configuration:
   ```bash
   # Replace example domain with your actual domain
   sed -i 's/api.skillgrid.example.com/api.yourdomain.com/g' nginx/conf/default.conf
   ```

3. Start the production environment:
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

4. Verify the deployment:
   ```bash
   curl https://api.yourdomain.com/health
   ```

### Updating the Application

To update the application:

```bash
# Pull the latest changes
git pull

# Rebuild and restart containers
docker-compose -f docker-compose.prod.yml up -d --build
```
