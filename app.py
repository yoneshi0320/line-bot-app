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

# ==== 環境変数から読み込む（Render/Herokuなどで設定）====
CHANNEL_ACCESS_TOKEN = os.getenv("CHANNEL_ACCESS_TOKEN", "YOUR_ACCESS_TOKEN")
CHANNEL_SECRET = os.getenv("CHANNEL_SECRET", "YOUR_CHANNEL_SECRET")

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

# ==== PDFテキストをまとめて読み込んでおく ====
PDF_TEXT = ""
PDF_FILE_PATH = "manual.pdf"  # 例: 同じフォルダに manual.pdf がある前提

try:
    with pdfplumber.open(PDF_FILE_PATH) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                PDF_TEXT += page_text
except Exception as e:
    print(f"PDF読み込みエラー: {e}")
    # 失敗した場合、PDF_TEXT は空のままにしておく or ログなどに書いておく


@app.route("/")
def health_check():
    # デプロイ先のヘルスチェックやブラウザ確認用に "OK" を返す
    return "Hello! This is LINE Bot server."


@app.route("/callback", methods=["POST"])
def callback():
    # 1. LINE 署名の取得
    signature = request.headers.get("X-Line-Signature")
    if signature is None:
        # 署名がついていない → 不正リクエストとして 400 を返す
        abort(400, "Missing X-Line-Signature header.")

    # 2. リクエストボディの取得
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # 3. 署名検証
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        # 署名が一致しない場合は 400
        abort(400, "Invalid signature. Please check your channel secret.")

    # 4. 正常処理できた場合は 200 OK を返す
    return "OK", 200


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    """
    ユーザーがテキストメッセージを送ったときに呼び出される関数。
    - PDF_TEXT内にユーザーのメッセージが含まれていれば、 https://kig.jp/ を返す。
    - 含まれていなければ「ありません」を返す。
    """
    user_text = event.message.text  # ユーザーからのメッセージ

    if user_text in PDF_TEXT:
        reply_text = "https://kig.jp/"
    else:
        reply_text = "ありません"

    # LINEにメッセージを返信
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text)
    )


if __name__ == "__main__":
    # ローカル実行のテスト用
    app.run(port=8000, debug=True)
