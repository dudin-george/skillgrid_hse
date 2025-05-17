.PHONY: dev prod build clean ssl restart logs deploy

# Development environment
dev:
	docker-compose up --build

# Production environment without SSL
prod:
	docker-compose -f docker-compose.prod.yml up -d --build

# Build for production without starting
build:
	docker-compose -f docker-compose.prod.yml build

# Clean up containers and volumes
clean:
	docker-compose -f docker-compose.prod.yml down -v

# Deploy with SSL (make sure to run certbot first)
ssl:
	chmod +x deploy-ssl.sh
	sudo ./deploy-ssl.sh

# Restart containers
restart:
	docker-compose -f docker-compose.prod.yml restart

# View logs
logs:
	docker-compose -f docker-compose.prod.yml logs -f

# Pull latest changes and redeploy with SSL
deploy:
	git pull
	make ssl 