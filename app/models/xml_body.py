# Std
from typing import Callable, Generic, Type, TypeVar
# 3trd
from fastapi import Request
from pydantic import BaseModel
from pydantic.error_wrappers import ValidationError as PydanticValidationError
# meemoo
from viaa.configuration import ConfigParser
from viaa.observability import logging

T = TypeVar("T", bound=BaseModel)


config = ConfigParser()
log = logging.get_logger(__name__, config=config)

class XmlBody(Generic[T]):
    def __init__(self, model_class: Type[T], parser: Callable):
        self.model_class = model_class
        self.parser = parser

    async def __call__(self, request: Request) -> T:
        body = await request.body()
        dict_data = self.parser(body)
        log.debug("Dict from incoming body: '%s'" % dict_data)
        try:
            assert dict_data["events"], "No events in request body? -> %s" % dict_data
        except (TypeError, AttributeError, KeyError, AssertionError) as e:
            log.error(
                "Could not properly parse/unpack PremisEvent (see: 'exception')",
                exception=str(e),)
            return None
        try:
            parsed_data = self.model_class.parse_obj(dict_data)
        except PydanticValidationError as e:
            log.error(
                "Could not validate PremisEvent (see: 'exception')",
                exception=str(e),)
            return None
        else:
            return parsed_data
