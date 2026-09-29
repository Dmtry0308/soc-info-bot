import json


async def event_handler(message):

    message = json.loads(message)
    
    if message.get("event") and message["event"] == "posted" and isinstance(message["data"]["post"], str):
        post = json.loads(message["data"]["post"])
        print(f"user_id: {post['user_id']}\n"
              f"channel_id: {post['channel_id']}\n"
              f"message: {post['message']}")
