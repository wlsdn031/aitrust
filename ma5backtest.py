import time
import pyupbit
import datetime

access = "0hNyHckgUEQ0GpFb97xmHOtLGKx8AevNu7pzz2Vo"
secret = "NtOH4y4d3G2I4gG13G1KVhAYhPck2xWMxLd6xYvd"

selled = True

def get_ma5m5(ticker):
    """5*5분 이동 평균선 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="minute5", count=5)
    time.sleep(0.3)
    ma5 = df['close'].rolling(5).mean().iloc[-1]
    return ma5

def get_ma5m10(ticker):
    """10*5분 이동 평균선 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="minute5", count=10)
    time.sleep(0.15)
    ma10 = df['close'].rolling(10).mean().iloc[-1]
    return ma10

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



"""상승률 1위 찾기"""
def get_next_target():
    global goldname
    global goldcoin
    while goldname == "what":
        tickers = pyupbit.get_tickers(fiat="KRW")
        buying_candidate = []
        for ticker in tickers:
            ma5m5 = get_ma5m5(ticker)
            ma5m10 = get_ma5m10(ticker)
            if ma5m10 < ma5m5 :
                buying_candidate.append([ticker,get_current_price(ticker)])
        buyinglist = []
        for coin in buying_candidate:
            ma5m5=get_ma5m5(coin[0])
            coin[1] = ((coin[1]-ma5m5)/ma5m5)
            buyinglist.append(coin)
        sorted_buying = sorted(buyinglist, key=lambda x:x[1])
        goldname = "what"
        if len(sorted_buying) == 0:
            goldname = "pass"
        goldcoin=sorted_buying[-1:]
        goldcoin= goldcoin[0]
        print(goldcoin)
        if goldname == "pass":
            goldname = "what"
            print("retarget")
        elif goldcoin[1] < 0:
            goldname = "what"
            print("retarget")
        else:
            goldname=goldcoin[0]
        return goldname, goldcoin
            
goldname = "what"
# 로그인
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")
# 자동매매 시작
get_next_target()
while True:
    try:
        krw = get_balance("KRW")
        if selled==True:
            get_next_target()
            print(goldcoin, goldname)
            if goldcoin[1]>0.005:
                if krw > 5000:
                    upbit.buy_market_order(goldname, krw*0.9995)
                    selled = False
                else:
                    time.sleep(1)
        else:
            get_current_price(goldname)
            btname = goldname[4:]
            btc = get_balance(btname)
            if btc > 5050/get_current_price(goldname):
                ma5m10=get_ma5m10(goldname)
                ma5m5=get_ma5m5(goldname)
                if ma5m5 > ma5m10 :
                    time.sleep(1)
                else:
                    upbit.sell_market_order(goldname, btc*0.9995)
                    selled = True
                    goldname = "what"
        time.sleep(1)
    except Exception as e:
        print(e)
        time.sleep(1)