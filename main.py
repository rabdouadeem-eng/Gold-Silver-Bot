# 🤖 البوت الرئيسي
import time
import MetaTrader5 as mt5
from datetime import datetime

from config.settings import ACCOUNT, RISK, ALLOWED_SYMBOLS, TRADING
from data.fetcher import initialize_mt5, get_historical_data, get_current_price
from strategy.bollinger_rsi import generate_signals
from risk.position_sizer import calculate_lot_size
from risk.trailing_stop import calculate_atr, update_trailing_stop, modify_sl_on_mt5
from notifications.telegram_bot import (
    notify_trade_open, notify_trade_close, notify_trailing_update
)


class GoldSilverBot:
    def __init__(self):
        self.symbols = list(ALLOWED_SYMBOLS.keys())
        self.open_positions = {}
        
    def run(self):
        """تشغيل البوت"""
        print("=" * 50)
        print("🥇🥈 بوت التداول - الذهب والفضة")
        print(f"⚙️ الوضع الحالي: {TRADING['mode'].upper()}")
        print("=" * 50)
        
        if TRADING['mode'] == 'live':
            print("⚠️ تحذير: البوت في وضع التداول الحي (LIVE)!")
            print("⚠️ سيتم تنفيذ صفقات حقيقية بأموال حقيقية.")
        
        initialize_mt5()
        account_info = mt5.account_info()
        print(f"💰 الرصيد: ${account_info.balance:.2f}")
        print(f"📊 الرموز: {self.symbols}")
        
        while True:
            try:
                self.check_signals()
                self.update_trailing_stops()
                time.sleep(60)
                
            except KeyboardInterrupt:
                print("\n🛑 إيقاف البوت...")
                mt5.shutdown()
                break
            except Exception as e:
                print(f"❌ خطأ: {e}")
                time.sleep(30)
    
    def check_signals(self):
        """فحص الإشارات لجميع الرموز"""
        for symbol in self.symbols:
            try:
                df = get_historical_data(symbol, 'H1', 500)
                df = generate_signals(df)
                
                # استعمال آخر شمعة مكتملة (index -2)، ماشي الشمعة الجارية (-1)
                latest = df.iloc[-2]
                signal = latest['signal']
                
                if signal != 0 and symbol not in self.open_positions:
                    self.open_trade(symbol, signal, latest, df)
                    
            except Exception as e:
                print(f"❌ خطأ في فحص {symbol}: {e}")
    
    def open_trade(self, symbol: str, signal: int, data, df):
        """فتح صفقة"""
        account_info = mt5.account_info()
        balance = account_info.balance
        
        price_info = get_current_price(symbol)
        entry = price_info['ask'] if signal == 1 else price_info['bid']
        
        # ✅ ATR الحقيقي (بدل BB width الخاطئة)
        atr = calculate_atr(df)
        sl_distance = atr * 1.5
        tp_distance = atr * 2.5
        
        if signal == 1:
            sl = entry - sl_distance
            tp = entry + tp_distance
            order_type = mt5.ORDER_TYPE_BUY
        else:
            sl = entry + sl_distance
            tp = entry - tp_distance
            order_type = mt5.ORDER_TYPE_SELL
        
        lot = calculate_lot_size(symbol, entry, sl, balance)
        
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": lot,
            "type": order_type,
            "price": entry,
            "sl": sl,
            "tp": tp,
            "magic": TRADING['magic_number'],
            "comment": "GoldSilver Bot",
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        result = mt5.order_send(request)
        
        if result is None:
            print(f"❌ فشل إرسال الأمر لـ {symbol}: لا يوجد رد من MT5")
            return
        
        if result.retcode == mt5.TRADE_RETCODE_DONE:
            self.open_positions[symbol] = result.order
            notify_trade_open(
                symbol, 
                'buy' if signal == 1 else 'sell',
                entry, sl, tp, lot
            )
            print(f"✅ تم فتح صفقة {symbol} @ {entry}")
        else:
            print(f"❌ فشل فتح الصفقة: {result.comment}")
    
    def update_trailing_stops(self):
        """تحديث Trailing Stop للصفقات المفتوحة"""
        for symbol, ticket in list(self.open_positions.items()):
            try:
                positions = mt5.positions_get(symbol=symbol)
                if not positions:
                    del self.open_positions[symbol]
                    continue
                
                pos = positions[0]
                df = get_historical_data(symbol, 'H1', 100)
                atr = calculate_atr(df)
                
                price_info = get_current_price(symbol)
                current_price = price_info['bid'] if pos.type == 0 else price_info['ask']
                
                order_type = 'buy' if pos.type == 0 else 'sell'
                new_sl = update_trailing_stop(
                    symbol, order_type, pos.sl, current_price, atr
                )
                
                if new_sl != pos.sl:
                    if modify_sl_on_mt5(symbol, ticket, new_sl):
                        notify_trailing_update(symbol, pos.sl, new_sl)
                        
            except Exception as e:
                print(f"❌ خطأ في trailing stop: {e}")


if __name__ == "__main__":
    bot = GoldSilverBot()
    bot.run()
