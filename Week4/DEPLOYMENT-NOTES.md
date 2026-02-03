# Deployment Notes 

## Overview 
This document describes the deployment setup, runtime requirements, and operational considerations for the backend application. The system is configured to be production-ready with process management, background job handling, structured logging, and environment-based configuration. 

## Runtime Requirements 
- Node.js (v18+ recommended) 
- MongoDB (running instance) 
- Redis (required for BullMQ job queues) 
- PM2 (process manager) 

## Environment Configuration 
The application relies on environment-based configuration to isolate runtime contexts. 
### Environment Files 
- .env.local – Local development 
- .env.production – Production runtime 
- prod/.env.example – Environment variable reference (non-sensitive) 

### Required Environment Variables 
```bash
PORT=3000 MONGO_URI=mongodb://localhost:27017/architecture_db REDIS_HOST=127.0.0.1 REDIS_PORT=6379 NODE_ENV=production 
```
Sensitive values must never be committed to version control. 

## Process Management (PM2) 
PM2 is used to manage the application lifecycle in production.

### Features Enabled 
- Automatic restarts on failure 
- Cluster mode (multi-core utilization) 
- Centralized log management 
- Zero-downtime restarts 

### Start Application 
```bash
pm2 start prod/ecosystem.config.js 
```

### Check Status 
```bash 
pm2 status 
```

### View Logs 
```bash
pm2 logs backend 
```

## Background Job Processing 
- Job queue implemented using BullMQ 
- Redis acts as the queue backend 
- Jobs execute asynchronously outside the request lifecycle 
- Automatic retries with exponential backoff are enabled

Example use cases: 
- Email notifications
- Background report generation 

## Logging & Observability 
- Logs are written using Winston 
- Request-level tracing via X-Request-ID 
- Logs are grouped by request ID for easier debugging 
- Output is written to both console and file (src/logs/app.log) 

## API Documentation 
- APIs are documented using a Postman Collection 
- Collection includes:
  - Users endpoints 
  - Products endpoints 
  - Query engine examples 
  - Soft delete behavior
- Environment variables are used for base URL abstraction 

Export format: 
- Postman Collection v2.1 (JSON) 

## Production Readiness Summary 
The application is production-ready with:
- Background job processing 
- Structured and correlated logging 
- Secure environment isolation 
- Process management and clustering Documented APIs Notes PM2 must be restarted after environment changes Redis is mandatory when job queues are enabled Logs should be monitored regularly in production