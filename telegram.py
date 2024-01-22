
import re
import configparser
import pyotp
from jugaad_trader import Zerodha
from telethon import TelegramClient, events, sync
import security
import asyncio
api_id = '25042394'
api_hash = '8ee0191890aad20ce78034468178db27'
bot_token = '6785415766:AAGUoJpWVn-8aJIIpgRF_wovRRSL8XDufes'

bot = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)
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
async def regex_parser(text):
    print(text)
    pattern = re.compile(r'Alert - (Breakout Detected|Breakdown Detected|Stop Loss hit)')

    # Search for the pattern in the text
    match = pattern.search(text)

    # Extract the matched action
    if match:
        action = match.group(1)
        await trade(action)
        print(action)
    else:
        print("No match found.")

async def trade(signal):
    print(f"{signal} is signal")

    # Read credentials from config file
    #kite.place_order(variety=kite.VARIETY_ICEBERG,exchange=kite.EXCHANGE_NFO,tradingsymbol=tradingsymbol,transaction_type=kite.TRANSACTION_TYPE_SELL,quantity=quantity,product=kite.MIS,iceberg_legs=4,order_type=)
    
    if signal == "Stop Loss hit":
        # Assuming cancel_orders and square_off_all_positions functions are defined in the security module
        await security.cancel_orders(kite)
        await security.square_off_all_positions(kite)
    elif signal == "Breakdown Detected":
        signal = -1
        # Assuming fire function is defined in the security module
        print(bot)
        await security.fire(signal, kite,bot)
    elif signal == "Breakout Detected":
        signal = 1
        # Assuming fire function is defined in the security module
        print(bot)
        await security.fire(signal, kite,bot)
    elif signal == "Move stop loss to entry point": 
        security.cancel_orders(kite)
        await security.move_sl(kite)

@bot.on(events.NewMessage(chats=(1002140069507)))
async def handle_new_message(event):
    sender = await event.get_sender()
    content = event.message.text
    if content == '/EXT' :
        print("positions squaring off")
        await security.square_off_all_positions(kite,bot)
    elif content == '/CTC' :
        print("Cost to cost")
        await security.ctc(kite,bot)
    # Call the regex_parser function with the message content
    await regex_parser(content)

    print(f'Username: {sender.username}, Message: {content}')

def main():
    bot.run_until_disconnected()

if __name__ == '__main__':
    main()

