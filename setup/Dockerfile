FROM python:3.7

ENV user=sticker
RUN useradd --user-group --create-home --no-log-init --shell /bin/bash $user
WORKDIR /home/$user

RUN apt update
RUN apt install ffmpeg -y

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
USER $user