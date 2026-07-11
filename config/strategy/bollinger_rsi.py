# strategy/bollinger_rsi.py
import pandas as pd
import numpy as np
from config.settings import BB, RSI

class BollingerRSIStrategy:
    """
    استراتيجية Bollinger Bands + RSI للذهب والفضة
    """
    
    def __init__(self):
        self.bb_period = BB['period']
        self.bb_std = BB['std_dev']
        self.rsi_period = RSI['period']
        self.rsi_oversold = RSI['oversold']
        self.rsi_overbought = RSI['overbought']
        self.rsi_middle = RSI['middle']
        self.name = "Bollinger + RSI"
    
    def calculate_bollinger_bands(self, df):
        """حساب Bollinger Bands"""
        period = self.bb_period
        std_dev = self.bb_std
        
        df['bb_middle'] = df['close'].rolling(window=period).mean()
        std = df['close'].rolling(window=period).std()
        df['bb_upper'] = df['bb_middle'] + (std * std_dev)
        df['bb_lower'] = df['bb_middle'] - (std * std_dev)
        df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['bb_middle']
        df['percent_b'] = (df['close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])
        
        return df
    
    def calculate_rsi(self, df):
        """حساب RSI"""
        period = self.rsi_period
        delta = df['close'].diff()
        
        gain = delta.where(delta > 0, 0).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        return df
    
    def calculate_macd(self, df):
        """حساب MACD للتأكيد"""
        exp1 = df['close'].ewm(span=12).mean()
        exp2 = df['close'].ewm(span=26).mean()
        df['macd'] = exp1 - exp2
        df['macd_signal'] = df['macd'].ewm(span=9).mean()
        df['macd_histogram'] = df['macd'] - df['macd_signal']
        
        return df
    
    def calculate_atr(self, df):
        """حساب ATR"""
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = np.max(ranges, axis=1)
        df['atr'] = true_range.rolling(14).mean()
        
        return df
    
    def detect_trend(self, df):
        """تحديد الاتجاه العام"""
        sma_50 = df['close'].rolling(window=50).mean()
        sma_200 = df['close'].rolling(window=200).mean()
        
        trend = pd.Series('neutral', index=df.index)
        trend[(df['close'] > sma_50) & (sma_50 > sma_200)] = 'up'
        trend[(df['close'] < sma_50) & (sma_50 < sma_200)] = 'down'
        
        return trend
    
    def generate_signals(self, df):
        """توليد إشارات الشراء والبيع"""
        # حساب المؤشرات
        df = self.calculate_bollinger_bands(df)
        df = self.calculate_rsi(df)
        df = self.calculate_macd(df)
        df = self.calculate_atr(df)
        df['trend'] = self.detect_trend(df)
        
        # تهيئة الأعمدة
        df['signal'] = 0
        df['signal_reason'] = ''
        df['confidence'] = 0.0
        df['buy_signal'] = False
        df['sell_signal'] = False
        df['exit_signal'] = False
        
        for i in range(50, len(df)):
            price = df['close'].iloc[i]
            prev_price = df['close'].iloc[i-1]
            lower = df['bb_lower'].iloc[i]
            upper = df['bb_upper'].iloc[i]
            middle = df['bb_middle'].iloc[i]
            rsi_val = df['rsi'].iloc[i]
            trend_val = df['trend'].iloc[i]
            macd_hist = df['macd_histogram'].iloc[i]
            prev_macd_hist = df['macd_histogram'].iloc[i-1]
            bb_width = df['bb_width'].iloc[i]
            
            # إشارة شراء
            if ((prev_price <= lower) & (price > lower) and 
                rsi_val < self.rsi_oversold + 5 and 
                trend_val in ['up', 'neutral'] and 
                macd_hist > prev_macd_hist and 
                bb_width > 0.02):
                
                df.at[df.index[i], 'signal'] = 1
                df.at[df.index[i], 'buy_signal'] = True
                df.at[df.index[i], 'signal_reason'] = f"BB bounce + RSI({rsi_val:.1f}) + {trend_val}"
                
                # درجة الثقة
                rsi_factor = (self.rsi_oversold + 5 - rsi_val) / (self.rsi_oversold + 5)
                bb_factor = (lower - price) / lower if price < lower else 0.5
                confidence = min(100, (rsi_factor * 50 + bb_factor * 50) * 1.2)
                df.at[df.index[i], 'confidence'] = max(30, min(100, confidence))
            
            # إشارة بيع
            elif ((prev_price >= upper) & (price < upper) and 
                  rsi_val > self.rsi_overbought - 5 and 
                  trend_val in ['down', 'neutral'] and 
                  macd_hist < prev_macd_hist and 
                  bb_width > 0.02):
                
                df.at[df.index[i], 'signal'] = -1
                df.at[df.index[i], 'sell_signal'] = True
                df.at[df.index[i], 'signal_reason'] = f"BB reject + RSI({rsi_val:.1f}) + {trend_val}"
                
                # درجة الثقة
                rsi_factor = (rsi_val - (self.rsi_overbought - 5)) / (100 - (self.rsi_overbought - 5))
                bb_factor = (price - upper) / upper if price > upper else 0.5
                confidence = min(100, (rsi_factor * 50 + bb_factor * 50) * 1.2)
                df.at[df.index[i], 'confidence'] = max(30, min(100, confidence))
            
            # إشارة خروج
            if (price >= middle or rsi_val > self.rsi_middle + 10 or macd_hist < 0) and df['signal'].iloc[i-1] != 0:
                df.at[df.index[i], 'exit_signal'] = True
        
        return df

def generate_signals(df):
    """دالة سريعة لتوليد الإشارات"""
    strategy = BollingerRSIStrategy()
    return strategy.generate_signals(df)
