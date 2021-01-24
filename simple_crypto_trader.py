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

crypto = input('Crypto to trade: ')
buying_power = input('Buying_power: ')

SELL_PRICE = float(input('Your target sell price: ') or '38700.00')
BUY_PRICE = float(input ('Your target buy price: ') or '38100.00')
print("looking to buy at ", BUY_PRICE, " and sell at ", SELL_PRICE)

def get_crypto_price():
    global crypto
    btc_price = r.crypto.get_crypto_quote(crypto)['mark_price']
    return round(float(btc_price), 8)

def sell_crypto():
    global crypto
    owned_bitcoin = get_owned_crypto()
    order = r.orders.order_sell_crypto_by_quantity(crypto, owned_bitcoin, priceType = 'mark_price')
    return order['id']

def check_order_status(order_id):
    data = r.orders.get_crypto_order_info(order_id)
    return data['state']


def buy_crypto():
    global crypto
    global buying_power
    
    if buying_power == "full":
        buying_power = r.profiles.load_account_profile('portfolio_cash')
        buying_power = float(buying_power) - 20.00 # leeway for transaction fees
    else:
        buying_power = float(buying_power)
    order = r.orders.order_buy_crypto_by_price(crypto, buying_power, priceType = 'mark_price')
    return order['id']

def get_owned_crypto():
    owned = r.crypto.get_crypto_positions()
    for x in owned:
        if x['currency']['code'] == crypto:
            return round(float(x['quantity']),8)
    # If you don't own BTC, then return 0
    return 0
    
@tl.job(interval=td(seconds=1))
def trade_btc():
    global sold
    global last_order_id
    global crypto

    crypto_price = get_crypto_price()
    print("current ", crypto, " price:", crypto_price)

    if last_order_id != "" and check_order_status(last_order_id) != "filled":
        return

    if (crypto_price > SELL_PRICE) and not(sold):
        last_order_id = sell_crypto()
        sold = True
        print("sold bitcoin at: ", crypto_price)

    if sold and (crypto_price < BUY_PRICE):
        last_order_id = buy_crypto()
        sold = False
        print("bought bitcoin at: ",  crypto_price)

if __name__ == "__main__":
    tl.start(block=True)



