FROM python:3.8-alpine
WORKDIR ./
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_SECRET_KEY='c3df7fe556f548dfb16a94342f7d0fad'
ENV REDIS_HOST='redis'
ENV REDIS_PORT=6379
RUN apk add --no-cache --update musl-dev gcc libffi-dev python3-dev openssl-dev && pip3 install --upgrade pip && pip3 install --upgrade setuptools
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
EXPOSE 5000
COPY . .
CMD ["flask", "run", "--cert=adhoc"]
