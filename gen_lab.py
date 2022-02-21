from BinanceClient import get_data
import binance.client
import datetime as dt
import pandas as pd
import numpy as np
import os
import datetime as dt
import json
import argparse


arguments = argparse.ArgumentParser()

arguments.add_argument("-c", "--instrument", required=False, help="cryptocurrency to predict pirce of (BTC, ETH, ...)")
arguments.add_argument("-p", "--period", required=False, help="period (in minutes)")
arguments.add_argument("-f", "--future", required=False, help="how far in future to start generating labels")


args = vars(arguments.parse_args())


#arguments
interval = binance.client.Client.KLINE_INTERVAL_5MINUTE

instrument = "BTC"
arg_instrument = args['instrument']
if not arg_instrument is None:
    instrument = arg_instrument


time_dif = 60
arg_time_dif = args['period']
if not arg_time_dif is None:
    time_dif = arg_time_dif

future = 60
arg_future = args['future']
if not arg_future is None:
    future = arg_future

folder_name = "images/" + instrument + "/" + str(np.max(list(map(lambda x : int(x),os.listdir("images/" + instrument)))))
dates = np.sort(list(map(lambda x:x.split(";")[0], filter(lambda x: "close" in x, os.listdir(folder_name+"/")))))




kline_df = 0
if not "KLINE_INTERVAL_5MINUTE.csv" in os.listdir():
    start_date = dt.datetime.strptime(dates[0], "%Y-%m-%dT%H:%M")
    kline_df = get_data(
            currency=instrument+"USDT",
            start_date=start_date,
            interval=interval)
    kline_df.to_csv("KLINE_INTERVAL_5MINUTE.csv")
else:
    kline_df = pd.read_csv("KLINE_INTERVAL_5MINUTE.csv")
#kline_df.head()

kline_df = kline_df.rename(columns={kline_df.columns[0] :'time'}, inplace = False)
kline_df.time = kline_df.time.map(lambda x: str(x).replace(" ", "T"))

zip_iter_close = zip(kline_df.time, kline_df.close)
zip_iter_high = zip(kline_df.time, kline_df.close)
zip_iter_low = zip(kline_df.time, kline_df.close)


dic_close = dict(zip_iter_close)
dic_high = dict(zip_iter_high)
dic_low = dict(zip_iter_low)

ratios = {}
unsupported = []

for date in dates:
    date += ":00"
    dt_date = dt.datetime.strptime(date, "%Y-%m-%dT%H:%M:%S") + dt.timedelta(minutes = future)
    maxval = np.min(list(dic_high.values())) - 1.0
    prev_max = maxval
    minval = np.max(list(dic_low.values())) + 1.0
    prev_max, prev_min = maxval, minval
    if not date in dic_close.keys():
        continue
    cur_val = dic_close[date]
    #mean_val = 0
    for delta in range(0, time_dif, 5):
        #print(delta)
        
        dt_date += dt.timedelta(minutes = delta)
        str_date = dt_date.strftime("%Y-%m-%dT%H:%M:%S")
        if not str_date in dic_high.keys():
            #unsupported.append(date)
            continue
        maxval = np.max([maxval, dic_high[str_date]])
        minval = np.min([minval, dic_low[str_date]])
        #mean_val += 
    if maxval == prev_max or minval == prev_min:
        unsupported.append(date)
        continue
    ratios[date[:-3]] = [maxval/cur_val-1., minval/cur_val-1.]

if len(unsupported) != 0:
    raise NotImplementedError("unsopprted list is not empty")

ratios_file = open("ratios.json", "w")
json.dump(ratios, ratios_file)
ratios_file.close()