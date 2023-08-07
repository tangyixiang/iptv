FROM python:3.10.12-slim-bullseye
# ENV http_proxy http://192.168.63.130:10809
# ENV https_proxy http://192.168.63.130:10809
WORKDIR /app
ADD . /app
RUN pip install -r requirements.txt
EXPOSE 8000
CMD ["uvicorn","main:app"]
