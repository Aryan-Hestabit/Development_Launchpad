# DAY 1 — Node.js Project Architecture

## 📌 Overview
This day focuses on building a production-ready Node.js backend foundation by applying professional architectural practices.
Instead of directly implementing features, the emphasis is on project structure, controlled application startup, configuration management, and logging.

## Concepts Covered

1. Node.js Internals
- Event-driven, non-blocking I/O model
- Single-threaded execution with asynchronous callbacks
- Importance of predictable startup flow

2. Layered Architecture
- The backend follows a layered design to enforce separation of concerns and scalability.
- Request → Route → Controller → Service → Repository → Database
Each layer has a single responsibility, making the system easier to maintain and extend.

3. Environment Configuration

- Multiple environment files supported:
    .env.local
    .env.dev
    .env.prod
Centralized config loader ensures environment isolation
Sensitive values are never hard-coded

4. Logging
- Centralized logging using Winston
- Logs include timestamps and severity levels
- Startup logs provide visibility into system state

## 📁 Project Structure
```bash
src/
├── config/         # Environment and application configuration
├── loaders/        # Application startup and initialization logic
├── models/         # Database models (placeholders for now)
├── routes/         # Route definitions
├── controllers/    # HTTP request handlers
├── services/       # Business logic layer
├── repositories/   # Data access abstraction
├── middlewares/    # Express middlewares
├── utils/          # Utilities such as logger
├── jobs/           # Background jobs / schedulers
└── logs/           # Application log files
```

This structure ensures clean separation of responsibilities and prepares the application for future scaling.

## ⚙️ Application Startup Flow

The application starts in a well-defined sequence:
- Environment variables are loaded
- Logger is initialized
- Express application is created
- Middlewares are registered
- Database connection is established
- Routes are mounted
- Server begins listening on the configured port
This explicit bootstrapping avoids hidden dependencies and unpredictable behavior.

## Health Check

A basic health route is provided to verify server availability:
```bash
GET /health
```

Response:
OK

## 📦 Deliverables

src/loaders/app.js – Express bootstrapping and startup control
src/loaders/db.js – Database initialization logic
src/utils/logger.js – Centralized logging utility
.env.local - local environment file 
readme.md – Architectural overview and design rationale

## Key Takeaways

- Backend systems should be designed as systems, not scripts
- Explicit startup order improves reliability and debuggability
- Environment isolation is critical for secure deployments
- Logging is a first-class concern in production applications
