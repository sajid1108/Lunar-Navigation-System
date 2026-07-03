# frontend/Dockerfile
FROM node:20-alpine

WORKDIR /app

# Copy package files and install dependencies
COPY package*.json ./
RUN npm install

# Copy the rest of the frontend files
COPY . .

# Vite default port
EXPOSE 5173

# Run Vite in host mode so it can be accessed from outside the container
CMD ["npm", "run", "dev", "--", "--host"]