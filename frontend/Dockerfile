# syntax=docker/dockerfile:1

FROM node:20-slim AS base

WORKDIR /app

COPY entrypoint.sh ./
RUN chmod +x ./entrypoint.sh

COPY package*.json ./
RUN npm ci

FROM base AS dev

ENV DOCKER_ENV=dev

EXPOSE 3000

ENTRYPOINT ["./entrypoint.sh"]

FROM base AS build

COPY . .
RUN npm run build

FROM mcr.microsoft.com/playwright:v1.60.0-jammy AS test

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN chmod +x ./entrypoint.test.sh

ENTRYPOINT ["./entrypoint.test.sh"]

FROM node:20-slim AS prod

WORKDIR /app

ENV NODE_ENV=production
ENV DOCKER_ENV=prod

COPY --from=build /app/build ./build
COPY --from=build /app/package*.json ./
COPY entrypoint.sh ./
RUN chmod +x ./entrypoint.sh
RUN npm ci --omit=dev

EXPOSE 3000

ENTRYPOINT ["./entrypoint.sh"]
