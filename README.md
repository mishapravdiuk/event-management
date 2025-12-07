# Event‑Management Server 

**Event‑Management** - a backend API server for creating, managing and registering for events (with users, JWT auth, Redis‑based token cache, etc).

## Basic info

This service provides a REST API (via Django + Django Ninja) for:
- User authentication and registration via email / phone + JWT tokens  
- CRUD operations for events (create, update, list, view)  
- Event registration for users  
- Token-based session caching via Redis  
- JSON‑serializable outputs (via Pydantic) for API responses  
This backend is meant to serve as a foundation for an event‑management / meetup / scheduling system.

## Features

- Custom user model (email + phone + roles)  
- JWT authentication with access + refresh tokens  
- Redis cache for token/session management  
- Event creation / update / listing / filtering / slug generation  
- Event registration / user‑to‑event relations  
- Pydantic‑based API schemas for clean, type‑safe JSON responses  
- Docker / Docker Compose setup for easy development & deployment 

## Tech Stack & Dependencies

- Python 3.12+  
- Django 6.0  
- Django Ninja  
- Pydantic  
- Redis (for token cache)  
- PostgreSQL 
- Docker / docker-compose (for local dev / deployment)  
- Poetry (for dependency & environment management)  

## Getting Started / Installation

- Clone repo from 
```bash
git clone https://github.com/mishapravdiuk/event-management.git
cd event_management_server
```
- Add file.env. Set custom values for variables used in example file
```bash
cp configs/example_file.env configs/file.env
nano configs/file.env
```

- Build docker
```bash
cd ..
docker compose -f docker-compose.dev.yaml build
```
- Start the services
```bash
docker compose -f docker-compose.dev.yaml up -d