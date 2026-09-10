import requests
import datetime
import os
from flask import Flask, request, jsonify

import os
BOT_TOKEN = os.environ.get('BOT_TOKEN')
API_KEY = os.environ.get('API_KEY')

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    update = request.get_json()

    if 'callback_query' in update:
        query = update['callback_query']
        chat_id = query['message']['chat']['id']
        message_id = query['message']['message_id']

        # دریافت قیمت طلا
        url = f"https://api.twelvedata.com/price?symbol=XAU/USD&apikey={API_KEY}"
        try:
            data = requests.get(url).json()
            price = float(data["price"])
            formatted = f"{price:,.2f}"
            now = datetime.datetime.now().strftime("%H:%M:%S")

            text = f"🥇 XAU/USD\n💵 {formatted} USD\n🕐 {now}"
        except:
            text = "❌ خطا در دریافت قیمت"

        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageText", json={
            "chat_id": chat_id,
            "message_id": message_id,
            "text": text
        })

    elif 'message' in update:
        chat_id = update['message']['chat']['id']

        keyboard = {
            "inline_keyboard": [[
                {"text": "📊 دریافت قیمت طلا", "callback_data": "get_price"}
            ]]
        }

        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json={
            "chat_id": chat_id,
            "text": "سلام! 👋\nبرای دریافت قیمت طلا دکمه رو بزن:",
            "reply_markup": keyboard
        })

    return 'ok'

@app.route('/')
def index():
    return 'ربات فعال است ✅'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
