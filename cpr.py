import pandas as pd
import numpy as np
import talib

def calculate_pivot_levels(df):
    """Calculate Pivot Points and related support/resistance levels"""
    high = df['High']
    low = df['Low']
    close = df['Close']
    
    # Pivot Point (PP)
    df['PP'] = (high + low + close) / 3
    
    # Top Central Pivot (TC) and Bottom Central Pivot (BC)
    df['TC'] = (high + low) / 2
    df['BC'] = (low + close) / 2
    
    # Resistance and Support Levels
    df['R1'] = (2 * df['PP']) - df['Low']
    df['S1'] = (2 * df['PP']) - df['High']
    df['R2'] = df['PP'] + (df['High'] - df['Low'])
    df['S2'] = df['PP'] - (df['High'] - df['Low'])
    
    return df

def identify_market_trend(df):
    """Identify market trend based on pivot point and closing price"""
    if df['Close'].iloc[-1] > df['PP'].iloc[-1]:
        return 'bullish'
    elif df['Close'].iloc[-1] < df['PP'].iloc[-1]:
        return 'bearish'
    else:
        return 'neutral'

def entry_signal(df, market_trend):
    """Generate entry signals based on market trend and pivot levels"""
    if market_trend == 'bullish':
        if df['Close'].iloc[-1] > df['R1'].iloc[-1]:  # Break above resistance
            return 'long'
        elif df['Close'].iloc[-1] > df['PP'].iloc[-1] and df['Close'].iloc[-2] < df['PP'].iloc[-2]:  # Support bounce
            return 'long'
    elif market_trend == 'bearish':
        if df['Close'].iloc[-1] < df['S1'].iloc[-1]:  # Break below support
            return 'short'
        elif df['Close'].iloc[-1] < df['PP'].iloc[-1] and df['Close'].iloc[-2] > df['PP'].iloc[-2]:  # Resistance rejection
            return 'short'
    return None

def exit_signal(df, position_type):
    """Generate exit signals based on market action and pivot levels"""
    if position_type == 'long':
        if df['Close'].iloc[-1] >= df['R2'].iloc[-1]:  # Target reached at R2
            return 'exit'
        elif df['Close'].iloc[-1] <= df['S1'].iloc[-1]:  # Stop loss if below S1
            return 'exit'
    elif position_type == 'short':
        if df['Close'].iloc[-1] <= df['S2'].iloc[-1]:  # Target reached at S2
            return 'exit'
        elif df['Close'].iloc[-1] >= df['R1'].iloc[-1]:  # Stop loss if above R1
            return 'exit'
    return None

def apply_rsi(df, period=14):
    """Calculate RSI for momentum confirmation"""
    df['RSI'] = talib.RSI(df['Close'], timeperiod=period)
    return df

def backtest_strategy(df):
    """Backtest the strategy based on entry/exit rules"""
    df = calculate_pivot_levels(df)
    df = apply_rsi(df)  # Adding RSI for confirmation
    
    position = None  # Track position (None, 'long', 'short')
    entry_price = None
    for i in range(1, len(df)):
        market_trend = identify_market_trend(df.iloc[:i+1])
        signal = entry_signal(df.iloc[:i+1], market_trend)
        
        # Enter trade
        if signal == 'long' and position != 'long':
            position = 'long'
            entry_price = df['Close'].iloc[i]
            print(f"Long entry at {entry_price} on {df.index[i]}")
        
        elif signal == 'short' and position != 'short':
            position = 'short'
            entry_price = df['Close'].iloc[i]
            print(f"Short entry at {entry_price} on {df.index[i]}")
        
        # Exit trade
        if position == 'long':
            exit_signal_result = exit_signal(df.iloc[:i+1], position)
            if exit_signal_result == 'exit':
                exit_price = df['Close'].iloc[i]
                print(f"Long exit at {exit_price} on {df.index[i]}")
                position = None
        
        elif position == 'short':
            exit_signal_result = exit_signal(df.iloc[:i+1], position)
            if exit_signal_result == 'exit':
                exit_price = df['Close'].iloc[i]
                print(f"Short exit at {exit_price} on {df.index[i]}")
                position = None
    print(df)
    return df

# Example: Sample data for testing (you would typically load data from a CSV or API)
data = {
    'Date': pd.date_range(start='2023-01-01', periods=10, freq='D'),
    'High': [150, 155, 160, 162, 161, 165, 167, 166, 170, 172],
    'Low': [145, 150, 155, 158, 157, 159, 161, 160, 165, 168],
    'Close': [148, 153, 158, 160, 159, 163, 165, 164, 169, 171],
}

# Convert to DataFrame
df = pd.DataFrame(data)
df.set_index('Date', inplace=True)

# Run the backtest
backtest_strategy(df)
