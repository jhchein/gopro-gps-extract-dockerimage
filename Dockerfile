#FROM alpine:latest
FROM mcr.microsoft.com/azure-cli:latest

RUN apk update && \
    apk add --update nodejs git nodejs-npm python3 ffmpeg && \
    ln -sf python3 /usr/bin/python

# Install Python Requirements
RUN python3 -m ensurepip
RUN pip3 install --no-cache --upgrade pip setuptools
RUN pip3 install azure-identity
RUN pip3 install azure-storage-blob
RUN pip3 install ffmpeg-python

# Install gpmf-extract and gopro-telemetry
RUN git clone https://github.com/JuanIrache/gpmf-extract.git
RUN git clone https://github.com/JuanIrache/gopro-telemetry.git
RUN npm i gpmf-extract
RUN npm i gopro-telemetry

RUN mkdir -p /usr/src/app
COPY main.py /usr/src/app/
COPY process.js /usr/src/app/
WORKDIR /usr/src/app

# environment variables for Azure Service Principal
ARG tenant_id
ARG client_id
ARG client_secret

ENV goprotenant_id=$tenant_id
ENV goproclient_id=$client_id
ENV goproclient_secret=$client_secret

ENTRYPOINT [ "python", "main.py"]