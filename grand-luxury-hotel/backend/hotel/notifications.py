import json,logging,os
from urllib.request import Request,urlopen

def alert(message):
    token=os.getenv("TELEGRAM_BOT_TOKEN")
    chat=os.getenv("TELEGRAM_CHAT_ID")
    if not (token and chat):return
    try:
        payload=json.dumps({"chat_id":chat,"text":message}).encode()
        with urlopen(Request("https://api.telegram.org/bot"+token+"/sendMessage",data=payload,headers={"Content-Type":"application/json"}),timeout=3) as resp:resp.read()
    except Exception:logging.getLogger(__name__).exception("Could not deliver booking alert")
