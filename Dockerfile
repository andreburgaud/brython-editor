FROM nginx:1.25.2-alpine3.18

ADD site /usr/share/nginx/html/

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
