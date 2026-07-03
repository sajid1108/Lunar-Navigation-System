# backend/Dockerfile
FROM nvcr.io/nvidia/pytorch:24.01-py3

WORKDIR /app

# Install GL libraries required by OpenCV (cv2)
RUN apt-get update && apt-get install -y libgl1 libglib2.0-0 && rm -rf /var/lib/apt/lists/*

# Copy and install Python requirements
COPY requirements.txt .

# Ensure uvicorn, fastapi, and scipy are included in your requirements.txt!
RUN pip uninstall -y opencv-python opencv-python-headless && pip install --no-cache-dir -r requirements.txt

# Copy the rest of the backend files (including main.py, model weights, and processed_data)
COPY . .

# Expose the port your FastAPI backend runs on
EXPOSE 8000

# Start the FastAPI app using Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]