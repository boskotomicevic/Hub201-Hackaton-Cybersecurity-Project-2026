from beanie import Document
from typing import Optional

class Email(Document):
    name: str
    isValid: Optional[bool] = None

    class Settings:
        name = "mail_list"
