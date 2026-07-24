# Base
FROM node:20-alpine@sha256:fb4cd12c85ee03686f6af5362a0b0d56d50c58a04632e6c0fb8363f609372293 AS base

WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

# Development
FROM base as dev

USER node

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host"]

# Builder
FROM base AS builder

COPY . .
RUN npm run build

# Production
FROM nginxinc/nginx-unprivileged:alpine AS prod

COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 8080
CMD ["nginx", "-g", "daemon off;"]
