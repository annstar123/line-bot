from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from dotenv import load_dotenv
from keep_alive import keep_alive
import os

# 載入環境變數
load_dotenv()
CHANNEL_ACCESS_TOKEN = os.getenv("CHANNEL_ACCESS_TOKEN")
CHANNEL_SECRET = os.getenv("CHANNEL_SECRET")

app = Flask(__name__)

# 輪流人員名單
three = ["文勝", "勝方", "方文"]
four = ["文勝", "心方"]
back = [three, four]

# 計數器
countN = 0
countM = 0
turn = 0  # 0 -> three, 1 -> four

# LINE API
line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

# 健康檢查
@app.route("/", methods=['GET'])
def home():
    return "Bot is running ✅"

# LINE webhook
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers.get('X-Line-Signature', '')
    body = request.get_data(as_text=True)
    print("Received body:", body)  # <- 這裡會把 webhook JSON 印出來

    try:
        handler.handle(body, signature)
    except Exception as e:
        print("Handler failed:", e)
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    global countN, countM, turn
    user_msg = event.message.text
    print(f"Received message: {user_msg}")  # <- log 收到的訊息

    if user_msg == "買 7-11":
        reply = back[turn][countN % len(back[turn])]
        countN += 1
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
        return

    elif user_msg == "買 麥當勞":
        reply = back[turn][countM % len(back[turn])]
        countM += 1
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
        return

    elif user_msg == "目前":
        reply_711 = back[turn][countN % len(back[turn])]
        reply_mcd = back[turn][countM % len(back[turn])]
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f"目前 7-11是 {reply_711} 買，麥當勞是 {reply_mcd} 買")
        )
        return

    elif user_msg == "換邊":
        turn = (turn + 1) % len(back)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="已換邊"))
        return
    elif user_msg in ["指令", "help"]:
        reply_text = (
            "📋 可用指令：\n"
            "1️⃣ 買 7-11\n"
            "2️⃣ 買 麥當勞\n"
            "3️⃣ 誰買\n"
            "4️⃣ 目前\n"
            "5️⃣ 換邊\n"
        )
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_text)
        )
        print("Replied with command list")
        return
    
# Render 上必須綁定 0.0.0.0 並使用動態 port
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)