FROM python:3.10.12-slim-bullseye
# ENV http_proxy http://192.168.63.130:10809
# ENV https_proxy http://192.168.63.130:10809
WORKDIR /app
ADD . /app
RUN pip install -r requirements.txt
RUN apt update -y && apt install -y android-tools-adb && apt install -y vim
EXPOSE 8200
CMD ["uvicorn","main:app","--host=0.0.0.0","--port=8200"]
