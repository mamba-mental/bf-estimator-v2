# BF Estimator React

A modern, web-based body fat estimation and weight loss prediction tool with AI-powered suggestions and comprehensive progress tracking.

## Overview

BF Estimator React is an enhanced version of the original terminal-based Body Fat Estimator application. It maintains the core calculation functionality while adding:

- Modern React-based UI with Vite and TypeScript
- Persistent data storage with Supabase
- AI-powered suggestions for optimizing progress
- Comprehensive dashboard for tracking progress and visualizing trends
- Docker containerization for easy deployment

## Project Structure

```
bf-estimator-react/
├── public/              # Static assets
├── src/                 # Source code
│   ├── components/      # React components
│   ├── context/         # React context providers
│   ├── hooks/           # Custom React hooks
│   ├── lib/             # Utility functions and libraries
│   ├── pages/           # Page components
│   ├── services/        # API and service integrations
│   ├── styles/          # Global styles
│   ├── types/           # TypeScript type definitions
│   ├── App.tsx          # Main application component
│   └── main.tsx         # Application entry point
├── scripts/             # Task Master AI scripts
├── tasks/               # Task Master AI task definitions
├── .env.example         # Example environment variables
├── .gitignore           # Git ignore file
├── docker-compose.yml   # Docker Compose configuration
├── Dockerfile           # Docker configuration
├── package.json         # NPM package configuration
├── tsconfig.json        # TypeScript configuration
└── vite.config.ts       # Vite configuration
```

## Prerequisites

- Node.js 18+
- Docker and Docker Compose (for containerized development)
- Supabase account (for database and authentication)
- AI service API key (for AI suggestions)

## Getting Started

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/mamba-mental/bf-estimator-v2.git
   cd bf-estimator-v2/122924_bf-estimator-terminal/bf-estimator-react
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Copy the example environment file and update with your credentials:
   ```bash
   cp .env.example .env
   ```

4. Update the `.env` file with your Supabase and AI service credentials.

### Development

#### Local Development

Start the development server:
```bash
npm run dev
```

The application will be available at http://localhost:5173.

#### Docker Development

Build and start the Docker containers:
```bash
docker-compose up -d
```

The application will be available at http://localhost:5173.

### Building for Production

Build the application:
```bash
npm run build
```

The built application will be in the `dist` directory.

## Features

- **User Authentication**: Secure user authentication and profile management
- **Goal Setting**: Set weight and body fat percentage goals with target dates
- **Progress Tracking**: Log weight, body fat, and other metrics over time
- **Calculation Engine**: Advanced algorithms for projecting weight loss and body composition changes
- **AI Suggestions**: Receive personalized advice and calorie adjustments based on progress
- **Interactive Dashboard**: Visualize progress, trends, and milestones
- **Reports**: Generate comprehensive reports on progress and projections
- **Mobile Optimization**: Responsive design for use on any device

## Development Roadmap

See the [tasks directory](./tasks) for detailed development tasks and roadmap.

## Contributing

1. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and commit:
   ```bash
   git commit -m "Add your feature"
   ```

3. Push to your branch:
   ```bash
   git push origin feature/your-feature-name
   ```

4. Create a pull request.

## License

© 2025 Mamba Matrix Solutions LLC. All rights reserved.

**Author**: Tiran Ronelle Winston  
**Contact**: mambamental3mil@gmail.com  
**License**: Apache License 2.0