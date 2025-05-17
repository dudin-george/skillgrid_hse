.PHONY: dev prod build clean ssl deploy logs

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

# Set up SSL certificates
ssl:
	sudo ./deploy.sh ssl

# Deploy with SSL
deploy:
	sudo ./deploy.sh

# View logs
logs:
	docker-compose -f docker-compose.prod.yml logs -f

# Only deploy application (assumes SSL is set up)
app:
	sudo ./deploy.sh app 