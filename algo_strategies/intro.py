import pandas as pd
import pandas_ta as ta
df = pd.read_csv('output.csv')
df['EMA'] = ta.ema(df.Close, length=10)
print(df)
