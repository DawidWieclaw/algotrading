import datetime as dt
import binance.client
import pandas as pd

class BinanceClient():
    column_names = [
        'open_time',
        'open',
        'high',
        'low',
        'close',
        'vol',
        'close_time',
        'quote_asset_volume',
        'number_of_trades',
        'taker_buy_base_asset_volume',
        'taker_buy_quote_asset_volume',
        'ignore'
    ]

    def __init__(self, interval):
        api_key = "vT0XoiF4FbrpHbH04ZEew6A9jOORd79J4RdmId0CTT6wwX97EuY9hPCBcp9F904f"
        api_secret = "wcpF4Ne1tNGbq5vPx2oaXrpbE2JnNXhn6tKV6I32uKNdBMuEazRfDPiMJkIVqVr8"
        self.client = binance.client.Client(api_key, api_secret)
        self.INTERVAL = interval

    def polish_kline(self, raw_kline):
        kline_d =  {
            'open_time': raw_kline[0],
            'open': raw_kline[1],
            'close': raw_kline[2],
            'low': raw_kline[3],
            'high': raw_kline[4],
            'vol': raw_kline[5]
        }
        kline_d['open_datetime'] = pd.to_datetime(kline_d['open_time'], unit='ms')
        return kline_d

    def historical_klines_generator(self, instrument, interval, start_dt, end_dt=None):
        for kline in self.client.get_historical_klines_generator(instrument, interval, str(start_dt), str(end_dt) if end_dt else None):
            yield self.polish_kline(kline)



def get_data(start_date = dt.datetime(2021,10,7,10,0,0), currency = "BTCUSDT"):
    client = BinanceClient(binance.client.Client.KLINE_INTERVAL_1HOUR)

    start_date = start_date #dt.datetime(2021,10,7,10,0,0)
    instrument = currency

    kline_df = pd.DataFrame(columns=["open","high","low","close","vol"])
    for kline in client.historical_klines_generator(instrument, client.INTERVAL, start_date):
        kline_df.loc[kline['open_datetime']] = (kline["open"], kline["high"], kline["low"], kline["close"], kline["vol"])


    kline_df.open = kline_df.open.astype(float)
    kline_df.close = kline_df.close.astype(float)
    kline_df.low = kline_df.low.astype(float)
    kline_df.high = kline_df.high.astype(float)
    kline_df.vol = kline_df.vol.astype(float)

    return kline_df