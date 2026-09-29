# SOC Info Bot

SOC Info Bot — бот для Mattermost, предназначенный для быстрой проверки IOC через VirusTotal API.

Бот принимает IOC через slash-команду `/vt`, автоматически определяет тип индикатора и возвращает основные данные, необходимые для первичного анализа SOC L1.

## Поддерживаемые IOC

- IPv4
- Domain
- URL
- MD5 / SHA-1 / SHA-256

## Возможности

- Автоматическое определение типа IOC
- Проверка IOC через VirusTotal API
- Отображение результатов анализа VirusTotal
- Вывод дополнительной информации в зависимости от типа IOC
- Defang IP-адресов, доменов и URL перед выводом в Mattermost
- Поддержка HTTP-прокси для запросов к VirusTotal
- Обработка отсутствующих IOC (HTTP 404)
- Обработка ошибок соединения с VirusTotal

## Установка

Клонировать репозиторий:

```bash
git clone <URL_РЕПОЗИТОРИЯ>
cd mattermost
```

Создать виртуальное окружение:

```bash
python3 -m venv venv
source venv/bin/activate
```

Установить зависимости:

```bash
pip install -r requirements.txt
```

## Настройка

Создать `.env` на основе примера:

```bash
cp .env.example .env
```

Заполнить необходимые переменные:

```env
MATTERMOST_URL=http://localhost:8065
MATTERMOST_TOKEN=<MATTERMOST_BOT_TOKEN>
VT_API_KEY=<VIRUSTOTAL_API_KEY>
VT_PROXY=<HTTP_PROXY>
```

`VT_PROXY` является необязательным. Если прокси не используется, значение можно оставить пустым:

```env
VT_PROXY=
```

Не добавляйте файл `.env` в Git — он содержит секретные данные.

## Запуск

Активировать виртуальное окружение:

```bash
source venv/bin/activate
```

Запустить приложение:

```bash
python -m app.main
```

После успешного запуска FastAPI будет доступен на:

```text
http://0.0.0.0:8000
```

Для остановки приложения используйте:

```text
Ctrl+C
```

## Настройка Mattermost Slash Command

Бот принимает запросы от Mattermost через FastAPI на порту `8000`.

FastAPI должен слушать все сетевые интерфейсы:

```text
0.0.0.0:8000
```

Это необходимо, чтобы к API мог обращаться Mattermost, запущенный внутри Docker-контейнера.

После запуска приложения в терминале должно отображаться:

```text
Uvicorn running on http://0.0.0.0:8000
```

### Настройка Slash Command

В Mattermost создать Slash Command со следующими параметрами:

```text
Command Trigger Word: vt
Request Method: POST
Request URL: http://<BOT_HOST>:8000/vt
```

Если Mattermost запущен в Docker, нельзя использовать:

```text
http://127.0.0.1:8000/vt
http://localhost:8000/vt
```

Внутри контейнера эти адреса указывают на сам контейнер Mattermost, а не на хост, где запущен бот.

Необходимо использовать IP-адрес хоста, доступный из Docker-сети.

Например:

```text
http://172.18.0.1:8000/vt
```

Адрес может отличаться в зависимости от конфигурации Docker-сети.

### Разрешение внутренних подключений Mattermost

Mattermost может блокировать HTTP-запросы к внутренним IP-адресам.

Если при обращении к боту возникает ошибка, связанная с запрещённым внутренним адресом, необходимо разрешить адрес хоста в настройке Mattermost:

```text
ServiceSettings.AllowedUntrustedInternalConnections
```

Например:

```text
172.18.0.1
```

После изменения конфигурации Mattermost необходимо применить изменения или перезапустить контейнер.

### Проверка доступности бота

Из контейнера Mattermost необходимо убедиться, что хост с FastAPI доступен:

```bash
curl http://<BOT_HOST>:8000
```

Например:

```bash
curl http://172.18.0.1:8000
```

Получение HTTP-ответа подтверждает, что контейнер Mattermost может обращаться к FastAPI.

### Использование

После настройки Slash Command IOC можно проверять непосредственно из канала Mattermost:

```text
/vt 8.8.8.8
/vt example.com
/vt https://example.com/
/vt <MD5_SHA1_SHA256>
```

IP-адреса, домены и URL в ответах бота выводятся в defang-виде, чтобы предотвратить случайный переход по потенциально вредоносному IOC.
