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
havelist=[]
buyinglist = []
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
    df=pyupbit.get_ohlcv(ticker, interval='minute3', count=60)
    time.sleep(0.2)
    df['up'] = np.where(df.diff(1)['close'] > 0, df.diff(1)['close'], 0)
    df['down'] = np.where(df.diff(1)['close'] < 0, df.diff(1)['close']*(-1), 0)
    df['ua'] = df['up'].rolling(window=14).mean()
    df['da'] = df['down'].rolling(window=14).mean()
    df['RSI'] = df['ua']*100 / (df['da'] + df['ua'])
    df['fast_k']=100*((df['close']-df['low'].rolling(9).min()) / (df['high'].rolling(9).max()-df['low'].rolling(9).min()))
    df['slow_k']=df['fast_k'].rolling(3).mean()
    df['slow_d']=df['slow_k'].rolling(3).mean()
    slow_d = df['slow_d'][-2]
    slow_k = df['slow_k'][-2]

    RSI =  df['ua'][-2]*100 / (df['da'][-2] + df['ua'][-2])

def targeting():
    tickers = pyupbit.get_tickers(fiat="KRW")
    time.sleep(0.2)
    for coin in tickers:
        df=pyupbit.get_ohlcv(coin, interval='minute1', count=80)
        time.sleep(0.2)
        df['up'] = np.where(df.diff(5)['close'] > 0, df.diff(5)['close'], 0)
        df['down'] = np.where(df.diff(5)['close'] < 0, df.diff(5)['close']*(-1), 0)
        df['ua'] = df['up'].rolling(window=70).mean()
        df['da'] = df['down'].rolling(window=70).mean()
        df['RSI'] = df['ua']*100 / (df['da'] + df['ua'])
        df['fast_k']=100*((df['close']-df['low'].rolling(45).min()) / (df['high'].rolling(45).max()-df['low'].rolling(45).min()))
        df['slow_k']=df['fast_k'].rolling(15).mean()
        df['slow_d']=df['slow_k'].rolling(15).mean()
        slow_d = df['slow_d'][-2]
        slow_k = df['slow_k'][-2]

        RSI = df['ua'][-2]*100 / (df['da'][-2] + df['ua'][-2])
        if RSI < 100:
            if slow_d < slow_k < 100 :
                buyinglist.append(coin)
    print(buyinglist)
    

def trading():
    buyinglist=[]
    for coin in havelist:
        df=pyupbit.get_ohlcv(coin, interval='minute3', count=60)
        time.sleep(0.2)
        df['up'] = np.where(df.diff(1)['close'] > 0, df.diff(1)['close'], 0)
        df['down'] = np.where(df.diff(1)['close'] < 0, df.diff(1)['close']*(-1), 0)
        df['ua'] = df['up'].rolling(window=14).mean()
        df['da'] = df['down'].rolling(window=14).mean()
        df['RSI'] = df['ua']*100 / (df['da'] + df['ua'])
        df['fast_k']=100*((df['close']-df['low'].rolling(9).min()) / (df['high'].rolling(9).max()-df['low'].rolling(9).min()))
        df['slow_k']=df['fast_k'].rolling(3).mean()
        df['slow_d']=df['slow_k'].rolling(3).mean()
        slow_d = df['slow_d'][-2]
        slow_k = df['slow_k'][-2]

        RSI = df['ua'][-2]*100 / (df['da'][-2] + df['ua'][-2])
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
        buyinglist=[]

        tickers = pyupbit.get_tickers(fiat="KRW")
        time.sleep(0.2)
        for coin in tickers:
            df=pyupbit.get_ohlcv(coin, interval='minute3', count=60)
            time.sleep(0.2)
            df['up'] = np.where(df.diff(1)['close'] > 0, df.diff(1)['close'], 0)
            df['down'] = np.where(df.diff(1)['close'] < 0, df.diff(1)['close']*(-1), 0)
            df['ua'] = df['up'].rolling(window=14).mean()
            df['da'] = df['down'].rolling(window=14).mean()
            df['RSI'] = df['ua']*100 / (df['da'] + df['ua'])
            df['fast_k']=100*((df['close']-df['low'].rolling(9).min()) / (df['high'].rolling(9).max()-df['low'].rolling(9).min()))
            df['slow_k']=df['fast_k'].rolling(3).mean()
            df['slow_d']=df['slow_k'].rolling(3).mean()
            slow_d = df['slow_d'][-2]
            slow_k = df['slow_k'][-2]

            RSI = df['ua'][-2]*100 / (df['da'][-2] + df['ua'][-2])
            if RSI < 25:
                if slow_d < slow_k < 25 :
                    buyinglist.append(coin)
        
        print(buyinglist)
        buyinglist=list(set(buyinglist)-set(havelist))
        new_buyinglist=[]
        if len(buyinglist) == 0:
            print(len(buyinglist))
            pass
        elif 0<(krw*0.0001)<2:
            new_buyinglist.append(buyinglist[0])
        else:
            krwf = math.floor(krw*0.0001)
            if len(buyinglist) > krwf :
                new_buyinglist=buyinglist[0:krwf]
                print(new_buyinglist)
            elif (1 <= len(buyinglist)) and (len(buyinglist) <= krwf)  :
                new_buyinglist=buyinglist[0:len(buyinglist)]
                print(new_buyinglist)        
        print(new_buyinglist)
        for coin in new_buyinglist:
            upbit.buy_market_order(coin, 9995)
            havelist.append(coin)
            print("buy" + coin)
    time.sleep(1)
    print("cycle")
    buyinglist=[]

print("autotrade start")
upbit = pyupbit.Upbit(access, secret)

schedule.every().hour.at(":00:00").do(trading)
schedule.every().hour.at(":03:00").do(trading)
schedule.every().hour.at(":06:00").do(trading)
schedule.every().hour.at(":09:00").do(trading)
schedule.every().hour.at(":12:00").do(trading)
schedule.every().hour.at(":15:00").do(trading)
schedule.every().hour.at(":18:00").do(trading)
schedule.every().hour.at(":21:00").do(trading)
schedule.every().hour.at(":24:00").do(trading)
schedule.every().hour.at(":27:00").do(trading)
schedule.every().hour.at(":30:00").do(trading)
schedule.every().hour.at(":33:00").do(trading)
schedule.every().hour.at(":36:00").do(trading)
schedule.every().hour.at(":39:00").do(trading)
schedule.every().hour.at(":42:00").do(trading)
schedule.every().hour.at(":45:00").do(trading)
schedule.every().hour.at(":48:00").do(trading)
schedule.every().hour.at(":51:00").do(trading)
schedule.every().hour.at(":54:00").do(trading)
schedule.every().hour.at(":57:00").do(trading)

while True:
    schedule.run_pending()
    time.sleep(1)
