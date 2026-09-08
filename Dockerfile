FROM python:3.12-slim-bookworm

LABEL org.opencontainers.image.description="US visa appointment rescheduler for Canada"
LABEL org.opencontainers.image.licenses="GPL-3.0"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    CHROME_BIN=/usr/bin/chromium \
    CHROMEDRIVER_PATH=/usr/bin/chromedriver \
    TEST_MODE=true \
    SHOW_GUI=false

RUN apt-get update \
    && apt-get install --no-install-recommends --yes \
        ca-certificates \
        chromium \
        chromium-driver \
        tini \
        tzdata \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --gid 1000 app \
    && useradd --uid 1000 --gid app --create-home app \
    && mkdir -p /app /data \
    && chown app:app /app /data

ENV COMPLETION_FILE=/data/state/reschedule-complete \
    DIAGNOSTICS_DIR=/data/diagnostics \
    IDLE_AFTER_SUCCESS=true

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir --requirement requirements.txt

COPY --chown=app:app . .

USER app
VOLUME ["/data"]

ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["python", "-u", "reschedule.py"]
