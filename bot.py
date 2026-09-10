import requests
import datetime
import os
from flask import Flask, request

BOT_TOKEN = os.environ.get('BOT_TOKEN')
API_KEY = os.environ.get('API_KEY')

app = Flask(__name__)

# ⬇️ آیدی کانال/پیج تو (هر وقت خواستی عوضش کنی فقط همین جا رو تغییر بده)
CHANNEL = '@AlphaTreadrs'

METALS = {
    'get_gold':   {'symbol': 'XAU/USD', 'short': 'XAU', 'emoji': '🥇', 'name': 'XAU/USD'},
    'get_silver': {'symbol': 'XAG/USD', 'short': 'XAG', 'emoji': '🥈', 'name': 'XAG/USD'},
}

def fetch_price(symbol, short):
    err = None

    # منبع ۱: TwelveData
    try:
        url = f"https://api.twelvedata.com/price?symbol={symbol}&apikey={API_KEY}"
        data = requests.get(url, timeout=10).json()
        if "price" in data:
            return float(data["price"]), None
        err = data.get("message", "price not found")
    except Exception as e:
        err = str(e)

    # منبع ۲ (زاپاس رایگان): gold-api.com
    try:
        data = requests.get(f"https://api.gold-api.com/price/{short}", timeout=10).json()
        if "price" in data:
            return float(data["price"]), None
    except Exception:
        pass

    # منبع ۳ (زاپاس رایگان): goldprice.org
    try:
        data = requests.get(
            "https://data-asg.goldprice.org/dbXRates/USD",
            timeout=10,
            headers={"User-Agent": "Mozilla/5.0"}
        ).json()
        item = data["items"][0]
        price = item.get("xauPrice") if short == "XAU" else item.get("xagPrice")
        if price:
            return float(price), None
    except Exception:
        pass

    return None, err

@app.route('/webhook', methods=['POST'])
def webhook():
    update = request.get_json()

    if 'callback_query' in update:
        query = update['callback_query']
        chat_id = query['message']['chat']['id']
        message_id = query['message']['message_id']
        key = query['data']

        if key not in METALS:
            return 'ok'

        m = METALS[key]
        price, err = fetch_price(m['symbol'], m['short'])

        if price is not None:
            formatted = f"{price:,.2f}"
            now = datetime.datetime.now().strftime("%H:%M:%S")
            text = (
                f"{m['emoji']} {m['name']}\n"
                f"💵 {formatted} USD\n"
                f"🕐 {now}\n\n"
                f"📢 {CHANNEL}"
            )
        else:
            text = f"❌ خطا در دریافت قیمت\n📛 دلیل: {err}\n\n📢 {CHANNEL}"

        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageText", json={
            "chat_id": chat_id,
            "message_id": message_id,
            "text": text
        })

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
            "text": f"سلام! 👋\nلطفاً یکی از گزینه‌ها رو انتخاب کن:\n\n📢 {CHANNEL}",
            "reply_markup": keyboard
        })

    return 'ok'

@app.route('/')
def index():
    return 'ربات فعال است ✅'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
