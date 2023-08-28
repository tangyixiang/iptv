FROM python:3.10.12-slim-bullseye
# ENV http_proxy http://192.168.63.130:10809
# ENV https_proxy http://192.168.63.130:10809

ENV NGINX_PATH /usr/sbin/nginx
EXPOSE 8100
WORKDIR /app
ADD . /app
RUN pip install -r requirements.txt
RUN apt update -y && apt install -y android-tools-adb && apt install -y vim && apt install -y nginx
# 复制 nginx 配置文件到容器中
COPY front/nginx.conf /etc/nginx/conf.d/default.conf
RUN mv /app/front/dist /front

# CMD ["nginx;","uvicorn","main:app","--host=0.0.0.0","--port=8200"]
ENTRYPOINT ["sh","entrypoint.sh"]
