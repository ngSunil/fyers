import pandas as pd
from fyers_apiv3 import fyersModel
import datetime as dt
import pytz


#generate trading session
client_id = open("client_id.txt",'r').read()
access_token = open("access_token.txt",'r').read()

# Initialize the FyersModel instance with your client_id, access_token, and enable async mode
fyers = fyersModel.FyersModel(client_id=client_id, is_async=False, token=access_token, log_path="")

def fetchOHLC2(ticker,interval,duration):
    range_from = dt.date.today()-dt.timedelta(duration)
    range_to = dt.date.today()

    from_date_string = range_from.strftime("%Y-%m-%d")
    to_date_string = range_to.strftime("%Y-%m-%d")
    data = {
        "symbol":ticker,
        "resolution":interval,
        "date_format":"1",
        "range_from":from_date_string,
        "range_to":to_date_string,
        "cont_flag":"1"
    }

    response = fyers.history(data=data)['candles']

    # Create a DataFrame
    columns = ['Timestamp','Open','High','Low','Close','Volume']
    df = pd.DataFrame(response, columns=columns)

    # Convert Timestamp to datetime in UTC
    df['Timestamp2'] = pd.to_datetime(df['Timestamp'],unit='s').dt.tz_localize(pytz.utc)

    # Convert Timestamp to IST
    ist = pytz.timezone('Asia/Kolkata')
    df['Timestamp2'] = df['Timestamp2'].dt.tz_convert(ist)
    df.drop(columns=['Timestamp'], inplace=True)

    return (df)



def doji(ohlc_df):
    """returns dataframe with doji candle column"""
    df = ohlc_df.copy()

    # Initialize an empty list to store the Doji values
    doji_values = []

    # Iterate through rows and perform the comparison
    for index, row in df.iterrows():
        if abs(row["Open"] - row["Close"]) <= 0.1 * (row['High'] - row['Low']):
            doji_values.append(True)
        else:
            doji_values.append(False)

    # Create a new 'doji' column in the DataFrame
    df["Doji"] = doji_values

    return df

# Fetch OHLC data using the function
response_df = fetchOHLC2("NSE:SBIN-EQ","30",5)
doji_df = doji(response_df)
print(doji_df)