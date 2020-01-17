FROM python:3.7

WORKDIR /sticker

RUN apt update
RUN apt install ffmpeg -y

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt