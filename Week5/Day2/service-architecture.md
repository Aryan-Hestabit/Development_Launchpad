# Multi-Container Service Architecture

## Services
- Client: Nginx serving frontend
![client](./Screenshots/ClientSide.png)
- Server: Node.js API
![Server](./Screenshots/ServerSide.png)
- Database: MongoDB


## Networking
- Docker Compose creates a private network
![Docker Compose ps](./Screenshots/ComposePs.png)
- Services communicate using service names
- Server connects to Mongo via `mongo:27017`

## Volumes
- mongo-data volume persists database files
![Volume](./Screenshots/Volume.png)
- Data survives container restarts
![Persistence](./Screenshots/Persistence.png)

## Logs
- Logs available via docker compose logs
![mongo logs](./Screenshots/mongoLogs.png)
![Server Logs](./Screenshots/ServerLogs.png)
- Stdout/stderr used for logging

## Startup
- Entire stack starts with:
```bash
  docker compose up -d
```