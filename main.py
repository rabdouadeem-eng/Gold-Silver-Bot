# main.py
import time
import MetaTrader5 as mt5
from datetime import datetime
from config.settings import ACCOUNT, RISK, ALLOWED_SYMBOLS, TRADING

print("=" * 50)
print("🥇🥈 بوت التداول - الذهب والفضة")
print("=" * 50)

# تهيئة MT5
if not mt5.initialize():
    print(f"❌ فشل تهيئة MT5: {mt5.last_error()}")
else:
    print("✅ تم الاتصال بـ MetaTrader 5")
    account_info = mt5.account_info()
    if account_info:
        print(f"💰 الرصيد: ${account_info.balance:.2f}")
        print(f"📊 الرموز: {list(ALLOWED_SYMBOLS.keys())}")

print("\n✅ البوت جاهز للتشغيل!")
print("⚠️ هذا هو إصدار اختبار بسيط للتحقق من الاتصال")
