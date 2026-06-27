FROM python:3.14-alpine

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
	PYTHONUNBUFFERED=1 \
	PIP_DISABLE_PIP_VERSION_CHECK=1 \
	PIP_NO_CACHE_DIR=0

COPY requirements.txt .

RUN apk add --no-cache ffmpeg

RUN pip install -r requirements.txt

COPY . .

CMD ["python", "main.py"]
