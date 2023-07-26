from fastapi import FastAPI

from viaa.configuration import ConfigParser
from viaa.observability import logging
from mediahaven import MediaHaven
from mediahaven.oauth2 import RequestTokenError, ROPCGrant

from app.api.api import api_router

app = FastAPI()

app.include_router(api_router)

config = ConfigParser()
log = logging.get_logger(__name__, config=config)
_mediahaven_client: MediaHaven = None


@app.on_event("startup")
async def startup_event():
    global _mediahaven_client
    mediahaven_config = config.app_cfg["mediahaven"]
    client_id = mediahaven_config["client_id"]
    client_secret = mediahaven_config["client_secret"]
    user = mediahaven_config["username"]
    password = mediahaven_config["password"]
    url = mediahaven_config["host"]
    grant = ROPCGrant(url, client_id, client_secret)
    try:
        grant.request_token(user, password)
    except RequestTokenError as e:
        log.error(e)
        raise e
    _mediahaven_client = MediaHaven(url, grant)
    log.info("avo-events-archived is now accepting requests.")


@app.on_event("shutdown")
async def shutdown_event():
    log.info("avo-events-archived is shutting down.")
