.PHONY: dev prod build clean ssl restart logs

# Development environment
dev:
	docker-compose up --build

# Production environment
prod:
	docker-compose -f docker-compose.prod.yml up -d --build

# Build for production without starting
build:
	docker-compose -f docker-compose.prod.yml build

# Clean up containers and volumes
clean:
	docker-compose -f docker-compose.prod.yml down -v

# Initialize SSL
ssl:
	chmod +x init-letsencrypt.sh
	./init-letsencrypt.sh

# Restart containers
restart:
	docker-compose -f docker-compose.prod.yml restart

# View logs
logs:
	docker-compose -f docker-compose.prod.yml logs -f

# Pull latest changes and redeploy
deploy:
	git pull
	docker-compose -f docker-compose.prod.yml up -d --build 