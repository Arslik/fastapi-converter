FROM python:3.9-slim
LABEL authors="Arlan"

WORKDIR /converter

COPY . .

RUN apt-get update && apt-get install -y ffmpeg libsm6 libxext6 && apt-get clean

RUN pip install --no-cache-dir fastapi uvicorn opencv-python-headless

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]