from app.core.events_parser import PremisEvent
from app.services.mediahaven import MediahavenService
from viaa.configuration import ConfigParser
import asyncio

async def handle_event(premis_event: PremisEvent) -> None:
    config = ConfigParser().app_cfg

    mediahaven_service = MediahavenService(config)

    fragment = mediahaven_service.get_fragment(premis_event.fragment_id)

    print(fragment)