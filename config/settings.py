# ⚙️ الإعدادات الرئيسية
import os
from dotenv import load_dotenv

load_dotenv()

# ============ الحساب ============
ACCOUNT = {
    'balance': 10000,
    'currency': 'USD',
    'leverage': 100,
}

# ============ المخاطر ============
RISK = {
    'risk_per_trade': 0.02,
    'max_daily_loss': 0.06,
    'max_open_trades': 2,
    'trailing_stop_atr_mult': 1.5,
    'atr_period': 14,
}

# ============ الرموز المسموحة ============
ALLOWED_SYMBOLS = {
    'XAUUSD': {
        'name': 'Gold',
        'pip_value': 0.1,
        'min_lot': 0.01,
        'max_lot': 5.0,
    },
    'XAGUSD': {
        'name': 'Silver',
        'pip_value': 0.01,
        'min_lot': 0.01,
        'max_lot': 10.0,
    }
}

# ============ Bollinger Bands ============
BB = {
    'period': 20,
    'std_dev': 2.0,
}

# ============ RSI ============
RSI = {
    'period': 14,
    'overbought': 70,
    'oversold': 30,
    'middle': 50,
}

# ============ Timeframes ============
TIMEFRAMES = {
    'primary': 'H1',
    'confirm': 'H4',
    'trend': 'D1',
}

# ============ Telegram ============
TELEGRAM = {
    'bot_token': os.getenv('TELEGRAM_BOT_TOKEN'),
    'chat_id': os.getenv('TELEGRAM_CHAT_ID'),
    'enabled': True,
}

# ============ التداول ============
# ⚠️ مهم جداً: خلّي القيمة 'paper' إلى أن تختبر البوت بعناية كافية
# لا تبدلها لـ 'live' إلا بعد أسابيع من الاختبار الناجح على حساب Demo
TRADING = {
    'mode': 'paper',            # 'live' أو 'backtest' أو 'paper'
    'magic_number': 234000,
    'slippage': 3,
}
