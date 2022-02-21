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
import gc 



module_path = os.path.abspath(os.path.join('../..'))
if module_path not in sys.path:
    print(module_path)
    sys.path.append(module_path)


arguments = argparse.ArgumentParser()

arguments.add_argument("-d", "--date", required=False, help="start date (yyyy-mm-dd)")
arguments.add_argument("-c", "--instrument", required=False, help="cryptocurrency (BTC, ETH, ...)")
arguments.add_argument("-t", "--interval", required=False, help="interval (1m,3m,5m,15m,30m,1h,2h,4h) default - 5minutes")
arguments.add_argument("-p", "--period", required=False, help="period (for indicators)")
arguments.add_argument("-i", "--indicator", required=False, help="specyfied indicator ('BB', 'close', ma', 'ADX0','ATR0', 'ARO0', 'WLR0')")


#ap.add_argument("-b", "--soperand", required=True, help="second operand")
args = vars(arguments.parse_args())

start_date = dt.datetime(2020,1,1,0,0,0)
arg_date = args['date']
if not arg_date is None:
    year = int(arg_date.split("-")[0])
    month = int(arg_date.split("-")[1])
    day = int(arg_date.split("-")[2])
    start_date = dt.datetime(year,month,day,0,0,0)

instrument = "BTC"
arg_instrument = args['instrument']
if not arg_instrument is None:
    instrument = arg_instrument


print("instrument: ", instrument, " start date: ", start_date)
interval = "5m"
arg_interval = args['interval']
if not arg_interval is None:
    interval = arg_interval

if interval == "5m" and "KLINE_INTERVAL_5MINUTE.csv" in os.listdir():
    kline_df = pd.read_csv("KLINE_INTERVAL_5MINUTE.csv")
else:
    kline_df = get_data(
        currency=instrument+"USDT",
        start_date=start_date,
        interval=interval)



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
#create folder
folder = "images/"
if not os.path.exists("images"):
    os.mkdir("images")

if not os.path.exists("images/"+str(instrument)):
    os.mkdir("images/"+str(instrument))
folder += str(instrument) + "/"

if not os.path.exists(folder + str(period)):
    os.mkdir(folder + str(period))

folder += str(period) + "/"



ready = set(os.listdir(folder))

def generate_image(row, name = "images/plot.png"):
    fig = plt.figure(figsize = (20,20))
    rev_row = np.flip(np.array(row)[1:]) #1: only input
    plt.plot(rev_row, 'k', linewidth=15.0)
    plt.axis('off')
    #plt.show()
    fig.savefig(name, dpi = 3)
    fig.clf()
    plt.close(fig)
    gc.collect()

df1 = image_data['upper_BB']
df2 = image_data['lower_BB']
df3 = image_data['middle_BB']
def gen_BB():
    for row1, row2, row3 in zip(df1.iloc, df2.iloc, df3.iloc):
        name = folder + str(row1.name).replace(" ", "T")[:16] + ";" + "BB" + ".png"
        if str(row1.name)[:16] + ";" + "BB" + ".png" in ready:
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
        #plt.show()
        fig.savefig(name, dpi = 3)
        fig.clf()
        plt.close(fig)
        gc.collect()

def gen_rest(col_name):
    global period, ready
    df = image_data[col_name]
    
    for row in df.iloc:
        if str(row.name).replace(" ", "T")[:16] + ";" + col_name + ".png" in ready:
            continue
        generate_image(row, folder + str(row.name).replace(" ", "T")[:16] + ";" + col_name + ".png")

arg_ind = args["indicator"]
if arg_ind is None:
    gen_BB()
    for indicator in ['close', 'ma', 'ADX0','ATR0', 'ARO0', 'WLR0']:
        gen_rest(indicator)
else:
    if arg_ind == "BB":
        gen_BB()
    else:
        gen_rest(arg_ind)