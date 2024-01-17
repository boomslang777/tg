from telethon import TelegramClient, events
import re
text = """Symbol : NSE:BANKNIFTY1!
Time : 2024-01-11 14:15:01 

Alert - Breakdown Detected 
NSE:BANKNIFTY1! price has closed below the marked low level of 47603.05

PCA-L $ 193.05 / PTM-HL $ 276.5 / BCS $ 308

 
OFA DATA

BUYERS in action.
DATE :: 2024-01-11 14:00:00

DELTA                161
===================
MAX_DELTA       182
MIN_DELTA       -46
===================4.0%
COT_HIGH          12
COT_LOW           3
===================0.25%
$VOLUME$         11.6K
OI                         2.4M
===================
    

 -Powered by BOT Office Assistant - Kate"""

# Define the regular expression pattern

# api_id = '25042394'
# api_hash = '8ee0191890aad20ce78034468178db27'
# bot_token = '6785415766:AAGUoJpWVn-8aJIIpgRF_wovRRSL8XDufes'

# bot = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

# @bot.on(events.NewMessage(chats=(1002140069507,)))
# async def handle_new_message(event):
#     sender = await event.get_sender()
#     print(f'Username: {sender.username}, Message: {event.message.text}')

# def main():
#     bot.run_until_disconnected()

# if __name__ == '__main__':
#     main()

def regex_parser():
    pattern = re.compile(r'Alert - (Breakout Detected|Breakdown Detected|Stop Loss hit)')

# Search for the pattern in the text
    match = pattern.search(text)

    # Extract the matched action
    if match:
        action = match.group(1)
        trade(action)
        print(action)
    else:
        print("No match found.")


import security


def trade(signal):
    print(f"{signal} is signal")
    import configparser
    import pyotp
    from jugaad_trader import Zerodha

    # Read credentials from config file
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
    print(login_response)
    margins = kite.margins()
    print(margins)
    ltp = kite.ltp("NSE:POLYCAB")
    print(ltp)
    if signal == "Stop Loss hit":
        security.cancel_orders(kite)
        security.square_off_all_positions(kite)
    elif signal == "Breakdown Detected":
        signal = -1
        security.fire(signal,kite)
    elif signal == "Breakout Detected":
        signal = 1
        security.fire(signal,kite)

regex_parser()    