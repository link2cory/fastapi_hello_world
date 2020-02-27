# base image
FROM python:3.8.0-slim as builder

RUN apt-get update \
&& apt-get install gcc -y \
&& apt-get clean

COPY requirements.txt /app/requirements.txt
WORKDIR app
RUN pip install --user -r requirements.txt
COPY . /app

FROM python:3.8.0-slim as app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PATH=/root/.local/bin:$PATH

COPY --from=builder /root/.local /root/.local
COPY --from=builder /app/ /app/
WORKDIR app
ENTRYPOINT ["/app/entrypoint.sh"]
