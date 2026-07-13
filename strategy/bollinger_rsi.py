# 📊 استراتيجية Bollinger Bands + RSI
import pandas as pd
import numpy as np
from config.settings import BB, RSI


def calculate_bollinger_bands(df: pd.DataFrame) -> pd.DataFrame:
    """حساب Bollinger Bands"""
    period = BB['period']
    std_dev = BB['std_dev']
    
    df['bb_middle'] = df['close'].rolling(window=period).mean()
    std = df['close'].rolling(window=period).std()
    df['bb_upper'] = df['bb_middle'] + (std * std_dev)
    df['bb_lower'] = df['bb_middle'] - (std * std_dev)
    df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['bb_middle']
    
    return df


def calculate_rsi(df: pd.DataFrame) -> pd.DataFrame:
    """حساب RSI"""
    period = RSI['period']
    delta = df['close'].diff()
    
    gain = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))
    
    return df


def detect_trend(df: pd.DataFrame) -> pd.Series:
    """تحديد الاتجاه العام"""
    sma_50 = df['close'].rolling(window=50).mean()
    sma_200 = df['close'].rolling(window=200).mean()
    
    trend = pd.Series('neutral', index=df.index)
    trend[(df['close'] > sma_50) & (sma_50 > sma_200)] = 'up'
    trend[(df['close'] < sma_50) & (sma_50 < sma_200)] = 'down'
    
    return trend


def generate_signals(df: pd.DataFrame) -> pd.DataFrame:
    """
    منطق الإشارات:
    - شراء: السعر يلامس BB السفلي + RSI < 35 + اتجاه صاعد
    - بيع: السعر يلامس BB العلوي + RSI > 65 + اتجاه هابط
    """
    df = calculate_bollinger_bands(df)
    df = calculate_rsi(df)
    df['trend'] = detect_trend(df)
    
    df['signal'] = 0
    df['signal_reason'] = ''
    
    for i in range(1, len(df)):
        price = df['close'].iloc[i]
        prev_price = df['close'].iloc[i-1]
        lower = df['bb_lower'].iloc[i]
        upper = df['bb_upper'].iloc[i]
        rsi_val = df['rsi'].iloc[i]
        trend_val = df['trend'].iloc[i]
        
        if (prev_price <= lower and price > lower and 
            rsi_val < 35 and trend_val == 'up'):
            df.at[df.index[i], 'signal'] = 1
            df.at[df.index[i], 'signal_reason'] = 'BB bounce + RSI oversold + Uptrend'
        
        elif (prev_price >= upper and price < upper and 
              rsi_val > 65 and trend_val == 'down'):
            df.at[df.index[i], 'signal'] = -1
            df.at[df.index[i], 'signal_reason'] = 'BB reject + RSI overbought + Downtrend'
    
    return df
