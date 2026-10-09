import httpx
import base64
import ipaddress
import re
from urllib.parse import urlparse
from datetime import datetime
from app.core.config import VT_PROXY, VT_API_KEY



def parse_iocs(text: str):
    return [ioc for ioc in re.split(r"[,\s]+", text) if ioc]


def detect_ioc_type(ioc: str):
    try:
        ipaddress.ip_address(ioc)
        return "ip"
    except ValueError:
        pass

    parsed = urlparse(ioc)
    if parsed.scheme and parsed.hostname:
        return "url"

    if len(ioc) in (32, 40, 64):
        try:
            int(ioc, 16)
            return "hash"
        except ValueError:
            pass

    parts = ioc.split(".")

    if len(parts) > 1 and all(parts):
        if all(
            part.replace("-", "").isalnum()
            and not part.startswith("-")
            and not part.endswith("-")
            for part in parts
        ):
            return "domain"

    return None



def build_vt_url(ioc: str, ioc_type: str):
    if ioc_type == "ip":
        return f"https://www.virustotal.com/api/v3/ip_addresses/{ioc}"
    elif ioc_type == "domain":
        return f"https://www.virustotal.com/api/v3/domains/{ioc}"
    elif ioc_type == "hash":
        return f"https://www.virustotal.com/api/v3/files/{ioc}"
    elif ioc_type == "url":
        encoded = base64.urlsafe_b64encode(ioc.encode()).decode()
        encoded = encoded.rstrip("=")
        return f"https://www.virustotal.com/api/v3/urls/{encoded}"
    return None



def format_timestamp(timestamp):
    
    if not timestamp:
        return "N/A"
    date = datetime.fromtimestamp(timestamp)
    return date.strftime("%d.%m.%Y")



def defang_ioc(ioc: str, ioc_type: str):

    if ioc_type == "hash":
        return ioc

    if ioc_type == "ip":
        parts = ioc.rsplit(".", 1)
        return parts[0] + "[.]" + parts[-1]

    return ioc.replace(".", "[.]")



async def check_ioc(ioc: str):

    ioc_type = detect_ioc_type(ioc)
    if ioc_type is None:
        return {
            "ok": False,
            "status_code": None,
            "error": "Не удалось определить тип IOC"
        }

    url = build_vt_url(ioc, ioc_type) 

    headers = {
    "accept": "application/json",
    "x-apikey": VT_API_KEY
    }
    async with httpx.AsyncClient(proxy=VT_PROXY if VT_PROXY else None) as client:
        try:
            response = await client.get(url, headers=headers)
        except httpx.RequestError:
            return {
                "ok": False,
                "status_code": None,
                "error": "Ошибка соединения с VirusTotal"
            }
        
        if response.status_code == 404:
            
            return {
                "ok": False,
                "status_code": response.status_code,
                "ioc_type": ioc_type,
                "error": "IOC не найден в VirusTotal"
            }
        if response.status_code != 200:
            return {
                "ok": False,
                "status_code": response.status_code,
                "error": f"Ошибка запроса VirusTotal: '{response.status_code}'"
            } 

        data = response.json()
        return {
            "ok": True,
            "ioc_type": ioc_type,
            "data": data["data"]
            }

