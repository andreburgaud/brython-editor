# syntax=docker/dockerfile:1

FROM nginx:1.25.4-alpine3.18

ADD site /usr/share/nginx/html/

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
