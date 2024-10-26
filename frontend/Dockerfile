FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --legacy-peer-deps && npm install -g @vue/cli-service
COPY . .
EXPOSE 8081
CMD ["npm", "run", "serve"]
