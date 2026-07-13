# 📥 جلب البيانات
import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime, timedelta
from config.settings import ALLOWED_SYMBOLS, TIMEFRAMES


def initialize_mt5():
    """تهيئة MT5"""
    if not mt5.initialize():
        raise Exception(f"❌ فشل تهيئة MT5: {mt5.last_error()}")
    print("✅ تم الاتصال بـ MetaTrader 5")


def get_historical_data(symbol: str, timeframe: str = 'H1', 
                       bars: int = 1000) -> pd.DataFrame:
    """جلب البيانات التاريخية"""
    if symbol not in ALLOWED_SYMBOLS:
        raise ValueError(f"❌ الرمز {symbol} غير مسموح!")
    
    tf_map = {
        'M1': mt5.TIMEFRAME_M1,
        'M5': mt5.TIMEFRAME_M5,
        'M15': mt5.TIMEFRAME_M15,
        'M30': mt5.TIMEFRAME_M30,
        'H1': mt5.TIMEFRAME_H1,
        'H4': mt5.TIMEFRAME_H4,
        'D1': mt5.TIMEFRAME_D1,
    }
    
    rates = mt5.copy_rates_from_pos(symbol, tf_map[timeframe], 0, bars)
    if rates is None or len(rates) == 0:
        raise Exception(f"❌ لا توجد بيانات للرمز {symbol}")
    
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    df.set_index('time', inplace=True)
    
    return df


def get_current_price(symbol: str) -> dict:
    """جلب السعر الحالي"""
    tick = mt5.symbol_info_tick(symbol)
    if tick is None:
        raise Exception(f"❌ لا يمكن جلب السعر لـ {symbol}")
    
    return {
        'bid': tick.bid,
        'ask': tick.ask,
        'spread': tick.ask - tick.bid
  }
