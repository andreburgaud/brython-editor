FROM nginx:1.23.3-alpine

COPY *.py index.html main.css favicon.ico /usr/share/nginx/html/

ADD images /usr/share/nginx/html/images

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
