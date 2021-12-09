import pyupbit
import datetime
import time, calendar
import numpy as np
import requests
access = "0hNyHckgUEQ0GpFb97xmHOtLGKx8AevNu7pzz2Vo"
secret = "NtOH4y4d3G2I4gG13G1KVhAYhPck2xWMxLd6xYvd"

def get_targetPrice(df, K) :
    range = df['high'][-2] - df['low'][-2]
    return df['open'][-1] + range * K

def buy_all(coin) :
    balance = invest
    if balance >= 5000 :
        upbit.buy_market_order(coin, balance)

def sell_all(coin) :
    balance = upbit.get_balance(coin)
    time.sleep(0.2)
    price = pyupbit.get_current_price(coin)
    time.sleep(0.2)
    if price * balance >= 5000 :
        upbit.sell_market_order(coin, balance)

def get_crr(df, fees, K) :
    df['range'] = df['high'].shift(1) - df['low'].shift(1)
    df['targetPrice'] = df['open'] + df['range'] * K
    df['drr'] = np.where(df['high'] > df['targetPrice'], (df['close'] / (1 + fees)) / (df['targetPrice'] * (1 + fees)) , 1)
    return df['drr'].cumprod()[-2]

def get_best_K(coin, fees) :
    max_crr = 0
    best_K = 0.5
    for k in np.arange(0.0, 1.0, 0.1) :
        crr = get_crr(df, fees, k)
        if crr > max_crr :
            max_crr = crr
            best_K = k
    return best_K

if __name__ == '__main__': 
    try:
        upbit = pyupbit.Upbit(access, secret)

        # set variable
        while True :
            K = 0.5
            fees = 0.002
            #______________-구매할 후보 목록 구하기_________________
            tickers = pyupbit.get_tickers(fiat="KRW")
            time.sleep(0.11)

            buy_list = []
            for ticker in tickers:
                df=pyupbit.get_ohlcv(ticker, interval='day1', count=21)
                time.sleep(0.2)
                mascore = 0
                df['closem'] = df['close'].shift(1)
                df['m_open'] = df['open'].shift(20)
                df['abs_m'] = df['m_open'] < df['closem']
                for days in range(3,21):
                    ma = df['closem'].rolling(days).mean().iloc[-1]
                    if df['closem'][-1] > ma:
                        mascore += 1
                if df['abs_m'][-1]:
                    targetPrice = get_targetPrice(df, get_best_K(ticker, fees))
                    buy_list.append([ticker, mascore, targetPrice])
            buy_list=sorted(buy_list, key=lambda x:x[1])
            if len(buy_list) > 7:
                buy_list = buy_list[-8:]
            print(buy_list)

            start_balance = upbit.get_balance("KRW")
            print("잔고확인")
            time.sleep(0.2)
            invest = start_balance/10

            now = datetime.datetime.now()
            while True:
                try:
                    if now.hour == 12 and now.minute == 00 :    # when am 09:02:00
                        for coin in buy_list:
                            balance = upbit.get_balance(coin)
                            time.sleep(0.2)
                            price = pyupbit.get_current_price(coin)
                            time.sleep(0.2)
                            if price * balance >= 5000 :
                                upbit.sell_market_order(coin, balance)
                                print("sell", coin)
                        time.sleep(43200)

                        tickers = pyupbit.get_tickers(fiat="KRW")
                        time.sleep(0.2)
                        buy_list = []
                        for ticker in tickers:
                            df=pyupbit.get_ohlcv(ticker, interval='day1', count=21)
                            time.sleep(0.2)
                            mascore = 0
                            df['closem'] = df['close'].shift(1)
                            df['m_open'] = df['open'].shift(20)
                            df['abs_m'] = df['m_open'] < df['closem']
                            for days in range(3,21):
                                ma = df['closem'].rolling(days).mean().iloc[-1]
                                if df['closem'][-1] > ma:
                                    mascore += 1
                            if df['abs_m'][-1]:
                                targetPrice = get_targetPrice(df, get_best_K(ticker, fees))
                                buy_list.append([ticker, mascore, targetPrice])
                        buy_list=sorted(buy_list, key=lambda x:x[1])
                        if len(buy_list) > 7:
                            buy_list = buy_list[-8:]

                        cur_balance = upbit.get_balance("KRW")
                        print("잔고확인")
                        if len(buy_list) > 0:
                            invest = (8*cur_balance)/(10*len(buy_list))
                        else:
                            invest = 0
                        time.sleep(1)

                    for coin in buy_list:
                        if coin[2] <= pyupbit.get_current_price(coin[0]) :
                            print(1)
                            balance = invest
                            meso=upbit.get_balance(coin[0])
                            print(2)
                            meso_price=pyupbit.get_current_price(coin[0])
                            print(3)
                            if meso*meso_price < 5000 :
                                upbit.buy_market_order(coin[0], balance)
                                print(4)
                                print("buy", coin)
                    
                    time.sleep(1)
                except Exception as e:
                    print(e)
                    time.sleep(1)

    except Exception as e:
        print(e)
        time.sleep(1)