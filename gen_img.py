import argparse
import os
import sys
import pandas as pd
from BinanceClient import get_data
import datetime as dt
import time
import numpy as np
import talib
from talib import MA_Type
import matplotlib.pyplot as plt



module_path = os.path.abspath(os.path.join('../..'))
if module_path not in sys.path:
    print(module_path)
    sys.path.append(module_path)


arguments = argparse.ArgumentParser()

arguments.add_argument("-d", "--date", required=False, help="start date (yyyy-mm-dd)")
arguments.add_argument("-c", "--instrument", required=False, help="cryptocurrency (BTC, ETH, ...)")
arguments.add_argument("-t", "--interval", required=False, help="interval in minutes")
arguments.add_argument("-p", "--period", required=False, help="period (for indicators)")


#ap.add_argument("-b", "--soperand", required=True, help="second operand")
args = vars(arguments.parse_args())

start_date = dt.datetime(2020,1,1,0,0,0)
arg_date = args['date']
if not arg_date is None:
    year = int(arg_date.split("-")[0])
    month = int(arg_date.split("-")[1])
    day = int(arg_date.split("-")[2])
    start_date = dt.datetime(year,month,day,0,0,0)

instrument = "BTCUSDT"
arg_instrument = args['instrument']
if not arg_instrument is None:
    instrument = arg_instrument + "USDT"


print("instrument: ", instrument, " start date: ", start_date)

influxclient = InfluxClient(host=InfluxConfig.host,
                            port=InfluxConfig.port,
                            user=InfluxConfig.user,
                            pswd=InfluxConfig.pswd,
                            dtbs=InfluxConfig.dtbs)


kline_df = influxclient.get_klines_since(
        instrument=instrument,
        start_date=start_date)


interval = 5
arg_interval = args['interval']
if not arg_interval is None:
    interval = int(arg_interval)

kline_df = kline_df.iloc[::interval, :]

period = 50
arg_period = args['period']
if not arg_period is None:
    period = int(arg_period)

upper, middle, lower = talib.BBANDS(
            kline_df.close,
            timeperiod=period,
            nbdevup=3,
            nbdevdn=2,
            matype=0
        )

kline_df["upper_BB"] = upper
kline_df["lower_BB"] = lower
kline_df["middle_BB"] = middle

kline_df["ma"] = talib.EMA(kline_df["close"], timeperiod=period)

kline_df['ADX0'] = talib.ADX(
        kline_df.high,
        kline_df.low,
        kline_df.close,
        timeperiod=period #20
    )

kline_df['ATR0'] = talib.ATR(
    kline_df.high,
    kline_df.low,
    kline_df.close,
    timeperiod=period
)

kline_df['ARO0'] = talib.AROONOSC(
high=kline_df.high,
low=kline_df.low,
timeperiod=period
)

kline_df['WLR0'] = talib.WILLR(
    kline_df.high,
    kline_df.low,
    kline_df.close,
    timeperiod=period
)

kline_df = kline_df.dropna()
image_data = {}

for column in ['close', 'upper_BB', 'lower_BB', 'middle_BB', 'ma', 'ADX0','ATR0', 'ARO0', 'WLR0']:
    ml_df = pd.DataFrame()
    for i in range(-1, 40):
      ml_df[f"t_{i}"] = kline_df[column].shift(i)
    ml_df = ml_df.dropna().astype('float32')
    image_data[column] = ml_df

ready = set(os.listdir("images/"+ str(period)))

def generate_image(row, name = "images/plot.png"):
    fig = plt.figure(figsize = (20,20))
    rev_row = np.flip(np.array(row)[1:]) #1: only input
    plt.plot(rev_row, 'k', linewidth=15.0)
    plt.axis('off')
    plt.show()
    fig.savefig(name, dpi = 3)
    plt.close(fig)

df1 = image_data['upper_BB']
df2 = image_data['lower_BB']
df3 = image_data['middle_BB']
for row1, row2, row3 in zip(df1.iloc, df2.iloc, df3.iloc):
    name = "images/"+ str(period) + "/" + row1.name[:16] + ";" + "BB" + ".png"
    if row1.name[:16] + ";" + "BB" + ".png" in ready:
        continue
    fig = plt.figure(figsize = (20,20))
    rev_row = np.flip(np.array(row1)[1:]) 
    plt.plot(rev_row, 'r', linewidth=15.0)
    plt.axis('off')
    rev_row = np.flip(np.array(row2)[1:]) 
    plt.plot(rev_row, 'g', linewidth=15.0)
    plt.axis('off')
    rev_row = np.flip(np.array(row3)[1:]) 
    plt.plot(rev_row, 'b', linewidth=15.0)
    plt.axis('off')
    plt.show()
    fig.savefig(name, dpi = 3)
    plt.close(fig)

ratios = []
for col_name in ['close', 'ma', 'ADX0','ATR0', 'ARO0', 'WLR0']:    
    df = image_data[col_name]
    
    for row in df.iloc:
        if row.name[:16] + ";" + col_name + ".png" in ready:
            continue
        generate_image(row, "images/"+ str(period) + "/" + row.name[:16] + ";" + col_name + ".png")
