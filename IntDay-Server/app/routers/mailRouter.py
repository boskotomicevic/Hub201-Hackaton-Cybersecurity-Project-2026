from fastapi import APIRouter
from app.service.mailService import checkOneEmailDomen, check_many_domains
from typing import List
from pydantic import BaseModel
from app.models.schemes import EmailItem, EmailsRequest

router = APIRouter(prefix="/mail")

class MailReq(BaseModel):
    email: str


class DomainReq(BaseModel):
    emails: List[str]


# provera jednog mejla
@router.post("/check-one-mail")
async def check_one_mail_domen(request: MailReq):

    if "@" not in request.email:
        return {"error": "Neispravan email"}

    domen = request.email.split("@")[-1]
    result = await checkOneEmailDomen(domen)

    return {"email": request.email, "result": result}


# provera vise mejlova
@router.post("/check-mails")
async def checkAllMails(request: EmailsRequest):
    result = await check_many_domains(request.items)
    return result
