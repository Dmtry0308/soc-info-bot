from fastapi import APIRouter, Form, Request
from app.services.virustotal import check_ioc, format_timestamp, defang_ioc



router = APIRouter()



FIELD_MAP = {
    "ip": [
        ("Страна", "country"),
        ("ASN", "asn"),
        ("Владелец сети", "as_owner"),
        ("Сеть", "network"),
    ],
    "domain": [
        ("Регистратор", "registrar"),
        ("Дата регистрации", "creation_date", format_timestamp),
        ("Дата окончания регистрации", "expiration_date", format_timestamp),
        ("Репутация", "reputation")
    ],
    "hash": [
        ("Имя файла","meaningful_name"),
        ("Тип файла", "type_description"),
        ("Размер", "size"),
        ("Репутация", "reputation")
    ],
    "url": [
        ("Заголовок страницы", "title"),
        ("HTTP-код", "last_http_response_code"),
        ("Конечный URL", "last_final_url", lambda value: value.replace(".", "[.]")),
        ("Репутация", "reputation")
    ]
}



def format_ioc_info(ioc_type, attributes):
    fields = FIELD_MAP.get(ioc_type, [])
    lines = []
    for label, key, *formatters in fields:
        value = attributes.get(key, "N/A")
        if formatters:
            value = formatters[0](value)

        lines.append(f"{label}: {value}")
    return "\n".join(lines)


@router.post("/vt")
async def get_vt(request: Request, text: str = Form(...), channel_id: str = Form(...), user_id: str = Form(...)):
 
    result = await check_ioc(text)

    if result["ok"]:

        ioc_type = result["ioc_type"]
        attributes = result["data"]["attributes"]

        stats = attributes.get("last_analysis_stats", {})
        ioc = defang_ioc(text, ioc_type)
        info = format_ioc_info(ioc_type, attributes)

        message = f"""🔎 Проверка IOC в VirusTotal

Индикатор: {ioc}
{info}

**Результаты анализа:**
🔴 Вредоносный: {stats.get("malicious", 0)}
🟠 Подозрительный: {stats.get("suspicious", 0)}
🟢 Безопасный: {stats.get("harmless", 0)}
⚪ Не определён: {stats.get("undetected", 0)}
⏱ Таймаут: {stats.get("timeout", 0)}"""
    else:
        if result["status_code"] == 404:
            safe_ioc = defang_ioc(text, result["ioc_type"])
            message = f"IOC не найден в VirusTotal: {safe_ioc}"
        else:
            message = result["error"]
    
    return {'response_type': 'in_channel',
            'text': message
       }
