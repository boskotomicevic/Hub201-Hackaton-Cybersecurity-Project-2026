from pydantic import BaseModel
from typing import List


class EmailItem(BaseModel):
    email: str
    urlFromEmail: str


class EmailsRequest(BaseModel):
    items: List[EmailItem]
