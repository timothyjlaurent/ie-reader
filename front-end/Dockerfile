# Use an official Node runtime as a parent image
FROM node:10-alpine as builder
LABEL maintainers="AI-team code monkeys <aiteam@invitae.com>"

# Create app directory
WORKDIR /app

# Install app dependencies
# A wildcard is used to ensure both package.json AND package-lock.json are copied
# where available (npm@5+)
COPY package*.json ./

# Build code for production
RUN npm install --only=production

# Bundle app source
COPY . .
RUN npm run-script build

FROM nginx:1.15-alpine

# Install Dockerize for environment varibiable interpolation
RUN apk add --no-cache openssl

ENV DOCKERIZE_VERSION v0.6.1
RUN wget https://github.com/jwilder/dockerize/releases/download/$DOCKERIZE_VERSION/dockerize-alpine-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && tar -C /usr/local/bin -xzvf dockerize-alpine-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && rm dockerize-alpine-linux-amd64-$DOCKERIZE_VERSION.tar.gz

WORKDIR /app

# copy react app into nginx app
COPY --from=builder /app/build /app/build

COPY etc/nginx.conf /etc/nginx/
COPY etc/default.tmpl /etc/nginx/conf.d/

# Dockerize allows interpolating environment variables in the template
# -g 'daemon off;' is to prevent the container from immediately exiting

ENV REACT_APP_BACKEND_URL=http://back-end:5000

CMD dockerize --template /etc/nginx/conf.d/default.tmpl:/etc/nginx/conf.d/default.conf nginx -g 'daemon off;'

EXPOSE 80
