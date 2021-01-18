import robin_stocks as r
import json
import time
import getpass as gp
from timeloop import Timeloop
from datetime import timedelta as td

username = input('Your Robinhood email: ')
passw = gp.getpass('Your pass: ')

login = r.login(username,  passw)

# global flags to fulfill orders
sold = False
last_order_id = ""

tl = Timeloop()

SELL_PRICE = float(input('Your BTC target sell price: ') or '38700.00')
BUY_PRICE = float(input ('Your BTC target buy price: ') or '38100.00')
print("looking to buy at ", BUY_PRICE, " and sell at ", SELL_PRICE)

def get_btc_price_robin():
    btc_price = r.crypto.get_crypto_quote('BTC')['mark_price']
    return round(float(btc_price), 8)

def sell_btc():
    owned_bitcoin = get_owned_bitcoin()
    order = r.orders.order_sell_crypto_by_quantity('BTC', owned_bitcoin, priceType = 'mark_price')
    return order['id']

def check_order_status(order_id):
    data = r.orders.get_crypto_order_info(order_id)
    return data['state']


def buy_btc():
    buying_power = r.profiles.load_account_profile('portfolio_cash')
    buying_power = float(buying_power) - 20.00 # leeway for transaction fees
    order = r.orders.order_buy_crypto_by_price('BTC', buying_power, priceType = 'mark_price')
    return order['id']

def get_owned_bitcoin():
    owned = r.crypto.get_crypto_positions()
    for x in owned:
        if x['currency']['code'] == 'BTC':
            return round(float(x['quantity']),8)
    # If you don't own BTC, then return 0
    return 0
    
@tl.job(interval=td(seconds=1))
def trade_btc():
    global sold
    global last_order_id

    btc = get_btc_price_robin()
    print("current btc price:", btc)

    if last_order_id != "" and check_order_status(last_order_id) != "filled":
        return

    if (btc > SELL_PRICE) and not(sold):
        last_order_id = sell_btc()
        sold = True
        print("sold bitcoin at: ", btc)

    if sold and btc < BUY_PRICE:
        last_order_id = buy_btc()
        sold = False
        print("bought bitcoin at: ", btc)

if __name__ == "__main__":
    tl.start(block=True)



