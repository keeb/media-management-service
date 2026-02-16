FROM denoland/deno:debian
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /opt/mms
COPY mms /opt/mms/mms
COPY swamp /usr/local/bin/swamp
COPY .swamp.yaml .
COPY .swamp/ .swamp/
RUN chmod +x /opt/mms/mms /usr/local/bin/swamp
CMD ["swamp", "workflow", "run", "media-inventory", "--json"]
