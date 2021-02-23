from typing import Callable, Generic, Type, TypeVar

from fastapi import Request
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class XmlBody(Generic[T]):
    def __init__(self, model_class: Type[T], parser: Callable):
        self.model_class = model_class
        self.parser = parser

    async def __call__(self, request: Request) -> T:
        body = await request.body()
        dict_data = self.parser(body)

        return self.model_class.parse_obj(dict_data)
