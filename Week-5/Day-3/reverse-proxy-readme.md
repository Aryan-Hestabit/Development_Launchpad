# NGINX Reverse Proxy with Load Balancing

## Architecture
- NGINX acts as reverse proxy
- Two backend Node.js containers
![Compose Ps](./Screenshots/ComposePs.png)
- Docker Compose provides networking
![Docker Build](./Screenshots/DockerComposeBuild.png)

## Routing
- /api → backend_service:3000
- Clients never access backend directly
![logs Backend](./Screenshots/logsBackend.png)

## Load Balancing
- Round-robin strategy
- Each request goes to a different container
![reuest mapping](./Screenshots/Curl.png)

## Networking
- Backend exposed only internally
- NGINX is the public entry point
![Logs nginx](./Screenshots/logsNginx.png)

## Startup
```bash
docker compose up -d
```