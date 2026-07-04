# 🌕 Lunar.OS – Lunar Orbital Reconnaissance & Navigation System

![CI](https://github.com/sajid1108/Lunar-Navigation-System/actions/workflows/docker-publish.yml/badge.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)
![React](https://img.shields.io/badge/React-Vite-61DAFB?logo=react&logoColor=black)

Lunar.OS is an AI-powered lunar terrain navigation system that uses a **U-Net** segmentation model to detect hazardous terrain and the **A*** algorithm to generate safe navigation paths. The project features a **FastAPI** backend and a **React + Vite** frontend, fully containerized with Docker.

## 🔗 Live Demo

- **Live UI:** https://lunar-navigation-system.vercel.app
- **Backend API docs:** https://sajidftw-lunar-backend.hf.space/docs

> **Note:** the hosted demo only has a curated subset of sectors loaded (IDs: 1, 151, 301, 451, 601, 751, 901, 1051, 1201, 1351, 1501, 1651, 1801, 1951, 2101, 2251, 2401, 2551, 2701, 2851). Other sector IDs will return a 404 on the live demo. Run locally via Docker (below) for access to the full dataset.

## 🚀 Quickstart: Run via Docker (Recommended)

You don't need Python, Node.js, or any local dependencies installed to run Lunar.OS. You can run the entire pre-built system using Docker.

**1. Create a file named `docker-compose.yml` anywhere on your computer and paste this configuration:**

```yaml
services:
  backend:
    image: sajid1108/lunar-backend:latest
    ports:
      - "7860:7860"

  frontend:
    image: sajid1108/lunar-frontend:latest
    ports:
      - "5173:5173"
    depends_on:
      - backend
```

**2. Open a terminal in that same folder and start the system:**

```bash
docker compose up
```

**3. Access the application:**

- **Frontend UI:** http://localhost:5173
- **Backend API Docs:** http://localhost:7860/docs

## 🛠️ Tech Stack

- **Backend:** FastAPI, PyTorch, U-Net, A* Pathfinding
- **Frontend:** React, Vite
- **Deployment:** Docker, Docker Compose

## 📦 Docker Images

- **Backend:** `sajid1108/lunar-backend`
- **Frontend:** `sajid1108/lunar-frontend`