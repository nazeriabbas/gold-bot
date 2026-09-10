import requests
import datetime
import os
from flask import Flask, request

BOT_TOKEN = os.environ.get('BOT_TOKEN')
API_KEY = os.environ.get('API_KEY')

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    update = request.get_json()

    # اگه دکمه زده شد
    if 'callback_query' in update:
        query = update['callback_query']
        chat_id = query['message']['chat']['id']
        message_id = query['message']['message_id']
        data_clicked = query['data']  # get_gold یا get_silver

        # انتخاب نماد بر اساس دکمه‌ای که زده شده
        if data_clicked == 'get_gold':
            symbol = 'XAU/USD'
            emoji = '🥇'
            name = 'XAU/USD'
        elif data_clicked == 'get_silver':
            symbol = 'XAG/USD'
            emoji = '🥈'
            name = 'XAG/USD'
        else:
            return 'ok'

        url = f"https://api.twelvedata.com/price?symbol={symbol}&apikey={API_KEY}"
        try:
            data = requests.get(url).json()
            price = float(data["price"])
            formatted = f"{price:,.2f}"
            now = datetime.datetime.now().strftime("%H:%M:%S")

            text = f"{emoji} {name}\n💵 {formatted} USD\n🕐 {now}"
        except:
            text = "❌ خطا در دریافت قیمت"

        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageText", json={
            "chat_id": chat_id,
            "message_id": message_id,
            "text": text
        })

    # اگه /start فرستاده شد
    elif 'message' in update:
        chat_id = update['message']['chat']['id']
        keyboard = {
            "inline_keyboard": [[
                {"text": "🥇 قیمت طلا", "callback_data": "get_gold"},
                {"text": "🥈 قیمت نقره", "callback_data": "get_silver"}
            ]]
        }
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json={
            "chat_id": chat_id,
            "text": "سلام! 👋\nلطفاً یکی از گزینه‌ها رو انتخاب کن:",
            "reply_markup": keyboard
        })

    return 'ok'

@app.route('/')
def index():
    return 'ربات فعال است ✅'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
