from app.models.email import Email
from typing import List
from app.service.phishing_vt_cf import analyze_url
from app.models.schemes import EmailItem, EmailsRequest
from app.models.email import Email
async def checkOneEmailDomen(domen: str):
    mailDomen = await Email.find_one(Email.name == domen)
    if mailDomen is None:
        return f"Domen:@{domen} nije u bazi"
    elif mailDomen.isValid:
        return f"Domen:@{domen} nije skem"
    else:
        return f"Domen:@{domen} je skem"




async def check_many_domains(mailsToVerify: List[EmailItem]) -> List[dict]:
    results = []

    for mail in mailsToVerify:
        domain = mail.email.split("@")[-1]

        checkedDomain = await Email.find_one(Email.name == domain)

        if checkedDomain is None:
            results.append({
                "domain": domain,
                "urlFromEmail": mail.urlFromEmail,
                "status": "nije u bazi",
                "analysis": None
            })
            newDomain = await Email(name = domain, isValid = None)
            newDomain.insert()

        elif not checkedDomain.isValid:
            analysis = await analyze_url(mail.urlFromEmail)

            results.append({
                "domain": domain,
                "urlFromEmail": mail.urlFromEmail,
                "status": "domen je skem",
                "analysis": analysis
            })

        else:
            analysis = await analyze_url(mail.urlFromEmail)

            results.append({
                "domain": domain,
                "urlFromEmail": mail.urlFromEmail,
                "status": "domen je dobar",
                "analysis": analysis
            })

    return results

