\# 🌕 Lunar.OS – Lunar Orbital Reconnaissance \& Navigation System



Lunar.OS is an AI-powered lunar terrain navigation system that uses a \*\*U-Net\*\* segmentation model to detect hazardous terrain and the \*\*A\*\*\* algorithm to generate safe navigation paths. The project features a \*\*FastAPI\*\* backend and a \*\*React + Vite\*\* frontend, fully containerized with Docker.



\## 🚀 Run with Docker



Create a `docker-compose.yml` file:



```yaml

services:

&#x20; backend:

&#x20;   image: sajid1108/lunar-backend:latest

&#x20;   ports:

&#x20;     - "8000:8000"



&#x20; frontend:

&#x20;   image: sajid1108/lunar-frontend:latest

&#x20;   ports:

&#x20;     - "5173:5173"

&#x20;   depends\_on:

&#x20;     - backend

```



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



