import os
import pdfplumber
from flask import Flask, request, abort

# LINE BOT SDK
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage
)

app = Flask(__name__)

# 環境変数からトークン・シークレットを取得（Render や Heroku で設定）
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", "YOUR_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET", "YOUR_CHANNEL_SECRET")

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# PDFを読み込んでテキストを一度だけ抽出しておく（大きいPDFの場合は別途工夫が必要）
PDF_TEXT = ""
try:
    with pdfplumber.open("manual.pdf") as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                PDF_TEXT += page_text
except Exception as e:
    print("PDFの読み込みに失敗しました:", e)


@app.route("/")
def hello():
    return "Hello, this is a LINE Bot server."

@app.route("/callback", methods=["POST"])
def callback():
    # LINE からの署名検証
    signature = request.headers["X-Line-Signature"]

    # リクエストボディを取得
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # 署名を検証して、問題なければhandlerに処理を任せる
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return "OK"


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_text = event.message.text  # ユーザーが送ってきたメッセージ

    # PDFのテキストにユーザーのメッセージが含まれているかを単純に検索
    if user_text in PDF_TEXT:
        reply_text = "https://kig.jp/"
    else:
        reply_text = "ありません"

    # LINEに返答する
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text)
    )


if __name__ == "__main__":
    # ローカル実行用
    app.run(host="0.0.0.0", port=8000, debug=True)

