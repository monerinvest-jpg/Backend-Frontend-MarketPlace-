# frontend/Dockerfile — Multi-stage с nginx
FROM node:20-alpine AS base
WORKDIR /app

# ─────────────────────────────────────────────────
FROM base AS deps
COPY package*.json ./
RUN npm ci && npm cache clean --force

# ─────────────────────────────────────────────────
FROM deps AS development
COPY . .
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nodeuser && \
    chown -R nodeuser:nodejs /app
USER nodeuser
EXPOSE 3000
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

# ─────────────────────────────────────────────────
FROM deps AS builder
COPY . .
# VITE_API_URL передаётся как build arg — не как секрет!
ARG VITE_API_URL
ENV VITE_API_URL=${VITE_API_URL}
RUN npm run build

# ─────────────────────────────────────────────────
# Production: nginx для раздачи статики
FROM nginx:1.27-alpine AS production

# ✅ Безопасная конфигурация nginx
COPY nginx/nginx.conf /etc/nginx/nginx.conf
COPY --from=builder /app/dist /usr/share/nginx/html

# ✅ Non-root nginx
RUN chown -R nginx:nginx /usr/share/nginx/html && \
    chmod -R 755 /usr/share/nginx/html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]