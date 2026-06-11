# backend/Dockerfile — Multi-stage безопасная сборка
# ✅ Non-root пользователь, минимальный образ

FROM node:20-alpine AS base
# ✅ Устанавливаем только системные зависимости
RUN apk add --no-cache libc6-compat curl
WORKDIR /app

# ─────────────────────────────────────────────────
FROM base AS deps
COPY package*.json ./
# ✅ npm ci — детерминированная установка по lockfile
RUN npm ci --only=production && npm cache clean --force

# ─────────────────────────────────────────────────
FROM base AS dev-deps
COPY package*.json ./
RUN npm ci && npm cache clean --force

# ─────────────────────────────────────────────────
FROM dev-deps AS development
COPY . .
# ✅ Создаём non-root пользователя
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nodeuser && \
    chown -R nodeuser:nodejs /app
USER nodeuser
EXPOSE 4000
CMD ["npm", "run", "dev"]

# ─────────────────────────────────────────────────
FROM base AS builder
COPY --from=dev-deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

# ─────────────────────────────────────────────────
FROM base AS production
ENV NODE_ENV=production

# ✅ Non-root user
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nodeuser

# Копируем только production dependencies
COPY --from=deps /app/node_modules ./node_modules
COPY --from=builder --chown=nodeuser:nodejs /app/dist ./dist
COPY --from=builder --chown=nodeuser:nodejs /app/package.json .

USER nodeuser

# ✅ Никаких секретов в образе! Всё через ENV при запуске.
# ✅ EXPOSE только один порт API
EXPOSE 4000

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD curl -f http://localhost:4000/api/v1/health || exit 1

CMD ["node", "dist/app.js"]