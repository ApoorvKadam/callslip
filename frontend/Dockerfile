# syntax=docker/dockerfile:1
# Build the static app with Node, then serve it (and proxy /api) with nginx.
FROM node:24-alpine AS build
WORKDIR /web
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

# Unprivileged nginx (port 8080, any UID), so the same image runs under OpenShift's restricted
# security context as well as in Compose.
FROM nginxinc/nginx-unprivileged:1.30-alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /web/dist /usr/share/nginx/html
