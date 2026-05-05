from fastapi import APIRouter
#
from viaa.configuration import ConfigParser
from viaa.observability import logging

router = APIRouter()

config = ConfigParser()
log = logging.get_logger(__name__, config=config)

@router.get("/live")
async def liveness_check():
    """
    Returns OK if the service is running.
    """
    log.debug("Health/live called")
    return "OK"
