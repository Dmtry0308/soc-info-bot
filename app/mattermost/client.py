from mattermostdriver import Driver
from urllib.parse import urlparse
from app.core.config import MATTERMOST_TOKEN, MATTERMOST_URL, MATTERMOST_BOT_USERNAME
from app.mattermost.events import event_handler
import asyncio



class MattermostClient:


    def __init__(self):

        parsed = urlparse(MATTERMOST_URL)
        host = parsed.hostname
        port = parsed.port
        scheme = parsed.scheme

        self.driver = Driver({
            "url": host,
            "port": port,
            "scheme": scheme,
            "token": MATTERMOST_TOKEN
        })


    def get_bot_user(self):
        user =  self.driver.users.get_user_by_username(MATTERMOST_BOT_USERNAME)
        return {"id": user["id"],
                "username":user["username"],
                "is_bot": user["is_bot"],
                "first_name": user["first_name"]
        }


    def login(self):
        self.driver.login()


    def start_websocket(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        self.driver.init_websocket(event_handler)
