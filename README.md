# Lunar Navigation System

## 🚀 Quickstart: Run via Docker (Recommended)

You don't need Python, Node.js, or any local dependencies installed to run Lunar.OS. You can run the entire pre-built system using Docker.

**1. Create a file named `docker-compose.yml` anywhere on your computer and paste this exact configuration:**

```yaml
services:
  backend:
    image: sajid1108/lunar-backend:latest
    ports:
      - "8000:8000"

  frontend:
    image: sajid1108/lunar-frontend:latest
    ports:
      - "5173:5173"
    depends_on:
      - backend


Start the application:



```bash

docker compose up

```



Open:



\* \*\*Frontend:\*\* http://localhost:5173

\* \*\*API Docs:\*\* http://localhost:8000/docs



\## 🛠️ Tech Stack



\* FastAPI

\* PyTorch

\* U-Net

\* A\* Pathfinding

\* React

\* Vite

\* Docker



\## 📦 Docker Images



\* \*\*Backend:\*\* `sajid1108/lunar-backend`

\* \*\*Frontend:\*\* `sajid1108/lunar-frontend`



