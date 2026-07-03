# =========================================================
# STAGE 1: The Builder (Heavy lifting)
# =========================================================
FROM python:3.10-slim AS builder

WORKDIR /app

# Install system dependencies needed to build packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Install dependencies into a specific folder to easily move them later
# We use the CPU version of PyTorch to drastically cut down size
RUN pip install --no-cache-dir --user torch torchvision --index-url https://download.pytorch.org/whl/cpu \
    && pip install --no-cache-dir --user -r requirements.txt

# =========================================================
# STAGE 2: The Final Runtime (Lean and clean)
# =========================================================
FROM python:3.10-slim AS runtime

WORKDIR /app

# Install ONLY the runtime system libraries OpenCV actually needs to execute
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy ONLY the installed Python packages from Stage 1, leaving the build junk behind
COPY --from=builder /root/.local /root/.local
COPY --from=builder /app /app

# Ensure Python can find the copied packages
ENV PATH=/root/.local/bin:$PATH

# Copy your actual application files and weights
COPY . .

EXPOSE 8000

# Start the FastAPI app using Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]