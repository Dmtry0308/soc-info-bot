import uvicorn
from app.mattermost.client import MattermostClient
from fastapi import FastAPI
from app.api.routes import router
from threading import Thread




client = MattermostClient()
client.login()

user = client.get_bot_user()
print(user)

thread = Thread(target=client.start_websocket)
thread.start()

app = FastAPI()
app.include_router(router)
print("FastAPI app created")
uvicorn.run(app, host="0.0.0.0")
