import os
import pdfplumber
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

app = Flask(__name__)

CHANNEL_ACCESS_TOKEN = os.environ.get("CHANNEL_ACCESS_TOKEN")
CHANNEL_SECRET = os.environ.get("CHANNEL_SECRET")

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

# --- もしPDFを読み込みたい場合はコメントアウト解除して使う ---
# with pdfplumber.open("kig研修マニュアル.pdf") as pdf:
#     text_content = pdf.pages[0].extract_text()

@app.route("/", methods=["GET"])
def index():
    # トップページにアクセスした時の表示
    return "Hello from /"

@app.route("/callback", methods=["POST"])
def callback():
    # LINE からのWebhook用エンドポイント

    signature = request.headers.get("X-Line-Signature")
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return "OK"

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # ユーザーがテキストを送ってきたときの処理
    user_text = event.message.text
    reply_text = f"あなたが入力したのは: {user_text}"

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text)
    )

if __name__ == "__main__":
    app.run()
