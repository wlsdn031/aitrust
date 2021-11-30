import time
import pyupbit
import datetime
import schedule
from fbprophet import Prophet
import numpy as np

access = "0hNyHckgUEQ0GpFb97xmHOtLGKx8AevNu7pzz2Vo"
secret = "NtOH4y4d3G2I4gG13G1KVhAYhPck2xWMxLd6xYvd"

def get_target_price(ticker, k):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price

def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    return start_time

def get_balance(ticker):
    """잔고 조회"""
    balances = upbit.get_balances()
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

predicted_close_price = 0
predicted_high_price = 0
def predict_price(ticker):
    """Prophet으로 당일 종가, 최고가 가격 예측"""
    global predicted_close_price
    global predicted_high_price
    df = pyupbit.get_ohlcv(ticker, interval="minute60")
    df = df.reset_index()
    df['ds'] = df['index']
    df['y'] = df['close']
    data = df[['ds','y']]
    model = Prophet(daily_seasonality=10,weekly_seasonality=10,changepoint_prior_scale=0.3)
    model.fit(data)
    future = model.make_future_dataframe(periods=24, freq='H')
    forecast = model.predict(future)
    closeDf = forecast[forecast['ds'] == forecast.iloc[-1]['ds'].replace(hour=9)]
    if len(closeDf) == 0:
        closeDf = forecast[forecast['ds'] == data.iloc[-1]['ds'].replace(hour=9)]
    closeValue = closeDf['yhat'].values[0]
    MaxDf=forecast.iloc[-25:-1]
    MaxDf=MaxDf[::-1]
    highprice=list(MaxDf['yhat'])
    sort_high_price=sorted(highprice)
    predicted_high_price=sort_high_price[-1]
    predicted_close_price = closeValue

predict_price("KRW-BTC")
schedule.every().hour.do(lambda: predict_price("KRW-BTC"))

def get_ma5d(ticker):
    """5일 이동 평균선 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=5)
    ma5d = df['close'].rolling(5).mean().iloc[-1]
    return ma5d
print(predicted_high_price)
selling = False
"""떡락장 감지"""
def DduckRack(ticker):
    global selling
    df1510 = pyupbit.get_ohlcv(ticker, interval="minute15", count=10)
    ma150m = df1510['close'].rolling(15).mean().iloc[-1]
    df155 = pyupbit.get_ohlcv(ticker, interval="minute15", count=5)
    ma75m = df155['close'].rolling(15).mean().iloc[-1]
    if ma150m > ma75m :
        selling = True
    else:
        selling = False

DduckRack("KRW-BTC")
print(selling)




# 로그인
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")

# 자동매매 시작
while True:
    try:
        now = datetime.datetime.now()
        start_time = get_start_time("KRW-BTC")
        end_time = start_time + datetime.timedelta(days=1)
        schedule.run_pending()

        if start_time < now < end_time - datetime.timedelta(seconds=600):
            target_price = get_target_price("KRW-BTC", 0.36)
            ma5d = get_ma5d("KRW-BTC")
            DduckRack("KRW-BTC")
            current_price = get_current_price("KRW-BTC")
            if target_price < current_price and current_price < predicted_close_price:
                krw = get_balance("KRW")
                if krw > 5000:
                    upbit.buy_market_order("KRW-BTC", krw*0.9995)
                    print("buy")
            if predicted_close_price *1.05 < current_price and selling == True :
                btc = get_balance("BTC")
                if btc > 5000/current_price:
                    upbit.sell_market_order("KRW-BTC", btc*0.9995)
            time.sleep(1)
        else:
            btc = get_balance("BTC")
            if btc > 0.00008:
                upbit.sell_market_order("KRW-BTC", btc*0.9995)
        print("f")
        time.sleep(3)
    except Exception as e:
        print(e)
        time.sleep(3)