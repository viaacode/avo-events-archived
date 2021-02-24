from fastapi import FastAPI
from viaa.configuration import ConfigParser
from viaa.observability import logging

from app.api.api import api_router

app = FastAPI()

app.include_router(api_router)

config = ConfigParser()
log = logging.get_logger(__name__, config=config)


@app.on_event("startup")
async def startup_event():
    log.info("avo-events-archived is now accepting requests.")


@app.on_event("shutdown")
async def shutdown_event():
    log.info("avo-events-archived is shutting down.")
