#!/usr/bin/env python3
from fastapi import FastAPI, Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
import uvicorn
from btcmi.metrics import registry

app = FastAPI()


@app.get("/metrics")
def metrics():
    return Response(generate_latest(registry), media_type=CONTENT_TYPE_LATEST)


def main():
    uvicorn.run(app, host="0.0.0.0", port=9101)


if __name__ == "__main__":
    main()
