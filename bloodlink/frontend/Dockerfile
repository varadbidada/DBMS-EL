FROM node:20-alpine as builder

WORKDIR /app

# Install pnpm (needs network, but we can use npm for simplicity)
RUN npm install -g npm

COPY package.json package-lock.json ./
RUN npm ci

COPY . .

RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
