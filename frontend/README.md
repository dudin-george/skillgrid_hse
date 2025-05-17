# SkillGrid Frontend

SkillGrid is an AI-powered platform for skill assessment and job matching for IT specialists.

## Project Structure

- `public/` - Static assets including icons and HTML template
- `src/` - React application source code
  - `components/` - Reusable UI components
  - `pages/` - Page components
  - `App.tsx` - Main application component
  - `index.tsx` - Application entry point

## Development

```
npm install
npm start
```

## Deployment

```
# Build Docker image
docker build -t skillgrid-frontend .

# Run Docker container
docker run -d -p 80:80 skillgrid-frontend
```

## Tech Stack

- React
- TypeScript
- Tailwind CSS
- Docker

## API Integration

The backend API is available at www.api.skillgrid.tech/docs for reference.

## Authentication

The project uses Ory for authentication and authorization.

## License

All rights reserved.
