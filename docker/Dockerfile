FROM python:3.10-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install . && adduser --system --group appuser && chown -R appuser /app
USER appuser
ENTRYPOINT ["btcmi"]
CMD ["--help"]
