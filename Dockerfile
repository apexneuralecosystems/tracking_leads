# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

# Build-time API base URL (no trailing slash). Override with --build-arg VITE_API_BASE_URL=...
ARG VITE_API_BASE_URL=https://api.meetapexneural.com
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}

COPY package.json package-lock.json* ./
RUN npm ci

COPY . .
RUN npm run build

# Production stage: serve static files with nginx
FROM nginx:alpine

# Remove default config and use our SPA-friendly config
RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d/default.conf

COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 8046

CMD ["nginx", "-g", "daemon off;"]
