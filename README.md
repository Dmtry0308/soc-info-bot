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

## Требования

Для запуска необходимы:

- Python 3
- Docker
- Docker Compose
- VirusTotal API Key

Тестовое окружение использует:

- Mattermost Team Edition 11.10.1
- PostgreSQL 16

## 1. Клонирование репозитория

```bash
git clone https://github.com/Dmtry0308/soc-info-bot.git
cd soc-info-bot
```

## 2. Создание виртуального окружения

```bash
python3 -m venv venv
source venv/bin/activate
```

Установить зависимости:

```bash
pip install -r requirements.txt
```

## 3. Запуск Mattermost

Mattermost и PostgreSQL запускаются через Docker Compose:

```bash
sudo docker compose up -d
```

Проверить состояние контейнеров:

```bash
sudo docker compose ps
```

Необходимо дождаться, пока контейнер Mattermost перейдёт в состояние `healthy`.

После запуска Mattermost будет доступен по адресу:

```text
http://localhost:8065
```

При первом запуске необходимо:

1. Создать учётную запись администратора.
2. Создать рабочее пространство Mattermost.
3. Завершить первоначальную настройку.

## 4. Настройка Site URL

Открыть:

```text
System Console → Environment → Web Server
```

Установить:

```text
Site URL: http://localhost:8065
```

Сохранить изменения.

После изменения Site URL перезапустить Mattermost:

```bash
sudo docker restart soc-info-bot-mattermost-1
```

Дождаться состояния `healthy`:

```bash
sudo docker ps
```

## 5. Разрешение создания Bot Accounts

Открыть:

```text
System Console → Integrations → Bot Accounts
```

Установить:

```text
Enable Bot Account Creation: True
```

Сохранить изменения.

## 6. Создание Bot Account

Открыть:

```text
Mattermost → Integrations → Bot Accounts
```

Нажать:

```text
Add Bot Account
```

Заполнить:

```text
Username: soc-info-bot
Display Name: SOC Info Bot
Description: SOC bot for IOC enrichment via VirusTotal
Role: Member
```

Дополнительные разрешения `post:all` и `post:channels` для базовой конфигурации не требуются.

Создать Bot Account и сохранить выданный Mattermost Token.

Токен является секретным и не должен добавляться в Git.

## 7. Настройка переменных окружения

Создать `.env` на основе примера:

```bash
cp .env.example .env
```

Открыть `.env` и заполнить:

```env
MATTERMOST_URL=http://localhost:8065
MATTERMOST_TOKEN=<MATTERMOST_BOT_TOKEN>
MATTERMOST_BOT_USERNAME=soc-info-bot
VT_API_KEY=<VIRUSTOTAL_API_KEY>
VT_PROXY=
```

Где:

- `MATTERMOST_TOKEN` — токен созданного Bot Account.
- `MATTERMOST_BOT_USERNAME` — username созданного Bot Account.
- `VT_API_KEY` — API-ключ VirusTotal.
- `VT_PROXY` — необязательный HTTP-прокси для запросов к VirusTotal.

Если прокси используется:

```env
VT_PROXY=http://user:password@host:port
```

Если прокси не требуется:

```env
VT_PROXY=
```

Файл `.env` содержит секретные данные и не должен добавляться в Git.

## 8. Определение адреса Docker Gateway

Mattermost работает внутри Docker-контейнера, поэтому `127.0.0.1` и `localhost` внутри контейнера указывают на сам контейнер, а не на хост с FastAPI.

Посмотреть Docker-сеть:

```bash
sudo docker network ls
```

При стандартном запуске этого проекта сеть будет называться:

```text
soc-info-bot_default
```

Узнать адрес Gateway:

```bash
sudo docker network inspect soc-info-bot_default | grep Gateway
```

Пример результата:

```text
"Gateway": "172.19.0.1"
```

Адрес может отличаться в зависимости от конфигурации Docker.

Далее этот адрес используется как `<BOT_HOST>`.

## 9. Разрешение подключения Mattermost к FastAPI

Mattermost по умолчанию может блокировать HTTP-запросы к внутренним IP-адресам.

Открыть:

```text
System Console → Developer → Connections
```

В поле:

```text
Allow untrusted internal connections to:
```

указать найденный Docker Gateway.

Например:

```text
172.19.0.1
```

Сохранить изменения.

## 10. Создание Slash Command

Открыть:

```text
Mattermost → Integrations → Slash Commands
```

Нажать:

```text
Add Slash Command
```

Заполнить:

```text
Title: VirusTotal IOC Check
Description: Check IOC via VirusTotal
Command Trigger Word: vt
Request Method: POST
Request URL: http://<BOT_HOST>:8000/vt
```

Например, если Docker Gateway:

```text
172.19.0.1
```

то Request URL:

```text
http://172.19.0.1:8000/vt
```

В `Command Trigger Word` необходимо указывать:

```text
vt
```

без символа `/`.

Сохранить Slash Command.

## 11. Запуск SOC Info Bot

Убедиться, что виртуальное окружение активно:

```bash
source venv/bin/activate
```

Запустить приложение:

```bash
python -m app.main
```

При успешном запуске в терминале должно появиться примерно следующее:

```text
FastAPI app created
Uvicorn running on http://0.0.0.0:8000
```

FastAPI должен слушать `0.0.0.0`, чтобы Mattermost из Docker-контейнера мог обращаться к приложению на хосте.

Для остановки приложения:

```text
Ctrl+C
```

## 12. Проверка работы

В любом канале Mattermost выполнить:

```text
/vt 8.8.8.8
```

При успешной настройке бот вернёт информацию VirusTotal и статистику анализа IOC.

Другие примеры:

```text
/vt example.com
/vt https://example.com/
/vt <MD5_SHA1_SHA256>
```

IP-адреса, домены и URL в ответах бота выводятся в defang-виде, чтобы предотвратить случайный переход по потенциально вредоносному IOC.

## Возможные проблемы

### SiteURL must be configured to use slash commands

Проверить:

```text
System Console → Environment → Web Server → Site URL
```

Для локального стенда:

```text
http://localhost:8065
```

После изменения перезапустить Mattermost.

### Mattermost блокирует Request URL

Проверить:

```text
System Console → Developer → Connections
```

В `Allow untrusted internal connections to` должен быть указан Docker Gateway хоста.

### Бот не находит Mattermost Bot Account

Проверить значения:

```env
MATTERMOST_TOKEN=
MATTERMOST_BOT_USERNAME=soc-info-bot
```

`MATTERMOST_BOT_USERNAME` должен совпадать с Username созданного Bot Account.

### Ошибка соединения с VirusTotal

Проверить:

```env
VT_API_KEY=
VT_PROXY=
```

Если используется прокси, убедиться, что он доступен и поддерживает соединение с VirusTotal API.
