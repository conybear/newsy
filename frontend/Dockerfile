# Use Node 18 image
FROM node:18-slim

# Set working directory
WORKDIR /app

# Copy package files
COPY frontend/package.json frontend/yarn.lock ./

# Install dependencies
RUN yarn install --frozen-lockfile

# Copy frontend code
COPY frontend/ .

# Build the React app
RUN yarn build

# Install serve globally
RUN yarn global add serve

# Expose port
EXPOSE 3000

# Start command
CMD ["serve", "-s", "build", "-l", "3000"]