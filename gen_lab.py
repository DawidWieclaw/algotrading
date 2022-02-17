import argparse
import os
import sys
import pandas as pd
from algotrading.influx.client import InfluxClient
from algotrading.config.influx import InfluxConfig
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

