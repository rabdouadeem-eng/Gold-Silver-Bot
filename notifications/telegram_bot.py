# 📲 تنبيهات تيليجرام
import datetime
import requests
from config.settings import TELEGRAM


def send_telegram(message: str, parse_mode: str = 'HTML') -> bool:
    """إرسال رسالة إلى تيليجرام"""
    if not TELEGRAM['enabled'] or not TELEGRAM['bot_token']:
        print(f"📲 [Telegram Disabled] {message}")
        return False
    
    url = f"https://api.telegram.org/bot{TELEGRAM['bot_token']}/sendMessage"
    payload = {
        'chat_id': TELEGRAM['chat_id'],
        'text': message,
        'parse_mode': parse_mode
    }
    
    try:
        response = requests.post(url, data=payload, timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Telegram Error: {e}")
        return False


def notify_trade_open(symbol: str, order_type: str, price: float, 
                      sl: float, tp: float, lot: float):
    """إشعار فتح صفقة"""
    emoji = "🟢" if order_type == "buy" else "🔴"
    msg = (
        f"{emoji} <b>صفقة جديدة - {order_type.upper()}</b>\n"
        f"━━━━━━━━━━━━━━━\n"
        f"📊 الرمز: <code>{symbol}</code>\n"
        f"💰 السعر: <code>{price}</code>\n"
        f"🛑 Stop Loss: <code>{sl}</code>\n"
        f"🎯 Take Profit: <code>{tp}</code>\n"
        f"📦 حجم اللوت: <code>{lot}</code>\n"
        f"⏰ {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}"
    )
    send_telegram(msg)


def notify_trade_close(symbol: str, order_type: str, open_price: float,
                       close_price: float, profit: float):
    """إشعار إغلاق صفقة"""
    emoji = "✅" if profit > 0 else "❌"
    msg = (
        f"{emoji} <b>إغلاق صفقة</b>\n"
        f"━━━━━━━━━━━━━━━\n"
        f"📊 الرمز: <code>{symbol}</code>\n"
        f"📈 النوع: {order_type.upper()}\n"
        f"💵 فتح: <code>{open_price}</code>\n"
        f"💵 إغلاق: <code>{close_price}</code>\n"
        f"💸 الربح/الخسارة: <code>${profit:.2f}</code>"
    )
    send_telegram(msg)


def notify_trailing_update(symbol: str, old_sl: float, new_sl: float):
    """إشعار تحديث Trailing Stop"""
    msg = (
        f"🔄 <b>تحديث Trailing Stop</b>\n"
        f"📊 <code>{symbol}</code>\n"
        f"🛑 SL القديم: <code>{old_sl}</code>\n"
        f"🛡️ SL الجديد: <code>{new_sl}</code>"
    )
    send_telegram(msg)
