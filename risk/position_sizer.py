# 💰 حساب حجم الصفقة بناءً على المخاطرة
import MetaTrader5 as mt5
from config.settings import RISK, ALLOWED_SYMBOLS


def calculate_lot_size(symbol: str, entry: float, sl: float, balance: float) -> float:
    """
    حساب حجم اللوت بحيث لا تتجاوز المخاطرة 2% من الرصيد
    """
    if symbol not in ALLOWED_SYMBOLS:
        raise ValueError(f"الرمز {symbol} غير مسموح! فقط الذهب والفضة.")
    
    risk_amount = balance * RISK['risk_per_trade']
    sl_distance = abs(entry - sl)
    
    if sl_distance == 0:
        return ALLOWED_SYMBOLS[symbol]['min_lot']
    
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None:
        return ALLOWED_SYMBOLS[symbol]['min_lot']
    
    tick_value = symbol_info.trade_tick_value
    tick_size = symbol_info.trade_tick_size
    
    lot_size = risk_amount / (sl_distance / tick_size * tick_value)
    
    min_lot = ALLOWED_SYMBOLS[symbol]['min_lot']
    max_lot = ALLOWED_SYMBOLS[symbol]['max_lot']
    
    lot_size = max(min_lot, min(lot_size, max_lot))
    lot_size = round(lot_size, 2)
    
    return lot_size
