import math
import pyupbit
import numpy as np
import openpyxl
import pandas as pd    
import time
import schedule
import datetime

access = "0hNyHckgUEQ0GpFb97xmHOtLGKx8AevNu7pzz2Vo"
secret = "NtOH4y4d3G2I4gG13G1KVhAYhPck2xWMxLd6xYvd"

buyinglist = []
havelist = []
def get_balance(ticker):
    """잔고 조회"""
    balances = upbit.get_balances()
    time.sleep(0.2)
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0
    return 0

def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(ticker=ticker)["orderbook_units"][0]["ask_price"]
    time.sleep(0.2)


def checking(ticker):
    df=pyupbit.get_ohlcv(ticker, interval='minute5', count=15)
    time.sleep(0.2)
    df['up'] = np.where(df.diff(1)['close'] > 0, df.diff(1)['close'], 0)
    df['down'] = np.where(df.diff(1)['close'] < 0, df.diff(1)['close']*(-1), 0)
    df['ua'] = df['up'].rolling(window=14).mean()
    df['da'] = df['down'].rolling(window=14).mean()
    df['RSI'] = df['ua']*100 / (df['da'] + df['ua'])
    df['fast_k']=100*((df['close']-df['low'].rolling(9).min()) / (df['high'].rolling(9).max()-df['low'].rolling(9).min()))
    df['slow_k']=df['fast_k'].rolling(3).mean()
    df['slow_d']=df['slow_k'].rolling(3).mean()
    slow_d = df['slow_d'][-1]
    slow_k = df['slow_k'][-1]

    RSI = (df['RSI'][-1] + df['RSI'][-2])/2

def targeting():
    tickers = pyupbit.get_tickers(fiat="KRW")
    time.sleep(0.2)
    for coin in tickers:
        df=pyupbit.get_ohlcv(coin, interval='minute5', count=15)
        time.sleep(0.2)
        df['up'] = np.where(df.diff(1)['close'] > 0, df.diff(1)['close'], 0)
        df['down'] = np.where(df.diff(1)['close'] < 0, df.diff(1)['close']*(-1), 0)
        df['ua'] = df['up'].rolling(window=14).mean()
        df['da'] = df['down'].rolling(window=14).mean()
        df['RSI'] = df['ua']*100 / (df['da'] + df['ua'])
        df['fast_k']=100*((df['close']-df['low'].rolling(3).min()) / (df['high'].rolling(3).max()-df['low'].rolling(3).min()))
        df['slow_k']=df['fast_k'].rolling(3).mean()
        df['slow_d']=df['slow_k'].rolling(3).mean()
        slow_d = df['slow_d'][-1]
        slow_k = df['slow_k'][-1]
        RSI = (df['RSI'][-1] + df['RSI'][-2])/2
        
        if RSI < 25:
            if slow_d < slow_k < 25 :
                buyinglist.append(coin)
    print(buyinglist)

print("autotrade start")
upbit = pyupbit.Upbit(access, secret)

while True:
    try:
        for coin in havelist:
            df=pyupbit.get_ohlcv(coin, interval='minute5', count=15)
            time.sleep(0.2)
            df['up'] = np.where(df.diff(1)['close'] > 0, df.diff(1)['close'], 0)
            df['down'] = np.where(df.diff(1)['close'] < 0, df.diff(1)['close']*(-1), 0)
            df['ua'] = df['up'].rolling(window=14).mean()
            df['da'] = df['down'].rolling(window=14).mean()
            df['RSI'] = df['ua']*100 / (df['da'] + df['ua'])
            df['fast_k']=100*((df['close']-df['low'].rolling(9).min()) / (df['high'].rolling(9).max()-df['low'].rolling(9).min()))
            df['slow_k']=df['fast_k'].rolling(3).mean()
            df['slow_d']=df['slow_k'].rolling(3).mean()
            slow_d = df['slow_d'][-1]
            slow_k = df['slow_k'][-1]

            RSI = (df['ua'][-1] / (df['ua'][-1]+df['da'][-1])) * 100
            if RSI > 65:
                if 75 < slow_k < slow_d: 
                    btc = get_balance(coin[4:])
                    upbit.sell_market_order(coin, btc*0.9995)
                    havelist.remove(coin)
                    print("sell", coin)
                else:
                    pass
            else:
                pass
        krw = get_balance("KRW")
        print(buyinglist)
        
        if 8000 < krw:
            targeting()
            buyinglist=list(set(buyinglist)-set(havelist))
            new_buyinglist=[]
            if len(buyinglist) == 0:
                pass
            elif 0<(krw*0.0001)<2:
                new_buyinglist.append(buyinglist[0])
            else:
                krwf = math.floor(krw*0.0001)
                if len(buyinglist) > krwf :
                    new_buyinglist=buyinglist[0:krwf]
                elif 1 <= len(buyinglist) and len(buyinglist) <= krwf  :
                    new_buyinglist=buyinglist[0:len(buyinglist)]
            print(new_buyinglist)
            for coin in new_buyinglist:
                upbit.buy_market_order(coin, 9995)
                havelist.append(coin)
                print("buy" + coin)
        time.sleep(1)
        print("cycle")
        buyinglist=[]
    except Exception as e:
        print(e)
        time.sleep(1)