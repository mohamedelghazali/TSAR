# TSAR reference: hardened multi-stage build.
FROM node:20.11.1-bookworm-slim AS builder
WORKDIR /build
COPY package.json package-lock.json ./
RUN npm ci --omit=dev
COPY src ./src
RUN npm run build

FROM gcr.io/distroless/nodejs20-debian12:nonroot
LABEL org.opencontainers.image.source="https://github.com/example/tsar-app"
LABEL org.opencontainers.image.licenses="Apache-2.0"
WORKDIR /app
COPY --from=builder /build/node_modules ./node_modules
COPY --from=builder /build/dist ./dist
COPY --from=builder /build/package.json ./
USER 10001:10001
EXPOSE 8443
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD ["/nodejs/bin/node", "-e", "require('http').get('http://127.0.0.1:8080/healthz',r=>process.exit(r.statusCode===200?0:1)).on('error',()=>process.exit(1))"]
ENTRYPOINT ["/nodejs/bin/node", "dist/server.js"]
