# Build stage
FROM node:18-alpine as build

WORKDIR /app

# Define ARGs for environment variables
ARG REACT_APP_ORY_URL
ARG REACT_APP_API_URL

# Set environment variables
ENV REACT_APP_ORY_URL=${REACT_APP_ORY_URL}
ENV REACT_APP_API_URL=${REACT_APP_API_URL}

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built assets from the build stage
COPY --from=build /app/build /usr/share/nginx/html

# We don't copy nginx.conf here because we'll mount it via docker-compose
# for different environments (dev/prod)

# Expose ports
EXPOSE 80
EXPOSE 443

# Start nginx
CMD ["nginx", "-g", "daemon off;"] 