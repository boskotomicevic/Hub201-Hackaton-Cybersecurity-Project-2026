import asyncio
import aiohttp
import base64
import os
from dotenv import load_dotenv

#Ovo trazi .env u tvom folderu, sa datim kljucevima
load_dotenv()

VT_API_KEY = os.getenv("VT_API_KEY")
CF_API_TOKEN = os.getenv("CF_API_TOKEN")
CF_ACCOUNT_ID = os.getenv("CF_ACCOUNT_ID")

async def get_virustotal_score(session, url, api_key):
    url_id = base64.urlsafe_b64encode(url.encode()).decode().strip("=")
    get_endpoint = f"https://www.virustotal.com/api/v3/urls/{url_id}"
    
    headers = {
        "accept": "application/json", 
        "x-apikey": api_key
    }
    
    try:
        #Da li dat URL vec postoji u bazi VT
        async with session.get(get_endpoint, headers=headers) as response:
            if response.status == 404:
                #Ako ne saljemo ga na scan
                post_endpoint = "https://www.virustotal.com/api/v3/urls"
                payload = {"url": url} # Podaci za formu
                
                async with session.post(post_endpoint, data=payload, headers=headers) as post_response:
                    if post_response.status == 200:
                        return {
                            "data_available": False, 
                            "message": "URL sent for scanning",
                            "status": "submitted"
                        }
                    else:
                        return {
                            "data_available": False, 
                            "message": "URL not in DB and scanning failed",
                            "error": f"HTTP {post_response.status}"
                        }
            
            #Greska sa statusom 429ZNAK je previse pokusaja, limit pokusaja u minutu je 4
            if response.status != 200:
                return {"data_available": False, "error": f"HTTP {response.status}"}
            
            #Kad jeste u bazi
            data = await response.json()
            stats = data['data']['attributes']['last_analysis_stats']
            malicious = stats.get('malicious', 0)
            suspicious = stats.get('suspicious', 0)
            
            return {
                "data_available": True,
                "malicious": malicious, #Brojcane vrednosti cuvamo ako budemo hteli da promenimo sa T/F na skalu
                "suspicious": suspicious,
                "is_phishing": malicious > 0 or suspicious > 2
            }
            
    except Exception as e:
        return {"data_available": False, "error": str(e)}
    
async def get_cloudflare_score(session, domain, api_token, account_id):
    endpoint = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/urlscanner/scan"
    headers = {"Authorization": f"Bearer {api_token}", "Content-Type": "application/json"}
    
    try:
        async with session.post(endpoint, json={"url": domain}, headers=headers) as response:
            if response.status not in (200, 201):
                return {"data_available": False, "error": f"HTTP {response.status}"}
            data = await response.json()
            scan_uuid = data.get('result', {}).get('uuid')
            
            if not scan_uuid:
                return {"data_available": False, "error": "Nije dobijen scan_id"}

        await asyncio.sleep(1) #Saltamo posle na 3 posto 1 skoro uvek nije dovoljno vremena ali je potrebno da brzo radi za MVP
        
        result_endpoint = f"{endpoint}/{scan_uuid}"
        async with session.get(result_endpoint, headers=headers) as res_response:
            res_data = await res_response.json()
            
            cf_result_data = res_data.get('result', {})
            
            verdicts = cf_result_data.get('verdicts')
            
            #Ako verdicts ne postoji, znaci da skeniranje nije gotovo
            if not verdicts:
                return {
                    "data_available": False,
                    "message": "Skeniranje nije zavrseno na vreme",
                    "scan_id": scan_uuid
                }

            overall = verdicts.get('overall', {})
            return {
                "data_available": True,
                "status": "completed",
                "is_malicious": overall.get('malicious', False),
                "is_phishing": overall.get('phishing', False),
                "scan_id": scan_uuid 
            }
    except Exception as e:
         return {"data_available": False, "error": str(e)}
    

#OVA FUNKCIJA SE POZIVA 
async def analyze_url(url_to_scan: str) -> dict:
    if not url_to_scan.startswith(("http://", "https://")):
        url_to_scan = "http://" + url_to_scan

    async with aiohttp.ClientSession() as session:
        task_vt = get_virustotal_score(session, url_to_scan, VT_API_KEY)
        task_cf = get_cloudflare_score(session, url_to_scan, CF_API_TOKEN, CF_ACCOUNT_ID)
        
        vt_result, cf_result = await asyncio.gather(task_vt, task_cf)

    #Proveravamo ko ima podatke
    vt_has_data = vt_result.get("data_available", False)
    cf_has_data = cf_result.get("data_available", False)

    is_phishing = False
    
    #Gledamo rezultate SAMO ako podaci zapravo postoje
    if vt_has_data and vt_result.get("is_phishing"):
        is_phishing = True
        
    if cf_has_data and (cf_result.get("is_phishing") or cf_result.get("is_malicious")):
        is_phishing = True

    
    if not vt_has_data and not cf_has_data:
        final_verdict = "UNKNOWN" #Nemamo pojma o ovom sajtu, boju vi odlucujte
    else:
        final_verdict = "SCAM" if is_phishing else "SAFE"

    return {
        "target_url": url_to_scan,
        "results": {
            "virustotal": vt_result,
            "cloudflare": cf_result
        },
        "final_verdict": final_verdict
    }