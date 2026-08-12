FROM postgres:14.13

RUN apt-get update && apt-get install -y curl cron && rm -rf /var/lib/apt/lists/*

RUN curl -L "https://github.com/wal-g/wal-g/releases/download/v3.0.8/wal-g-pg-ubuntu-20.04-amd64.tar.gz" | tar -xz && \
    mv wal-g-pg-ubuntu-20.04-amd64 /usr/local/bin/wal-g && \
    chmod +x /usr/local/bin/wal-g

COPY setup-walg.sh /docker-entrypoint-initdb.d/
COPY entrypoint-wrapper.sh /usr/local/bin/
COPY walg-cron /etc/cron.d/walg-cron

RUN chmod +x /usr/local/bin/entrypoint-wrapper.sh && \
    chmod +x /docker-entrypoint-initdb.d/setup-walg.sh && \
    chmod 0644 /etc/cron.d/walg-cron && \
    crontab /etc/cron.d/walg-cron

ENTRYPOINT ["entrypoint-wrapper.sh"]
CMD ["postgres"]
