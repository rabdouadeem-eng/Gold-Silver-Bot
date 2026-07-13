# 📈 إدارة Trailing Stop
import pandas as pd
import MetaTrader5 as mt5
from config.settings import RISK


def calculate_atr(df, period: int = None) -> float:
    """حساب ATR لتحديد Trailing Stop"""
    period = period or RISK['atr_period']
    
    high = df['high']
    low = df['low']
    close = df['close'].shift(1)
    
    tr1 = high - low
    tr2 = (high - close).abs()
    tr3 = (low - close).abs()
    
    tr = pd.DataFrame({'tr1': tr1, 'tr2': tr2, 'tr3': tr3}).max(axis=1)
    atr = tr.rolling(window=period).mean().iloc[-1]
    
    return atr


def update_trailing_stop(symbol: str, order_type: str, current_sl: float, 
                         current_price: float, atr_value: float) -> float:
    """
    تحديث Trailing Stop
    - للشراء: SL يتحرك للأعلى فقط
    - للبيع: SL يتحرك للأسفل فقط
    """
    new_sl = current_sl
    trailing_distance = atr_value * RISK['trailing_stop_atr_mult']
    
    if order_type == 'buy':
        potential_sl = current_price - trailing_distance
        if potential_sl > current_sl:
            new_sl = potential_sl
    
    elif order_type == 'sell':
        potential_sl = current_price + trailing_distance
        if potential_sl < current_sl:
            new_sl = potential_sl
    
    return round(new_sl, 2)


def modify_sl_on_mt5(symbol: str, ticket: int, new_sl: float) -> bool:
    """تعديل SL على MT5"""
    positions = mt5.positions_get(symbol=symbol)
    if not positions:
        return False
    
    for pos in positions:
        if pos.ticket == ticket:
            request = {
                "action": mt5.TRADE_ACTION_SLTP,
                "position": ticket,
                "sl": new_sl,
                "tp": pos.tp,
            }
            result = mt5.order_send(request)
            
            if result is None:
                print(f"❌ فشل تعديل SL لـ {symbol}: لا يوجد رد من MT5")
                return False
            
            return result.retcode == mt5.TRADE_RETCODE_DONE
    
    return False
