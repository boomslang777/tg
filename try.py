import re
import configparser
import pyotp
from jugaad_trader import Zerodha
from telethon import TelegramClient, events, sync
import security
import asyncio
config = configparser.ConfigParser()
config.read('creds.ini')
user_id = config['DEFAULT']['user_id']
password = config['DEFAULT']['password']
totp_secret = config['DEFAULT']['totp_secret']


# Initialize TOTP with the secret key
otp_gen = pyotp.TOTP(totp_secret)

# Generate current OTP
current_otp = otp_gen.now()

# Initialize Zerodha class with credentials and OTP
kite = Zerodha(user_id=user_id, password=password, twofa=current_otp)

# Login to Zerodha
login_response = kite.login()
margins = kite.margins()
print(margins)
ltp = kite.ltp("NSE:POLYCAB")
print(ltp)
print(login_response)

def place_order(instrument, qty):
    print(instrument)
    if qty >0 and qty < 900 :
        kite.place_order(variety=kite.VARIETY_REGULAR, exchange="NFO",
                        tradingsymbol=instrument,
                        transaction_type="BUY",
                        quantity=qty,
                        order_type="MARKET",
                        product="MIS",
                        validity="DAY",
                        price=0,
                        trigger_price=0)
        print("Position entered successfully")
    else :
        legs = qty//900
        if qty%900 != 0 :
            legs += 1
        kite.place_order(variety=kite.VARIETY_ICEBERG,exchange = "NFO"
                         ,tradingsymbol=instrument,transaction_type = 'BUY',quantity=qty,
                         order_type="MARKET",product="MIS",validity="DAY",
                         iceberg_legs = legs,price =0,trigger_price =0,iceberg_quantity=900)
        
# place_order("BANKNIFTY2411748200CE",15)  
def square_off_all_positions():
    # Fetch current positions
    positions =  kite.positions()
    # Iterate through each position type ('net', 'day')
    for position_type in ['net']:
        # Iterate through positions of the current type
        for position in positions.get(position_type, []):
            # Extract relevant information
            tradingsymbol = position['tradingsymbol']
            quantity = position['quantity']
            if quantity > 0 and quantity < 900:
                # Place a market sell order to square off the position
                order_id = kite.place_order(variety=kite.VARIETY_REGULAR,
                                            exchange=kite.EXCHANGE_NFO,
                                            tradingsymbol=tradingsymbol,
                                            transaction_type=kite.TRANSACTION_TYPE_SELL,
                                            quantity=quantity,
                                            product=kite.PRODUCT_MIS,
                                            order_type=kite.ORDER_TYPE_MARKET,
                                            tag="SquareOff")

                # Print information about the square off order
                print(f"Square off order placed for {tradingsymbol} with order id {order_id}")
            # else :
            #     legs = quantity//900
            #     # remaining_qty = quantity % 900
            #     order_id = await kite.place_order(variety=kite.VARIETY_ICEBERG,exchange=kite.EXCHANGE_NFO,tradingsymbol=tradingsymbol,transaction_type=kite.TRANSACTION_TYPE_SELL,quantity=quantity,product=kite.MIS,iceberg_legs=legs+1,order_type=kite.ORDER_TYPE_MARKET)
            #     print("All orders squared off")
            #     message = "All positions squared off"
            #     entity = await bot.get_entity(1002140069507)  # Replace 'your_channel_username' with your channel's username
            #     print(entity.id)
            #     group_id = entity.id

            #     # Now use the obtained group_id in the send_message call
            #     await bot.send_message(group_id, message)      
                
square_off_all_positions()                