from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from dotenv import load_dotenv
import os

load_dotenv()

CHANNEL_ACCESS_TOKEN = os.getenv("CHANNEL_ACCESS_TOKEN")
CHANNEL_SECRET = os.getenv("CHANNEL_SECRET")

app = Flask(__name__)

three = ["文勝", "勝方", "方文"]
four = ["文勝", "心方"]
countN = 1
countM = 0

back = [three, four]
turn = 0

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    global countN, countM, turn
    user_msg = event.message.text

    if user_msg == "買 7-11":
        reply = back[turn][countN % len(back[turn])]
        countN += 1

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply)
        )
    if user_msg == "買 麥當勞":
        reply = back[turn][countM % len(back[turn])]
        countM += 1

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply)
        )
    if user_msg == "目前":
        reply1 = back[turn][countM % len(back[turn])]
        reply2 = back[turn][countN % len(back[turn])]
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f"目前 7-11是 {reply1} 買，麥當勞是 {reply2} 買")
        )
    if user_msg == "換邊":
        turn = (turn + 1) % len(back)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="已換邊")
        )


if __name__ == "__main__":
    app.run(port=5000)